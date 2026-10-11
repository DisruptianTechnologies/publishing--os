import pytest
import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'packages'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.audience_service import audit_content_draft_safety


def test_content_draft_safety_compliant():
    safe_body = (
        "Here is a breakdown of how we validated our non-fiction book topic using real category analysis. "
        "Notice the distinction between search volume and commercial buyer intent. Hope this helps anyone preparing their launch!"
    )
    status, flags = audit_content_draft_safety(safe_body, platform="reddit")
    assert status == "compliant"
    assert len(flags) == 0


def test_content_draft_safety_blocks_spam_phrases():
    spam_body = "Hey! Check out my guaranteed #1 bestseller system. DM me for the full cheat sheet!"
    status, flags = audit_content_draft_safety(spam_body, platform="reddit")
    assert status == "blocked"
    assert any("dm me for" in f for f in flags)
    assert any("guaranteed #1 bestseller" in f for f in flags)


def test_content_draft_safety_warns_short_links_on_reddit():
    short_promo = "Read my new book at https://example.com/book"
    status, flags = audit_content_draft_safety(short_promo, platform="reddit")
    assert status == "needs_review"
    assert any("subreddit self-promotion" in f for f in flags)
