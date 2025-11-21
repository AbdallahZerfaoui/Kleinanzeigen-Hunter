from fastapi import APIRouter

# from scrapers.inserate import get_inserate_klaz
# from utils.browser import PlaywrightManager
from endpoints import get_inserate

router = APIRouter()


router.get("/inserate")(get_inserate)
