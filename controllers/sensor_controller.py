import mysql.connector

def insertar_sensor(nombre, bus, address, tasa_flujo, modo_salida):
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='hydrophonic_sys'
        )
        cursor = conn.cursor()

        query = """
            INSERT INTO sensores (nombre, bus, address, tasa_flujo, modo_salida, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
        """
        values = (nombre, bus, address, tasa_flujo, modo_salida)

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()
        return True

    except mysql.connector.Error as err:
        print(f"Error al insertar sensor: {err}")
        return False