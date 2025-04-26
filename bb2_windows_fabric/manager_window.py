from PyQt6 import QtCore, QtGui, QtWidgets, uic
from config_to_db import *

class ManagerWindow(QtWidgets.QMainWindow):
    def __init__(self,parent, id):
        super().__init__(parent)
        uic.loadUi('ui/manager_window.ui', self)
        self.id = id
        self.setWindowFlag(QtCore.Qt.WindowType.Dialog)

        self.pushButton_edit = self.findChild(QtWidgets.QPushButton, "pushButton_edit")
        self.pushButton_edit.clicked.connect(self.enter_to_win)

        self.pushButton_back = self.findChild(QtWidgets.QPushButton, "pushButton_back")
        self.pushButton_back.clicked.connect(self.window_back)

    def enter_to_win(self):
        print(self.id)

    def window_back(self):
        parent = self.parent()
        parent.show()
        self.close()