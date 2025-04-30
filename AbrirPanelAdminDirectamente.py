from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from views.homeapp_admin import HomeappAdmin
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1E1B2E"))
    palette.setColor(QPalette.WindowText, QColor("#FFFFFF")) 
    app.setPalette(palette)
    window = HomeappAdmin(None)
    window.showFullScreen()
    sys.exit(app.exec())