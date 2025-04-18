from PySide6 import QtCore
from PySide6.QtUiTools import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys
import mysql.connector
from mysql.connector import Error
from db_connection import *

ui_trabajadores, _= loadUiType("trabajadores.ui");

class main_trabjadores(QWidget, ui_trabajadores):
    def __init__(self):
        super(main_trabjadores, self).__init__()
        # Remove default title bar
        flags = Qt.WindowFlags(Qt.FramelessWindowHint)
        self.setMaximumSize(1080, 720)
        self.setWindowFlags(flags)
        self.setupUi(self)
        self.showNormal()
        self.offset = None
        self.usuario_seleccionado = None
        self.current_displayed_users = []  # Para almacenar los usuarios mostrados

        self.push_close.clicked.connect(self.close_win)
        self.push_maxiniza.clicked.connect(self.mini_maximize)
        self.push_miniza.clicked.connect(self.minimize_win)

        self.push_editar.mousePressEvent = self.open_trabajadores_editar
        self.push_editar.setAttribute(QtCore.Qt.WA_Hover, True)
        self.push_editar.setMouseTracking(True)

        self.push_eliminar.mousePressEvent = self.open_modal_eliminar
        self.push_eliminar.setAttribute(QtCore.Qt.WA_Hover, True)
        self.push_eliminar.setMouseTracking(True)

        # Configurar scroll area para la lista de usuarios
        self.scroll_area = QScrollArea(self.frame_lista)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setGeometry(0, 0, self.frame_lista.width(), self.frame_lista.height())
        
        # Widget contenedor para los usuarios
        self.scroll_widget = QWidget()
        self.scroll_area.setWidget(self.scroll_widget)
        
        # Layout vertical para organizar los usuarios
        self.users_layout = QVBoxLayout(self.scroll_widget)
        self.users_layout.setAlignment(Qt.AlignTop)
        self.users_layout.setSpacing(10)
        
        self.cargar_datos()

    def cargar_datos(self):
        try:
            conexion = cconexion.conexiondatos()
            if conexion.is_connected():
                cursor = conexion.cursor()
                cursor.execute("SELECT id, nombre, apellido_paterno, apellido_materno, email, password FROM users")
                self.lista_usuarios = cursor.fetchall()
                
                # Limpiar el layout antes de agregar nuevos usuarios
                for i in reversed(range(self.users_layout.count())): 
                    self.users_layout.itemAt(i).widget().setParent(None)
                
                self.current_displayed_users = []
                
                # Crear un frame para cada usuario
                for usuario in self.lista_usuarios:
                    self.agregar_usuario_a_lista(usuario)
            
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos: {str(e)}")
        
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def agregar_usuario_a_lista(self, usuario):
        # Crear frame para el usuario
        user_frame = QFrame()
        user_frame.setObjectName("userFrame")
        user_frame.setStyleSheet("""
            #userFrame {
                background-color: rgb(28, 21, 84);
                border-radius: 18px;
            }
        """)
        user_frame.setFixedHeight(80)
        
        # Layout horizontal para organizar los elementos del usuario
        layout = QHBoxLayout(user_frame)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Mostrar información del usuario
        lbl_nombre = QLabel(f"{usuario[1]} {usuario[2]} {usuario[3]}")
        lbl_nombre.setStyleSheet("color: white; font-size: 12px;")
        lbl_nombre.setFixedWidth(200)
        
        lbl_email = QLabel(usuario[4])
        lbl_email.setStyleSheet("color: white; font-size: 12px;")
        lbl_email.setFixedWidth(200)
        
        # Botones de acción
        btn_editar = QPushButton("Editar")
        btn_editar.setStyleSheet("""
            QPushButton {
                background-color: rgb(0, 170, 0);
                border-radius: 20px;
                color: white;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgb(0, 247, 0);
            }
        """)
        btn_editar.setFixedSize(100, 40)
        btn_editar.clicked.connect(lambda: self.abrir_editar_usuario(usuario))
        
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setStyleSheet("""
            QPushButton {
                background-color: rgb(138, 0, 0);
                border-radius: 20px;
                color: white;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgb(255, 0, 0);
            }
        """)
        btn_eliminar.setFixedSize(100, 40)
        btn_eliminar.clicked.connect(lambda: self.abrir_eliminar_usuario(usuario))
        
        # Agregar widgets al layout
        layout.addWidget(lbl_nombre)
        layout.addWidget(lbl_email)
        layout.addStretch()
        layout.addWidget(btn_editar)
        layout.addWidget(btn_eliminar)
        
        # Agregar frame al layout principal
        self.users_layout.addWidget(user_frame)
        self.current_displayed_users.append(user_frame)

    def abrir_editar_usuario(self, usuario):
        self.trabajadores_window = modal_editar(usuario)
        self.trabajadores_window.datos_actualizados.connect(self.refrescar_datos)
        self.trabajadores_window.show()

    def abrir_eliminar_usuario(self, usuario):
        self.eliminar_window = modal_eliminar(usuario)
        self.eliminar_window.show()

    def open_trabajadores_editar(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            QMessageBox.warning(self, "Advertencia", "Por favor use los botones de editar en cada usuario")

    def refrescar_datos(self):
        self.cargar_datos()
        QMessageBox.information(
            self, 
            "Datos actualizados", 
            "La información de los trabajadores ha sido actualizada.",
            QMessageBox.Ok
        )

    def open_modal_eliminar(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            QMessageBox.warning(self, "Advertencia", "Por favor use los botones de eliminar en cada usuario")

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

    def minimize_win(self):
        self.showMinimized()

    def mini_maximize(self):
        if self.isMaximized():
            self.push_maxiniza.setIcon(QIcon("./resources/icons/maximize.svg"))
            self.showNormal()
        else:
            self.push_maxiniza.setIcon(QIcon("./resources/icons/minimize.svg"))
            self.showMaximized()

    def close_win(self):
        self.close()

    def resizeEvent(self, event):
        # Ajustar el tamaño del scroll area cuando la ventana cambia de tamaño
        self.scroll_area.setGeometry(0, 0, self.frame_lista.width(), self.frame_lista.height())
        super().resizeEvent(event)

# Las clases modal_eliminar, modal_acepta_eliminacion y modal_editar permanecen iguales
# ... [resto del código de las clases modales] ...
class modal_eliminar(QWidget):
    def __init__(self, usuario):
        super(modal_eliminar, self).__init__()
        self.usuario = usuario
        self.setWindowTitle("eliminar trabajadores")
        self.resize(400,300)

        self.vertica = QVBoxLayout()
        self.vertica2 = QHBoxLayout()
        self.forma = QFormLayout()

        self.label_titulo = QLabel(f"¿Deseas eliminar al trabajador {usuario[1]} {usuario[2]}?")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setContentsMargins(0,20,20,0)

        self.vertica.addWidget(self.label_titulo)
        self.forma.addRow(self.vertica)

        self.input_eliminar = QPushButton("Aceptar")
        self.input_eliminar.setContentsMargins(0,20,20,0)

        self.input_eliminar2 = QPushButton("Cancelar")
        self.input_eliminar2.setContentsMargins(0,20,20,0)

        self.input_eliminar.mousePressEvent = lambda event: self.open_acepta_eliminacion(event, usuario)
        self.input_eliminar.setAttribute(QtCore.Qt.WA_Hover, True)
        self.input_eliminar.setMouseTracking(True)

        self.vertica2.addWidget(self.input_eliminar)
        self.vertica2.addWidget(self.input_eliminar2)
        self.forma.addRow(self.vertica2)

        self.input_eliminar2.mousePressEvent = self.open_cancelar_eliminacion
        self.input_eliminar2.setAttribute(QtCore.Qt.WA_Hover, True)
        self.input_eliminar2.setMouseTracking(True)

        main_widget = QWidget()
        main_widget.setLayout(self.forma)

        self.set_centrar_widget(main_widget)

    def set_centrar_widget(self, widget):
        layout = QVBoxLayout()
        layout.addWidget(widget, alignment=Qt.AlignTop)
        self.setLayout(layout)

    def open_acepta_eliminacion(self, event, usuario):
        if event.button() == QtCore.Qt.LeftButton:
            self.trabajadores_window = modal_acepta_eliminacion(usuario)
            self.trabajadores_window.show()
            self.close()

    def open_cancelar_eliminacion(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.close()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)
        else:
            super().mouseMoveEvent(event)

class modal_acepta_eliminacion(QWidget):
    def __init__(self, usuario):
        super(modal_acepta_eliminacion, self).__init__()
        self.usuario = usuario
        self.resize(400,300)

        self.horizontal = QVBoxLayout()
        self.vertical = QHBoxLayout()
        self.form = QFormLayout()

        self.titulo = QLabel(f"¿Está seguro de eliminar a {usuario[1]} {usuario[2]}?")
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setContentsMargins(0,20,20,0)

        self.horizontal.addWidget(self.titulo)
        self.form.addRow(self.horizontal)

        self.push_acepta = QPushButton("Sí, eliminar")
        self.push_acepta.setContentsMargins(0,20,0,20)
        self.push_acepta.clicked.connect(self.eliminar_usuario)

        self.push_cancelar = QPushButton("Cancelar")
        self.push_cancelar.setContentsMargins(0,20,0,20)
        self.push_cancelar.clicked.connect(self.close)

        self.vertical.addWidget(self.push_acepta)
        self.vertical.addWidget(self.push_cancelar)
        self.form.addRow(self.vertical)

        main_widget = QWidget()
        main_widget.setLayout(self.form)

        self.set_centrar_widget(main_widget)

    def set_centrar_widget(self, widget):
        layout = QVBoxLayout()
        layout.addWidget(widget, alignment=Qt.AlignTop)
        self.setLayout(layout)

    def eliminar_usuario(self):
        try:
            conexion = cconexion.conexiondatos()
            if conexion.is_connected():
                cursor = conexion.cursor()
                query = "DELETE FROM users WHERE id = %s"
                cursor.execute(query, (self.usuario[0],))
                conexion.commit()
                
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    "El usuario ha sido eliminado correctamente"
                )
                self.close()
                
        except Error as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudo eliminar el usuario: {str(e)}"
            )
            
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

# class modal_eliminar(QWidget):
#     def __init__(self):
#         super(modal_eliminar, self).__init__()
#         self.setWindowTitle("eliminar trabajadores")
#         self.resize(400,300)

#         self.vertica = QVBoxLayout()
#         self.vertica2 = QHBoxLayout()
#         self.forma = QFormLayout()

#         self.label_titulo = QLabel("¿Deseas eliminar este trabajador?")
#         self.label_titulo.setAlignment(Qt.AlignCenter)
#         self.label_titulo.setContentsMargins(0,20,20,0)

#         self.vertica.addWidget(self.label_titulo)
#         self.forma.addRow(self.vertica)

#         self.input_eliminar = QPushButton("Acepta")
#         self.input_eliminar.setContentsMargins(0,20,20,0)

#         self.input_eliminar2 = QPushButton("Cancelar")
#         self.input_eliminar2.setContentsMargins(0,20,20,0)

#         self.input_eliminar.mousePressEvent = self.open_acepta_eliminacion
#         self.input_eliminar.setAttribute(QtCore.Qt.WA_Hover, True)
#         self.input_eliminar.setMouseTracking(True)

#         self.vertica2.addWidget(self.input_eliminar)
#         self.vertica2.addWidget(self.input_eliminar2)
#         self.forma.addRow(self.vertica2)

#         self.input_eliminar2.mousePressEvent = self.open_cancelar_eliminacion
#         self.input_eliminar2.setAttribute(QtCore.Qt.WA_Hover, True)
#         self.input_eliminar2.setMouseTracking(True)

#         main_widget = QWidget()
#         main_widget.setLayout(self.forma)

#         self.set_centrar_widget(main_widget)

#     def set_centrar_widget(self, widget):
#         layout = QVBoxLayout()
#         layout.addWidget(widget, alignment=Qt.AlignTop)
#         self.setLayout(layout)

#     def open_acepta_eliminacion(self,event):
#         if event.button() == QtCore.Qt.LeftButton:
#             self.trabajadores_window = modal_acepta_eliminacion()
#             self.trabajadores_window.show()
#             self.close()

#     def open_cancelar_eliminacion(self, event):
#         if event.button() == QtCore.Qt.LeftButton:
#             self.close()

#     def mousePressEvent(self, event):
#         if event.button() == QtCore.Qt.LeftButton:
#             self.offset = event.pos()
#         else:
#             super().mousePressEvent(event)

#     def mouseMoveEvent(self, event):
#         if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
#             self.move(self.pos() + event.pos() - self.offset)
#         else:
#             super().mouseMoveEvent(event)

# class modal_acepta_eliminacion(QWidget):
    def __init__(self):
        super(modal_acepta_eliminacion, self).__init__()
        self.resize(400,300)

        self.horizontal = QVBoxLayout()
        self.vertical = QHBoxLayout()
        self.form = QFormLayout()

        self.titulo = QLabel("¿Esta seguro de eliminar este trabajador")
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setContentsMargins(0,20,20,0)

        self.horizontal.addWidget(self.titulo)
        self.form.addRow(self.horizontal)

        self.push_acepta = QPushButton("si")
        self.push_acepta.setContentsMargins(0,20,0,20)

        self.push_cancelar = QPushButton("No")
        self.push_cancelar.setContentsMargins(0,20,0,20)

        self.vertical.addWidget(self.push_acepta)
        self.vertical.addWidget(self.push_cancelar)
        self.form.addRow(self.vertical)

        main_widget = QWidget()
        main_widget.setLayout(self.form)

        self.set_centrar_widget(main_widget)

    def set_centrar_widget(self, widget):
        layout = QVBoxLayout()
        layout.addWidget(widget, alignment=Qt.AlignTop)
        self.setLayout(layout)



class modal_editar(QWidget):
    datos_actualizados = Signal()
    def __init__(self, usuario):
        super(modal_editar, self).__init__()
        self.usuario = usuario
        self.setWindowTitle("editar trabajador")
        self.resize(500,400)

        self.setup_ui()

    def setup_ui(self):
        self.vertical1 = QVBoxLayout()
        self.horizontal1 = QHBoxLayout()
        self.form_container = QFormLayout()

        self.label_titulo = QLabel(f"Editar registro de trabajador # {self.usuario[0]}")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("color: white; font-size: 16px;")

        self.vertical1.addWidget(self.label_titulo)
        self.form_container.addRow(self.vertical1)

        self.label_nombre = QLabel("nombre")
        self.input_nombre = QLineEdit()
        self.input_nombre.setContentsMargins(43,0,0,0)
        self.input_nombre.setText(self.usuario[1])
        self.horizontal1.addWidget(self.label_nombre)
        self.horizontal1.addWidget(self.input_nombre)
        self.horizontal1.setContentsMargins(20,30,20,30)
        self.form_container.addRow(self.horizontal1)

        self.horizontal2 = QHBoxLayout()

        self.label_apellido_paterno = QLabel("apellido paterno")
        self.input_apellido_paterno = QLineEdit()
        self.input_apellido_paterno.setText(self.usuario[2])
        self.horizontal2.addWidget(self.label_apellido_paterno)
        self.horizontal2.addWidget(self.input_apellido_paterno)
        self.horizontal2.setContentsMargins(20,0,20,30)
        self.form_container.addRow(self.horizontal2)

        self.horizontal3 = QHBoxLayout()

        self.label_apellido_materno = QLabel("apellido materno")
        self.input_apellido_materno = QLineEdit()
        self.input_apellido_materno.setText(self.usuario[3])
        self.horizontal3.addWidget(self.label_apellido_materno)
        self.horizontal3.addWidget(self.input_apellido_materno)
        self.horizontal3.setContentsMargins(20,0,20,30)
        self.form_container.addRow(self.horizontal3)

        self.horizontal4 = QHBoxLayout()

        self.label_email = QLabel("email")
        self.input_email = QLineEdit()
        self.input_email.setContentsMargins(63,0,0,0)
        self.input_email.setText(self.usuario[4])
        self.horizontal4.addWidget(self.label_email)
        self.horizontal4.addWidget(self.input_email)
        self.horizontal4.setContentsMargins(20,0,20,30)
        self.form_container.addRow(self.horizontal4)

        self.horizontal5 = QHBoxLayout()

        self.label_passw = QLabel("contraseña")
        self.input_passw = QLineEdit()
        self.input_passw.setContentsMargins(35,0,0,0)
        self.input_passw.setText(self.usuario[5])
        self.horizontal5.addWidget(self.label_passw)
        self.horizontal5.addWidget(self.input_passw)
        self.horizontal5.setContentsMargins(20,0,20,30)
        self.form_container.addRow(self.horizontal5)

        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.clicked.connect(self.guardar_cambios)
        self.form_container.addRow(self.btn_guardar)

        main_widget = QWidget()
        main_widget.setLayout(self.form_container)

        self.set_centrar_widget(main_widget)

    def set_centrar_widget(self, widget):
        layout = QVBoxLayout()
        layout.addWidget(widget, alignment=Qt.AlignTop)
        self.setLayout(layout)

    def guardar_cambios(self):

        # Validar campos obligatorios
        if not all([
            self.input_nombre.text(),
            self.input_apellido_paterno.text(),
            self.input_apellido_materno.text(),
            self.input_email.text(),
            self.input_passw.text()
        ]):
            QMessageBox.warning(
                self, 
                "Campos incompletos", 
                "Por favor complete todos los campos obligatorios"
            )
            return
    
        respuesta = QMessageBox.question(
            self,
            "Confirmar cambios",
            "¿Está seguro que desea guardar los cambios?",
            QMessageBox.Yes | QMessageBox.No
        )
    
        if respuesta == QMessageBox.No:
            return

        try:
            nuevos_datos = {
                'id' : self.usuario[0],
                'nombre' : self.input_nombre.text(),
                'apellido_paterno': self.input_apellido_paterno.text(),
                'apellido_materno': self.input_apellido_materno.text(),
                'email': self.input_email.text(),
                'password': self.input_passw.text()
            }
            conexion = cconexion.conexiondatos()
            if conexion.is_connected():
                cursor = conexion.cursor()

                # Consulta SQL para actualizar
                query = """
                UPDATE users SET 
                    nombre = %s, 
                    apellido_paterno = %s, 
                    apellido_materno = %s, 
                    email = %s, 
                    password = %s 
                WHERE id = %s
                """
                
                valores = (
                    nuevos_datos['nombre'],
                    nuevos_datos['apellido_paterno'],
                    nuevos_datos['apellido_materno'],
                    nuevos_datos['email'],
                    nuevos_datos['password'],
                    nuevos_datos['id']
                )
                
                cursor.execute(query, valores)
                conexion.commit()
                # Mostrar mensaje de éxito
                QMessageBox.information(
                    self, 
                    "Éxito", 
                    "Los cambios se guardaron correctamente"
                )
                self.datos_actualizados.emit()
                self.close()  # Cerrar el modal después de guardar
                
        except Error as e:
            QMessageBox.critical(
                self, 
                "Error", 
                f"No se pudieron guardar los cambios: {str(e)}"
            )
            
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

        