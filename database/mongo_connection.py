import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from utils.paths import app_base_dir

BASE_DIR = Path(app_base_dir())
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017").strip()
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "softrelief_nosql").strip()

_client = None
_database = None


def get_mongo_client():
    global _client
    if _client is None:
        _client = MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )
    return _client


def get_mongo_database():
    global _database
    if _database is None:
        client = get_mongo_client()
        _database = client[MONGO_DB_NAME]
    return _database


def get_wellbeing_collection():
    db = get_mongo_database()
    return db["bienestar_usuario"]


def test_connection():
    try:
        client = get_mongo_client()
        client.admin.command("ping")
        return True, "Conexión a MongoDB exitosa."
    except (ConnectionFailure, ServerSelectionTimeoutError) as error:
        return False, f"No se pudo conectar a MongoDB: {error}"


def close_connection():
    global _client, _database
    if _client is not None:
        _client.close()
        _client = None
        _database = None
