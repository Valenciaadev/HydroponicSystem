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

def get_admin_password():
    conn = connect_db()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        query = "SELECT clabe FROM administradores ad join usuarios us WHERE ad.id_usuario = us.id"
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result else None
    except mysql.connector.Error as err:
        print(f"ERROR en `get_admin_password()`: {err}")
        return None
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
