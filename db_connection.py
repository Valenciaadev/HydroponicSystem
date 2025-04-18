import mysql.connector
from mysql.connector import Error
from PySide6 import QtCore
from PySide6.QtUiTools import *
from PySide6.QtWidgets import *
from PySide6.QtGui import *
from PySide6.QtCore import *
import sys

class cconexion:
    def conexiondatos():
        try:
            conexion = mysql.connector.connect(
                user = 'root',
                password = '',
                host = 'localhost',
                database = 'hydroponic_sys'
            ) 
            return conexion
        except mysql.connector.Error as error:
            #print("Error al conecta la base de datos {}".format(error))
            # def error(self):
            #     """Muestra modal de confirmación para guardar cambios"""
            #     modal = QDialog(self)
            #     modal.setWindowTitle("Error de conexion")
            #     modal.setFixedSize(400, 200)
                
            #     layout = QVBoxLayout()
                
            #     mensaje = QLabel("Error al conecta la base de datos {}".format(error))
            #     mensaje.setStyleSheet("color: white; font-size: 14px;")
            #     layout.addWidget(mensaje, alignment=Qt.AlignCenter)
                
            #     layout_botones = QHBoxLayout()
                
            #     btn_aceptar = QPushButton("Sí, guardar")
            #     btn_aceptar.setStyleSheet("""
            #         QPushButton {
            #             background-color: rgb(0, 170, 0);
            #             color: white;
            #             border-radius: 10px;
            #             padding: 8px 16px;
            #         }
            #         QPushButton:hover {
            #             background-color: rgb(0, 247, 0);
            #         }
            #     """)
            #     btn_aceptar.clicked.connect(modal.close)
                
                
            #     layout_botones.addWidget(btn_aceptar)
                
            #     layout.addSpacing(20)
            #     layout.addLayout(layout_botones)
                
            #     modal.setLayout(layout)
            #     modal.exec()
            # Crear una aplicación QApplication si no existe
            app = QApplication.instance()
            if not app:
                app = QApplication(sys.argv)
            
            # Mostrar mensaje de error en un QMessageBox (modal)
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error de conexión")
            msg.setText(f"Error al conectar a la base de datos: {error}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()
            return None

    
    conexiondatos()

    

