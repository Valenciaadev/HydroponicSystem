from PyQt5.QtWidgets import QLabel
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import mysql.connector
import matplotlib.pyplot as plt

def connect_db():
    try:
        print("Intentando conectar a la base de datos...")
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
        print("📊 Datos recibidos para la gráfica:", rows)
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
    fig.patch.set_facecolor('#1e2b3c')
    ax.set_facecolor('#1e2b3c')
    
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
                'pH' AS categoria,
                AVG(ph_value) AS valor
            FROM registro_mediciones
            UNION ALL
            SELECT 
                'CE' AS categoria,
                AVG(ce_value) AS valor
            FROM registro_mediciones
            UNION ALL
            SELECT 
                'Temp Agua' AS categoria,
                AVG(tagua_value) AS valor
            FROM registro_mediciones
            UNION ALL
            SELECT 
                'Ultrasónico' AS categoria,
                AVG(us_value) AS valor
            FROM registro_mediciones
            LIMIT 4
        """)
        rows = cursor.fetchall()
    except Exception as e:
        print(f"❌ Error en la consulta SQL para gráfica de barras: {e}")
        return QLabel(f"Error al cargar la gráfica de barras: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if conn:
            conn.close()

    if not rows:
        print("⚠️ No hay datos para la gráfica de barras")
        return QLabel("Sin datos para mostrar")

    # Extraer categorías y valores
    categorias = [row[0] for row in rows]
    valores = [float(row[1]) for row in rows]

    # Crear la figura
    fig = plt.figure(figsize=(9, 4))
    fig.patch.set_facecolor('#1e2b3c')

    ax = fig.subplots()
    ax.set_facecolor('#1e2b3c')
    
    # Paleta de colores vibrantes para cada barra
    colores = ['#00FFFF', '#FF00FF', '#FFFF00', '#00FF00']
    
    # Gráfica de barras con datos reales
    bars = ax.bar(categorias, valores, color=colores, edgecolor='white', linewidth=1)
    
    # Añadir valores encima de cada barra
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}',
                ha='center', va='bottom', 
                color='white', fontweight='bold', fontsize=10)

    ax.set_title("Promedio de Mediciones", color='white', fontsize=12, pad=20)
    ax.tick_params(axis='x', colors='white', labelsize=10)
    ax.tick_params(axis='y', colors='white', labelsize=10)
    ax.set_ylabel("Valor promedio", color='white', fontsize=11)

    ax.grid(axis='y', color='#2a3b4d', alpha=0.3, linestyle='--')
    
    for spine in ax.spines.values():
        spine.set_color('white')
        spine.set_linewidth(1.5)

    plt.tight_layout()    
    
    canvas = FigureCanvas(fig)
    return canvas