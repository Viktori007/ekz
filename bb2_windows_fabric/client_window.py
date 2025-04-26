from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtGui import QStandardItemModel, QStandardItem

from client_win_order import ClientOrderWindow
from config_to_db import *

class ClientWindow(QtWidgets.QMainWindow):
    def __init__(self,parent, id):
        super().__init__(parent)
        uic.loadUi('ui/client_window.ui', self)
        self.id = id
        self.setWindowFlag(QtCore.Qt.WindowType.Window, True)

        self.pushButton_order = self.findChild(QtWidgets.QPushButton, "pushButton_order")
        self.pushButton_order.clicked.connect(self.enter_to_win)

        self.pushButton_back = self.findChild(QtWidgets.QPushButton, "pushButton_back")
        self.pushButton_back.clicked.connect(self.window_back)

        self.tableView =  self.findChild(QtWidgets.QTableView, "tableView")
        self.model = QStandardItemModel()
        self.table()
        self.ui = None

    def enter_to_win(self):
        self.ui = ClientOrderWindow(self, self.id)
        self.hide()
        self.ui.show()

    def table(self):
        data = get_orders_user(self.id)
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['номер', 'материал', 'производитель', 'длина', 'ширина', 'количество', 'цена' ])

        for row in data:
            print(row)
            items = [QStandardItem(str(row[i])) for i in range(len(row))]
            self.model.appendRow(items)
        self.tableView.setModel(self.model)
        self.tableView.resizeRowsToContents()




    def window_back(self):
        parent = self.parent()
        parent.show()
        self.close()

