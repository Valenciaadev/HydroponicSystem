from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QLabel, 
                               QLineEdit, QPushButton, QApplication, QFormLayout)
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys

class VentanaConGroupBox(QWidget):
    def __init__(self):
        super(VentanaConGroupBox, self).__init__()
        self.setWindowTitle("Ejemplo de QGroupBox en PySide6")
        self.resize(400, 300)

        # Layout principal
        layout_principal = QVBoxLayout(self)

        # Creación del QGroupBox
        grupo = QGroupBox("Información del Usuario")  # Título del grupo
        grupo.setAlignment(Qt.AlignCenter)
        grupo.setStyleSheet("QGroupBox { font-size: 14px; font-weight: bold; }")  

        # Layout para los elementos dentro del QGroupBox
        layout_grupo = QFormLayout()

        # Campos dentro del QGroupBox
        label_nombre = QLabel("Nombre:")
        input_nombre = QLineEdit()

        label_edad = QLabel("Edad:")
        input_edad = QLineEdit()

        boton_guardar = QPushButton("Guardar")
        
        # Agregar elementos al layout del grupo
        layout_grupo.addRow(label_nombre, input_nombre)
        layout_grupo.addRow(label_edad, input_edad)
        layout_grupo.addRow(boton_guardar)

        # Aplicar el layout al grupo
        grupo.setLayout(layout_grupo)

        # Agregar el grupo al layout principal
        layout_principal.addWidget(grupo)

        self.setLayout(layout_principal)

# Ejecución de la aplicación
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaConGroupBox()
    ventana.show()
    sys.exit(app.exec())
