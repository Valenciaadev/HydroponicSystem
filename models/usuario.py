from models.database import connect_db

class Usuario:
    def __init__(self, nombre, apellido_paterno, apellido_materno, email, clabe, password, telefono, tipo_usuario):
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.email = email
        self.clabe = clabe
        self.password = password
        self.telefono = telefono
        self.tipo_usuario = tipo_usuario
        self.perfil_image = "empresa.png"

    def guardar_en_db(self):
        conn = connect_db()
        if conn:
            try:
                cursor = conn.cursor()
                sql = """
                    INSERT INTO usuarios (
                        perfil_image, nombre, apellido_paterno, apellido_materno, email,
                        clabe, password, telefono, tipo_usuario
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    self.perfil_image, self.nombre, self.apellido_paterno, self.apellido_materno,
                    self.email, self.clabe, self.password, self.telefono, self.tipo_usuario
                )
                cursor.execute(sql, valores)
                conn.commit()
                print(f"✅ Usuario {self.nombre} registrado con éxito.")
                return cursor.lastrowid
            except Exception as e:
                print(f"❌ Error al registrar usuario: {e}")
                return None
            finally:
                cursor.close()
                conn.close()
        else:
            print("❌ No se pudo conectar a la base de datos.")
            return None