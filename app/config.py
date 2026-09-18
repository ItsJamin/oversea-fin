import os

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
POSTERS_DIR = os.path.join(DATA_DIR, "posters")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this")
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "32-char-change-this")
    DATA_DIR = DATA_DIR
    POSTERS_DIR = POSTERS_DIR
    SERVER_DATA_FILE = os.path.join(DATA_DIR, "servers.enc")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(DATA_DIR, 'media.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
