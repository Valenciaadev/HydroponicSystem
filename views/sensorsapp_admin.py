from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QDialog, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SensorsAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__()
        
        layout = QVBoxLayout()
        
        #Caja container
        box = QFrame()
        box.setFixedSize(1600, 900) #Width x Heigth
        box.setStyleSheet("""
            QFrame {
        background-color: #28243C;
        border-radius: 15px;
            }
        """)
        
        #Layout interno de la caja
        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(25, 0, 20, 5) #margenes para que no quede pegado
        inner_layout.setSpacing(5) #espacio entre los widgets internos
        
        #Título
        label = QLabel("SENSORES")
        label.setObjectName("Titulo")
        label.setStyleSheet("""
                QLabel#Titulo
                color: white; 
                font-size: 25px; 
                font-weight: bold;
                border: transparent;
                padding: 5px;
            """)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        inner_layout.addWidget(label, alignment=Qt.AlignLeft)
        
                # --- Creamos el botón y lo estilizamos como antes ---
        addSensBtn = QPushButton("+ Agregar Sensor")
        addSensBtn.setObjectName("AgregarSensorBtn")
        addSensBtn.setFixedSize(190, 40)
        addSensBtn.setStyleSheet("""
            QPushButton#AgregarSensorBtn {
                background-color: #1F2232;
                color: white;
                font-size: 15px;
                font-weight: bold;
                padding: 5px 20px;
                border: none;
                border-radius: 30px;
            }
            QPushButton#AgregarSensorBtn:hover {
                background-color: #1F2F32;
            }
        """)
        addSensBtn.clicked.connect(self.feature)

        # --- Ahora lo envolvemos en un frame exterior degradado ---
        add_btn_outer = QFrame()
        add_btn_outer.setFixedHeight(40 + 2*2)  # 2px padding arriba y abajo
        add_btn_outer.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #60D4B8, stop:1 #1E2233);
                border-radius: 32px;
                padding: 2px;
            }
        """)

        # --- Opcional: un frame interior para fondo sólido (igual al inner_box) ---
        add_btn_inner = QFrame()
        add_btn_inner.setFixedHeight(40)
        add_btn_inner.setStyleSheet("""
            QFrame {
                background-color: #1F2232;
                border-radius: 30px;
            }
        """)

        # --- Layouts para incrustar el botón ---
        inner_btn_layout = QHBoxLayout()
        inner_btn_layout.setContentsMargins(0,0,0,0)
        inner_btn_layout.addWidget(addSensBtn)
        add_btn_inner.setLayout(inner_btn_layout)

        outer_btn_layout = QHBoxLayout()
        outer_btn_layout.setContentsMargins(0,0,0,0)
        outer_btn_layout.addWidget(add_btn_inner)
        add_btn_outer.setLayout(outer_btn_layout)

        # --- Finalmente lo añadimos al layout principal igual que antes ---
        btnAddSens_layout = QHBoxLayout()
        btnAddSens_layout.addStretch()
        btnAddSens_layout.addWidget(add_btn_outer)
        inner_layout.addLayout(btnAddSens_layout)
        
        #Caja contenido
        inner_box = QFrame()
        inner_box.setObjectName("InnerBox")
        inner_box.setFixedSize(1590, 750)
        inner_box.setStyleSheet("""
            QFrame#InnerBox {
        background-color: #28243C;
        
            }
        """)
        
        inner_layout.addWidget(inner_box, alignment=Qt.AlignTop)
        
        ## Aplicar el layout al box principal
        box.setLayout(inner_layout)
        
        
        # Agregar la caja principal al layout de la ventana
        layout.addWidget(box, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        
        #Layout interno para inner-box
        
        inner_box_layout = QVBoxLayout()
        inner_box_layout.setContentsMargins(25, 0, 20, 0)
        inner_box_layout.setSpacing(0)
        
        #Lista con los nombres de los sensores
        sensores = [
            "Sensor de pH / Sensor de RCI / Sensor de temperatura",
            "Sensor Ultrasónico",
            "Sensor de temperatura",
            "Sensor de humedad"
        ]
        
        for nombre in sensores:
            sensor_frameOuter = QFrame()
            sensor_frameOuter.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #60D4B8, stop:1 #1E2233);
                    border-radius: 35px;
                    padding: 2px;
                }
            """)
            sensor_frameOuter.setFixedHeight(75)
            sensor_frameOuter.setFixedWidth(1400)

            # Contenedor interno con fondo sólido
            sensor_frameInner = QFrame()
            sensor_frameInner.setStyleSheet("""
                QFrame {
                    background-color: #1f2232;
                    border-radius: 35px;
                }
            """)
            sensor_frameInner.setFixedHeight(70)
            sensor_frameInner.setFixedWidth(1395)

            # Layout para el contenido interno
            sensor_layout = QHBoxLayout()
            sensor_layout.setContentsMargins(10, 5, 15, 5)
            sensor_layout.setSpacing(10)

            # LED, nombre y botón
            LED = QLabel()
            LED.setFixedSize(20, 20)
            LED.setStyleSheet("""
                QLabel {
                    background-color: #00FF00;
                    border-radius: 10px;
                }
            """)

            sensor_label = QLabel(nombre)
            sensor_label.setStyleSheet("color: white; font-weight: bold; font-size: 16px;")

            chars_btn = QPushButton("características")
            chars_btn.setFixedSize(170, 30)
            chars_btn.setStyleSheet("""
                QPushButton {
                    background-color: #7FD1B9;
                    color: black;
                    font-weight: bold;
                    border-radius: 15px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #429E88 ;
                }
            """)

            chars_btn.clicked.connect(self.feature)

            # Añadir al layout interno
            sensor_layout.addWidget(LED)
            sensor_layout.addWidget(sensor_label)
            sensor_layout.addStretch()
            sensor_layout.addWidget(chars_btn)

            sensor_frameInner.setLayout(sensor_layout)

            # Envolverlo en el layout del borde
            outer_layout = QVBoxLayout()
            outer_layout.setContentsMargins(0, 0, 0, 0)
            outer_layout.addWidget(sensor_frameInner)
            sensor_frameOuter.setLayout(outer_layout)

            # Agregar al layout principal
            inner_box_layout.addWidget(sensor_frameOuter)
            
            
        #Aplicar el layout al inner-box
        inner_box.setLayout(inner_box_layout)
        
    def feature(self):
        """Abre una ventana con un formulario para añadir un nuevo Sensor."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Agregar nuevo sensor")
        dialog.setGeometry(100, 100, 500, 700)
        
        #cambiar el color de la ventana
        dialog.setStyleSheet("background-color: #28243C ; color:white;")
        
        layout = QVBoxLayout()
        
        tituloModal = QLabel("Añadir sensor")
        tituloModal.setObjectName("title")
        tituloModal.setStyleSheet("""
            QLabel#title{
                color: white;
                font-size: 15px;
                font-weight: bold;
                }""")
        
        addSensorBox = QFrame()
        addSensorBox.setFixedSize(450, 650)
        addSensorBox.setObjectName("AddSensorContainer")
        addSensorBox.setStyleSheet("""
            QFrame#AddSensorContainer {
                border-radius: 8px;
                }""")
        
        box_layout = QVBoxLayout()
        box_layout.setContentsMargins(15, 15, 15, 15)
        box_layout.setSpacing(30)
        
        #campos para rellenar
        nombreSensorField = QLineEdit(self)
        busField = QLineEdit(self)
        addressField = QLineEdit(self)
        tasaFlujoField = QLineEdit(self)
        modoSalidaField = QLineEdit(self)
        
        #Place holders de los campos
        nombreSensorField.setPlaceholderText("Nombre del sensor")
        busField.setPlaceholderText("Bus")
        addressField.setPlaceholderText("Address")
        tasaFlujoField.setPlaceholderText("Tasa de Flujo")
        modoSalidaField.setPlaceholderText("Modo de salida")
        
        # Estilos para los placeholders
        nombreSensorField.setObjectName("NombreDeSensor")
        busField.setObjectName("Bus")
        addressField.setObjectName("Address")
        tasaFlujoField.setObjectName("TasaDeFlujo")
        modoSalidaField.setObjectName("ModoDeSalida")
        
        nombreSensorField.setStyleSheet("""
                QLineEdit#NombreDeSensor {
                    background-color: #2e3048; 
                    color:white;
                    border-radius: 25px;
                    }
                    """)
        busField.setStyleSheet("""
                QLineEdit#Bus {
                    background-color: #2e3048; 
                    color:white;
                    border-radius: 25px;
                    }
                    """)
        addressField.setStyleSheet("""
                QLineEdit#Address {
                    background-color: #2e3048; 
                    color:white;
                    border-radius: 25px;
                    }
                    """)
        tasaFlujoField.setStyleSheet("""
                QLineEdit#TasaDeFlujo {
                    background-color: #2e3048; 
                    color:white;
                    border-radius: 25px;
                }
                """)
        modoSalidaField.setStyleSheet("""
                QLineEdit#ModoDeSalida {
                    background-color: #2e3048; 
                    color:white;
                    border-radius: 25px;
                }
                """)
        
        
        #posicionar los QLineEdit(s)
        nombreSensorField.setFixedHeight(60)
        busField.setFixedHeight(60)
        addressField.setFixedHeight(60)
        tasaFlujoField.setFixedHeight(60)
        modoSalidaField.setFixedHeight(60)
        
        #Botones de guardar y cancelar
        guardar_btn = QPushButton("Guardar")
        cancelar_btn = QPushButton("Cancelar")
        
        #Tamaño de los botones "Guardar" y "Cancelar"
        guardar_btn.setFixedWidth(100)
        cancelar_btn.setFixedWidth(100)
        
        
        #se añaden widgets al layout del contenedor
        box_layout.addWidget(nombreSensorField)
        box_layout.addWidget(busField)
        box_layout.addWidget(addressField)
        box_layout.addWidget(tasaFlujoField)
        box_layout.addWidget(modoSalidaField)
        
        #Añadir Botones de "Guardar" y "Cancelar"
        box_layout.addStretch()
        botones_layout = QHBoxLayout()
        botones_layout.addWidget(guardar_btn)
        botones_layout.addWidget(cancelar_btn)
        botones_layout.setAlignment(Qt.AlignHCenter)
        box_layout.addLayout(botones_layout)

        
        #se asigna el layout al QFrame
        addSensorBox.setLayout(box_layout)
        
        #se agregan widgets al layout principal
        tituloModal.setAlignment(Qt.AlignHCenter)
        layout.addWidget(tituloModal)
        
        
        
        layout.addWidget(addSensorBox, alignment= Qt.AlignHCenter)
        
        dialog.setLayout(layout)
        dialog.exec_()
        