from models.database import connect_db

class Usuario:
    def __init__(self, nombre, apellido_paterno, apellido_materno, email, clabe, password, telefono, perfil_image="empresa.png"):
        self.nombre = nombre
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.email = email
        self.clabe = clabe
        self.password = password
        self.telefono = telefono
        self.perfil_image = perfil_image
        self.conn = connect_db()

    def guardar_en_db(self):
        if self.conn:
            try:
                cursor = self.conn.cursor()
                query = """INSERT INTO usuarios (perfil_image, nombre, apellido_paterno, apellido_materno, email, clabe, password, telefono) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                valores = (self.perfil_image, self.nombre, self.apellido_paterno, self.apellido_materno, self.email, self.clabe, self.password, self.telefono)
                cursor.execute(query, valores)
                self.conn.commit()
                user_id = cursor.lastrowid  # Obtener el ID del usuario
                print(f"✅ Usuario {self.nombre} registrado con éxito.")
                return user_id, self.conn  # Retorna ID y conexión activa
            except Exception as e:
                print(f"Error al registrar usuario: {e}")
                return None, None