import bcrypt
from mysql.connector import Error
from models.database import connect_db
from controllers.auth_controller import show_message, is_valid_email
from PyQt5 import QtCore
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #1E1B2E; color: white;")

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)

        self.title = QLabel("Sistema Hidropónico")
        self.title.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.title)

        self.minimize_button = QPushButton("")
        self.minimize_button.setIcon(QIcon("assets/icons/btn-minimize-white.svg"))
        self.minimize_button.setIconSize(QSize(24, 24))
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("background-color: transparent;")
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        self.minimize_button.setCursor(Qt.PointingHandCursor)
        self.minimize_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.minimize_button)

        self.close_button = QPushButton("")
        self.close_button.setIcon(QIcon("assets/icons/btn-close-white.svg"))
        self.close_button.setIconSize(QSize(24, 24))
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("background-color: transparent;")
        self.close_button.clicked.connect(self.parent.close)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.close_button)

        self.setLayout(layout)
        self.drag_position = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()

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
                margin-left: 15px;
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

        # --- Frame principal ---
        container_frame = QFrame()
        container_frame.setStyleSheet("background-color: #28243C; border-radius: 15px;")
        container_layout = QVBoxLayout(container_frame)
        container_layout.setContentsMargins(20, 40, 20, 20)

        # --- Título ---
        titulo = QLabel("Gestor de usuarios")
        titulo.setObjectName("Title")

        # --- Layout horizontal para título ---
        top_layout = QHBoxLayout()
        top_layout.addWidget(titulo, alignment=Qt.AlignVCenter)
        top_layout.addStretch()

        # --- Contenedor para los usuarios ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
            }
            QScrollBar:vertical {
                width: 12px;
                background: #252535;
            }
            QScrollBar::handle:vertical {
                background: #4a4a5a;
                min-height: 20px;
                border-radius: 6px;
            }
        """)
        
        scroll_content = QWidget()
        scroll_content.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)

        # --- Frame de búsqueda ---
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
        self.input_field = self.create_gradient_input("ingresa texto")
        label = QLabel("Buscador de usuarios")
        label.setStyleSheet("font-size: 15px; min-width: 150px; background: transparent;")
        form_layout.addRow(label, self.input_field)
        self.input_field.input_field.textChanged.connect(self.filtrar_usuarios)
        frame_busqueda_layout.addLayout(form_layout, stretch=1)

        # --- Layout principal ---
        container_layout.addLayout(top_layout)

        # Espacio entre el título y el buscador
        space_between = QWidget()
        space_between.setFixedHeight(30)
        container_layout.addWidget(space_between)

        container_layout.addWidget(frame_busqueda)

        # Espacio entre el buscador y la lista
        space_between2 = QWidget()
        space_between2.setFixedHeight(20)
        container_layout.addWidget(space_between2)

        # Configurar el scroll area
        self.scroll_layout = QVBoxLayout(scroll_content)
        scroll_content.setContentsMargins(0, 0, 0, 0)
        scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(30)

        scroll_area.setWidget(scroll_content)
        container_layout.addWidget(scroll_area)

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
        # Frame exterior con gradiente
        outer_frame = QFrame()
        outer_frame.setObjectName("usuarioFrame")
        outer_frame.setStyleSheet("""
            #usuarioFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D4B8, stop:1 #1E2233);
                border-radius: 35px;
                padding: 2px;
            }
        """)
        outer_frame.setFixedHeight(75)  # Misma altura que en ActuatorsAppAdmin

        # Frame interior
        inner_frame = QFrame()
        inner_frame.setStyleSheet("""
            background-color: #1f2232;
            border-radius: 35px;
        """)
        inner_frame.setFixedHeight(70)  # Misma altura que en ActuatorsAppAdmin
        
        # Layout del frame interior
        frame_layout = QHBoxLayout(inner_frame)
        frame_layout.setContentsMargins(20, 10, 20, 10)  # Mismos márgenes que en ActuatorsAppAdmin

        # Etiqueta con el nombre del usuario
        lbl_nombre = QLabel(f"{usuario['nombre']}")
        lbl_nombre.setStyleSheet("""
            color: white;
            font-weight: bold;
            font-size: 16px;
            background-color: transparent;
        """)
        frame_layout.addWidget(lbl_nombre)

        frame_layout.addStretch()

        # Botones de acción (estilo igual que en ActuatorsAppAdmin)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)  # Espaciado entre botones

        # Botón Editar (estilo similar al de "Características")
        btn_editar = QPushButton("Editar")
        btn_editar.setObjectName("btnEditar")
        btn_editar.setStyleSheet("""
            #btnEditar {
                background-color: #0D2B23;
                color: white;
                font-weight: bold;
                border-radius: 14px;
                padding: 6px 14px;
                border: 1px solid #10B981;
                min-width: 98px;
            }
            #btnEditar:hover {
                background-color: #218463;
            }
        """)
        btn_editar.clicked.connect(lambda: self.open_usuarios_editar(usuario))

        # Botón Eliminar (estilo similar al de "Apagar")
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.setObjectName("btnEliminar")
        btn_eliminar.setStyleSheet("""
            #btnEliminar {
                background-color: #3A1212;
                color: white;
                font-weight: bold;
                border-radius: 14px;
                padding: 6px 14px;
                min-width: 98px;
                border: 1px solid #DC2626;
            }
            #btnEliminar:hover {
                background-color: #8B1E1E;
            }
        """)
        btn_eliminar.clicked.connect(lambda: self.open_usuarios_eliminados(usuario))

        btn_layout.addWidget(btn_editar)
        btn_layout.addWidget(btn_eliminar)

        frame_layout.addLayout(btn_layout)

        # Layout principal del frame exterior
        outer_layout = QVBoxLayout(outer_frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.addWidget(inner_frame)

        # Agregar al layout de scroll
        self.scroll_layout.addWidget(outer_frame)

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

class ModalEliminar(QDialog):
    usuario_eliminado = pyqtSignal()
    
    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(450, 150)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1B2E;
                border: 2px solid black;
                border-radius: 10px;
                font: bold;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 15)
        
        # Barra de título personalizada
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        content_layout = QVBoxLayout()
        
        label = QLabel(f"¿Deseas eliminar al usuario {self.usuario['nombre']}?")
        label.setFont(QFont("Candara", 12))
        label.setStyleSheet("color: white; font:bold;")
        label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(label)
        
        button_layout = QHBoxLayout()
        
        confirm_button = QPushButton(" Aceptar")
        confirm_button.setIcon(QIcon("assets/icons/btn-accept-white.svg"))
        confirm_button.setIconSize(QSize(24, 24))
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #F10D32;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font: bold;
            }
            QPushButton:hover {
                background-color: #D20B2C;
            }
        """)        
        confirm_button.clicked.connect(self.aceptar_eliminacion)
        button_layout.addWidget(confirm_button)
        
        cancel_button = QPushButton(" Cancelar")
        cancel_button.setIcon(QIcon("assets/icons/btn-return-white.svg"))
        cancel_button.setIconSize(QSize(24, 24))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: gray;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)
        
        content_layout.addLayout(button_layout)
        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)

    def aceptar_eliminacion(self):
        self.confirmacion_window = modal_confirmar_eliminacion(self.usuario)
        self.confirmacion_window.usuario_eliminado.connect(self.cerrar_modales)
        self.confirmacion_window.show()

    def cerrar_modales(self):
        self.usuario_eliminado.emit()
        self.close()

class modal_confirmar_eliminacion(QDialog):
    usuario_eliminado = pyqtSignal()

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(450, 150)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1B2E;
                border: 2px solid black;
                border-radius: 10px;
                font: bold;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 15)
        
        # Barra de título personalizada
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        content_layout = QVBoxLayout()
        
        label = QLabel(f"¿Está seguro de eliminar a {self.usuario['nombre']}?")
        label.setFont(QFont("Candara", 12))
        label.setStyleSheet("color: white; font:bold;")
        label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(label)
        
        button_layout = QHBoxLayout()
        
        confirm_button = QPushButton(" Sí, eliminar")
        confirm_button.setIcon(QIcon("assets/icons/btn-accept-white.svg"))
        confirm_button.setIconSize(QSize(24, 24))
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #F10D32;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font: bold;
            }
            QPushButton:hover {
                background-color: #D20B2C;
            }
        """)        
        confirm_button.clicked.connect(self.eliminar_usuario)
        button_layout.addWidget(confirm_button)
        
        cancel_button = QPushButton(" Cancelar")
        cancel_button.setIcon(QIcon("assets/icons/btn-return-white.svg"))
        cancel_button.setIconSize(QSize(24, 24))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: gray;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        cancel_button.clicked.connect(self.close)
        button_layout.addWidget(cancel_button)
        
        content_layout.addLayout(button_layout)
        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)

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

                # Mostrar mensaje de éxito usando show_message
                show_message("Éxito", "Usuario eliminado correctamente", "success", self)

                # Emitir señal para actualizar la lista principal
                self.usuario_eliminado.emit()
                self.close()

        except Exception as e:
            show_message("Error", f"No se pudo eliminar el usuario:\n{str(e)}", "error", self)
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()


class ModalEditar(QDialog):
    datos_actualizados = pyqtSignal()

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(400, 600)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 10)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        title_label = QLabel(f"Editar Usuario: {self.usuario['nombre']}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Candara", 14))
        title_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title_label)

        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setVerticalSpacing(15)

        # Campos del formulario
        self.nombre_input = self.create_labeled_input("Nombre", self.usuario['nombre'])
        form_layout.addRow("", self.nombre_input)

        self.apellido_p_input = self.create_labeled_input("Apellido Paterno", self.usuario['apellido_paterno'])
        form_layout.addRow("", self.apellido_p_input)

        self.apellido_m_input = self.create_labeled_input("Apellido Materno", self.usuario['apellido_materno'])
        form_layout.addRow("", self.apellido_m_input)

        self.email_input = self.create_labeled_input("Email", self.usuario['email'])
        form_layout.addRow("", self.email_input)

        self.password_input = self.create_labeled_input("Nueva Contraseña", "", is_password=True)
        form_layout.addRow("", self.password_input)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)

        # Botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)

        back_button = QPushButton("Cancelar")
        back_button.setIcon(QIcon("assets/icons/btn-undo-white.svg"))
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: white;
                border: 2px solid #444;
                border-radius: 30px;
                padding: 6px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #444;
            }
        """)
        back_button.clicked.connect(self.close)
        back_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        save_button = QPushButton("Guardar")
        save_button.setIcon(QIcon("assets/icons/btn-save-white.svg"))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #30EACE;
                color: black;
                border: 2px solid #30EACE;
                border-radius: 30px;
                padding: 6px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #25C9B0;
            }
        """)
        save_button.clicked.connect(self.validar_campos)
        save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        button_layout.addStretch()
        button_layout.addWidget(back_button)
        button_layout.addWidget(save_button)
        button_layout.addStretch()

        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.setStyleSheet("background-color: #1E1B2E;")

    def create_labeled_input(self, label_text, initial_value="", is_password=False):
        """Crea un contenedor con label + input editable"""
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(2)

        # Label descriptivo
        label = QLabel(label_text)
        label.setFont(QFont("Candara", 12))
        label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 15px;
                font-weight: bold;
                margin-left: 12px;
                margin-bottom: 2px;
            }
        """)
        container_layout.addWidget(label)

        # Input field editable
        input_field = QLineEdit()
        input_field.setFont(QFont("Candara", 10))
        input_field.setText(initial_value)
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        
        input_field.setStyleSheet("""
            QLineEdit {
                font: bold;
                color: white;
                background-color: #1E1B2E;
                padding: 10px;
                border: 2px solid #30EACE;
                border-radius: 20px;
            }
        """)
        input_field.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        container_layout.addWidget(input_field)

        # Guardamos referencia al input
        container.input_field = input_field

        return container

    def validar_campos(self):
        """Valida que todos los campos estén completos y cumplan con los requisitos"""
        # Obtener valores de los campos
        nombre = self.nombre_input.input_field.text().strip()
        apellido_p = self.apellido_p_input.input_field.text().strip()
        apellido_m = self.apellido_m_input.input_field.text().strip()
        email = self.email_input.input_field.text().strip()
        password = self.password_input.input_field.text().strip()
        
        # Validar campos requeridos
        campos_vacios = []
        if not nombre:
            campos_vacios.append("nombre")
        if not apellido_p:
            campos_vacios.append("apellido paterno")
        if not apellido_m:
            campos_vacios.append("apellido materno")
        if not email:
            campos_vacios.append("email")
        if not password:
            campos_vacios.append("contraseña")
        
        # Validar que no haya números en el nombre
        if any(caracter.isdigit() for caracter in nombre):
            show_message("Error", "El nombre no puede contener números", "error", self)
            return
        
        # Validar que no haya números en los apellidos
        if any(caracter.isdigit() for caracter in apellido_p):
            show_message("Error", "El apellido paterno no puede contener números", "error", self)
            return
        
        if any(caracter.isdigit() for caracter in apellido_m):
            show_message("Error", "El apellido materno no puede contener números", "error", self)
            return
        
        if not nombre.replace(" ", "").isalpha():
            show_message("Error", "El nombre solo puede contener letras y espacios", "error", self)
            return
        
        # Validar formato de correo electrónico (usando la función de auth_controller)
        if not is_valid_email(email):
            show_message("Error", "Por favor ingresa un correo electrónico válido", "error", self)
            return
        
        if campos_vacios:
            self.mostrar_modal_campos_vacios(campos_vacios)
        else:
            self.mostrar_modal_confirmacion()

    def mostrar_modal_campos_vacios(self, campos_vacios):
        """Muestra modal indicando qué campos están vacíos con el diseño unificado de error"""
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setFixedSize(330, 220)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1B2E;
                border: 2px solid black;
                border-radius: 10px;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 15)

        # Barra de título personalizada
        title_bar = TitleBar(dialog)
        main_layout.addWidget(title_bar)

        content_layout = QVBoxLayout()
        
        # Icono y título de error (usando el mismo estilo que auth_controller)
        icon = "🚨"  # Emoji de alerta igual que en auth_controller
        title = "¡Campos incompletos!"
        message = "Ingresa una contraseña válida"
        
        # Lista de campos vacíos formateada
        campos_texto = "\n".join([f"• {campo.capitalize()}" for campo in campos_vacios])
        
        # Mensaje completo con formato HTML como en auth_controller
        label = QLabel(f"<div style='text-align: center;'>"
                    f"<h1>{icon}</h1>"
                    f"<h2 style='color: white;'>{title}</h2>"
                    f"<p style='font-size: 14px; color: white; font: bold;'>{message}</p></div>")
                    # f"<p style='font-size: 13px; color: white; font: bold;'>{campos_texto}</p></div>")
        label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(label)
        
        # Mensaje especial para contraseña si aplica
        # if "contraseña" in campos_vacios:
        #     password_msg = QLabel("(La contraseña no puede estar vacía)")
        #     password_msg.setAlignment(Qt.AlignCenter)
        #     password_msg.setStyleSheet("""
        #         color: #F10D32;
        #         font-size: 12px;
        #         font: bold;
        #         margin-top: 5px;
        #     """)
        #     content_layout.addWidget(password_msg)
        
        # Botón de aceptar (estilo idéntico al de auth_controller)
        accept_button = QPushButton("Aceptar")
        accept_button.setStyleSheet("""
            QPushButton {
                background-color: #F10D32;
                color: white;
                border-radius: 10px;
                padding: 10px;
                font-weight: bold;
                min-width: 120px;
                text-align: center;
            }
            QPushButton:hover {
                background-color: #E43F5A;
            }
        """)
        accept_button.clicked.connect(dialog.accept)
        content_layout.addWidget(accept_button, alignment=Qt.AlignCenter)
        
        main_layout.addLayout(content_layout)
        dialog.setLayout(main_layout)
        dialog.exec_()

    def mostrar_modal_confirmacion(self):
        """Muestra modal de confirmación para guardar cambios con el nuevo diseño"""
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setFixedSize(450, 150)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #1E1B2E;
                border: 2px solid black;
                border-radius: 10px;
                font: bold;
            }
        """)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 15)
        
        title_bar = TitleBar(dialog)
        main_layout.addWidget(title_bar)
        
        content_layout = QVBoxLayout()
        
        label = QLabel("¿Está seguro que desea guardar los cambios?")
        label.setFont(QFont("Candara", 12))
        label.setStyleSheet("color: white; font:bold;")
        label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(label)
        
        button_layout = QHBoxLayout()
        
        confirm_button = QPushButton(" Aceptar")
        confirm_button.setIcon(QIcon("assets/icons/btn-accept-white.svg"))
        confirm_button.setIconSize(QSize(24, 24))
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: #30EACE;
                color: black;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font: bold;
            }
            QPushButton:hover {
                background-color: #25C9B0;
            }
        """)        
        confirm_button.clicked.connect(lambda: self.guardar_cambios_confirmados(dialog))
        button_layout.addWidget(confirm_button)
        
        cancel_button = QPushButton(" Cancelar")
        cancel_button.setIcon(QIcon("assets/icons/btn-return-white.svg"))
        cancel_button.setIconSize(QSize(24, 24))
        cancel_button.setStyleSheet("""
            QPushButton {
                background-color: gray;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font: bold;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        cancel_button.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_button)
        
        content_layout.addLayout(button_layout)
        main_layout.addLayout(content_layout)
        
        dialog.setLayout(main_layout)
        
        if dialog.exec_() == QDialog.Accepted:
            self.guardar_cambios()

    def guardar_cambios_confirmados(self, dialog):
        """Maneja la confirmación de guardar cambios"""
        dialog.accept()
        self.guardar_cambios()

    def guardar_cambios(self):
        """Guarda los cambios en la base de datos sin mostrar mensaje de confirmación"""
        conn = None
        cursor = None
        try:
            nuevos_datos = {
                'id': self.usuario['id'],
                'nombre': self.nombre_input.input_field.text().strip(),
                'apellido_paterno': self.apellido_p_input.input_field.text().strip(),
                'apellido_materno': self.apellido_m_input.input_field.text().strip(),
                'email': self.email_input.input_field.text().strip(),
                'password': self.password_input.input_field.text().strip()
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
                        hashed_password.decode('utf-8'),
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

                self.datos_actualizados.emit()
                self.close()
            else:
                show_message("Error", "No se pudo conectar a la base de datos.", "error", self)

        except Error as e:
            show_message("Error", f"No se pudieron guardar los cambios:\n{str(e)}", "error", self)
            print(f"Error en guardar_cambios: {str(e)}")

        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

    # def mostrar_modal_exito(self):
    #     """Muestra modal indicando que los cambios se guardaron correctamente"""
    #     modal = QDialog(self)
    #     modal.setWindowTitle("Cambios guardados")
    #     modal.setFixedSize(400, 200)
    #     modal.setStyleSheet("""
    #         QDialog {
    #             background-color: #1E1B2E;
    #             border-radius: 15px;
    #         }
    #         QLabel {
    #             color: white;
    #         }
    #     """)

    #     layout = QVBoxLayout()

    #     mensaje = QLabel("Los cambios se guardaron correctamente")
    #     mensaje.setStyleSheet("font-size: 14px;")
    #     layout.addWidget(mensaje, alignment=Qt.AlignCenter)

    #     success_icon = self.style().standardIcon(QStyle.SP_DialogOkButton)
    #     icon_label = QLabel()
    #     icon_label.setPixmap(success_icon.pixmap(64, 64))
    #     icon_label.setAlignment(Qt.AlignCenter)
    #     layout.addWidget(icon_label)

    #     btn_aceptar = QPushButton("Aceptar")
    #     btn_aceptar.setStyleSheet("""
    #         QPushButton {
    #             background-color: #7FD1B9;
    #             color: black;
    #             font-weight: bold;
    #             border-radius: 20px;
    #             min-width: 120px;
    #             padding: 8px;
    #         }
    #         QPushButton:hover {
    #             background-color: #6bc0a8;
    #         }
    #     """)
    #     btn_aceptar.clicked.connect(modal.close)

    #     layout.addSpacing(20)
    #     layout.addWidget(btn_aceptar, alignment=Qt.AlignCenter)

    #     modal.setLayout(layout)
    #     modal.exec()