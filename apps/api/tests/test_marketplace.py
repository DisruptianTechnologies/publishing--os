import pytest
import os
import sys

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
sys.path.insert(0, root_dir)
sys.path.insert(0, os.path.join(root_dir, 'packages'))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.marketplace import MarketplaceAccount
from services.marketplace_service import KDPConnector, EtsyConnector, get_connector


@pytest.mark.asyncio
async def test_kdp_connector_pending_authorization():
    account = MarketplaceAccount(
        tenant_id="tenant-123",
        marketplace="kdp",
        name="Amazon KDP Test Account",
        auth_status="pending_authorization",
    )
    connector = get_connector(account)
    assert isinstance(connector, KDPConnector)

    conn_status = await connector.test_connection()
    assert conn_status["success"] is False
    assert conn_status["status"] == "pending_authorization"


@pytest.mark.asyncio
async def test_kdp_connector_sandbox_submission():
    account = MarketplaceAccount(
        tenant_id="tenant-123",
        marketplace="kdp",
        name="Amazon KDP Test Account",
        auth_status="authorized",
    )
    connector = KDPConnector(account)
    submission = await connector.submit_listing({"title": "Mindful Productivity Handbook", "price_usd": 4.99})

    assert submission["success"] is True
    assert submission["marketplace"] == "kdp"
    assert submission["external_listing_id"].startswith("B0")
    assert "amazon.com/dp/" in submission["listing_url"]


@pytest.mark.asyncio
async def test_etsy_connector_sandbox_submission():
    account = MarketplaceAccount(
        tenant_id="tenant-123",
        marketplace="etsy",
        name="Etsy Printables Shop",
        auth_status="authorized",
    )
    connector = EtsyConnector(account)
    submission = await connector.submit_listing({"title": "Daily Habit Planner PDF", "price_usd": 3.50})

    assert submission["success"] is True
    assert submission["marketplace"] == "etsy"
    assert "ETSY-" in submission["external_listing_id"]
