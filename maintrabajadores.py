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
        flags = Qt.WindowFlags(Qt.FramelessWindowHint)  # | Qt.WindowStaysOnTopHint -> put windows on top
        self.setMaximumSize(1080, 720)
        self.setWindowFlags(flags)
        self.setupUi(self)
        self.showNormal()
        self.offset = None
        self.usuario_seleccionado = None

        self.push_close.clicked.connect(self.close_win)
        self.push_maxiniza.clicked.connect(self.mini_maximize)
        self.push_miniza.clicked.connect(self.minimize_win)

        self.push_editar.mousePressEvent = self.open_trabajadores_editar  # Conectar evento
        self.push_editar.setAttribute(QtCore.Qt.WA_Hover, True)
        self.push_editar.setMouseTracking(True)

        self.push_eliminar.mousePressEvent = self.open_modal_eliminar
        self.push_eliminar.setAttribute(QtCore.Qt.WA_Hover, True)
        self.push_eliminar.setMouseTracking(True)

        # Obtener referencia al frame_lista
        self.frame_lista = self.findChild(QFrame, "frame_lista")
        self.scroll_area = QScrollArea(self.frame_lista)
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        self.input_busquedad = self.findChild(QLineEdit, "input_busquedad")
        self.input_busquedad.textChanged.connect(self.filtrar_usuarios)
        
        # Lista completa de usuarios (sin filtrar)
        self.usuarios_completos = []
        
        # Configurar el scroll area
        self.setup_scroll_area()
        
        self.cargar_datos()

    def setup_scroll_area(self):
        """Configura el área de desplazamiento para la lista de usuarios"""
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_content)
        
        # Establecer el layout del frame_lista y añadir el scroll area
        layout = QVBoxLayout(self.frame_lista)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scroll_area)
        
        # Estilo para el scroll area
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 10px;
                background-color: rgb(21, 15, 61);
            }
            QScrollBar::handle:vertical {
                background-color: rgb(28, 21, 84);
                min-height: 20px;
                border-radius: 5px;
            }
        """)

    def cargar_datos(self):
        try:
            conexion = cconexion.conexiondatos()
            if conexion.is_connected():
                cursor = conexion.cursor()
                cursor.execute("SELECT id, nombre, apellido_paterno, apellido_materno, email, password FROM users")
                self.usuarios_completos = cursor.fetchall()
                #self.lista_usuarios = cursor.fetchall()
                self.mostrar_todos_usuarios()
                
                # Limpiar el layout antes de agregar nuevos usuarios
                # for i in reversed(range(self.scroll_layout.count())): 
                #     self.scroll_layout.itemAt(i).widget().setParent(None)
                
                # Crear un widget para cada usuario
                # for usuario in self.lista_usuarios:
                #     self.agregar_usuario_a_lista(usuario)

            
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            QMessageBox.critical(self, "Error", f"No se pudieron cargar los datos: {str(e)}")
        
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def mostrar_todos_usuarios(self):
        """Muestra todos los usuarios sin filtrar"""
        # Limpiar el layout primero
        for i in reversed(range(self.scroll_layout.count())): 
            self.scroll_layout.itemAt(i).widget().setParent(None)
        
        # Mostrar todos los usuarios
        for usuario in self.usuarios_completos:
            self.agregar_usuario_a_lista(usuario)

    def filtrar_usuarios(self):
        """Filtra usuarios según el texto ingresado en el buscador"""
        texto_busqueda = self.input_busquedad.text().lower().strip()
        
        # Limpiar el layout antes de mostrar nuevos resultados
        for i in reversed(range(self.scroll_layout.count())): 
            self.scroll_layout.itemAt(i).widget().setParent(None)
        
        if not texto_busqueda:
            # Si no hay texto de búsqueda, mostrar todos
            self.mostrar_todos_usuarios()
            return
        
        # Filtrar usuarios que coincidan en cualquier campo
        usuarios_filtrados = []
        for usuario in self.usuarios_completos:
            # Buscar en nombre, apellidos y email
            texto_usuario = f"{usuario[1]} {usuario[2]} {usuario[3]} {usuario[4]}".lower()
            if texto_busqueda in texto_usuario:
                usuarios_filtrados.append(usuario)
        
        # Mostrar resultados
        if usuarios_filtrados:
            for usuario in usuarios_filtrados:
                self.agregar_usuario_a_lista(usuario)
        else:
            # Mostrar mensaje si no hay resultados
            self.mostrar_mensaje_sin_resultados(texto_busqueda)

    def mostrar_mensaje_sin_resultados(self, texto_busqueda):
        """Muestra mensaje cuando no hay coincidencias"""
        lbl_no_resultados = QLabel(f"No se encontraron trabajadores relacionados con '{texto_busqueda}'")
        lbl_no_resultados.setStyleSheet("""
            color: white; 
            font-size: 14px;
            padding: 20px;
            qproperty-alignment: AlignCenter;
        """)
        self.scroll_layout.addWidget(lbl_no_resultados)

    def agregar_usuario_a_lista(self, usuario):
        """Crea un widget para mostrar la información de un usuario"""
        frame_usuario = QFrame()
        frame_usuario.setObjectName("frame_usuario")
        frame_usuario.setStyleSheet("""
            #frame_usuario {
                background-color: rgb(28, 21, 84);
                border-radius: 18px;
                margin: 5px;
            }
            QLabel {
                color: white;
                font-size: 12px;
            }
        """)
        frame_usuario.setFixedHeight(80)
        
        # Layout horizontal para los elementos del usuario
        layout = QHBoxLayout(frame_usuario)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Nombre completo
        lbl_nombre = QLabel(f"{usuario[1]}")
        lbl_nombre.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_nombre.setFixedWidth(200)
        
        # Email
        lbl_email = QLabel(usuario[4])
        lbl_email.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        lbl_email.setFixedWidth(200)
        
        # Botón editar
        btn_editar = QPushButton("Editar")
        btn_editar.setObjectName("btn_editar")
        btn_editar.setStyleSheet("""
            #btn_editar {
                background-color: rgb(0, 170, 0);
                border-radius: 20px;
                color: white;
                padding: 5px 15px;
            }
            #btn_editar:hover {
                background-color: rgb(0, 247, 0);
            }
        """)
        btn_editar.setFixedSize(100, 40)
        btn_editar.mousePressEvent = lambda event, u=usuario: self.open_trabajadores_editar(event, u)
        
        # Botón eliminar
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setObjectName("btn_eliminar")
        btn_eliminar.setStyleSheet("""
            #btn_eliminar {
                background-color: rgb(138, 0, 0);
                border-radius: 20px;
                color: white;
                padding: 5px 15px;
            }
            #btn_eliminar:hover {
                background-color: rgb(255, 0, 0);
            }
        """)
        btn_eliminar.setFixedSize(100, 40)
        btn_eliminar.mousePressEvent = lambda event, u=usuario: self.open_modal_eliminar(event, u)
        
        # Agregar widgets al layout
        layout.addWidget(lbl_nombre)
        layout.addWidget(lbl_email)
        layout.addStretch()
        layout.addWidget(btn_editar)
        layout.addWidget(btn_eliminar)
        
        # Agregar el frame al scroll layout
        self.scroll_layout.addWidget(frame_usuario)

    #     self.cargar_datos()

    # def cargar_datos(self):
    #     try:
    #         conexion = cconexion.conexiondatos()
    #         if conexion.is_connected():
    #             cursor = conexion.cursor()
    #             cursor.execute("SELECT id, nombre, apellido_paterno, apellido_materno, email, password FROM users")
    #             self.lista_usuarios = cursor.fetchall()  # Guardar todos los usuarios
                
    #         if self.lista_usuarios:
    #             # Mostrar el primer usuario (puedes ajustar esto para selección)
    #             usuario = self.lista_usuarios[1]
    #             self.label_nombre_trabajadores.setText(usuario[1])  # name
    #             self.label_email_trabajadores.setText(usuario[4])   # email
            
    #     except Error as e:
    #         print(f"Error al conectar a MySQL: {e}")
    #         self.label_nombre_trabajadores.setText("Error al cargar datos")
    #         self.label_email_trabajadores.setText("Error al cargar datos")
        
    #     finally:
    #         if 'conexion' in locals() and conexion.is_connected():
    #             cursor.close()
    #             conexion.close()
            
    def open_trabajadores_editar(self, event, usuario=None):
        if event.button() == QtCore.Qt.LeftButton:
            if not usuario and self.usuario_seleccionado:
                usuario = self.usuario_seleccionado
            elif not usuario:
                QMessageBox.warning(self, "Advertencia", "Por favor seleccione un usuario primero")
                return
                
            self.trabajadores_window = modal_editar(usuario)
            self.trabajadores_window.datos_actualizados.connect(self.refrescar_datos)
            self.trabajadores_window.show()

    def refrescar_datos(self):
        """Recarga la lista de usuarios y muestra notificación"""
        self.cargar_datos()
        
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

    def open_modal_eliminar(self, event, usuario=None):
        if event.button() == QtCore.Qt.LeftButton:
            if not usuario and self.usuario_seleccionado:
                usuario = self.usuario_seleccionado
            elif not usuario:
                QMessageBox.warning(self, "Advertencia", "Por favor seleccione un usuario primero")
                return
                
            self.eliminar_window = modal_eliminar(usuario)
            # Conectar señal para actualizar después de eliminar
            self.eliminar_window.datos_eliminados.connect(self.refrescar_datos)
            self.eliminar_window.show()

class modal_eliminar(QWidget):
    datos_eliminados = Signal()
    def __init__(self, usuario):
        super(modal_eliminar, self).__init__()
        self.usuario = usuario
        self.setWindowTitle("Eliminar trabajador")
        self.resize(400, 300)
        self.setWindowModality(Qt.ApplicationModal)
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(20, 20, 20, 20)
        
        # Título
        lbl_titulo = QLabel(f"¿Deseas eliminar al trabajador {usuario[1]} {usuario[2]}?")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 16px; color: white;")
        layout_principal.addWidget(lbl_titulo)
        
        # Espaciador
        layout_principal.addSpacing(30)
        
        # Botones
        layout_botones = QHBoxLayout()
        
        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: rgb(138, 0, 0);
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgb(255, 0, 0);
            }
        """)
        btn_aceptar.setFixedSize(120, 40)
        btn_aceptar.clicked.connect(self.aceptar_eliminacion)
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: rgb(70, 70, 70);
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgb(100, 100, 100);
            }
        """)
        btn_cancelar.setFixedSize(120, 40)
        btn_cancelar.clicked.connect(self.close)
        
        layout_botones.addStretch()
        layout_botones.addWidget(btn_aceptar)
        layout_botones.addSpacing(20)
        layout_botones.addWidget(btn_cancelar)
        layout_botones.addStretch()
        
        layout_principal.addLayout(layout_botones)
        
        self.setLayout(layout_principal)
        
        # Estilo del modal
        self.setStyleSheet("""
            QWidget {
                background-color: rgb(13, 9, 36);
            }
        """)

    def aceptar_eliminacion(self):
        """Muestra el segundo modal de confirmación"""
        self.confirmacion_window = modal_confirmar_eliminacion(self.usuario)
        self.confirmacion_window.datos_eliminados.connect(self.cerrar_modales)
        self.confirmacion_window.show()

    def cerrar_modales(self):
        """Cierra ambos modales cuando se confirma la eliminación"""
        self.datos_eliminados.emit()
        self.close()

class modal_confirmar_eliminacion(QWidget):
    datos_eliminados = Signal()
    
    def __init__(self, usuario):
        super(modal_confirmar_eliminacion, self).__init__()
        self.usuario = usuario
        self.setWindowTitle("Confirmar eliminación")
        self.resize(400, 300)
        self.setWindowModality(Qt.ApplicationModal)
        
        # Layout principal
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(20, 20, 20, 20)
        
        # Título
        lbl_titulo = QLabel(f"¿Está seguro de eliminar a {usuario[1]} {usuario[2]}?")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 16px; color: white;")
        layout_principal.addWidget(lbl_titulo)
        
        # Espaciador
        layout_principal.addSpacing(30)
        
        # Botones
        layout_botones = QHBoxLayout()
        
        btn_si = QPushButton("Sí, eliminar")
        btn_si.setStyleSheet("""
            QPushButton {
                background-color: rgb(138, 0, 0);
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgb(255, 0, 0);
            }
        """)
        btn_si.setFixedSize(120, 40)
        btn_si.clicked.connect(self.eliminar_usuario)
        
        btn_no = QPushButton("No, cancelar")
        btn_no.setStyleSheet("""
            QPushButton {
                background-color: rgb(70, 70, 70);
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgb(100, 100, 100);
            }
        """)
        btn_no.setFixedSize(120, 40)
        btn_no.clicked.connect(self.close)
        
        layout_botones.addStretch()
        layout_botones.addWidget(btn_si)
        layout_botones.addSpacing(20)
        layout_botones.addWidget(btn_no)
        layout_botones.addStretch()
        
        layout_principal.addLayout(layout_botones)
        
        self.setLayout(layout_principal)
        
        # Estilo del modal
        self.setStyleSheet("""
            QWidget {
                background-color: rgb(13, 9, 36);
            }
        """)

    def datos_actualizados(self, modal_anterior):
        """Muestra modal indicando que los datos se han refrescado"""
        # Cerrar el modal anterior primero
        modal_anterior.close()
        
        modal = QDialog(self)
        modal.setWindowTitle("Actualización")
        modal.setFixedSize(400, 200)
        modal.setModal(True)
        
        layout = QVBoxLayout()
        
        mensaje = QLabel("Los datos se han actualizado correctamente")
        mensaje.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(mensaje, alignment=Qt.AlignCenter)
        
        icono = QLabel()
        icono.setPixmap(QIcon.fromTheme("view-refresh").pixmap(48, 48))
        layout.addWidget(icono, alignment=Qt.AlignCenter)
        
        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: rgb(0, 120, 215);
                color: white;
                border-radius: 10px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: rgb(0, 150, 255);
            }
        """)
        btn_aceptar.clicked.connect(modal.close)
        
        layout.addSpacing(20)
        layout.addWidget(btn_aceptar, alignment=Qt.AlignCenter)
        
        modal.setLayout(layout)
        modal.exec_()

    def elimiacion_usuario(self):
        modal =QDialog(self)
        modal.setWindowTitle("usuario eliminado")
        modal.setFixedSize(300,200)

        layout = QVBoxLayout()

        mensaje = QLabel("Usuario eliminado correctamente")
        mensaje.setStyleSheet("color: #fff; font-size: 15px")
        layout.addWidget(mensaje, alignment=Qt.AlignCenter)

        layout_boton = QHBoxLayout()

        btn_cerrar = QPushButton("Aceptar")
        btn_cerrar.setStyleSheet("""
             QPushButton {
                background-color: rgb(0, 170, 0);
                color: white;
                border-radius: 10px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: rgb(0, 247, 0);
            }  
        """)
        #btn_cerrar.clicked.connect(modal.close)
        btn_cerrar.clicked.connect(lambda: self.datos_actualizados(modal))
        layout.addSpacing(20)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignCenter)
        
        modal.setLayout(layout)
        modal.exec_()

    def eliminar_usuario(self):
        """Elimina el usuario de la base de datos"""
        try:
            conexion = cconexion.conexiondatos()
            if conexion.is_connected():
                cursor = conexion.cursor()
                query = "DELETE FROM users WHERE id = %s"
                cursor.execute(query, (self.usuario[0],))
                conexion.commit()

                self.elimiacion_usuario()
                
                # Emitir señal con el ID del usuario eliminado
                self.datos_eliminados.emit()
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



class modal_editar(QWidget):
    datos_actualizados = Signal()
    
    def __init__(self, usuario):
        super(modal_editar, self).__init__()
        self.usuario = usuario
        self.setWindowTitle("Editar trabajador")
        self.resize(500, 400)
        self.setWindowModality(Qt.ApplicationModal)
        self.setup_ui()

    def setup_ui(self):
        self.vertical1 = QVBoxLayout()
        self.horizontal1 = QHBoxLayout()
        self.form_container = QFormLayout()

        self.label_titulo = QLabel(f"Editar registro de trabajador #{self.usuario[0]}")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("color: white; font-size: 16px; margin-bottom: 20px;")

        self.vertical1.addWidget(self.label_titulo)
        self.form_container.addRow(self.vertical1)

        # Campos del formulario
        self.label_nombre = QLabel("Nombre:")
        self.input_nombre = QLineEdit()
        self.input_nombre.setText(self.usuario[1])
        self.input_nombre.setStyleSheet("margin-bottom: 20px;")
        
        self.label_apellido_paterno = QLabel("Apellido Paterno:")
        self.input_apellido_paterno = QLineEdit()
        self.input_apellido_paterno.setText(self.usuario[2])
        self.input_apellido_paterno.setStyleSheet("margin-bottom: 20px;")
        
        self.label_apellido_materno = QLabel("Apellido Materno:")
        self.input_apellido_materno = QLineEdit()
        self.input_apellido_materno.setText(self.usuario[3])
        self.input_apellido_materno.setStyleSheet("margin-bottom: 20px")
        
        self.label_email = QLabel("Email:")
        self.input_email = QLineEdit()
        self.input_email.setText(self.usuario[4])
        self.input_email.setStyleSheet("margin-bottom: 20px")
        
        self.label_passw = QLabel("Contraseña:")
        self.input_passw = QLineEdit()
        self.input_passw.setText(self.usuario[5])
        self.input_passw.setEchoMode(QLineEdit.Password)
        self.input_passw.setStyleSheet("margin-bottom: 20px")

        # Agregar campos al layout
        self.form_container.addRow(self.label_nombre, self.input_nombre)
        self.form_container.addRow(self.label_apellido_paterno, self.input_apellido_paterno)
        self.form_container.addRow(self.label_apellido_materno, self.input_apellido_materno)
        self.form_container.addRow(self.label_email, self.input_email)
        self.form_container.addRow(self.label_passw, self.input_passw)

        # Botón Guardar
        self.btn_guardar = QPushButton("Guardar Cambios")
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: rgb(0, 170, 0);
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgb(0, 247, 0);
            }
        """)
        self.btn_guardar.clicked.connect(self.validar_campos)
        self.form_container.addRow(self.btn_guardar)

        main_widget = QWidget()
        main_widget.setLayout(self.form_container)

        # Estilo del modal
        self.setStyleSheet("""
            QWidget {
                background-color: rgb(13, 9, 36);
            }
            QLabel {
                color: #fff;
            }
            QLineEdit {
                background-color: #fff;
                border-radius: 5px;
                padding: 5px;
                color: #000;
            }
        """)

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(main_widget)

    def validar_campos(self):
        """Valida que todos los campos estén completos"""
        campos = [
            ("nombre", self.input_nombre.text()),
            ("apellido paterno", self.input_apellido_paterno.text()),
            ("apellido materno", self.input_apellido_materno.text()),
            ("email", self.input_email.text()),
            ("contraseña", self.input_passw.text())
        ]

        campos_vacios = [nombre for nombre, valor in campos if not valor.strip()]

        if campos_vacios:
            self.mostrar_modal_campos_vacios(campos_vacios)
        else:
            self.mostrar_modal_confirmacion()

    def mostrar_modal_campos_vacios(self, campos_vacios):
        """Muestra modal indicando qué campos están vacíos"""
        modal = QDialog(self)
        modal.setWindowTitle("Campos incompletos")
        modal.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        mensaje = QLabel("Por favor complete los siguientes campos:")
        mensaje.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(mensaje)
        
        for campo in campos_vacios:
            lbl_campo = QLabel(f"- {campo.capitalize()}")
            lbl_campo.setStyleSheet("color: white;")
            layout.addWidget(lbl_campo)
        
        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: rgb(70, 70, 70);
                color: white;
                border-radius: 10px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: rgb(100, 100, 100);
            }
        """)
        btn_aceptar.clicked.connect(modal.close)
        
        layout.addSpacing(20)
        layout.addWidget(btn_aceptar, alignment=Qt.AlignCenter)
        
        modal.setLayout(layout)
        modal.exec()

    def mostrar_modal_confirmacion(self):
        """Muestra modal de confirmación para guardar cambios"""
        modal = QDialog(self)
        modal.setWindowTitle("Confirmar cambios")
        modal.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        mensaje = QLabel("¿Está seguro que desea guardar los cambios?")
        mensaje.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(mensaje, alignment=Qt.AlignCenter)
        
        layout_botones = QHBoxLayout()
        
        btn_aceptar = QPushButton("Sí, guardar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: rgb(0, 170, 0);
                color: white;
                border-radius: 10px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: rgb(0, 247, 0);
            }
        """)
        btn_aceptar.clicked.connect(lambda: self.guardar_cambios(modal))
        
        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: rgb(70, 70, 70);
                color: white;
                border-radius: 10px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: rgb(100, 100, 100);
            }
        """)
        btn_cancelar.clicked.connect(modal.close)
        
        layout_botones.addWidget(btn_aceptar)
        layout_botones.addWidget(btn_cancelar)
        
        layout.addSpacing(20)
        layout.addLayout(layout_botones)
        
        modal.setLayout(layout)
        modal.exec()

    def guardar_cambios(self, modal_confirmacion):
        """Guarda los cambios en la base de datos"""
        try:
            nuevos_datos = {
                'id': self.usuario[0],
                'nombre': self.input_nombre.text(),
                'apellido_paterno': self.input_apellido_paterno.text(),
                'apellido_materno': self.input_apellido_materno.text(),
                'email': self.input_email.text(),
                'password': self.input_passw.text()
            }
            
            conexion = cconexion.conexiondatos()
            if conexion.is_connected():
                cursor = conexion.cursor()
                
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
                
                # Cerrar modal de confirmación
                modal_confirmacion.close()
                
                # Mostrar modal de éxito
                self.mostrar_modal_exito()
                
                # Emitir señal para actualizar datos
                self.datos_actualizados.emit()


                self.close()
                
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

    def mostrar_modal_refrescado(self, modal_anterior):
        """Muestra modal indicando que los datos se han refrescado"""
        # Cerrar el modal anterior primero
        modal_anterior.close()
        
        modal = QDialog(self)
        modal.setWindowTitle("Actualización")
        modal.setFixedSize(400, 200)
        modal.setModal(True)
        
        layout = QVBoxLayout()
        
        mensaje = QLabel("Los datos se han actualizado correctamente")
        mensaje.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(mensaje, alignment=Qt.AlignCenter)
        
        icono = QLabel()
        icono.setPixmap(QIcon.fromTheme("view-refresh").pixmap(48, 48))
        layout.addWidget(icono, alignment=Qt.AlignCenter)
        
        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: rgb(0, 120, 215);
                color: white;
                border-radius: 10px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: rgb(0, 150, 255);
            }
        """)
        btn_aceptar.clicked.connect(modal.close)
        
        layout.addSpacing(20)
        layout.addWidget(btn_aceptar, alignment=Qt.AlignCenter)
        
        modal.setLayout(layout)
        modal.exec_()


    def mostrar_modal_exito(self):
        """Muestra modal indicando que los cambios se guardaron correctamente"""
        modal = QDialog(self)
        modal.setWindowTitle("Cambios guardados")
        modal.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        mensaje = QLabel("Los cambios se guardaron correctamente")
        mensaje.setStyleSheet("color: white; font-size: 14px;")
        layout.addWidget(mensaje, alignment=Qt.AlignCenter)
        
        icono = QLabel()
        icono.setPixmap(QIcon.fromTheme("dialog-ok").pixmap(48, 48))
        layout.addWidget(icono, alignment=Qt.AlignCenter)
        
        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: rgb(0, 170, 0);
                color: white;
                border-radius: 10px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: rgb(0, 247, 0);
            }
        """)
        btn_aceptar.clicked.connect(lambda: self.mostrar_modal_refrescado(modal))
        
        layout.addSpacing(20)
        layout.addWidget(btn_aceptar, alignment=Qt.AlignCenter)
        
        modal.setLayout(layout)
        modal.exec()