from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SensorsAppAdmin(QWidget):
    def __init__(self, ventana_login, embed=False):
        super().__init__()
        
        layout = QVBoxLayout()
        
        box = QFrame()
        box.setFixedSize(600, 500) #for mi when i will changig size, first is the WIDTH and then go the Height
        box.setStyleSheet("""
            QFrame {
        background-color: #2C6E63;  /* color entre azul marino y verde */
        border-radius: 10px;
        border: 2px solid #1E4D45;
            }
        """)
        
        layout.addWidget(box, alignment=Qt.AlignCenter)
        self.setLayout(layout)
        
        
    def testSlot(self):
        print("Hola mundo")
        
        