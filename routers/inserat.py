from scrapers.inserat import get_inserate_details
from fastapi import APIRouter, HTTPException
from utils.browser import PlaywrightManager
from config import INSERAT_URL_TEMPLATE

router = APIRouter()


@router.get("/inserat/{id}")
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
