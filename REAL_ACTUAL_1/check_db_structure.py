import sqlite3
import os

def check_db_structure(db_path):
    """Проверяет структуру базы данных и выводит информацию о таблицах и колонках"""
    if not os.path.exists(db_path):
        print(f"База данных {db_path} не существует!")
        return
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Получаем список таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"Таблицы в базе данных {db_path}:")
        for table in tables:
            table_name = table[0]
            print(f"\nТаблица: {table_name}")
            
            # Получаем структуру таблицы
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print("Структура:")
            for col in columns:
                col_id, name, type_name, not_null, default_val, primary_key = col
                print(f"  {col_id}: {name} ({type_name}), NOT NULL={not_null}, DEFAULT={default_val}, PK={primary_key}")
                
            # Получаем пример данных
            try:
                cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
                row = cursor.fetchone()
                if row:
                    print("Пример данных:")
                    print(f"  {row}")
                else:
                    print("Таблица пуста")
            except sqlite3.Error as e:
                print(f"Ошибка при чтении данных: {e}")
                
        conn.close()
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    # Проверяем все доступные базы данных в текущей директории
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    
    if not db_files:
        print("Файлы баз данных не найдены в текущей директории")
    else:
        print(f"Найдено баз данных: {len(db_files)}")
        for db_file in db_files:
            check_db_structure(db_file)
            print("\n" + "=" * 80 + "\n") 