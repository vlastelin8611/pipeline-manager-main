import sqlite3
import os

def check_database(db_path):
    if not os.path.exists(db_path):
        print(f"База данных {db_path} не найдена")
        return
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Получаем список таблиц
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    
    print(f"Таблицы в базе данных {db_path}:")
    for table in tables:
        print(f"  - {table}")
        
        # Получаем информацию о структуре таблицы
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        print(f"    Столбцы:")
        for col in columns:
            col_id, name, type_name, notnull, default_val, pk = col
            print(f"      {name} ({type_name})")
        
        # Получаем первые 3 строки из таблицы для примера
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            
            print(f"    Примеры данных ({len(rows)} строк):")
            for row in rows:
                print(f"      {row}")
        except sqlite3.Error as e:
            print(f"    Ошибка при чтении данных: {e}")
        
        print()
    
    conn.close()

if __name__ == "__main__":
    check_database("new_database.db") 