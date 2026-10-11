"""
DEMO RESEARCH TOOLS — MOCK DATA ONLY

These tools return pre-built mock data for demonstration purposes.
They are clearly labeled to prevent confusion with real market data.
Real connectors (Amazon API, keyword research APIs) are pending authorization
and will replace these when approved and configured.

Do NOT use this data to make real publishing decisions.
"""
from __future__ import annotations
import json
from datetime import datetime, timezone


DEMO_DISCLAIMER = (
    'DEMO DATA: This is simulated market data for demonstration purposes only. '
    'Do not make publishing decisions based on this data. '
    'Real connector (pending_authorization) will provide live data when configured.'
)


def search_web_demo(query: str, max_results: int = 5) -> dict:
    """
    DEMO ONLY: Returns simulated web search results.
    Real implementation requires: web search API authorization.
    Status: pending_authorization
    """
    return {
        'disclaimer': DEMO_DISCLAIMER,
        'query': query,
        'results': [
            {
                'title': f'[DEMO] Article about {query}',
                'url': 'https://example.com/demo',
                'snippet': f'[DEMO DATA] This is a simulated search result for "{query}". Real data pending API authorization.',
                'source_type': 'demo',
                'relevance': 0.8,
            }
        ] * min(max_results, 3),
        'total_found': 3,
        'freshness': 'demo',
        'connector_status': 'pending_authorization',
    }


def analyze_keywords_demo(seed_keywords: list[str], market: str = 'amazon_us') -> dict:
    """
    DEMO ONLY: Returns simulated keyword competition data.
    Real implementation requires: keyword research API authorization.
    Status: pending_authorization
    """
    return {
        'disclaimer': DEMO_DISCLAIMER,
        'market': market,
        'keywords': [
            {
                'keyword': kw,
                'monthly_search_volume': '[DEMO: ~1000-5000]',
                'competition_level': 'medium',
                'kdp_backend_eligible': True,
                'note': 'DEMO DATA: Real volume data requires authorized keyword API',
            }
            for kw in seed_keywords[:7]
        ],
        'connector_status': 'pending_authorization',
        'analyzed_at': datetime.now(timezone.utc).isoformat(),
    }


def get_amazon_bestsellers_demo(category_url: str) -> dict:
    """
    DEMO ONLY: Returns simulated Amazon bestseller data.
    IMPORTANT: Direct Amazon scraping violates ToS. Real implementation
    requires Amazon Product Advertising API authorization.
    Status: pending_authorization
    """
    return {
        'disclaimer': DEMO_DISCLAIMER,
        'category_url': category_url,
        'note': 'Amazon scraping is not authorized. This returns demo data only.',
        'bestsellers': [
            {
                'rank': i,
                'title': f'[DEMO] Example Bestseller #{i}',
                'asin': f'DEMOASIN{i:04d}',
                'price_usd': 9.99 + i * 0.50,
                'review_count': '[DEMO: ~500-2000]',
                'rating': 4.2 + (i % 8) * 0.1,
                'source': 'demo_only',
            }
            for i in range(1, 11)
        ],
        'connector_status': 'pending_authorization',
        'scraped_at': datetime.now(timezone.utc).isoformat(),
    }
