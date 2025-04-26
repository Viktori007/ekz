import MySQLdb as mdb
from MySQLdb._exceptions import Error


def connection_client():
    connection = mdb.connect(host="localhost", user="client_window", password="", db="window_fabric", port=3306)
    return connection

def connection_manager():
    connection = mdb.connect(host="localhost", user="admin_window", password="", db="window_fabric", port=3306)
    return connection

def get_user(login, password):
    connection = connection_manager()
    cursor = connection.cursor()

    cursor.execute("select id, role from users where username= %s and password_hash= SHA2(%s, 256)", (login, password))
    user = cursor.fetchone()
    return user

def get_orders_user(id_user):
    connection = connection_client()
    cursor = connection.cursor()
    cursor.execute("""select order_id, window_materials.name,manufacturers.name, width, height, quantity, price 
                        from order_items JOIN
                        window_materials on window_materials.id = material_id
                        join orders on `order_id` = orders.id
                        JOIN manufacturers on manufacturers.id = `manufacturer_id`
                        where orders.client_id = 1;""")
    orders = cursor.fetchall()
    return orders


def get_window_materials():
    connection = connection_client()
    cursor = connection.cursor()
    cursor.execute("""select * from window_materials""")
    str = cursor.fetchall()
    return str

def get_manufacturers():
    connection = connection_client()
    cursor = connection.cursor()
    cursor.execute("""select * from manufacturers""")
    str = cursor.fetchall()
    return str

def get_categories_accessories():
    connection = connection_client()
    cursor = connection.cursor()
    cursor.execute("""select * from categories_accessories""")
    str = cursor.fetchall()
    return str

# Добавьте в config_to_db.py

def get_opening_types():
    connection = connection_client()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM opening_types")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def get_accessories_by_category(category_id):
    connection = connection_client()
    cursor = connection.cursor()
    cursor.execute("""
        SELECT * FROM accessories 
        WHERE category_id = %s
    """, (category_id,))
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result

def get_additional_params():
    connection = connection_client()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM additional_params")
    result = cursor.fetchall()
    cursor.close()
    connection.close()
    return result


def get_categories_accessories():
    try:
        conn = connection_client()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories_accessories")
            return cursor.fetchall()
    except Error as e:
        print(f"Ошибка получения категорий: {e}")
        return []
    finally:
        if conn: conn.close()


def create_order(client_id, material_id, manufacturer_id, width, height,
                 sashes_count, opening_types, accessories, params, phone, total_price):
    try:
        conn = connection_client()
        if conn:
            cursor = conn.cursor()

            # Основной заказ
            cursor.execute(
                "INSERT INTO orders (client_id, status_id, total_price, phone) VALUES (%s, 0, %s, %s)",
                (client_id, total_price, phone)
            )
            order_id = cursor.lastrowid

            # Элемент заказа (окно)
            cursor.execute(
                """INSERT INTO order_items 
                (order_id, material_id, manufacturer_id, width, height, quantity, price) 
                VALUES (%s, %s, %s, %s, %s, 1, %s)""",
                (order_id, material_id, manufacturer_id, width, height, total_price)
            )
            item_id = cursor.lastrowid

            # Створки
            for i, opening in enumerate(opening_types):
                cursor.execute(
                    "INSERT INTO window_sashes (order_item_id, position, opening_type_id) VALUES (%s, %s, %s)",
                    (item_id, i + 1, opening['id'])
                )

            # Комплектующие
            for accessory in accessories:
                cursor.execute(
                    "INSERT INTO order_accessories (order_id, accessory_id, quantity) VALUES (%s, %s, 1)",
                    (order_id, accessory['id'])
                )

            # Параметры
            for param in params:
                cursor.execute(
                    "INSERT INTO item_additional_params (order_item_id, param_id) VALUES (%s, %s)",
                    (item_id, param['id'])
                )

            conn.commit()
            return order_id
    except Error as e:
        print(f"Ошибка при создании заказа: {e}")
        conn.rollback()
        return None
    finally:
        if conn: conn.close()