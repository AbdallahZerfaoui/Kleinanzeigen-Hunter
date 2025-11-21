# from scrapers.inserat import get_inserate_details
from fastapi import APIRouter

# from utils.browser import PlaywrightManager
# from config import INSERAT_URL_TEMPLATE
from endpoints import get_inserat

router = APIRouter()


router.get("/inserat/{id}")(get_inserat)
