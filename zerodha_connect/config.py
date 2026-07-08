"""
config.py

Reads all configuration from .env
"""

from dotenv import load_dotenv
import os

load_dotenv()


class Config:

    API_KEY = os.getenv("API_KEY")

    API_SECRET = os.getenv("API_SECRET")

    ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

    REQUEST_TOKEN = os.getenv("REQUEST_TOKEN")

    REDIRECT_URL = os.getenv(
        "REDIRECT_URL",
        "http://127.0.0.1:8000"
    )