from models.trabajador import Trabajador
from models.database import connect_db

class Administrador(Trabajador):
    def __init__(self, nombre, apellido_paterno, apellido_materno, email, clabe, password, telefono):
        super().__init__(nombre, apellido_paterno, apellido_materno, email, clabe, password, telefono)

    def guardar_en_db(self):
        id_trabajador, conn = super().guardar_en_db()
        if id_trabajador and conn:
            try:
                cursor = conn.cursor()
                query = "INSERT INTO administradores (id_trabajador) VALUES (%s)"
                cursor.execute(query, (id_trabajador,))
                conn.commit()
                print(f"Administrador {self.nombre} registrado con éxito.")
            except Exception as e:
                print(f"Error al registrar administrador: {e}")
            finally:
                cursor.close()
                self.conn.close()