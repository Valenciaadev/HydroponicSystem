# from PyQt5.QtWidgets import QApplication, QLabel, QDialog, QVBoxLayout, QPushButton, QWidget
# from PyQt5.QtCore import Qt

# class ModalWindow(QDialog):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Ventana Modal")
#         self.setFixedSize(300, 150)
        
#         layout = QVBoxLayout()
#         close_button = QPushButton("Cerrar")
#         close_button.clicked.connect(self.close)
        
#         layout.addWidget(close_button)
#         self.setLayout(layout)

# class MainWindow(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Ventana Principal")
#         self.setFixedSize(400, 300)

#         self.label = QLabel("Haga clic aquí", self)
#         self.label.setAlignment(Qt.AlignCenter)
#         self.label.setStyleSheet("color: rgb(220, 220, 220); font-size: 14pt; font-weight: bold;")
#         self.label.setGeometry(100, 100, 200, 50)

#     def mousePressEvent(self, event):
#         if self.label.underMouse():  # Verifica si se hizo clic en el label
#             self.show_modal()

#     def show_modal(self):
#         modal = ModalWindow()
#         modal.exec_()  # Abre como ventana modal

# if __name__ == "__main__":
#     import sys
#     app = QApplication(sys.argv)
#     window = MainWindow()
#     window.show()
#     sys.exit(app.exec_())

from PySide6.QtWidgets import QApplication, QLabel, QMainWindow, QDialog, QVBoxLayout
from PySide6.QtCore import Qt, QPoint
import sys

class ModalDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Modal Window")
        self.setFixedSize(300, 150)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Esta es una ventana modal", self))
        self.setLayout(layout)
        
        # Centrar la ventana modal en la parte superior de la principal
        if parent:
            parent_geometry = parent.geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + 10  # Ajuste para colocarla en la parte superior
            self.move(QPoint(x, y))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ventana Principal")
        self.setGeometry(100, 100, 400, 300)
        
        self.label = QLabel("Haz clic aquí para abrir el modal", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setGeometry(50, 20, 300, 50)
        self.label.setStyleSheet("border: 1px solid black; padding: 5px;")
        
        self.label.mousePressEvent = self.open_modal
    
    def open_modal(self, event):
        dialog = ModalDialog(self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
