"""
Authentication and tenant context resolution.
Supports Clerk JWT (with real JWKS verification) and demo mode.
"""
from __future__ import annotations
import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

import httpx
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_async_db
from core.config import settings
from models.tenant import User, Tenant

logger = logging.getLogger(__name__)

# Cache Clerk JWKS in memory (refreshed on JWTError to handle key rotation)
_jwks_cache: dict | None = None
_jwks_cache_url: str = ''


@dataclass
class TenantContext:
    user_id: str
    tenant_id: str
    email: str
    roles: list[str]
    is_demo: bool


async def _fetch_clerk_jwks() -> dict:
    """Fetch Clerk's JWKS. Returns the keys dict."""
    global _jwks_cache, _jwks_cache_url
    if not settings.CLERK_PUBLISHABLE_KEY:
        raise HTTPException(status_code=401, detail='Clerk not configured')

    # Derive JWKS URL from publishable key: pk_test_xxx -> https://xxx.clerk.accounts.dev/.well-known/jwks.json
    # Full URL pattern: https://<frontend-api-host>/.well-known/jwks.json
    # Clerk exposes it at: https://api.clerk.com/v1/jwks
    jwks_url = 'https://api.clerk.com/v1/jwks'

    if _jwks_cache and _jwks_cache_url == jwks_url:
        return _jwks_cache

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            headers = {'Authorization': f'Bearer {settings.CLERK_SECRET_KEY}'}
            resp = await client.get(jwks_url, headers=headers)
            resp.raise_for_status()
            _jwks_cache = resp.json()
            _jwks_cache_url = jwks_url
            return _jwks_cache
    except Exception as e:
        logger.error(f'Failed to fetch Clerk JWKS: {e}')
        raise HTTPException(status_code=503, detail='Auth service unavailable')


async def verify_clerk_token(token: str) -> dict:
    """
    Verify a Clerk JWT.
    - In DEMO_MODE with demo-token: return demo payload.
    - Otherwise fetch JWKS and verify signature.
    """
    global _jwks_cache

    if settings.DEMO_MODE and token == 'demo-token':
        return {'sub': settings.DEMO_USER_ID, 'email': 'demo@kindlepreneur.dev'}

    try:
        # Get unverified header to find the key id
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')

        if not settings.CLERK_SECRET_KEY:
            # No Clerk configured — decode without verification for dev
            logger.warning('CLERK_SECRET_KEY not set; skipping signature verification (dev mode only)')
            payload = jwt.decode(token, '', algorithms=['RS256', 'HS256'],
                                 options={'verify_signature': False, 'verify_exp': True})
            return payload

        # Fetch JWKS and find matching key
        jwks = await _fetch_clerk_jwks()
        keys = jwks.get('keys', [])
        public_key = None
        for key in keys:
            if key.get('kid') == kid:
                from jose.backends import RSAKey
                public_key = RSAKey(key, algorithm='RS256')
                break

        if public_key is None and keys:
            # Try first available key
            from jose.backends import RSAKey
            public_key = RSAKey(keys[0], algorithm='RS256')

        if public_key is None:
            raise HTTPException(status_code=401, detail='No matching signing key found')

        payload = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            options={'verify_exp': True, 'verify_aud': False},
        )
        return payload

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail='Token expired')
    except JWTError as e:
        logger.warning(f'JWT verification failed: {e}')
        # Invalidate JWKS cache to handle key rotation
        _jwks_cache = None
        raise HTTPException(status_code=401, detail='Invalid token')


async def _provision_user_and_tenant(
    db: AsyncSession,
    clerk_user_id: str,
    email: str,
    display_name: str = '',
) -> User:
    """
    Auto-provision a Tenant + User on first login.
    Creates a new tenant scoped to this user.
    """
    # Create tenant
    tenant_slug = email.split('@')[0].lower().replace('.', '-')[:80]
    tenant = Tenant(
        id=str(uuid.uuid4()),
        name=f"{display_name or email}'s Workspace",
        slug=f'{tenant_slug}-{str(uuid.uuid4())[:8]}',
        plan='free',
        settings={},
        feature_flags={},
        is_active=True,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(tenant)
    await db.flush()

    # Create user
    user = User(
        id=str(uuid.uuid4()),
        tenant_id=str(tenant.id),
        clerk_user_id=clerk_user_id,
        email=email,
        display_name=display_name or email,
        roles=['owner'],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    logger.info(f'Provisioned new tenant {tenant.id} and user {user.id} for {email}')
    return user


async def get_tenant_context(
    request: Request,
    db: AsyncSession,
) -> Optional[TenantContext]:
    """Extract and resolve TenantContext from request."""
    auth_header = request.headers.get('Authorization', '')
    token = None

    if auth_header.startswith('Bearer '):
        token = auth_header[7:].strip()

    # Demo mode fallback
    if not token and settings.DEMO_MODE:
        return TenantContext(
            user_id=settings.DEMO_USER_ID,
            tenant_id=settings.DEMO_TENANT_ID,
            email='demo@kindlepreneur.dev',
            roles=['admin'],
            is_demo=True,
        )

    if not token:
        return None

    # Verify token
    payload = await verify_clerk_token(token)
    clerk_user_id = payload.get('sub', '')
    email = payload.get('email', payload.get('email_address', ''))
    display_name = payload.get('name', '')

    if not clerk_user_id:
        raise HTTPException(status_code=401, detail='Invalid token: missing sub')

    # Look up user
    result = await db.execute(
        select(User).where(User.clerk_user_id == clerk_user_id)
    )
    user = result.scalars().first()

    # Auto-provision on first login
    if not user:
        logger.info(f'First login for {email}, provisioning tenant/user')
        user = await _provision_user_and_tenant(db, clerk_user_id, email, display_name)

    return TenantContext(
        user_id=str(user.id),
        tenant_id=str(user.tenant_id),
        email=user.email,
        roles=list(user.roles or ['author']),
        is_demo=False,
    )


async def require_auth(
    request: Request,
    db: AsyncSession = Depends(get_async_db),
) -> TenantContext:
    """FastAPI dependency: returns TenantContext or raises 401."""
    ctx = await get_tenant_context(request, db)
    if not ctx:
        raise HTTPException(status_code=401, detail='Authentication required')
    return ctx
