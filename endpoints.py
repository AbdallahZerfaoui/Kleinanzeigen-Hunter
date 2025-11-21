"""
Main application file for the Kleinanzeigen API.
Sets up the FastAPI app and includes routers for different endpoints.
"""

from utils.browser import PlaywrightManager
from config import INSERAT_URL_TEMPLATE
from scrapers.inserate import get_inserate_klaz
from scrapers.inserat import get_inserate_details
from fastapi import Query


async def root():
    """
    Root endpoint providing basic API information.
    Returns:
        dict: A welcome message and available endpoints.
    """
    return {
        "message": "Welcome to the Kleinanzeigen API",
        "endpoints": ["/inserate", "/inserat/{id}"],
    }


async def get_inserat(id: str) -> dict:
    """
    Fetch details of a specific inserat by ID.
    """
    browser_manager = PlaywrightManager()
    await browser_manager.start()
    try:
        page = await browser_manager.new_context_page()
        url = INSERAT_URL_TEMPLATE.format(id=id)
        result = await get_inserate_details(url, page)
        return {"success": True, "data": result}
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

    browser_manager = PlaywrightManager()
    await browser_manager.start()
    try:
        results = await get_inserate_klaz(
            browser_manager, query, location, radius, min_price, max_price, page_count
        )
        return {"success": True, "data": results}
    finally:
        await browser_manager.close()
