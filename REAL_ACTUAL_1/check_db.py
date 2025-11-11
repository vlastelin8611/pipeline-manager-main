import sqlite3

def check_database_structure(db_file):
    try:
        # Подключаемся к базе данных
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        print("Таблицы в базе данных:")
        for table in tables:
            print(f"- {table[0]}")
            # Получаем структуру таблицы
            cursor.execute(f"PRAGMA table_info({table[0]});")
            columns = cursor.fetchall()
            print("  Столбцы:")
            for column in columns:
                print(f"  - {column[1]} (Тип: {column[2]})")

        # Закрываем соединение
        conn.close()
    except Exception as e:
        print(f"Ошибка: {e}")

# Укажите путь к вашей базе данных
check_database_structure('new_database.db')