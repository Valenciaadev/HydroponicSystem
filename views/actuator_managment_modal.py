from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from models.database import connect_db


class TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(30)
        self.setStyleSheet("background-color: #1E1B2E; color: white;")

        layout = QHBoxLayout()
        layout.setContentsMargins(5, 0, 5, 0)

        self.title = QLabel("Sistema Hidrop\u00f3nico")
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


class ActuatorManagmentWidget(QDialog):
    def __init__(self, ventana_login, actuator_id=None):
        super().__init__()
        self.actuator_id = actuator_id
        self.ventana_login = ventana_login
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(400, 450)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 5, 0, 10)

        self.title_bar = TitleBar(self)
        layout.addWidget(self.title_bar)

        title_label = QLabel("Gestiona la dosis")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Candara", 14))
        title_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(title_label)

        mode_widget = QWidget()
        mode_layout = QHBoxLayout()
        mode_layout.setContentsMargins(20, 0, 20, 0)
        mode_layout.setSpacing(10)

        self.auto_button = QPushButton("Automatizado")
        self.manual_button = QPushButton("Manual")

        for btn in (self.auto_button, self.manual_button):
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setFixedWidth(180)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1E1B2E;
                    color: white;
                    border: 2px solid #30EACE;
                    border-radius: 15px;
                    font-weight: bold;
                }
                QPushButton:checked {
                    background-color: #30EACE;
                    color: black;
                }
            """)
            mode_layout.addWidget(btn)

        self.auto_button.setChecked(True)
        self.auto_button.clicked.connect(self.set_automated_mode)
        self.manual_button.clicked.connect(self.set_manual_mode)

        mode_widget.setLayout(mode_layout)
        layout.addWidget(mode_widget)

        form_layout = QFormLayout()
        self.dosis_input = self.create_labeled_input("Dosis (ml)", enabled=False)
        self.fecha_input = self.create_date_input("Fecha de aplicaci\u00f3n", enabled=False)
        self.hora_input = self.create_time_input("Hora de aplicaci\u00f3n", enabled=False)

        for widget in (self.dosis_input, self.fecha_input, self.hora_input):
            form_layout.addRow("", widget)

        form_widget = QWidget()
        form_widget.setLayout(form_layout)
        layout.addWidget(form_widget)

        self.button_layout = QHBoxLayout()
        self.close_button = QPushButton("Cerrar")
        self.supply_button = QPushButton("Suministrar")

        for btn in (self.close_button, self.supply_button):
            btn.setStyleSheet("""
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
            btn.setCursor(Qt.PointingHandCursor)

        self.close_button.clicked.connect(self.reject)
        self.supply_button.clicked.connect(self.supply_doses)

        self.update_buttons()
        layout.addLayout(self.button_layout)

        self.setLayout(layout)

    def create_labeled_input(self, label_text, enabled=True):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(2)

        label = QLabel(label_text)
        label.setFont(QFont("Candara", 12))
        label.setStyleSheet("color: white; font-size: 15px; font-weight: bold; margin-left: 12px;")
        layout.addWidget(label)

        input_field = QLineEdit()
        input_field.setFont(QFont("Candara", 10))
        input_field.setReadOnly(not enabled)
        input_field.setStyleSheet("""
            QLineEdit {
                font: bold;
                color: #AAAAAA;
                background-color: #1E1B2E;
                padding: 10px;
                border: 2px solid #30EACE;
                border-radius: 20px;
            }
        """)
        layout.addWidget(input_field)
        container.input_field = input_field
        return container

    def create_date_input(self, label_text, enabled=True):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        label.setStyleSheet("color: white; font-size: 15px; font-weight: bold; margin-left: 12px;")
        layout.addWidget(label)

        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1E1B2E;
                border: 2px solid #30EACE;
                border-radius: 20px;
            }
        """)
        frame.setFixedHeight(40)
        inner_layout = QHBoxLayout(frame)
        inner_layout.setContentsMargins(10, 0, 0, 0)

        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        date_edit.setDisplayFormat("yyyy-MM-dd")
        date_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)
        date_edit.setEnabled(enabled)
        date_edit.setStyleSheet("""
            QDateEdit {
                color: #AAAAAA;
                background-color: transparent;
                border: none;
                font-weight: bold;
            }
        """)
        inner_layout.addWidget(date_edit)

        spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        inner_layout.addItem(spacer)

        icon_button = QPushButton()
        icon_button.setIcon(QIcon("assets/icons/input-calendar-white.svg"))
        icon_button.setIconSize(QSize(20, 20))
        icon_button.setCursor(Qt.PointingHandCursor)
        icon_button.setStyleSheet("QPushButton { background: transparent; border: none; padding-right: 10px; }")
        icon_button.setFixedSize(30, 30)
        icon_button.clicked.connect(lambda: self.show_calendar_dialog(date_edit))
        inner_layout.addWidget(icon_button)

        layout.addWidget(frame)
        container.input_field = date_edit
        return container

    def create_time_input(self, label_text, enabled=True):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        label = QLabel(label_text)
        label.setStyleSheet("color: white; font-size: 15px; font-weight: bold; margin-left: 12px;")
        layout.addWidget(label)

        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #1E1B2E;
                border: 2px solid #30EACE;
                border-radius: 20px;
            }
        """)
        frame.setFixedHeight(40)
        inner_layout = QHBoxLayout(frame)
        inner_layout.setContentsMargins(10, 0, 0, 0)

        time_edit = QTimeEdit()
        time_edit.setDisplayFormat("HH:mm")
        time_edit.setTime(QTime.currentTime())
        time_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)
        time_edit.setEnabled(enabled)
        time_edit.setStyleSheet("""
            QTimeEdit {
                color: #AAAAAA;
                background-color: transparent;
                border: none;
                font-weight: bold;
            }
        """)
        inner_layout.addWidget(time_edit)

        spacer = QSpacerItem(1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum)
        inner_layout.addItem(spacer)

        icon_button = QPushButton()
        icon_button.setIcon(QIcon("assets/icons/input-clock-white.svg"))
        icon_button.setIconSize(QSize(20, 20))
        icon_button.setCursor(Qt.PointingHandCursor)
        icon_button.setStyleSheet("QPushButton { background: transparent; border: none; padding-right: 10px; }")
        icon_button.setFixedSize(30, 30)
        icon_button.clicked.connect(lambda: self.show_time_dialog(time_edit))
        inner_layout.addWidget(icon_button)

        layout.addWidget(frame)
        container.input_field = time_edit
        return container

    def show_calendar_dialog(self, target_edit):
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecciona una fecha")
        dialog.setStyleSheet("background-color: #1E1B2E; color: white;")
        dialog.setFixedSize(450, 300)

        calendar = QCalendarWidget()
        calendar.setGridVisible(True)
        calendar.setStyleSheet("""
            QCalendarWidget QToolButton {
                color: white;
                font-weight: bold;
            }
            QCalendarWidget QMenu {
                background-color: #1E1B2E;
                color: white;
            }
            QCalendarWidget QWidget {
                alternate-background-color: #2A2A2A;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: white;
                selection-background-color: #30EACE;
                selection-color: black;
            }
        """)

        calendar.clicked.connect(lambda date: (target_edit.setDate(date), dialog.accept()))
        layout = QVBoxLayout(dialog)
        layout.addWidget(calendar)
        dialog.exec_()

    def show_time_dialog(self, target_edit):
        dialog = QDialog(self)
        dialog.setWindowTitle("Selecciona la hora")
        dialog.setStyleSheet("background-color: #1E1B2E; color: white;")
        dialog.setFixedSize(300, 100)

        time_selector = QTimeEdit()
        time_selector.setTime(target_edit.time())
        time_selector.setDisplayFormat("HH:mm")
        time_selector.setStyleSheet("""
            QTimeEdit {
                background-color: #1E1B2E;
                color: white;
                font-weight: bold;
                border: 2px solid #30EACE;
                border-radius: 10px;
                padding: 6px;
            }
        """)

        time_selector.timeChanged.connect(lambda time: target_edit.setTime(time))
        layout = QVBoxLayout(dialog)
        layout.addWidget(time_selector)
        dialog.exec_()

    def set_manual_mode(self):
        self.auto_button.setChecked(False)
        self.manual_button.setChecked(True)
        self.dosis_input.input_field.setReadOnly(False)
        self.fecha_input.input_field.setEnabled(True)
        self.hora_input.input_field.setEnabled(True)
        self.update_buttons()

    def set_automated_mode(self):
        self.auto_button.setChecked(True)
        self.manual_button.setChecked(False)
        self.dosis_input.input_field.setReadOnly(True)
        self.fecha_input.input_field.setEnabled(False)
        self.hora_input.input_field.setEnabled(False)
        self.update_buttons()

    def update_buttons(self):
        for i in reversed(range(self.button_layout.count())):
            self.button_layout.itemAt(i).widget().setParent(None)

        if self.manual_button.isChecked():
            self.button_layout.addWidget(self.supply_button)
        self.button_layout.addWidget(self.close_button)

    def supply_doses(self):
        print("Suministrar dosis:", {
            "dosis": self.dosis_input.input_field.text(),
            "fecha": self.fecha_input.input_field.text(),
            "hora": self.hora_input.input_field.text()
        })

    def load_actuator_data(self):
        conn = connect_db()
        if conn:
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT nombre, tipo, bus, address, modo_activacion, estado_actual
                FROM actuadores
                WHERE id_actuador = %s
            """
            cursor.execute(query, (self.actuator_id,))
            row = cursor.fetchone()
            if row:
                self.name_input.input_field.setText(row['nombre'] or "")
                self.tipo_input.input_field.setText(row['tipo'] or "")
                self.bus_input.input_field.setText(str(row['bus'] or ""))
                self.address_input.input_field.setText(str(row['address'] or ""))
                self.modo_input.input_field.setText(row['modo_activacion'] or "")
                self.estado_input.input_field.setText("Encendido" if row['estado_actual'] else "Apagado")
            cursor.close()
            conn.close()
        else:
            print("No se pudo conectar a la base de datos para cargar datos del actuador.")
            