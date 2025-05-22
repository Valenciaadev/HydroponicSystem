import bcrypt
from mysql.connector import Error
from models.database import connect_db
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys


class ManagmentAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__(ventana_login)
        self.ventana_login = ventana_login
        self.offset = None
        self.usuario_seleccionado = None

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
            QLabel#Title {
                font-size: 28px;
                font-weight: bold;
                color: white;
                margin-bottom: 20px;
                qproperty-alignment: AlignCenter;
            }

            QPushButton {
                padding: 8px 16px;
                border-radius: 20px;
                background-color: #7FD1B9;
                color: black;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6fc9a9;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        container_frame = QFrame()
        container_frame.setStyleSheet("background-color: #28243C; border-radius: 15px;")
        container_layout = QVBoxLayout(container_frame)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(18)

        titulo = QLabel("Gestor de usuarios")
        titulo.setObjectName("Title")

        # Sección superior
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(20)
        layout.addWidget(titulo)

        # Frame de búsqueda
        frame_busqueda = QFrame()
        frame_busqueda.setFrameShape(QFrame.StyledPanel)
        frame_busqueda.setObjectName("frame_busquedad")
        frame_busqueda.setStyleSheet("""
            #frame_busquedad {
                padding: 15px;
                border-radius: 10px;
                background-color: #1E1B2E;
            }
        """)
        frame_busqueda_layout = QHBoxLayout(frame_busqueda)
        frame_busqueda_layout.setContentsMargins(20, 20, 20, 20)
        frame_busqueda_layout.setSpacing(20)

        form_layout = QFormLayout()
        # form_layout.setVerticalSpacing(15)
        # form_layout.setHorizontalSpacing(15)
        # form_layout.setContentsMargins(0,0,0,0)

        self.input_field = self.create_gradient_input("ingresa texto")

        label = QLabel("Buscador de usuarios")
        label.setStyleSheet("font-size: 15px; min-width: 150px; background: transparent;")

        form_layout.addRow(label, self.input_field)

        self.input_field.input_field.textChanged.connect(self.filtrar_usuarios)

        frame_busqueda_layout.addLayout(form_layout, stretch=1)

        layout.addWidget(frame_busqueda)

        # Scroll Area
        scrollarea = QScrollArea()
        scrollarea.setWidgetResizable(True)
        scrollarea.setStyleSheet("""
            QScrollArea {
                border-radius: 20px;
                background-color: #1E1B2E;
                padding: 10px;
            }
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #f1f1f1;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        self.frame_container = QWidget()
        self.scroll_layout = QVBoxLayout(self.frame_container)
        self.scroll_layout.setAlignment(Qt.AlignTop)
        self.scroll_layout.setSpacing(15)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)

        scrollarea.setWidget(self.frame_container)
        # top_layout.addWidget(scrollarea)

        frame_scroll = QFrame()
        frame_scroll.setStyleSheet("""
            background-color: #7FD1B9;
            border-radius: 20px;
        """)
        frame_scroll_layout = QVBoxLayout(frame_scroll)
        frame_scroll_layout.setContentsMargins(7,7,7,7)
        frame_scroll_layout.setSpacing(20)
        frame_scroll_layout.addWidget(scrollarea)

        layout.addWidget(frame_scroll)

        space_between = QWidget()
        space_between.setFixedHeight(30)
        container_layout.addWidget(space_between)

        container_layout.addLayout(layout)
        main_layout.addWidget(container_frame)

        self.usuarios_completos = []

        self.cargar_datos()

    def create_gradient_input(self, placeholder_text=""):
        """Crea un input con el marco degradado como los actuadores"""
        outer_frame = QFrame()
        outer_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D4B8, stop:1 #1E2233);
                border-radius: 20px;
                padding: 2px;
            }
        """)
        outer_frame.setFixedHeight(45)

        inner_frame = QFrame()
        inner_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 18px;
            }
        """)

        layout = QHBoxLayout(inner_frame)
        layout.setContentsMargins(10, 0, 10, 0)

        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder_text)
        input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QLineEdit::placeholder {
                color: #f1f1f1;  /* Color del texto */
                font-style: italic;  /* Cursiva */
            }
        """)
        layout.addWidget(input_field)

        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(inner_frame)

        # Guardamos referencia al input
        outer_frame.input_field = input_field

        return outer_frame

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

    def cargar_datos(self):
        """Carga los datos de usuarios usando la clase CargarUsuarios"""
        try:
            # Obtener todos los usuarios usando la clase CargarUsuarios
            conn = connect_db()
            if conn:
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT * FROM usuarios")
                self.usuarios_completos = cursor.fetchall()
                cursor.close()
                conn.close()

                if self.usuarios_completos:
                    self.mostrar_todos_usuarios()
                else:
                    self.mostrar_mensaje_sin_resultado("No hay usuarios registrados")
            else:
                raise Exception("No se pudo conectar a la base de datos")

        except Exception as e:
            print(f"❌ Error al cargar usuarios: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron cargar los usuarios:\n{str(e)}"
            )
            self.usuarios_completos = []
            self.limpiar_lista_usuarios()

    def buscar_usuario(self, texto, exacto=False):
        """Busca usuario con opción de coincidencia exacta o parcial"""
        texto = texto.strip().lower()
        resultados = []
        
        for usuario in self.usuarios_completos:
            nombre = usuario.get('nombre', '').lower()
            apellido_p = usuario.get('apellido_paterno', '').lower()
            apellido_m = usuario.get('apellido_materno', '').lower()
            nombre_completo = f"{nombre} {apellido_p} {apellido_m}".strip()
            
            if exacto:
                if texto == nombre_completo:
                    return [usuario]  # Retorna lista con un solo elemento
            else:
                if (texto in nombre or 
                    texto in apellido_p or 
                    texto in apellido_m or
                    texto in nombre_completo):
                    resultados.append(usuario)
        
        return resultados if not exacto else None

    def filtrar_usuarios(self):
        """Filtra usuarios según el texto de búsqueda"""
        texto_busqueda = self.input_field.input_field.text().strip().lower()

        # Limpiar la lista actual
        self.limpiar_lista_usuarios()

        if not texto_busqueda:
            self.mostrar_todos_usuarios()
            return

        usuarios = self.buscar_usuario(texto_busqueda)

        if usuarios:
            for usuario in usuarios:
                self.agregar_usuario_a_lista(usuario)
        else:
            self.mostrar_mensaje_sin_resultado(texto_busqueda)

        
    def limpiar_lista_usuarios(self):
        """Elimina todos los widgets de la lista de usuarios"""
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def mostrar_todos_usuarios(self):
        """Muestra todos los usuarios en la lista"""
        self.limpiar_lista_usuarios()
        for usuario in self.usuarios_completos:
            self.agregar_usuario_a_lista(usuario)

    def agregar_usuario_a_lista(self, usuario):
        """Crea y agrega un widget de usuario a la lista"""
        frame = QFrame()
        frame.setObjectName("usuarioFrame")
        frame.setStyleSheet("""
            #usuarioFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #60D4B8, stop:1 #1E2233);
                    border-radius: 35px;
                    padding: 2px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
        """)
        frame.setFixedHeight(80)

        frame_layout = QFrame()
        frame_layout.setStyleSheet("""
            background-color: #28243C;
            border-radius: 35px;
        """)
        frame_layout.setFixedHeight(75)
        frame_layout_content = QHBoxLayout(frame_layout)
        frame_layout_content.setContentsMargins(20,10,20,10)

        lbl_nombre = QLabel(
            f"{usuario['nombre']}"
        )
        lbl_nombre.setStyleSheet("font-weight: bold; font-size: 16px; background-color: transparent;")
        frame_layout_content.addWidget(lbl_nombre)

        frame_layout_content.addStretch()

        # Botones de acción
        btn_layout = QHBoxLayout()

        btn_editar = QPushButton("Editar")
        btn_editar.setObjectName("btnEditar")
        btn_editar.setStyleSheet("""
            #btnEditar {
                background-color: #4CAF50;
                color: white;
                border-radius: 15px;
            }
            #btnEditar:hover {
                background-color: #45a049;
            }
        """)
        btn_editar.setFixedWidth(180)
        btn_editar.clicked.connect(lambda: self.open_usuarios_editar(usuario))

        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setObjectName("btnEliminar")
        btn_eliminar.setStyleSheet("""
            #btnEliminar {
                background-color: #f44336;
                color: white;
                border-radius: 15px;
            }
            #btnEliminar:hover {
                background-color: #d32f2f;
            }
        """)
        btn_eliminar.setFixedWidth(180)
        btn_eliminar.clicked.connect(lambda: self.open_usuarios_eliminados(usuario))

        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_eliminar)

        frame_layout_content.addLayout(btn_layout)

        outer_layout = QVBoxLayout(frame)
        outer_layout.setContentsMargins(0,0,0,0)
        outer_layout.addWidget(frame_layout)

        self.scroll_layout.addWidget(frame)

    def mostrar_mensaje_sin_resultado(self, texto_busqueda):
        """Muestra un mensaje cuando no hay resultados de búsqueda"""
        frame = QFrame()
        frame.setStyleSheet("""
            background-color: #2c3e50;
            border-radius: 10px;
        """)
        
        layout = QVBoxLayout(frame)
        layout.setContentsMargins(20, 20, 20, 20)
        
        lbl = QLabel(f"No se encontraron usuarios para: '{texto_busqueda}'")
        lbl.setStyleSheet("""
            color: #FFFFFF;
            font-size: 16px;
            qproperty-alignment: AlignCenter;
        """)
        
        layout.addWidget(lbl)
        self.scroll_layout.addWidget(frame)

    def open_usuarios_editar(self, usuario):
        self.editar_window = ModalEditar(usuario)
        self.editar_window.datos_actualizados.connect(self.actualizar_datos)
        self.editar_window.show()

    def open_usuarios_eliminados(self, usuario):
        self.eliminar_window = ModalEliminar(usuario)
        self.eliminar_window.usuario_eliminado.connect(self.actualizar_datos)
        self.eliminar_window.show()

    def actualizar_datos(self):
        self.cargar_datos()

class ModalEliminar(QWidget):
    usuario_eliminado = pyqtSignal()
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Elimiar usuario")
        self.resize(400,300)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        lbl_titulo = QLabel(f"¿Deseas eliminar al usuario {self.usuario['nombre']}?")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 16px; color; white;")
        layout.addWidget(lbl_titulo)

        layout.setSpacing(30)

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

        layout.addLayout(layout_botones)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: rgb(13,9,36);
            }
        """)

    def aceptar_eliminacion(self):
        self.confirmacion_window = modal_confirmar_eliminacion(self.usuario)
        self.confirmacion_window.usuario_eliminado.connect(self.cerrar_modales)
        self.confirmacion_window.show()

    def cerrar_modales(self):
        self.usuario_eliminado.emit()
        self.close()

class modal_confirmar_eliminacion(QWidget):
    usuario_eliminado = pyqtSignal()

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Confirmar eliminacion")
        self.resize(400,300)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        layout = QVBoxLayout()
        layout.setContentsMargins(20,20,20,20)

        lbl_titulo = QLabel(f"¿Está seguro de eliminar a {usuario['nombre']}")
        lbl_titulo.setAlignment(Qt.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 16px; color: #fff;")
        layout.addWidget(lbl_titulo)

        layout.addSpacing(30)

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
        layout_botones.setSpacing(20)
        layout_botones.addWidget(btn_no)
        layout_botones.addStretch()

        layout.addLayout(layout_botones)

        self.setLayout(layout)

        self.setStyleSheet("""
            QWidget {
                background-color: rgb(13, 9, 36);
            }
        """)

    def datos_actualizados(self, modal_anterior):
        """Muestra modal indicando que los datos se han refrescado"""
        # Cerrar el modal anterior primero
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
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
        modal = QDialog(self)
        modal.setWindowTitle("usuario eliminado")
        modal.setFixedSize(300, 200)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

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
        btn_cerrar.clicked.connect(lambda: self.datos_actualizados(modal))
        layout.addSpacing(20)
        layout.addWidget(btn_cerrar, alignment=Qt.AlignCenter)

        modal.setLayout(layout)
        modal.exec_()


    def eliminar_usuario(self):
        """Elimina el usuario de la base de datos"""
        try:
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                query = "DELETE FROM usuarios WHERE id = %s"
                cursor.execute(query, (self.usuario["id"],))
                conn.commit()

                # Mostrar mensaje de éxito
                self.elimiacion_usuario()

                # Emitir señal para actualizar la lista principal
                self.usuario_eliminado.emit()
                self.close()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo eliminar el usuario:\n{str(e)}"
            )
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()


class ModalEditar(QWidget):
    datos_actualizados = pyqtSignal()

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Editar usuario")
        self.resize(450, 550)
        self.setWindowModality(Qt.ApplicationModal)
        #self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)

        self.setStyleSheet("""
            QWidget {
                background-color: #28243C;
                color: white;
                border-radius: 30px;
            }
        """)
        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 25, 25, 30)
        main_layout.setSpacing(20)

        # --- Título ---
        self.label_titulo = QLabel(f"EDITAR USUARIO #{self.usuario['nombre']}")
        self.label_titulo.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #7FD1B9;
                qproperty-alignment: AlignCenter;
                margin-bottom: 20px;
            }
        """)
        main_layout.addWidget(self.label_titulo)

        # --- Formulario ---
        form_layout = QFormLayout()
        # form_layout.setVerticalSpacing(20)
        # form_layout.setHorizontalSpacing(15)

        # Campos del formulario con nombres de objeto
        self.frame_nombre = self.create_gradient_input(self.usuario["nombre"])
        self.frame_apellido_paterno = self.create_gradient_input(self.usuario["apellido_paterno"])
        self.frame_apellido_materno = self.create_gradient_input(self.usuario["apellido_materno"])
        self.frame_email = self.create_gradient_input(self.usuario["email"])
        self.frame_password = self.create_gradient_input("Ingresa nueva contraseña")

        campos = [
            ("Nombre", self.frame_nombre),
            ("Apellido Paterno", self.frame_apellido_paterno),
            ("Apellido Materno", self.frame_apellido_materno),
            ("Email", self.frame_email),
            ("Nueva Contraseña", self.frame_password)
        ]

        for label_text, input_widget in campos:
            label = QLabel(label_text)
            label.setStyleSheet("font-size: 14px; font-weight: bold;")
            form_layout.addRow(label, input_widget)

        main_layout.addLayout(form_layout)
        main_layout.addStretch()

        # --- Botones ---
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(20)

        btn_guardar = QPushButton("Guardar Cambios")
        btn_cancelar = QPushButton("Cancelar")

        for btn in [btn_guardar, btn_cancelar]:
            btn.setFixedHeight(40)
            btn.setCursor(Qt.PointingHandCursor)

        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #7FD1B9;
                color: black;
                font-weight: bold;
                border-radius: 20px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #6bc0a8;
            }
        """)

        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                font-weight: bold;
                border-radius: 20px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #e05c5c;
            }
        """)

        btn_layout.addStretch()
        btn_layout.addWidget(btn_cancelar)
        btn_layout.addWidget(btn_guardar)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        # Conexiones
        btn_guardar.clicked.connect(self.validar_campos)
        btn_cancelar.clicked.connect(self.close)

    def create_gradient_input(self, placeholder_text=""):
        """Crea un input con el marco degradado como los actuadores"""
        outer_frame = QFrame()
        outer_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D4B8, stop:1 #1E2233);
                border-radius: 20px;
                padding: 2px;
            }
        """)
        outer_frame.setFixedHeight(45)

        inner_frame = QFrame()
        inner_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                border-radius: 18px;
            }
        """)

        layout = QHBoxLayout(inner_frame)
        layout.setContentsMargins(10, 0, 10, 0)

        input_field = QLineEdit()
        input_field.setText(placeholder_text)
        #input_field.setPlaceholderText(placeholder_text)
        input_field.setStyleSheet("""
            QLineEdit {
                background: transparent;
                border: none;
                color: white;
                font-size: 14px;
                padding: 5px;
            }
            QLineEdit::placeholder {
                color: #f1f1f1;  /* Color del texto */
                font-style: italic;  /* Cursiva */
            }
        """)
        layout.addWidget(input_field)

        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(inner_frame)

        # Guardamos referencia al input
        outer_frame.input_field = input_field

        return outer_frame

    def validar_campos(self):
        """Valida que todos los campos estén completos"""
        # Obtener todos los campos del formulario
        campos = [
            ("nombre", self.frame_nombre.input_field.text()),
            ("apellido paterno", self.frame_apellido_paterno.input_field.text()),
            ("apellido materno", self.frame_apellido_materno.input_field.text()),
            ("email", self.frame_email.input_field.text()),
            ("contraseña", self.frame_password.input_field.text())
        ]

        # Solo requerir campos obligatorios (excluyendo contraseña si no es necesaria)
        campos_requeridos = campos[:-1]  # Excluye la contraseña
        campos_vacios = [nombre for nombre, valor in campos_requeridos if not valor.strip()]

        if campos_vacios:
            self.mostrar_modal_campos_vacios(campos_vacios)
        else:
            self.mostrar_modal_confirmacion()

    def mostrar_modal_campos_vacios(self, campos_vacios):
        """Muestra modal indicando qué campos están vacíos"""
        modal = QDialog(self)
        modal.setWindowTitle("Campos incompletos")
        modal.setFixedSize(400, 200)
        modal.setStyleSheet("""
            QDialog {
                background-color: #1E1B2E;
                border-radius: 15px;
            }
            QLabel {
                color: white;
            }
        """)

        layout = QVBoxLayout()

        mensaje = QLabel("Por favor complete los siguientes campos:")
        mensaje.setStyleSheet("font-size: 14px;")
        layout.addWidget(mensaje)

        for campo in campos_vacios:
            lbl_campo = QLabel(f"- {campo.capitalize()}")
            lbl_campo.setStyleSheet("color: #FF6B6B;")
            layout.addWidget(lbl_campo)

        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #7FD1B9;
                color: black;
                font-weight: bold;
                border-radius: 20px;
                min-width: 120px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #6bc0a8;
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
        modal.setStyleSheet("""
            QDialog {
                background-color: #1E1B2E;
                border-radius: 15px;
            }
            QLabel {
                color: white;
            }
        """)

        layout = QVBoxLayout()

        mensaje = QLabel("¿Está seguro que desea guardar los cambios?")
        mensaje.setStyleSheet("font-size: 14px;")
        layout.addWidget(mensaje, alignment=Qt.AlignCenter)

        layout_botones = QHBoxLayout()

        btn_aceptar = QPushButton("Sí, guardar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #7FD1B9;
                color: black;
                font-weight: bold;
                border-radius: 20px;
                min-width: 120px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #6bc0a8;
            }
        """)
        btn_aceptar.clicked.connect(lambda: self.guardar_cambios(modal))

        btn_cancelar = QPushButton("Cancelar")
        btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #FF6B6B;
                color: white;
                font-weight: bold;
                border-radius: 20px;
                min-width: 120px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #e05c5c;
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
        conn = None
        cursor = None
        try:
            nuevos_datos = {
                'id': self.usuario['id'],
                'nombre': self.frame_nombre.input_field.text().strip(),
                'apellido_paterno': self.frame_apellido_paterno.input_field.text().strip(),
                'apellido_materno': self.frame_apellido_materno.input_field.text().strip(),
                'email': self.frame_email.input_field.text().strip(),
                'password': self.frame_password.input_field.text().strip()
            }

            conn = connect_db()
            if conn and conn.is_connected():
                cursor = conn.cursor()

                if nuevos_datos['password']:
                    # Encriptar la nueva contraseña
                    salt = bcrypt.gensalt()
                    hashed_password = bcrypt.hashpw(nuevos_datos['password'].encode('utf-8'), salt)

                    query = """
                    UPDATE usuarios SET
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
                        hashed_password.decode('utf-8'),  # Guardamos el hash como string
                        nuevos_datos['id']
                    )
                else:
                    query = """
                    UPDATE usuarios SET
                        nombre = %s,
                        apellido_paterno = %s,
                        apellido_materno = %s,
                        email = %s
                    WHERE id = %s
                    """
                    valores = (
                        nuevos_datos['nombre'],
                        nuevos_datos['apellido_paterno'],
                        nuevos_datos['apellido_materno'],
                        nuevos_datos['email'],
                        nuevos_datos['id']
                    )

                cursor.execute(query, valores)
                conn.commit()

                modal_confirmacion.close()
                self.mostrar_modal_exito()
                self.datos_actualizados.emit()
                self.close()

        except Error as e:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudieron guardar los cambios: {str(e)}"
            )
            print(f"Error en guardar_cambios: {str(e)}")

        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    def mostrar_modal_exito(self):
        """Muestra modal indicando que los cambios se guardaron correctamente"""
        modal = QDialog(self)
        modal.setWindowTitle("Cambios guardados")
        modal.setFixedSize(400, 200)
        modal.setStyleSheet("""
            QDialog {
                background-color: #1E1B2E;
                border-radius: 15px;
            }
            QLabel {
                color: white;
            }
        """)

        layout = QVBoxLayout()

        mensaje = QLabel("Los cambios se guardaron correctamente")
        mensaje.setStyleSheet("font-size: 14px;")
        layout.addWidget(mensaje, alignment=Qt.AlignCenter)

        success_icon = self.style().standardIcon(QStyle.SP_DialogOkButton)
        icon_label = QLabel()
        icon_label.setPixmap(success_icon.pixmap(64, 64))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)

        btn_aceptar = QPushButton("Aceptar")
        btn_aceptar.setStyleSheet("""
            QPushButton {
                background-color: #7FD1B9;
                color: black;
                font-weight: bold;
                border-radius: 20px;
                min-width: 120px;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #6bc0a8;
            }
        """)
        btn_aceptar.clicked.connect(modal.close)

        layout.addSpacing(20)
        layout.addWidget(btn_aceptar, alignment=Qt.AlignCenter)

        modal.setLayout(layout)
        modal.exec()