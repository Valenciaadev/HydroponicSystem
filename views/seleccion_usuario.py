from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QDialog, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #1E1B2E; color: white;")

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)

        self.title = QLabel("Sistema Hidropónico")
        self.title.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.title)

        self.minimize_button = QPushButton("🟡")
        self.minimize_button.setFixedSize(30, 30)
        self.minimize_button.setStyleSheet("background-color: transparent; color: white;")
        self.minimize_button.clicked.connect(self.parent.showMinimized)
        self.minimize_button.setCursor(Qt.PointingHandCursor)
        self.minimize_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.minimize_button)

        self.maximize_button = QPushButton("🟢")
        self.maximize_button.setFixedSize(30, 30)
        self.maximize_button.setStyleSheet("background-color: transparent; color: white;")
        self.maximize_button.clicked.connect(self.toggle_maximize)
        self.maximize_button.setCursor(Qt.PointingHandCursor)
        self.maximize_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.maximize_button)

        self.close_button = QPushButton("🔴")
        self.close_button.setFixedSize(30, 30)
        self.close_button.setStyleSheet("background-color: transparent; color: white;")
        self.close_button.clicked.connect(self.parent.close)
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setStyleSheet("QPushButton:hover { background-color: blue; }")
        layout.addWidget(self.close_button)
        
        self.setLayout(layout)
        self.drag_position = None

    def toggle_maximize(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_position is not None:
            self.parent.move(event.globalPos() - self.drag_position)
            event.accept()

class SeleccionUsuarioWidget(QWidget):
    def __init__(self, switch_to_admin, switch_to_worker):
        super().__init__()
        self.switch_to_admin = switch_to_admin
        self.switch_to_worker = switch_to_worker
        
        layout = QVBoxLayout()

        # Texto de encabezado
        title_label = QLabel("¿Cómo deseas iniciar?")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Candara", 20))
        title_label.setStyleSheet("color: white; padding-bottom: 20px; font: bold;")
        layout.addWidget(title_label)

        # Botón Administrador
        admin_button = QPushButton("Administrador")
        admin_button.setStyleSheet("""
            QPushButton {
                background-color: blue;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)
        admin_button.clicked.connect(self.prompt_admin_password)
        layout.addWidget(admin_button)

        # Botón Trabajador
        worker_button = QPushButton("Trabajador")
        worker_button.setStyleSheet("""
            QPushButton {
                background-color: gray;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
        """)
        worker_button.clicked.connect(self.confirm_worker_selection)
        layout.addWidget(worker_button)

        self.setLayout(layout)
        
    def confirm_worker_selection(self):
        """Muestra un cuadro de confirmación antes de cambiar de vista."""
        dialog = QDialog(self)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setFixedSize(430, 150)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        title_bar = TitleBar(dialog)
        main_layout.addWidget(title_bar)
        
        content_layout = QVBoxLayout()
        
        label = QLabel("¿Está seguro que desea ingresar como Trabajador?")
        label.setFont(QFont("Candara", 12))
        label.setStyleSheet("color: white; font:bold;")
        content_layout.addWidget(label)
        
        button_layout = QHBoxLayout()
        
        confirm_button = QPushButton("Aceptar")
        confirm_button.setStyleSheet("""
            QPushButton {
                background-color: blue;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)        
        confirm_button.clicked.connect(lambda: self.accept_worker(dialog))
        button_layout.addWidget(confirm_button)
        
        cancel_button = QPushButton("Regresar")
        cancel_button.setStyleSheet("background-color: gray; color: white; padding: 5px; border-radius: 5px;")
        cancel_button.setStyleSheet("""
        QPushButton {
            background-color: gray;
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
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
        dialog.exec_()
        
    def prompt_admin_password(self):
        """Muestra un cuadro de diálogo para ingresar la clave de administrador."""
        print("Se abrió el cuadro de contraseña del administrador")  # Para depuración

        dialog = QDialog(self if self.isVisible() else None)
        dialog.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        dialog.setFixedSize(320, 150)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Barra de título personalizada
        title_bar = TitleBar(dialog)
        main_layout.addWidget(title_bar)

        content_layout = QVBoxLayout()

        label = QLabel("Ingresa la clave del administrador")
        label.setFont(QFont("Candara", 12))
        label.setStyleSheet("color:white; font:bold;")
        label.setAlignment(Qt.AlignCenter)
        content_layout.addWidget(label)

        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setStyleSheet("background-color: white; color: black; padding: 5px; border-radius: 5px; width:70%")
        content_layout.addWidget(password_input)

        submit_button = QPushButton("Aceptar")
        password_input.returnPressed.connect(submit_button.click)
        submit_button.setStyleSheet("""
            QPushButton {
                background-color: blue;
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #005A9E;
            }
        """)        
        submit_button.clicked.connect(lambda: self.check_admin_password(password_input.text(), dialog))
        content_layout.addWidget(submit_button)

        main_layout.addLayout(content_layout)
        dialog.setLayout(main_layout)

        # Asegurarse de que se muestre correctamente
        dialog.show()
        dialog.raise_()
        dialog.activateWindow()

    def check_admin_password(self, password, dialog):
        """Verifica si la clave de administrador es correcta y cambia a la vista de login."""
        ADMIN_PASSWORD = "1234"  # Puedes cambiarla o validar con una base de datos
        if password == ADMIN_PASSWORD:
            dialog.accept()
            self.switch_to_admin()
        else:
            dialog.reject()
    
    
    def accept_worker(self, dialog):
        dialog.accept()
        self.switch_to_worker()