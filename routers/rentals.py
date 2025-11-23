"""Router for rental property endpoints."""

from fastapi import APIRouter, Query

from models.results import ListingResult
from scrapers.rentals import get_rentals_klaz, build_search_url
from utils.browser import PlaywrightManager
from utils.cache import build_cache_key, get_cached_value, set_cached_value
from config import CACHE_TTL_SECONDS

router = APIRouter(prefix="/rentals", tags=["rentals"])


@router.get("/")
async def get_rentals(
    postal_code: str = Query("74072", description="Postal code for the search location"),
    category: str = Query("c203", description="Category code (c203 = Wohnung Mieten)"),
    location_id: str = Query("l9245", description="Optional location ID (e.g., l9245)"),
    radius: int = Query(5, ge=1, le=100, description="Search radius in km"),
    min_price: int = Query(None, description="Minimum rent price"),
    max_price: int = Query(None, description="Maximum rent price"),
    page_count: int = Query(1, ge=1, le=10, description="Number of pages (1-10)"),
) -> dict:
    """
    Get rental property listings for a specific location.

    Example: GET /rentals?postal_code=74072&radius=5&max_price=1000
    """
    cache_key = build_cache_key(
        "rentals",
        postal_code=postal_code,
        category=category,
        location_id=location_id,
        radius=radius,
        min_price=min_price,
        max_price=max_price,
        page_count=page_count,
    )

    # Build the search URL for debugging purposes
    search_url = await build_search_url(
        postal_code,
        category,
        location_id,
        radius,
        min_price,
        max_price,
        page=1,
    )
    # Check cache first
    cached = await get_cached_value(cache_key)
    if cached is not None:
        return {
            "success": True,
            "search_url": search_url,
            "data": cached,
            "cached": True,
        }

    # Scrape fresh data
    browser_manager = PlaywrightManager()
    await browser_manager.start()
    try:
        results = await get_rentals_klaz(
            browser_manager=browser_manager,
            postal_code=postal_code,
            category=category,
            location_id=location_id,
            radius=radius,
            min_price=min_price,
            max_price=max_price,
            page_count=page_count,
        )
        print(f"Scraped {len(results)} rental listings.")
        # Validate and normalize with ListingResult model
        listings = [ListingResult(**item).model_dump() for item in results]
        await set_cached_value(cache_key, listings, ttl=CACHE_TTL_SECONDS)
        return {
            "success": True,
            "search_url": search_url,
            "data": listings,
            "cached": False,
        }
    finally:
        await browser_manager.close()
