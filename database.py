
import os
import mysql.connector


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("CONNECT_DB_HOST", "localhost"),
        user=os.getenv("CONNECT_DB_USER", "root"),
        password=os.getenv("CONNECT_DB_PASSWORD", "root"),
        database="connect_ngo"
    )
