from PyQt5.QtWidgets import QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import mysql.connector
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def connect_db():
    try:
        print("Intentando conectar a la base de datos...")
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="admin",
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
            AVG(ph_value) as avg_ph,
            AVG(ce_value) as avg_ce,
            AVG(tagua_value) as avg_t_agua,
            AVG(us_value) as avg_nivel,
            AVG(tam_value) as avg_t_ambiente,
            AVG(hum_value) as avg_humedad
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


def update_hortaliza_seleccion(id_hortaliza):
    conn = connect_db()
    if not conn:
        return False

    try:
        cursor = conn.cursor()
        # Primero deseleccionar todas
        cursor.execute("UPDATE seleccion_hortalizas SET seleccion = 0")
        # Luego seleccionar la específica
        cursor.execute("UPDATE seleccion_hortalizas SET seleccion = 1 WHERE id_hortaliza = %s", (id_hortaliza,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating hortaliza: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_sensor_ranges(hortaliza_id, sensor_id):
    """Obtiene los rangos mínimos y máximos para un sensor específico de una hortaliza"""
    query = """
        SELECT valor_min_acept, valor_max_acept 
        FROM config_sensores 
        WHERE id_hortaliza = %s AND id_sensor = %s
    """
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (hortaliza_id, sensor_id))
            result = cursor.fetchone()
            if result:
                return {
                    'min': result[0],  # valor_min_acept está en la posición 0
                    'max': result[1]   # valor_max_acept está en la posición 1
                }
            return {'min': 0, 'max': 0}
    finally:
        connection.close()

def get_sensors_data(hortaliza_id):
    """Obtiene todos los sensores con sus rangos configurados para una hortaliza"""
    query = """
        SELECT s.id_sensor, s.nombre, cs.valor_min_acept, cs.valor_max_acept
        FROM sensores s
        LEFT JOIN config_sensores cs ON s.id_sensor = cs.id_sensor AND cs.id_hortaliza = %s
        ORDER BY s.id_sensor
    """
    connection = connect_db()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, (hortaliza_id,))
            columns = [column[0] for column in cursor.description]  # Obtenemos los nombres de las columnas
            return [
                {
                    'id': row[columns.index('id_sensor')],
                    'nombre': row[columns.index('nombre')],
                    'rango_min': row[columns.index('valor_min_acept')] or 0,
                    'rango_max': row[columns.index('valor_max_acept')] or 0
                }
                for row in cursor.fetchall()
            ]
    finally:
        connection.close()


def get_hortalizas():
    conn = connect_db()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id_hortaliza, nombre, seleccion FROM seleccion_hortalizas")
    hortalizas = cursor.fetchall()
    cursor.close()
    conn.close()
    return hortalizas

def update_hortaliza_seleccion(id_hortaliza):
    conn = connect_db()
    if not conn:
        return False

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id_hortaliza FROM seleccion_hortalizas WHERE seleccion = 1")
        current = cursor.fetchone()
        if current and current["id_hortaliza"] == id_hortaliza:
            return True  # Ya está seleccionada, no hacer nada

        cursor = conn.cursor()
        cursor.execute("UPDATE seleccion_hortalizas SET seleccion = 0")
        cursor.execute("UPDATE seleccion_hortalizas SET seleccion = 1 WHERE id_hortaliza = %s", (id_hortaliza,))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error updating hortaliza: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def get_averages_all():
    """Obtiene los promedios de todos los registros"""
    conn = connect_db()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        query = """
        
        SELECT 
            AVG(ph_value) as avg_ph,
            AVG(ce_value) as avg_ce,
            AVG(tagua_value) as avg_t_agua,
            AVG(us_value) as avg_nivel,
            AVG(tam_value) as avg_t_ambiente,
            AVG(hum_value) as avg_humedad
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



def get_date_ranges(weeks=False, months=False):
    """Genera etiquetas de rango de fechas"""
    ranges = []
    today = datetime.now()
    
    if weeks:
        for i in range(4):
            end_date = today - timedelta(weeks=i)
            start_date = end_date - timedelta(weeks=1)
            ranges.append(f"{start_date.strftime('%b %d')} - {end_date.strftime('%b %d')}")
        return list(reversed(ranges))
    
    elif months:
        for i in range(months):
            end_date = today - relativedelta(months=i)
            start_date = end_date - relativedelta(months=1)
            ranges.append(f"{start_date.strftime('%b')} - {end_date.strftime('%b')}")
        return list(reversed(ranges))
    
    return []

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
                COALESCE(AVG(ph_value), 0) as avg_ph,
                COALESCE(AVG(ce_value), 0) as avg_ce,
                COALESCE(AVG(tagua_value), 0) as avg_t_agua,
                COALESCE(AVG(us_value), 0) as avg_nivel,
                COALESCE(AVG(tam_value), 0) as avg_t_ambiente,
                COALESCE(AVG(hum_value), 0) as avg_humedad
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
                COALESCE(AVG(ph_value), 0) as avg_ph,
                COALESCE(AVG(ce_value), 0) as avg_ce,
                COALESCE(AVG(tagua_value), 0) as avg_t_agua,
                COALESCE(AVG(us_value), 0) as avg_nivel,
                COALESCE(AVG(tam_value), 0) as avg_t_ambiente,
                COALESCE(AVG(hum_value), 0) as avg_humedad
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
        query = """
            SELECT us.clabe 
            FROM administradores ad 
            JOIN usuarios us ON ad.id_usuario = us.id
            LIMIT 1
        """
        cursor.execute(query)
        result = cursor.fetchone()
        return result[0] if result else None

    except mysql.connector.Error as err:
        print(f"ERROR en `get_admin_password()`: {err}")
        return None

    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()

def create_line_graph():
    conn = connect_db()
    print("🔌 Conexión a DB:", conn)
    if conn is None:
        print("No se pudo conectar a la base de datos para graficar.")
        return QLabel("Error al cargar la gráfica")

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha, ph_value, ce_value, tagua_value, us_value, tam_value, hum_value
            FROM registro_mediciones
            ORDER BY fecha DESC
            LIMIT 10
        """)
        rows = cursor.fetchall()
        """ print("📊 Datos recibidos para la gráfica:", rows) """
    except Exception as e:
        import traceback
        print("❌ Error en la consulta SQL:")
        traceback.print_exc()
        return QLabel("Error al cargar la gráfica")
    finally:
        cursor.close()
        conn.close()
    
    if not rows:
        print("⚠️ No hay datos en la tabla `registro_mediciones`")
        return QLabel("Sin datos para mostrar")

    try:
        fechas = [row[0].strftime("%d/%m %H:%M") for row in rows][::-1]
        ph = [row[1] for row in rows][::-1]
        ce = [row[2] for row in rows][::-1]
        tagua = [row[3] for row in rows][::-1]
        us = [row[4] for row in rows][::-1]
        tam = [row[5] for row in rows][::-1]
        hum = [row[6] for row in rows][::-1]
    except Exception as e:
        print("❌ Error procesando los datos de la gráfica:", e)
        return QLabel("Error al procesar los datos")

    # Crear la figura de matplotlib
    fig, ax = plt.subplots(figsize=(7, 4))
    fig.patch.set_facecolor('#1f2232')
    ax.set_facecolor('#1f2232')
    
    ax.plot(fechas, ph, label="pH", color='#00FFFF', linewidth=2)
    ax.plot(fechas, ce, label="CE", color='#FF00FF', linewidth=2)
    ax.plot(fechas, tagua, label="Temp. Agua", color='#FFFF00', linewidth=2)
    ax.plot(fechas, us, label="Ultrasónico", color='#00FF00', linewidth=2)
    ax.plot(fechas, tam, label="Temp. Aire", color='#FFA500', linewidth=2)
    ax.plot(fechas, hum, label="Humedad", color='#FF1493', linewidth=2)

    ax.set_title("Mediciones recientes", color='white')
    ax.set_xlabel("Fecha y hora", color='white')
    ax.set_ylabel("Valores", color='white')
    ax.tick_params(axis='x', rotation=45, colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.legend(loc="upper left", 
                facecolor="#2c3e50", 
                edgecolor="white", 
                labelcolor="white",
                fontsize='small')
    ax.grid(True, color='gray')

    ax.grid(True, color='#2a3b4d', alpha=0.5, linestyle='--', linewidth=0.5)
    
    for spine in ax.spines.values():
        spine.set_color('white')
    
    plt.tight_layout()

    canvas = FigureCanvas(fig)
    return canvas


def create_bar_graph():
    conn = connect_db()
    if conn is None:
        print("No se pudo conectar a la base de datos para graficar.")
        return QLabel("Error al cargar la gráfica de barras")

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                AVG(ph_value) as avg_ph,
                AVG(ce_value) as avg_ce,
                AVG(tagua_value) as avg_t_agua,
                AVG(us_value) as avg_nivel,
                AVG(tam_value) as avg_t_ambiente,
                AVG(hum_value) as avg_humedad
            FROM registro_mediciones
        """)
        row = cursor.fetchone()
    except Exception as e:
        print(f"❌ Error en la consulta SQL para gráfica de barras: {e}")
        return QLabel(f"Error al cargar la gráfica de barras: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn:
            conn.close()

    if not row or all(val is None for val in row):
        print("⚠️ No hay datos para la gráfica de barras")
        return QLabel("Sin datos para mostrar")

    # Etiquetas y valores
    categorias = [
        "Sensor de pH",
        "Sensor de ORP",
        "Temperatura Agua",
        "Nivel de agua",
        "Temperatura Ambiente",
        "Sensor humedad"
    ]
    valores = [float(val) if val is not None else 0.0 for val in row]

    # Crear la figura
    fig = plt.figure(figsize=(10, 4))
    fig.patch.set_facecolor('#1f2232')

    ax = fig.subplots()
    ax.set_facecolor('#1f2232')

    colores = ['#00FFFF', '#FF00FF', '#FFFF00', '#00FF00', '#FFA500', '#6495ED']

    bars = ax.bar(categorias, valores, color=colores, edgecolor='white', linewidth=1)

    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2., height,
                f'{height:.2f}',
                ha='center', va='bottom',
                color='white', fontweight='bold', fontsize=10)

    ax.set_title("Promedio de Mediciones", color='white', fontsize=12, pad=20)
    ax.tick_params(axis='x', colors='white', labelsize=9, rotation=20)
    ax.tick_params(axis='y', colors='white', labelsize=10)
    ax.set_ylabel("Valor promedio", color='white', fontsize=11)

    ax.grid(axis='y', color='#2a3b4d', alpha=0.3, linestyle='--')
    for spine in ax.spines.values():
        spine.set_color('white')
        spine.set_linewidth(1.5)

    plt.tight_layout()

    return FigureCanvas(fig)

def getAll():
    """Obtiene todos los datos del historial."""
    conn = connect_db()
    if conn is None:
        return []
    
    try:
        cursor = conn.cursor()
        query = "SELECT ph_value, ce_value, tagua_value, us_value, tam_value, hum_value, fecha FROM registro_mediciones"
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
            SELECT ph_value, ce_value, tagua_value, us_value, tam_value, hum_value, fecha
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
            SELECT ph_value, ce_value, tagua_value, us_value, tam_value, hum_value, fecha
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
            SELECT ph_value, ce_value, tagua_value, us_value, tam_value, hum_value, fecha
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
            SELECT ph_value, ce_value, tagua_value, us_value, tam_value, hum_value, fecha
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

def guardar_mediciones_cada_6h(ph, orp, temp_agua, nivel_agua=0.0, temp_aire=0.0, humedad_aire=0.0):
    """
    Guarda todos los valores en la tabla `registro_mediciones` si la hora actual es 06:00, 12:00, 18:00 o 00:00.
    """
    from datetime import datetime
    from models.database import connect_db

    hora_actual = datetime.now().strftime("%H:%M")
    if hora_actual in ["06:00", "12:00", "18:00", "00:00"]:
        try:
            conn = connect_db()
            if not conn:
                print("❌ No se pudo conectar para guardar datos.")
                return

            cursor = conn.cursor()
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            query = """
                INSERT INTO registro_mediciones 
                (ph_value, ce_value, tagua_value, us_value, tam_value, hum_value, fecha)
                VALUES (%s, %s, %s, %s, %s, 0.0, %s)
            """
            cursor.execute(query, (
                ph,
                orp,
                temp_agua,
                nivel_agua,
                temp_aire,
                now
            ))
            conn.commit()
            print(f"✅ Datos guardados automáticamente a las {hora_actual}:\n"
                  f"pH={ph}, ORP={orp}, TempAgua={temp_agua}, Nivel={nivel_agua}, TempAire={temp_aire}")
        except Exception as e:
            print(f"❌ Error al guardar datos en DB:", e)
        finally:
            cursor.close()
            conn.close()

