"""
Main application file for the Kleinanzeigen API.
Sets up the FastAPI app and includes routers for different endpoints.
"""

from fastapi import FastAPI
from routers import inserate, inserat
from endpoints import root
from routers import rentals

app = FastAPI(
    title="Kleinanzeigen Hunter API",
    version="1.0.0",
    description="API for scraping and managing Kleinanzeigen listings"
)


app.get("/")(root)


app.include_router(inserate.router)
app.include_router(inserat.router)
app.include_router(rentals.router)
