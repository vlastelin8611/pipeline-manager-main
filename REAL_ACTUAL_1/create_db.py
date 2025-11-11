import sqlite3
import os

def create_test_db(db_number=1):
    """
    Создает тестовую базу данных с таблицей cells.
    
    Args:
        db_number (int): Номер базы данных (1, 2 или 3)
    """
    # Имя файла базы данных
    db_file = f'nefteprovod_{db_number}.db'
    
    # Проверяем, существует ли уже такой файл
    if os.path.exists(db_file):
        print(f"БД {db_file} уже существует. Удалите файл, если хотите создать новую БД.")
        return
        
    # Создаем БД и подключаемся к ней
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Создаем таблицу cells для хранения состояний ячеек
    cursor.execute('''
    CREATE TABLE cells (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        line_id INTEGER NOT NULL,  -- Номер линии (1-4)
        cell_id INTEGER NOT NULL,  -- Номер ячейки в линии (1-10)
        working_status TEXT DEFAULT "не работает",  -- Состояние ("работает" или любое другое)
        UNIQUE(line_id, cell_id)    -- Уникальный ключ по линии и ячейке
    )
    ''')
    
    # Заполняем таблицу тестовыми данными
    # Каждая третья ячейка в линии будет в рабочем состоянии
    for line_id in range(1, 5):  # 4 линии
        for cell_id in range(1, 11):  # 10 ячеек в каждой линии
            # Задаем разные паттерны состояний для разных БД
            if db_number == 1:
                # В БД 1 каждая третья ячейка рабочая
                status = "работает" if cell_id % 3 == 0 else "не работает"
            elif db_number == 2:
                # В БД 2 каждая вторая ячейка рабочая
                status = "работает" if cell_id % 2 == 0 else "повреждена"
            else:
                # В БД 3 ячейки с нечетным номером рабочие
                status = "работает" if cell_id % 2 != 0 else "отключена"
                
            cursor.execute(
                "INSERT INTO cells (line_id, cell_id, working_status) VALUES (?, ?, ?)",
                (line_id, cell_id, status)
            )
    
    # Сохраняем изменения и закрываем соединение
    conn.commit()
    conn.close()
    
    print(f"База данных {db_file} успешно создана и заполнена тестовыми данными.")

if __name__ == "__main__":
    # Создаем три тестовые базы данных
    for i in range(1, 4):
        create_test_db(i) 