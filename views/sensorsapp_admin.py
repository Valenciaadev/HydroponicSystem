from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SensorsAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__()
        
        layout = QVBoxLayout()
        
        #Caja container
        box = QFrame()
        box.setFixedSize(1200, 700) #for mi when i will changig size, first is the WIDTH and then go the Height
        box.setStyleSheet("""
            QFrame {
        background-color: #2C6E63;  /* color entre azul marino y verde */
        border-radius: 10px;
        border: 2px solid #1E4D45;
            }
        """)
        
        #Layout interno de la caja
        inner_layout = QVBoxLayout()
        inner_layout.setContentsMargins(20, 20, 20, 20) #margenes para que no quede pegado
        inner_layout.setSpacing(20) #espacio entre los widgets internos
        
        #Título
        label = QLabel("SENSORES")
        label.setStyleSheet("color: white; font-size: 18px; font-weight: bold;")
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        inner_layout.addWidget(label, alignment=Qt.AlignLeft)
        
        #Caja contenido
        inner_box = QFrame()
        inner_box.setFixedSize(1100, 550)
        inner_box.setStyleSheet("""
            QFrame {
        background-color: #3D8A7A;
        border-radius: 8px;
        border: 1px solid #256056;
            }
        """)
        
        inner_layout.addWidget(inner_box, alignment=Qt.AlignTop)
        
        ## Aplicar el layout al box principal
        box.setLayout(inner_layout)
        
        
        # Agregar la caja principal al layout de la ventana
        layout.addWidget(box, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        
        
    def testSlot(self):
        print("Hola mundo")
        
        