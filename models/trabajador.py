# from models.usuario import Usuario
from models.database import connect_db

class Trabajador:
    def __init__(self, id_usuario):
        self.id_usuario = id_usuario

    def guardar_en_db(self):
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                sql = "INSERT INTO trabajadores (id_usuario) VALUES (%s)"
                valores = (self.id_usuario,)
                cursor.execute(sql, valores)
                conn.commit()
                print(f"✅ Trabajador registrado con éxito (id_usuario={self.id_usuario}).")
                return cursor.lastrowid
            except Exception as e:
                print(f"❌ Error al registrar trabajador: {e}")
                return None
            finally:
                cursor.close()
                conn.close()
        else:
            print("❌ No se pudo conectar a la base de datos para registrar trabajador.")
            return None