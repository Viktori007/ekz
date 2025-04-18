import sys
import mysql.connector
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                            QVBoxLayout, QTextEdit, QLineEdit, 
                            QPushButton, QLabel, QMessageBox)
from PyQt6.QtCore import QTimer

class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Простой чат")
        self.setGeometry(100, 100, 500, 400)
        
        # Подключение к БД
        self.db_connection = self.connect_to_db()
        self.create_table()
        
        # Интерфейс
        self.init_ui()
        
        # Таймер для обновления сообщений
        self.timer = QTimer()
        self.timer.timeout.connect(self.load_messages)
        self.timer.start(1000)  # Обновление каждую секунду
        
    def connect_to_db(self):
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="chat_db"
            )
            return conn
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось подключиться к БД: {e}")
            sys.exit(1)
    
    def create_table(self):
        cursor = self.db_connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.db_connection.commit()
    
    def init_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()
        
        # Поле для отображения сообщений
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)
        
        # Поле для ввода имени
        self.username_label = QLabel("Ваше имя:")
        layout.addWidget(self.username_label)
        
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)
        
        # Поле для ввода сообщения
        self.message_label = QLabel("Сообщение:")
        layout.addWidget(self.message_label)
        
        self.message_input = QLineEdit()
        self.message_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.message_input)
        
        # Кнопка отправки
        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)
        
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        # Загружаем сообщения при старте
        self.load_messages()
    
    def send_message(self):
        username = self.username_input.text().strip()
        message = self.message_input.text().strip()
        
        if not username or not message:
            QMessageBox.warning(self, "Ошибка", "Введите имя и сообщение")
            return
        
        try:
            cursor = self.db_connection.cursor()
            query = "INSERT INTO messages (username, message) VALUES (%s, %s)"
            cursor.execute(query, (username, message))
            self.db_connection.commit()
            
            self.message_input.clear()
            self.load_messages()
        except mysql.connector.Error as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось отправить сообщение: {e}")
    
    def load_messages(self):
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT username, message, timestamp 
                FROM messages 
                ORDER BY timestamp DESC 
                LIMIT 50
            """)
            messages = cursor.fetchall()
            
            self.chat_display.clear()
            for msg in reversed(messages):
                username, message, timestamp = msg
                self.chat_display.append(
                    f"[{timestamp}] <{username}>: {message}"
                )
        except mysql.connector.Error as e:
            print(f"Ошибка при загрузке сообщений: {e}")
    
    def closeEvent(self, event):
        self.db_connection.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Создаем базу данных, если ее нет
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password=""
        )
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS chat_db")
        conn.close()
    except mysql.connector.Error as e:
        QMessageBox.critical(None, "Ошибка", f"Не удалось создать БД: {e}")
        sys.exit(1)
    
    window = ChatWindow()
    window.show()
    sys.exit(app.exec())
