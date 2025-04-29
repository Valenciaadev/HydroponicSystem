from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QHBoxLayout, QPushButton, QDialog,QTextBrowser
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SensorsAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__()
        
        layout = QVBoxLayout()
        
        #Caja container
        box = QFrame()
        box.setFixedSize(1200, 700) #Width x Heigth
        box.setStyleSheet("""
            QFrame {
        background-color: #040A08;
        border-radius: 10px;
        border: 2px solid #00AAA5;
            }
        """)
        
        #Layout interno de la caja
        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(20, 20, 20, 20) #margenes para que no quede pegado
        inner_layout.setSpacing(20) #espacio entre los widgets internos
        
        #Título
        label = QLabel("SENSORES")
        label.setObjectName("Titulo")
        label.setStyleSheet("""
                QLabel#Titulo
                color: white; 
                font-size: 25px; 
                font-weight: bold;
                border: transparent;
            """)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        inner_layout.addWidget(label, alignment=Qt.AlignLeft)
        
        #botón agregar sensor
        addSensBtn = QPushButton("+ Agregar Sensor")
        addSensBtn.setObjectName("AgregarSensorBtn")
        addSensBtn.setFixedSize(160,40)
        addSensBtn.setStyleSheet("""
            QPushButton#AgregarSensorBtn {
                background-color: transparent;
                color: #eee;
                border-radius: 15px;
                font-size: 15px;
                font-weight: normal;
                border: 1px solid #039066;
            }
            
            QPushButton#AgregarSensorBtn:hover {
                background-color: #0f2623
                
            }
            """)
        #inner_layout.addWidget(addSensBtn) 
        btnAddSens_layout = QHBoxLayout()
        btnAddSens_layout.addStretch()
        btnAddSens_layout.addWidget(addSensBtn)
        
        inner_layout.addLayout(btnAddSens_layout)
        addSensBtn.clicked.connect(self.testSlot)
        
        #Caja contenido
        inner_box = QFrame()
        inner_box.setObjectName("InnerBox")
        inner_box.setFixedSize(1100, 550)
        inner_box.setStyleSheet("""
            QFrame#InnerBox {
        background-color: #040A08;
        border-radius: 8px;
        border: 1px solid #DE209F;
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
        inner_box_layout.setContentsMargins(20, 20, 20, 20)
        inner_box_layout.setSpacing(15)
        
        #Lista con los nombres de los sensores
        sensores = [
            "Sensor de pH / Sensor de RCI / Sensor de temperatura",
            "Sensor Ultrasónico",
            "Sensor de temperatura",
            "Sensor de humedad"
        ]
        
        for nombre in sensores:
            # Frame para cada sensor
            sensor_frame = QFrame()
            sensor_frame.setStyleSheet("""
                QFrame {
                    background-color: #11211F;
                    border: 1px solid transparent;
                    border-radius: 20px;
                }
            """)

            sensor_frame.setFixedHeight(60)
            
            #Layout horizontal para los elementos
            sensor_layout = QHBoxLayout()
            sensor_layout.setContentsMargins(10, 5, 10, 5)
            sensor_layout.setSpacing(20)
            
            #Circulo verde que representa el estado del sensor
            led = QLabel()
            led.setFixedSize(20, 20)
            led.setStyleSheet("""
                QLabel {
                    background-color: #00FF00;
                    border-radius: 10px;
                }
            """)
            
            #Nombre del sensor
            sensor_label = QLabel(nombre)
            sensor_label.setStyleSheet("color: white; font-size: 16px")
            
            #Botón de características
            chars_btn = QPushButton("Características")
            chars_btn.setFixedSize(120,30)
            chars_btn.setStyleSheet("""
                QPushButton {
                    background-color: #0B1C4D;
                    color: white;
                    border: 1px solid #3B5998; 
                    border-radius: 10px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #1A2F7A;
                }
            """)
            #probar la funcionalidad de los botones
            chars_btn.clicked.connect(self.testSlot)
            
            #Agregar los widgets al layout del sensor
            sensor_layout.addWidget(led)
            sensor_layout.addWidget(sensor_label)
            sensor_layout.addStretch()
            sensor_layout.addWidget(chars_btn)
            
            sensor_frame.setLayout(sensor_layout)
            
            #Agregar el frame del sensor al layout general
            inner_box_layout.addWidget(sensor_frame)
            
        #Aplicar el layout al inner-box
        inner_box.setLayout(inner_box_layout)
        
    def testSlot(self):
        """Abre una ventana emergente con los términos y condiciones."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Términos y Condiciones")
        dialog.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()
        text_browser = QTextBrowser()
        text_browser.setText("""
            <h3>Términos y Condiciones</h3>
            <p>Bienvenido a nuestra plataforma. Antes de continuar, por favor lee los siguientes términos:</p>
            <ul>
                <li>No compartas tu contraseña con terceros.</li>
                <li>Respetar a los demás usuarios en la comunidad.</li>
                <li>No utilizar información falsa en el registro.</li>
                <li>El uso indebido de la plataforma puede resultar en la suspensión de la cuenta.</li>
            </ul>
            <p>Al continuar, aceptas estos términos.</p>
        """)
        text_browser.setOpenExternalLinks(True)

        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(dialog.accept)

        layout.addWidget(text_browser)
        layout.addWidget(close_button)
        dialog.setLayout(layout)
        dialog.exec_()
        
        