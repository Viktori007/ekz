import sys

import MySQLdb as mdb
from PyQt6 import QtCore, QtGui, QtWidgets, uic
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QWidget, QMessageBox, QDialog, \
    QTableView, QComboBox, QDialogButtonBox, QVBoxLayout


def connect_to_db():
    connect = mdb.connect(host='localhost',user='root', port=3306, password='',db='ekz1')
    return connect


def get_sales():
    connect = connect_to_db()
    cursor = connect.cursor()
    qwery = """select * from users"""

    cursor.execute(qwery)
    users = cursor.fetchall()
    return users

def get_users():
    connect = connect_to_db()
    cursor = connect.cursor()
    qwery = """SELECT id, login, password, role FROM users"""
    cursor.execute(qwery)
    users = cursor.fetchall()
    return users

def add_user_to_db(login, password, role):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = "INSERT INTO users (login, password, role) VALUES (%s, %s, %s)"
        cursor.execute(query, (login, password, role))
        conn.commit()
        conn.close()
    except mdb.Error as e:
        conn.rollback()
        raise Exception(f"Не удалось добавить пользователя: {e}")

def update_user_in_db(user_id, login, password, role):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        query = "UPDATE users SET login = %s, password = %s, role = %s WHERE id = %s"
        cursor.execute(query, (login, password, role, user_id))
        conn.commit()
        conn.close()
    except mdb.Error as e:
        conn.rollback()
        raise Exception(f"Не удалось обновить данные: {e}")

def delete_user_from_db(user_id):
    try:
        conn = connect_to_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        conn.close()
    except mdb.Error as e:
        conn.rollback()
        raise Exception(f"Не удалось удалить пользователя: {e}")



def get_role(login, password):
    try:
        connect = connect_to_db()
        with connect.cursor() as cursor:
            query = "SELECT role FROM users WHERE login = %s AND password = %s"
            cursor.execute(query, (login, password))  # Используем параметризованный запрос
            return cursor.fetchone()
    except Exception as e:
        print(f"Database error: {e}")
        return None

class Ui_MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi("enter.ui", self)

        self.lineEdit_login = self.findChild(QLineEdit, "lineEdit_login")
        self.lineEdit_password = self.findChild(QLineEdit, "lineEdit_password")
        self.pushButton_enter = self.findChild(QPushButton, "pushButton_enter")

        self.pushButton_enter.clicked.connect(self.get_login)

    def authenticate(self):
        login = self.lineEdit_login.text()
        password = self.lineEdit_password.text()

        if not login or not password:
            QMessageBox.warning(self, "Ошибка", "Введите логин и пароль")
            return

        role = get_role(login, password)

        if role:
            self.open_admin_window()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def open_admin_window(self):
        self.admin_window.show()
        self.hide()

    def closeEvent(self, event):
        # Закрываем все дочерние окна при закрытии главного
        if hasattr(self, 'admin_window') and self.admin_window:
            self.admin_window.close()
        event.accept()

    def get_login(self):
        login = self.lineEdit_login.text()
        password = self.lineEdit_password.text()
        role = get_role(login, password)
        if role:
            print(role)
            self.admin_window = AdminWindow(self)
            self.admin_window.show()
            self.hide()


class AdminWindow(QMainWindow):  # Лучше использовать QMainWindow для согласованности
    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi("admin2.ui", self)
        self.setWindowTitle("Админ-панель")

        self.tableView = self.findChild(QTableView, "tableView")
        self.pushButton_exit = self.findChild(QPushButton, "pushButton_exit")
        self.pushButton_edit = self.findChild(QPushButton, "pushButton_edit")
        self.pushButton_delete = self.findChild(QPushButton, "pushButton_delete")
        self.pushButton_add = self.findChild(QPushButton, "pushButton_add")
        self.pushButton_exit.clicked.connect(self.close_and_return)

        self.model = QStandardItemModel()
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        # Загрузка данных
        self.load_users()

        # Подключение кнопок
        self.pushButton_exit.clicked.connect(self.close_and_return)
        self.pushButton_add.clicked.connect(self.add_user)
        self.pushButton_delete.clicked.connect(self.delete_user)
        self.pushButton_edit.clicked.connect(self.edit_user)


    def close_and_return(self):
        if self.parent():
            self.parent().show()
        self.close()

    def load_users(self):
        try:
            users = get_users()
            # Очищаем модель
            self.model.clear()

            # Устанавливаем заголовки
            self.model.setHorizontalHeaderLabels(["ID", "Логин", "Пароль", "Роль"])

            # Заполняем модель данными
            for user in users:
                items = [
                    QStandardItem(str(user[0])),  # ID
                    QStandardItem(user[1]),  # Логин
                    QStandardItem(user[2]),  # Пароль
                    QStandardItem(user[3])  # Роль
                ]
                self.model.appendRow(items)

            # Настраиваем таблицу
            self.tableView.resizeColumnsToContents()

        except mdb.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при загрузке пользователей: {e}")

    def add_user(self):
        dialog = UserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            login = dialog.lineEdit_login.text()
            password = dialog.lineEdit_password.text()
            role = dialog.comboBox_role.currentText()

            try:
                add_user_to_db(login, password, role)
                self.load_users()
                QMessageBox.information(self, "Успех", "Пользователь добавлен")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def delete_user(self):
        selected = self.tableView.selectionModel().selectedRows()

        if not selected:
            QMessageBox.warning(self, "Ошибка", "Выберите пользователя для удаления")
            return

        reply = QMessageBox.question(
            self, "Подтверждение",
            "Вы уверены, что хотите удалить выбранных пользователей?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                for index in selected:
                    user_id = self.model.item(index.row(), 0).text()
                    delete_user_from_db(user_id)

                self.load_users()
                QMessageBox.information(self, "Успех", "Пользователи удалены")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))

    def edit_user(self):
        selected = self.tableView.selectionModel().selectedRows()

        if not selected or len(selected) > 1:
            QMessageBox.warning(self, "Ошибка", "Выберите одного пользователя для редактирования")
            return

        row = selected[0].row()
        user_id = self.model.item(row, 0).text()
        current_login = self.model.item(row, 1).text()
        current_password = self.model.item(row, 2).text()
        current_role = self.model.item(row, 3).text()

        dialog = UserDialog(self)
        dialog.setWindowTitle("Редактировать пользователя")
        dialog.lineEdit_login.setText(current_login)
        dialog.lineEdit_password.setText(current_password)
        dialog.comboBox_role.setCurrentText(current_role)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_login = dialog.lineEdit_login.text()
            new_password = dialog.lineEdit_password.text()
            new_role = dialog.comboBox_role.currentText()

            try:
                update_user_in_db(user_id, new_login, new_password, new_role)
                self.load_users()
                QMessageBox.information(self, "Успех", "Данные пользователя обновлены")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", str(e))


class UserDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        uic.loadUi("edit.ui", self)  # Загружаем ваш UI файл
        self.setWindowTitle("Добавить пользователя")

        self.comboBox_role = self.findChild(QComboBox, "comboBox_role")
        self.comboBox_role.addItems(["админ", "пользователь"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Ui_MainWindow()
    window.show()
    sys.exit(app.exec())
