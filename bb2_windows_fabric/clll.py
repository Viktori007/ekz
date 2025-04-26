from PyQt6 import QtWidgets, QtGui, uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import MySQLdb
from MySQLdb.cursors import DictCursor


class ClientOrderWindow1(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('ui/client_order_window.ui', self)

        # Инициализация данных
        self.current_step = 0
        self.window_data = {
            'material_id': None,
            'manufacturer_id': None,
            'sashes_count': 1,
            'width': 100,
            'height': 120,
            'accessories': [],
            'params': []
        }
        self.tableView = self.findChild(QtWidgets.QTableView, "tableView")

        self.load_data()
        self.go_to_accessories()
        self.id = 1


    def load_data(self):
        """Загрузка данных из БД"""
        try:
            conn = MySQLdb.connect(host="localhost", user="client_window", password="", db="window_fabric", port=3306)
            cursor = conn.cursor()


            # Загрузка комплектующих (id, name, price, image_path, category_id)
            cursor.execute("""
                SELECT a.id, a.name, a.price, a.image_path, c.name 
                FROM accessories a
                JOIN categories_accessories c ON a.category_id = c.id
            """)
            self.accessories = cursor.fetchall()

            # Загрузка параметров (id, name, price_modifier)
            cursor.execute("SELECT id, name, price_modifier FROM additional_params")
            self.params = cursor.fetchall()

        except MySQLdb.Error as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить данные: {e}")
        finally:
            if 'conn' in locals():
                conn.close()



    def go_to_accessories(self):


        self.model = QtGui.QStandardItemModel()
        # Заголовки столбцов
        self.model.setHorizontalHeaderLabels(["Фото", "Название", "Цена", "Выбрать"])

        for accessory in self.accessories:
            row = []

            # 1. Столбец с фото
            if accessory[3]:
                item_img = QtGui.QStandardItem()
                pixmap = QtGui.QPixmap(accessory[3]).scaled(100, 100)
                item_img.setData(pixmap, Qt.ItemDataRole.DecorationRole)
                row.append(item_img)
            else:
                row.append(QtGui.QStandardItem("Нет фото"))

            # 2. Название и категория
            item_text = QtGui.QStandardItem(
                f"{accessory[1]}\nКатегория: {accessory[4]}"
            )
            row.append(item_text)

            # 3. Цена
            item_price = QtGui.QStandardItem(f"{accessory[2]} руб")
            row.append(item_price)

            # 4. Чекбокс
            item_checkbox = QtGui.QStandardItem()
            item_checkbox.setCheckable(True)
            item_checkbox.setAccessibleDescription(str(accessory[0]))  # Сохраняем ID
            row.append(item_checkbox)

            self.model.appendRow(row)

        self.tableView.setModel(self.model)
        self.tableView.resizeRowsToContents()
        self.tableView.horizontalHeader().setStretchLastSection(True)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = ClientOrderWindow1()
    ui.show()
    sys.exit(app.exec())
