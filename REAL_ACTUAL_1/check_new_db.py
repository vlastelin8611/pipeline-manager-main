import sqlite3
import os
import sys

def check_db(db_file='new_database.db'):
    """
    Проверяет содержимое указанной базы данных.
    
    Args:
        db_file (str): Имя файла базы данных
    """
    print(f"Проверка БД: {db_file}")
    
    # Проверяем, существует ли файл БД
    if not os.path.exists(db_file):
        print(f"БД {db_file} не существует!")
        
        # Поиск всех файлов .db в текущей директории
        db_files = [f for f in os.listdir() if f.endswith('.db')]
        if db_files:
            print(f"Найдены следующие файлы БД: {db_files}")
            print("Запустите скрипт с именем файла в качестве аргумента: python check_new_db.py имя_файла.db")
        return
        
    # Подключаемся к БД
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    try:
        # Получаем список всех таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Таблицы в БД: {tables}")
        
        # Если есть таблица cells, проверяем её
        if 'cells' in tables:
            # Получаем структуру таблицы
            cursor.execute("PRAGMA table_info(cells)")
            columns = [(col[0], col[1], col[2]) for col in cursor.fetchall()]
            print("\nСтруктура таблицы cells:")
            for col in columns:
                print(f"  {col[0]}: {col[1]} ({col[2]})")
            
            # Получаем количество записей
            cursor.execute("SELECT COUNT(*) FROM cells")
            count = cursor.fetchone()[0]
            print(f"\nВсего записей в cells: {count}")
            
            # Выводим первые 10 записей
            print("\nПервые 10 записей:")
            cursor.execute("SELECT * FROM cells LIMIT 10")
            rows = cursor.fetchall()
            for row in rows:
                print(row)
            
            # Список всех столбцов
            column_names = [col[1] for col in columns]
            
            # Проверяем наличие столбцов для статуса
            status_columns = ['working_status', 'status', 'state', 'work_status']
            found_status_column = None
            
            for col_name in status_columns:
                if col_name in column_names:
                    found_status_column = col_name
                    print(f"\nНайден столбец статуса: {col_name}")
                    
                    # Выводим уникальные значения в этом столбце
                    cursor.execute(f"SELECT DISTINCT {col_name} FROM cells")
                    values = [row[0] for row in cursor.fetchall()]
                    print(f"Уникальные значения в {col_name}: {values}")
                    
                    # Проверяем наличие значения "работает"
                    working_values = [v for v in values if str(v).strip().lower() == "работает"]
                    if working_values:
                        # Считаем количество рабочих ячеек
                        cursor.execute(f"SELECT COUNT(*) FROM cells WHERE {col_name} = 'работает'")
                        working_count = cursor.fetchone()[0]
                        print(f"Ячеек со статусом 'работает': {working_count}")
                    else:
                        print(f"ВНИМАНИЕ: В столбце {col_name} нет значения 'работает'!")
                        
                        # Выводим все значения для анализа
                        print(f"Все значения в {col_name}:")
                        cursor.execute(f"SELECT ROWID, {col_name} FROM cells LIMIT 20")
                        for row in cursor.fetchall():
                            print(f"  ROWID={row[0]}: '{row[1]}'")
                    break
            
            if not found_status_column:
                print("\nВНИМАНИЕ: Не найден столбец для статуса ячеек!")
        else:
            print("\nВНИМАНИЕ: Таблица cells не найдена в БД!")
        
    except Exception as e:
        print(f"Ошибка при проверке БД: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    # Если есть аргумент командной строки, используем его как имя файла БД
    if len(sys.argv) > 1:
        check_db(sys.argv[1])
    else:
        check_db() 