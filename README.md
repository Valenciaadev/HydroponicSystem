Para que el proyecto funcione correctamente con la base de datos debemos dirigirnos a la carpeta models/database.py dentro del proyecto y justo en esta parte:

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

Debemos cambiar el valor de password y databasse(de ser necesario) por los de nuestro cliente de mysql o mariadb.


Para la creación de usuario al importar la base de datos se deben de hace lo siguiente:
Hay un archivo en el proyecto que se llama main.py ahí debe buscar justo esta parte:

# Crear un nuevo usuario trabajador
'''usuario_trabajador = Usuario(
    nombre="Alexis",
    apellido_paterno="Verduzco",
    apellido_materno="Lopez",
    email="wverduzco@ucol.mx",
    clabe=123456,
    password=hash_password("qwerty"),
    telefono="3141234567",
    tipo_usuario="trabajador"
)

id_usuario_trabajador = usuario_trabajador.guardar_en_db()

if id_usuario_trabajador:
    trabajador = Trabajador(id_usuario=id_usuario_trabajador)
    trabajador.guardar_en_db()

# Crear un nuevo usuario administrador
usuario_admin = Usuario(
    nombre="Manuel",
    apellido_paterno="Valencia",
    apellido_materno="Antonio",
    email="mvalencia18@ucol.mx",
    clabe=789101,
    password=hash_password("qwerty"),
    telefono="3147654321",
    tipo_usuario="administrador"
)

id_usuario_admin = usuario_admin.guardar_en_db()

if id_usuario_admin:
    administrador = Administrador(id_usuario=id_usuario_admin)
    administrador.guardar_en_db()
'''

Debemos descomentar esta parte(Elimine las ''' de la parte inferior y de la parte superior de esta sección del código en el archivo correspondiente) e ingresar los datos de su preferencia para poder ingresar a la interfaz sin problemas.
