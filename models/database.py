import mysql.connector
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="manuel123",
            database="hydrophonic_sys",
            port=3306,
        )
        print("✅ Conexión exitosa a la base de datos desde `connect_db()`")
        return conn

    except mysql.connector.Error as err:
        print(f"ERROR en `connect_db()`: {err}")
        return None


def get_averages_all():
    """Obtiene los promedios de todos los registros"""
    conn = connect_db()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        query = """
        SELECT 
            AVG(ph) as avg_ph,
            AVG(ce) as avg_ce,
            AVG(t_agua) as avg_t_agua,
            AVG(ultrasonico) as avg_nivel,
            AVG(t_ambiente) as avg_t_ambiente,
            AVG(humedad) as avg_humedad
        FROM registro_mediciones
        """
        cursor.execute(query)
        return cursor.fetchone()
    except Exception as e:
        print(f"Error al obtener promedios generales: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_averages_by_weeks(weeks=4):
    """Obtiene los promedios por semanas del último mes"""
    conn = connect_db()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        end_date = datetime.now()
        start_date = end_date - timedelta(days=28)  # 4 semanas
        
        results = []
        for i in range(weeks):
            week_start = start_date + timedelta(days=7*i)
            week_end = week_start + timedelta(days=7)
            
            query = """
            SELECT 
                COALESCE(AVG(ph), 0) as avg_ph,
                COALESCE(AVG(ce), 0) as avg_ce,
                COALESCE(AVG(t_agua), 0) as avg_t_agua,
                COALESCE(AVG(ultrasonico), 0) as avg_nivel,
                COALESCE(AVG(t_ambiente), 0) as avg_t_ambiente,
                COALESCE(AVG(humedad), 0) as avg_humedad
            FROM registro_mediciones
            WHERE fecha BETWEEN %s AND %s
            """
            cursor.execute(query, (week_start, week_end))
            week_data = cursor.fetchone()
            if week_data:
                results.append(week_data[:6])  # Solo los primeros 6 valores (sin week_num)
        
        return results if results else [(0,0,0,0,0,0) for _ in range(weeks)]
    except Exception as e:
        print(f"Error al obtener promedios por semanas: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def get_averages_by_months(months):
    """Obtiene los promedios por meses"""
    conn = connect_db()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        end_date = datetime.now()
        results = []
        
        for i in range(months):
            month_end = end_date - relativedelta(months=i)
            month_start = month_end - relativedelta(months=1)
            
            query = """
            SELECT 
                COALESCE(AVG(ph), 0) as avg_ph,
                COALESCE(AVG(ce), 0) as avg_ce,
                COALESCE(AVG(t_agua), 0) as avg_t_agua,
                COALESCE(AVG(ultrasonico), 0) as avg_nivel,
                COALESCE(AVG(t_ambiente), 0) as avg_t_ambiente,
                COALESCE(AVG(humedad), 0) as avg_humedad
            FROM registro_mediciones
            WHERE fecha BETWEEN %s AND %s
            """
            cursor.execute(query, (month_start, month_end))
            month_data = cursor.fetchone()
            if month_data:
                results.append(month_data)
        
        return results if results else [(0,0,0,0,0,0) for _ in range(months)]
    except Exception as e:
        print(f"Error al obtener promedios por meses: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

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
        
def getAll():
    """Obtiene todos los datos del historial."""
    conn = connect_db()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        query = "SELECT ph, ce, t_agua, ultrasonico, t_ambiente, humedad, fecha FROM registro_mediciones"
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener todos los datos: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def getbyMonth():
    """Obtiene los datos del último mes."""
    conn = connect_db()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        query = """
            SELECT ph, ce, t_agua, ultrasonico, t_ambiente, humedad, fecha
            FROM registro_mediciones
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 1 MONTH)
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener datos del último mes: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def getbyQuarter():
    """Obtiene los datos del último trimestre."""
    conn = connect_db()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        query = """
            SELECT ph, ce, t_agua, ultrasonico, t_ambiente, humedad, fecha
            FROM registro_mediciones
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener datos del último trimestre: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def getbySemester():
    """Obtiene los datos del último semestre."""
    conn = connect_db()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        query = """
            SELECT ph, ce, t_agua, ultrasonico, t_ambiente, humedad, fecha
            FROM registro_mediciones
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener datos del último semestre: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def getbyYear():
    """Obtiene los datos del último año."""
    conn = connect_db()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        query = """
            SELECT ph, ce, t_agua, ultrasonico, t_ambiente, humedad, fecha
            FROM registro_mediciones
            WHERE fecha >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener datos del último año: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
