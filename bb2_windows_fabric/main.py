from PyQt6 import QtWidgets

from enter_window import EnterWindow

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = EnterWindow()
    ui.show()
    sys.exit(app.exec())
