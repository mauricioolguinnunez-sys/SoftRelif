import os
import pymysql


DB_CONFIG = {
    "host": os.getenv("SOFTRELIF_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("SOFTRELIF_DB_PORT", "3307")),
    "user": os.getenv("SOFTRELIF_DB_USER", "softrelif_app"),
    "password": os.getenv("SOFTRELIF_DB_PASSWORD", "SoftRelif_1234!"),
    "database": os.getenv("SOFTRELIF_DB_NAME", "softrelif_db"),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": False
}


def get_connection():
    return pymysql.connect(**DB_CONFIG)