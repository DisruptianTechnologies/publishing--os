"""
AudienceOS service.
Manages permission-based audience growth, first-class consent records,
content safety scanning, nurture sequences, and global kill switches.
"""
from __future__ import annotations
import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models.audience import (
    SubscriberProfile,
    ConsentRecord,
    ContentDraft,
    ContentOpportunity,
    GlobalKillSwitch,
    NurtureSequence,
)
from packages.policy_engine.engine import get_policy_engine, PolicyAction

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Global Kill Switch Management
# ---------------------------------------------------------------------------
async def check_kill_switch(db: AsyncSession, tenant_id: str, scope: str) -> bool:
    """
    Returns True if an active kill switch exists for this scope or all_outreach.
    """
    res = await db.execute(
        select(GlobalKillSwitch).where(
            GlobalKillSwitch.tenant_id == tenant_id,
            GlobalKillSwitch.is_active == True,
            GlobalKillSwitch.scope.in_([scope, 'all_outreach']),
        )
    )
    switch = res.scalars().first()
    return switch is not None


async def toggle_kill_switch(
    db: AsyncSession,
    tenant_id: str,
    scope: str,
    is_active: bool,
    user_id: str | None = None,
    reason: str = '',
) -> GlobalKillSwitch:
    res = await db.execute(
        select(GlobalKillSwitch).where(
            GlobalKillSwitch.tenant_id == tenant_id,
            GlobalKillSwitch.scope == scope,
        )
    )
    switch = res.scalars().first()

    now = datetime.now(timezone.utc)
    if not switch:
        switch = GlobalKillSwitch(
            tenant_id=tenant_id,
            scope=scope,
            is_active=is_active,
            activated_by=user_id if is_active else None,
            reason=reason,
            activated_at=now if is_active else None,
            deactivated_at=now if not is_active else None,
        )
        db.add(switch)
    else:
        switch.is_active = is_active
        switch.reason = reason
        if is_active:
            switch.activated_by = user_id
            switch.activated_at = now
            switch.deactivated_at = None
        else:
            switch.deactivated_at = now

    await db.commit()
    await db.refresh(switch)
    return switch


# ---------------------------------------------------------------------------
# Subscriber & Consent Engine
# ---------------------------------------------------------------------------
async def register_subscriber_with_consent(
    db: AsyncSession,
    tenant_id: str,
    email: str,
    first_name: str = '',
    last_name: str = '',
    source: str = 'landing_page',
    tags: list[str] | None = None,
    consent_granted: bool = True,
    opt_in_mechanism: str = 'form_submit',
    ip_address: str = '',
    user_agent: str = '',
) -> SubscriberProfile:
    """
    Registers a subscriber and atomically binds an immutable ConsentRecord.
    If consent is not granted, subscriber is flagged as unconfirmed/suppressed.
    """
    clean_email = email.strip().lower()

    # Look up existing
    res = await db.execute(
        select(SubscriberProfile).where(
            SubscriberProfile.tenant_id == tenant_id,
            SubscriberProfile.email == clean_email,
        )
    )
    subscriber = res.scalars().first()

    status = 'active' if consent_granted else 'unconfirmed'

    if not subscriber:
        subscriber = SubscriberProfile(
            tenant_id=tenant_id,
            email=clean_email,
            first_name=first_name,
            last_name=last_name,
            source=source,
            status=status,
            tags=tags or [],
        )
        db.add(subscriber)
        await db.flush()
    else:
        subscriber.status = status
        if first_name:
            subscriber.first_name = first_name
        if last_name:
            subscriber.last_name = last_name

    # Create immutable ConsentRecord
    consent = ConsentRecord(
        tenant_id=tenant_id,
        subscriber_id=str(subscriber.id),
        consent_type='email_marketing',
        granted=consent_granted,
        legal_basis='explicit_opt_in',
        opt_in_mechanism=opt_in_mechanism,
        ip_address=ip_address,
        user_agent=user_agent,
        consent_timestamp=datetime.now(timezone.utc),
    )
    db.add(consent)

    await db.commit()
    await db.refresh(subscriber)
    return subscriber


async def revoke_subscriber_consent(
    db: AsyncSession,
    tenant_id: str,
    email: str,
    reason: str = 'user_unsubscribe',
) -> bool:
    """
    Revokes consent and marks subscriber suppressed.
    """
    clean_email = email.strip().lower()
    res = await db.execute(
        select(SubscriberProfile).where(
            SubscriberProfile.tenant_id == tenant_id,
            SubscriberProfile.email == clean_email,
        )
    )
    subscriber = res.scalars().first()
    if not subscriber:
        return False

    subscriber.status = 'unsubscribed'

    # Find latest consent record and revoke
    c_res = await db.execute(
        select(ConsentRecord).where(
            ConsentRecord.subscriber_id == subscriber.id,
            ConsentRecord.revoked_at == None,
        )
    )
    active_consents = c_res.scalars().all()
    now = datetime.now(timezone.utc)
    for c in active_consents:
        c.revoked_at = now
        c.revocation_reason = reason

    await db.commit()
    return True


# ---------------------------------------------------------------------------
# Content Safety & Policy Scanner
# ---------------------------------------------------------------------------
FORBIDDEN_OUTREACH_PATTERNS = [
    'dm me for',
    'click the link in my bio to buy',
    'guaranteed 10k/month',
    'guaranteed #1 bestseller',
    'buy my course',
    'send me a direct message',
    'limited time discount for reddit users',
]


def audit_content_draft_safety(body: str, platform: str) -> tuple[str, list[str]]:
    """
    Scans content against platform policy constraints and spam patterns.
    Returns (policy_status, policy_flags).
    """
    flags = []
    lower_body = body.lower()

    for pattern in FORBIDDEN_OUTREACH_PATTERNS:
        if pattern in lower_body:
            flags.append(f"Forbidden outreach/spam pattern detected: '{pattern}'")

    if platform == 'reddit' and ('http://' in lower_body or 'https://' in lower_body):
        # Value-first rule: pure link posts or affiliate drops violate subreddit self-promo rules
        if len(lower_body.split()) < 50:
            flags.append("Short post with direct links may violate subreddit self-promotion rules. Ensure value-first context.")

    if len(flags) == 0:
        return 'compliant', []
    elif any('Forbidden' in f for f in flags):
        return 'blocked', flags
    else:
        return 'needs_review', flags
