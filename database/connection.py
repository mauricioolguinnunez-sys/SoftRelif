import os
from pathlib import Path

import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


DB_HOST = os.getenv("DB_HOST", "127.0.0.1").strip()
DB_PORT = int(os.getenv("DB_PORT", "3306").strip())
DB_USER = os.getenv("DB_USER", "root").strip()
DB_PASSWORD = os.getenv("DB_PASSWORD", "").strip()
DB_NAME = os.getenv("DB_NAME", "softrelief").strip()


def validate_config():
    if not DB_PASSWORD:
        raise ValueError(
            "No se encontró DB_PASSWORD. Revisa que exista el archivo .env "
            "en la raíz del proyecto y que tenga DB_PASSWORD configurado."
        )


def debug_config():
    print("========== DB CONFIG ==========")
    print("ENV_PATH:", ENV_PATH)
    print("ENV_EXISTS:", ENV_PATH.exists())
    print("DB_HOST:", DB_HOST)
    print("DB_PORT:", DB_PORT)
    print("DB_USER:", DB_USER)
    print("DB_PASSWORD_LOADED:", "YES" if DB_PASSWORD else "NO")
    print("DB_PASSWORD_LENGTH:", len(DB_PASSWORD))
    print("DB_NAME:", DB_NAME)
    print("===============================")


def create_database_if_not_exists():
    validate_config()
    debug_config()

    connection = None

    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD
        )

        cursor = connection.cursor()

        cursor.execute(
            f"""
            CREATE DATABASE IF NOT EXISTS `{DB_NAME}`
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci;
            """
        )

        connection.commit()
        cursor.close()

    except Error as error:
        print(f"Error creando/verificando la base de datos: {error}")
        raise

    finally:
        if connection and connection.is_connected():
            connection.close()


def get_connection():
    create_database_if_not_exists()

    try:
        return mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

    except Error as error:
        print(f"Error conectando a MySQL: {error}")
        raise