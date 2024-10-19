from PyQt5.QtWidgets import QApplication
from ui import RemoveBGApp
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RemoveBGApp()
    window.show()
    sys.exit(app.exec_())
