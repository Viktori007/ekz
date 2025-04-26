from PyQt6 import QtCore, QtGui, QtWidgets, uic

from client_win_order import ClientOrderWindow
from config_to_db import *
from client_window import ClientWindow
from manager_window import ManagerWindow

class EnterWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/enter.ui', self)

        self.pushButton_enter = self.findChild(QtWidgets.QPushButton, "pushButton_enter")
        self.lineEdit_login = self.findChild(QtWidgets.QLineEdit, "lineEdit_login")
        self.lineEdit_password = self.findChild(QtWidgets.QLineEdit, "lineEdit_password")
        self.pushButton_enter.clicked.connect(self.enter_to_win)
        self.ui = None
        self.setWindowFlag(QtCore.Qt.WindowType.Window, True)
        self.setWindowFlag(QtCore.Qt.WindowType.Dialog)  # Указываем, что это диалоговое окно


    def enter_to_win(self):
        login = self.lineEdit_login.text()
        password = self.lineEdit_password.text()
        id, role = get_user(login, password)
        print(id)
        if role == 'manager':
            self.ui = ManagerWindow(self, id)
            self.ui.show()
            self.hide()

        elif role == 'client':
            self.ui = ClientWindow(self, id)
            self.ui.show()
            self.hide()