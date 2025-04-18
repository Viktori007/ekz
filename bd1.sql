drop database ekz1;
create database ekz1;
use ekz1;

-- Пользователи системы
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    role ENUM('пользователь', 'админ') NOT NULL DEFAULT 'пользователь'
);

-- Структурные подразделения
CREATE TABLE departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL UNIQUE
);

-- Документы (объединяем дела, описи и документы)
CREATE TABLE documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    doc_number VARCHAR(50) NOT NULL,
    type ENUM('case', 'inventory', 'document') NOT NULL,
    parent_id INT NULL,
    department_id INT NULL,
    file_path VARCHAR(255) null,
    upload_date datetime DEFAULT CURRENT_TIMESTAMP,
    uploaded_by INT NULL,
    signature_verified BOOLEAN DEFAULT FALSE,
    is_complete BOOLEAN DEFAULT FALSE,
    is_reproducible BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'new',
    FOREIGN KEY (parent_id) REFERENCES documents(id),
    FOREIGN KEY (department_id) REFERENCES departments(id),
    FOREIGN KEY (uploaded_by) REFERENCES users(id)
);

CREATE TABLE requests_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL
    );

-- Заявки
CREATE TABLE requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    req_number VARCHAR(50) NOT NULL UNIQUE,
    type_id int NOT NULL,
    priority TINYINT DEFAULT 3 COMMENT '1-высокий, 2-средний, 3-низкий',
    status VARCHAR(50) DEFAULT 'открытый',
    created_by INT NOT NULL,
    created_at datetime,
    document_id INT NULL,
    FOREIGN KEY (created_by) REFERENCES users(id),
    FOREIGN KEY (type_id) REFERENCES requests_type(id),
    FOREIGN KEY (document_id) REFERENCES documents(id)
);


-- Файлы заявок
CREATE TABLE request_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    uploaded_at datetime,
    FOREIGN KEY (request_id) REFERENCES requests(id)
);

-- Сообщения и история
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    request_id INT NULL,
    document_id INT NULL,
    sender_id INT NOT NULL,
    sent_at datetime,
    message_text TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (request_id) REFERENCES requests(id),
    FOREIGN KEY (document_id) REFERENCES documents(id),
    FOREIGN KEY (sender_id) REFERENCES users(id)
);

-- Уведомления
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    created_at datetime,
    is_read BOOLEAN DEFAULT FALSE,
    related_to VARCHAR(50) NULL COMMENT 'заявка, документ',
    related_id INT NULL, 
    FOREIGN KEY (user_id) REFERENCES users(id)
);

INSERT INTO users (login, password, full_name, email, role) VALUES
('admin', 'admin123', 'Администратор Системы', 'admin@company.com', 'админ'),
('user1', 'user1123', 'Иванов Иван Иванович', 'ivanov@company.com', 'пользователь'),
('user2', 'user2123', 'Петров Петр Петрович', 'petrov@company.com', 'пользователь'),
('user3', 'user3123', 'Сидорова Анна Владимировна', 'sidorova@company.com', 'пользователь'),
('user4', 'user4123', 'Кузнецова Елена Сергеевна', 'kuznetsova@company.com', 'пользователь');


INSERT INTO departments (name, code) VALUES
('Отдел кадров', 'HR-001'),
('Бухгалтерия', 'ACC-002'),
('IT-отдел', 'IT-003'),
('Отдел продаж', 'SALES-004'),
('Отдел технического обслуживания', 'TECH-005');

INSERT INTO requests_type (title) VALUES
('Регистрация нового документа'),
('Проверка электронной подписи'),
('Запрос на исправление'),
('Запрос на удаление'),
('Вопрос по комплектности');


-- Описи
INSERT INTO documents (title, doc_number, type, department_id, upload_date, uploaded_by, signature_verified, is_complete, is_reproducible, status) VALUES
('Опись документов отдела кадров за 2023 год', 'INV-HR-2023-001', 'inventory', 1, '2023-01-15 10:00:00', 2, TRUE, TRUE, TRUE, 'approved'),
('Опись бухгалтерских документов за 2023 год', 'INV-ACC-2023-001', 'inventory', 2, '2023-01-20 11:30:00', 3, TRUE, TRUE, TRUE, 'approved'),
('Опись IT-документации за 2023 год', 'INV-IT-2023-001', 'inventory', 3, '2023-02-01 14:15:00', 4, FALSE, FALSE, TRUE, 'rejected');

-- Дела (привязаны к описям)
INSERT INTO documents (title, doc_number, type, parent_id, department_id, upload_date, uploaded_by, signature_verified, is_complete, is_reproducible, status) VALUES
('Дело по кадровым приказам 2023', 'CASE-HR-2023-001', 'case', 1, 1, '2023-01-16 09:20:00', 2, TRUE, TRUE, TRUE, 'approved'),
('Дело по трудовым договорам 2023', 'CASE-HR-2023-002', 'case', 1, 1, '2023-01-17 10:45:00', 2, TRUE, FALSE, TRUE, 'pending'),
('Дело по финансовым отчетам 2023', 'CASE-ACC-2023-001', 'case', 2, 2, '2023-01-21 13:10:00', 3, TRUE, TRUE, TRUE, 'approved'),
('Дело по сетевым настройкам 2023', 'CASE-IT-2023-001', 'case', 3, 3, '2023-02-02 15:30:00', 4, FALSE, FALSE, FALSE, 'rejected');

-- Документы (привязаны к делам)
INSERT INTO documents (title, doc_number, type, parent_id, department_id, file_path, upload_date, uploaded_by, signature_verified, is_complete, is_reproducible, status) VALUES
('Приказ о приеме на работу №45', 'DOC-HR-2023-045', 'document', 4, 1, '/files/hr/orders/45.pdf', '2023-01-16 09:25:00', 2, TRUE, TRUE, TRUE, 'approved'),
('Трудовой договор с Ивановым И.И.', 'DOC-HR-2023-101', 'document', 5, 1, '/files/hr/contracts/101.pdf', '2023-01-17 10:50:00', 2, TRUE, FALSE, TRUE, 'pending'),
('Финансовый отчет за январь 2023', 'DOC-ACC-2023-001', 'document', 6, 2, '/files/acc/reports/001.pdf', '2023-01-21 13:15:00', 3, TRUE, TRUE, TRUE, 'approved'),
('Схема локальной сети', 'DOC-IT-2023-015', 'document', 7, 3, '/files/it/network/015.pdf', '2023-02-02 15:35:00', 4, FALSE, FALSE, FALSE, 'rejected');

INSERT INTO requests (title, req_number, type_id, priority, status, created_by, created_at, document_id) VALUES
('Проверка подписи на приказе', 'REQ-2023-001', 2, 2, 'закрытый', 2, '2023-01-16 09:30:00', 8),
('Неполный комплект документов', 'REQ-2023-002', 5, 1, 'открытый', 3, '2023-01-21 13:20:00', 6),
('Ошибка в сетевой схеме', 'REQ-2023-003', 3, 1, 'в обработке', 4, '2023-02-02 15:40:00', 11),
('Удаление дубликата документа', 'REQ-2023-004', 4, 3, 'открытый', 2, '2023-02-10 11:15:00', NULL),
('Регистрация нового договора', 'REQ-2023-005', 1, 2, 'в обработке', 3, '2023-02-12 14:30:00', NULL);

INSERT INTO request_files (request_id, file_path, file_name, uploaded_at) VALUES
(1, '/files/requests/2023-001/scan1.pdf', 'Скан подписи.pdf', '2023-01-16 09:32:00'),
(2, '/files/requests/2023-002/missing.pdf', 'Список отсутствующих.pdf', '2023-01-21 13:25:00'),
(3, '/files/requests/2023-003/error.png', 'Скрин ошибки.png', '2023-02-02 15:45:00'),
(5, '/files/requests/2023-005/contract.docx', 'Новый договор.docx', '2023-02-12 14:35:00');


INSERT INTO messages (request_id, document_id, sender_id, sent_at, message_text, is_read) VALUES
(1, NULL, 2, '2023-01-16 09:30:00', 'Прошу проверить электронную подпись на приказе', TRUE),
(1, NULL, 1, '2023-01-16 10:15:00', 'Подпись проверена, все в порядке', TRUE),
(2, NULL, 3, '2023-01-21 13:20:00', 'В деле отсутствуют некоторые финансовые отчеты', TRUE),
(2, NULL, 1, '2023-01-21 14:00:00', 'Запросите недостающие документы у бухгалтерии', FALSE),
(3, NULL, 4, '2023-02-02 15:40:00', 'Обнаружена ошибка в IP-адресации на схеме', TRUE),
(NULL, 8, 2, '2023-01-18 11:20:00', 'Приказ принят в архив', TRUE),
(NULL, 11, 1, '2023-02-03 09:10:00', 'Документ отклонен из-за несоответствия формата', TRUE);



INSERT INTO notifications (user_id, title, message, created_at, is_read, related_to, related_id) VALUES
(2, 'Проверка подписи', 'Ваша подпись на документе DOC-HR-2023-045 проверена', '2023-01-16 10:20:00', TRUE, 'документ', 8),
(3, 'Неполный комплект', 'По вашему делу CASE-ACC-2023-001 поступила заявка о неполном комплекте', '2023-01-21 13:30:00', FALSE, 'заявка', 2),
(4, 'Ошибка в документе', 'Ваш документ DOC-IT-2023-015 отклонен из-за ошибок', '2023-02-03 09:15:00', TRUE, 'документ', 11),
(1, 'Новая заявка', 'Поступила новая заявка REQ-2023-003 на исправление', '2023-02-02 15:45:00', TRUE, 'заявка', 3),
(2, 'Напоминание', 'Не забудьте предоставить недостающие документы по делу CASE-HR-2023-002', '2023-01-25 16:00:00', FALSE, 'документ', 5);







