from PyQt6 import QtWidgets, QtGui, uic
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import MySQLdb
from MySQLdb.cursors import DictCursor


class ClientOrderWindow(QtWidgets.QMainWindow):
    def __init__(self, parent, id):
        super().__init__(parent)
        uic.loadUi('ui/order_window.ui', self)

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

        self.setup_ui()
        self.load_data()
        self.connect_buttons()
        self.id = id

    def setup_ui(self):
        """Настройка интерфейса"""
        self.setWindowTitle("Оформление заказа окна")
        self.resize(800, 600)

        # Настройка ComboBox и SpinBox
        self.spinSashes.setRange(1, 5)
        self.spinWidth.setRange(50, 300)
        self.spinHeight.setRange(50, 300)

        # Настройка списка параметров
        self.listParams.setSelectionMode(QtWidgets.QListWidget.SelectionMode.MultiSelection)

    def load_data(self):
        """Загрузка данных из БД"""
        try:
            conn = MySQLdb.connect(host="localhost", user="client_window", password="", db="window_fabric", port=3306)
            cursor = conn.cursor()

            # Загрузка материалов (предполагаем структуру: (id, name, ...))
            cursor.execute("SELECT id, name FROM window_materials")
            for material in cursor.fetchall():
                self.comboMaterial.addItem(material[1], material[0])  # name, id

            # Загрузка производителей (id, name, ...)
            cursor.execute("SELECT id, name FROM manufacturers")
            for manufacturer in cursor.fetchall():
                self.comboManufacturer.addItem(manufacturer[1], manufacturer[0])  # name, id

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

    def connect_buttons(self):
        self.btnNext1.clicked.connect(self.go_to_dimensions)
        self.btnBack2.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        self.btnNext2.clicked.connect(self.go_to_accessories)
        self.btnBack3.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        self.btnNext3.clicked.connect(self.go_to_params)
        self.btnBack4.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(2))
        self.btnFinish.clicked.connect(self.finish_order)
        self.btnBack.clicked.connect(self.close)


    def go_to_dimensions(self):
        """Переход к шагу с размерами"""
        self.window_data['material_id'] = self.comboMaterial.currentData()
        self.window_data['manufacturer_id'] = self.comboManufacturer.currentData()
        self.window_data['sashes_count'] = self.spinSashes.value()
        combo = QtWidgets.QComboBox()

        self.stackedWidget.setCurrentIndex(1)

    def go_to_accessories(self):
        self.window_data['width'] = self.spinWidth.value()
        self.window_data['height'] = self.spinHeight.value()

        self.tableAccessories = QtWidgets.QTableView()
        self.model = QtGui.QStandardItemModel()
        self.tableAccessories.setModel(self.model)

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

        self.layoutAccessories.addWidget(self.tableAccessories)
        self.stackedWidget.setCurrentIndex(2)

    def go_to_params(self):
        """Переход к шагу с параметрами"""
        # Сохраняем выбранные комплектующие
        self.window_data['accessories'] = []


        # Заполняем список параметров
        self.listParams.clear()
        for param in self.params:
            item = QtWidgets.QListWidgetItem(f"{param[1]} (x{param[2]})")
            item.setData(Qt.ItemDataRole.UserRole, param)
            self.listParams.addItem(item)

        self.stackedWidget.setCurrentIndex(3)

    def finish_order(self):
        """Завершение оформления заказа"""
        # Сохраняем выбранные параметры
        self.window_data['params'] = [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.listParams.selectedItems()
        ]

        # Рассчитываем стоимость
        total_price = self.calculate_price()

        # Показываем итог
        QtWidgets.QMessageBox.information(
            self,
            "Заказ оформлен",
            f"Ваш заказ успешно оформлен!\nИтоговая стоимость: {total_price:.2f} руб"
        )

    def calculate_price(self):
        """Расчет стоимости заказа"""
        # Здесь должна быть логика расчета на основе window_data
        # Это упрощенный пример - в реальном приложении нужно учитывать:
        # - площадь окна
        # - выбранные материалы
        # - комплектующие
        # - параметры

        base_price = 5000  # Базовая цена
        accessories_price = sum(float(acc['price']) for acc in self.window_data['accessories'])
        params_modifier = 1.0

        for param in self.window_data['params']:
            params_modifier *= float(param[2])

        return (base_price + accessories_price) * params_modifier

