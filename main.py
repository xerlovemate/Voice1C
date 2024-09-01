import sys
from PyQt5.QtWidgets import QApplication
from gui import VoiceControlApp

# Запуск программы
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VoiceControlApp()
    window.show()
    sys.exit(app.exec_())
