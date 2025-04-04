from models.usuario import Usuario
from models.database import connect_db

class Trabajador(Usuario):
    def __init__(self, nombre, apellido_paterno, apellido_materno, email, clabe, password, telefono):
        super().__init__(nombre, apellido_paterno, apellido_materno, email, clabe, password, telefono)

    def guardar_en_db(self):
        id_usuario, conn = super().guardar_en_db()
        if id_usuario and conn:
            try:
                cursor = conn.cursor()
                query = "INSERT INTO trabajadores (id_usuario) VALUES (%s)"
                cursor.execute(query, (id_usuario,))
                conn.commit()
                trabajador_id = cursor.lastrowid
                print(f"Trabajador {self.nombre} registrado con éxito.")
                return trabajador_id, conn
            except Exception as e:
                print(f"Error al registrar trabajador: {e}")
                return None, None