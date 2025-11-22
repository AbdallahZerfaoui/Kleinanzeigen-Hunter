"""Endpoint implementations for the Kleinanzeigen API."""

from fastapi import Query

from config import CACHE_TTL_SECONDS, INSERAT_URL_TEMPLATE
from models.results import ListingResult
from scrapers.inserate import get_inserate_klaz
from scrapers.inserat import get_inserate_details
from utils.browser import PlaywrightManager
from utils.cache import build_cache_key, get_cached_value, set_cached_value


async def root():
    """
    Root endpoint providing basic API information.
    Returns:
        dict: A welcome message and available endpoints.
    """
    return {
        "message": "Welcome to the Kleinanzeigen API",
        "endpoints": ["/inserate", "/inserat/{inserat_id}"],
    }


async def get_inserat(inserat_id: str) -> dict:
    """
    Fetch details of a specific inserat by ID.
    """
    cache_key = build_cache_key("inserat", id=inserat_id)
    cached = await get_cached_value(cache_key)
    if cached is not None:
        return {"success": True, "data": cached, "cached": True}

    browser_manager = PlaywrightManager()
    await browser_manager.start()
    try:
        page = await browser_manager.new_context_page()
        url = INSERAT_URL_TEMPLATE.format(id=inserat_id)
        result = await get_inserate_details(url, page)
        await set_cached_value(cache_key, result, ttl=CACHE_TTL_SECONDS)
        return {"success": True, "data": result, "cached": False}
    finally:
        await browser_manager.close()


async def get_inserate(
    query: str = Query(None),
    location: str = Query(None),
    radius: int = Query(None),
    min_price: int = Query(None),
    max_price: int = Query(None),
    page_count: int = Query(1, ge=1, le=20),
) -> dict:
    """
    Search for inserate based on query parameters.
    """
    cache_key = build_cache_key(
        "inserate",
        query=query,
        location=location,
        radius=radius,
        min_price=min_price,
        max_price=max_price,
        page_count=page_count,
    )
    cached = await get_cached_value(cache_key)
    if cached is not None:
        return {"success": True, "data": cached, "cached": True}

    browser_manager = PlaywrightManager()
    await browser_manager.start()
    try:
        results = await get_inserate_klaz(
            browser_manager, query, location, radius, min_price, max_price, page_count
        )
        # Validate and normalize with ListingResult model
        listings = [ListingResult(**item).model_dump() for item in results]
        await set_cached_value(cache_key, listings, ttl=CACHE_TTL_SECONDS)
        return {"success": True, "data": listings, "cached": False}
    finally:
        await browser_manager.close()
