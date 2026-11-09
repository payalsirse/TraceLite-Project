import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATABASE = os.path.join(BASE_DIR, "database", "tracelite.db")

SECRET_KEY = os.environ.get("SECRET_KEY")

if not SECRET_KEY:
    SECRET_KEY = "dev-only-change-this-secret-key"

APP_TIMEZONE = "Asia/Kolkata"
