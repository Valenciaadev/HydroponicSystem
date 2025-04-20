import mysql.connector

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="hydrophonic_sys",
            port=3306,
        )
        print("✅ Conexión exitosa a la base de datos desde `connect_db()`")
        return conn

    except mysql.connector.Error as err:
        print(f"ERROR en `connect_db()`: {err}")
        return None