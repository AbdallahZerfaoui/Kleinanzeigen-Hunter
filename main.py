"""
Main application file for the Kleinanzeigen API.
Sets up the FastAPI app and includes routers for different endpoints.
"""

from fastapi import FastAPI
from routers import inserate, inserat
from endpoints import root

app = FastAPI(version="1.0.0")


app.get("/")(root)


app.include_router(inserate.router)
app.include_router(inserat.router)
