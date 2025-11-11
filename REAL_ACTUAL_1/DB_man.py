import sqlite3
import os
import sys
import psycopg2
from psycopg2 import sql

class DBNormalizer:
    """
    Класс для нормализации разных типов баз данных.
    Преобразует различные форматы статусов ячеек в стандартный булевый формат (1 = работает, 0 = не работает).
    """
    
    def __init__(self, db_file=None, db_type='sqlite', postgres_conn_string=None):
        """
        Инициализация нормализатора БД.
        
        Args:
            db_file (str): Путь к файлу SQLite базы данных
            db_type (str): Тип БД ('sqlite' или 'postgres')
            postgres_conn_string (str): Строка подключения к PostgreSQL
        """
        self.db_file = db_file
        self.db_type = db_type.lower()
        self.postgres_conn_string = postgres_conn_string
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Подключение к базе данных"""
        try:
            if self.db_type == 'sqlite':
                if not self.db_file:
                    raise ValueError("Не указан файл SQLite базы данных")
                if not os.path.exists(self.db_file):
                    raise FileNotFoundError(f"Файл БД не найден: {self.db_file}")
                self.conn = sqlite3.connect(self.db_file)
            elif self.db_type == 'postgres':
                if not self.postgres_conn_string:
                    raise ValueError("Не указана строка подключения к PostgreSQL")
                self.conn = psycopg2.connect(self.postgres_conn_string)
            else:
                raise ValueError(f"Неподдерживаемый тип БД: {self.db_type}")
            
            self.cursor = self.conn.cursor()
            print(f"Подключено к БД: {self.db_type}")
            return True
        except Exception as e:
            print(f"Ошибка при подключении к БД: {e}")
            return False
    
    def disconnect(self):
        """Отключение от базы данных"""
        if self.conn:
            self.conn.close()
            print("Отключено от БД")
    
    def get_table_structure(self, table_name):
        """Получение структуры таблицы"""
        try:
            if self.db_type == 'sqlite':
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [(col[1], col[2]) for col in self.cursor.fetchall()]
            else:  # postgres
                self.cursor.execute(
                    "SELECT column_name, data_type FROM information_schema.columns "
                    f"WHERE table_name = '{table_name}'"
                )
                columns = self.cursor.fetchall()
            
            print(f"Структура таблицы {table_name}:")
            for col in columns:
                print(f"  {col[0]} ({col[1]})")
            
            return columns
        except Exception as e:
            print(f"Ошибка при получении структуры таблицы: {e}")
            return []
    
    def find_status_column(self, table_name):
        """Находит столбец, содержащий информацию о статусе ячеек"""
        columns = self.get_table_structure(table_name)
        column_names = [col[0] for col in columns]
        
        # Возможные имена столбцов со статусом
        status_columns = ['status', 'state', 'working_status', 'work_status', 'is_working']
        
        for col_name in status_columns:
            if col_name in column_names:
                print(f"Найден столбец статуса: {col_name}")
                return col_name
        
        print("Не найден столбец статуса")
        return None
    
    def normalize_status_column(self, table_name, status_column=None):
        """
        Нормализует столбец статуса, преобразуя различные значения в булевы (1 или 0).
        
        Args:
            table_name (str): Имя таблицы
            status_column (str): Имя столбца со статусом (если None, будет найден автоматически)
        """
        try:
            # Если столбец статуса не указан, пытаемся найти его
            if not status_column:
                status_column = self.find_status_column(table_name)
                if not status_column:
                    return False
            
            # Получаем все уникальные значения в столбце статуса
            if self.db_type == 'sqlite':
                self.cursor.execute(f"SELECT DISTINCT {status_column} FROM {table_name}")
            else:  # postgres
                self.cursor.execute(
                    sql.SQL("SELECT DISTINCT {} FROM {}").format(
                        sql.Identifier(status_column),
                        sql.Identifier(table_name)
                    )
                )
            
            unique_values = [row[0] for row in self.cursor.fetchall()]
            print(f"Уникальные значения в столбце {status_column}: {unique_values}")
            
            # Подсчитываем количество записей до обновления
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_records = self.cursor.fetchone()[0]
            
            # Создаем временный столбец
            temp_column = f"{status_column}_normalized"
            
            # Добавляем временный столбец
            if self.db_type == 'sqlite':
                self.cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {temp_column} INTEGER DEFAULT 0")
            else:  # postgres
                self.cursor.execute(
                    sql.SQL("ALTER TABLE {} ADD COLUMN {} INTEGER DEFAULT 0").format(
                        sql.Identifier(table_name),
                        sql.Identifier(temp_column)
                    )
                )
            
            # Обновляем значения во временном столбце
            for value in unique_values:
                # Определяем, работает ли ячейка с таким значением
                is_working = False
                
                if value is None:
                    is_working = False
                elif isinstance(value, bool):
                    is_working = value
                elif isinstance(value, (int, float)):
                    is_working = bool(value)
                else:
                    # Если строка
                    value_str = str(value).strip().lower()
                    is_working = value_str in ('1', 'true', 'yes', 'работает', 't', 'y')
                
                # Преобразуем в 1 или 0
                normalized_value = 1 if is_working else 0
                print(f"Значение '{value}' нормализовано в {normalized_value}")
                
                # Обновляем временный столбец
                if value is None:
                    if self.db_type == 'sqlite':
                        self.cursor.execute(f"UPDATE {table_name} SET {temp_column} = ? WHERE {status_column} IS NULL", (normalized_value,))
                    else:  # postgres
                        self.cursor.execute(
                            sql.SQL("UPDATE {} SET {} = %s WHERE {} IS NULL").format(
                                sql.Identifier(table_name),
                                sql.Identifier(temp_column),
                                sql.Identifier(status_column)
                            ),
                            (normalized_value,)
                        )
                else:
                    if self.db_type == 'sqlite':
                        self.cursor.execute(f"UPDATE {table_name} SET {temp_column} = ? WHERE {status_column} = ?", (normalized_value, value))
                    else:  # postgres
                        self.cursor.execute(
                            sql.SQL("UPDATE {} SET {} = %s WHERE {} = %s").format(
                                sql.Identifier(table_name),
                                sql.Identifier(temp_column),
                                sql.Identifier(status_column)
                            ),
                            (normalized_value, value)
                        )
            
            # Удаляем старый столбец и переименовываем новый
            if self.db_type == 'sqlite':
                # SQLite не поддерживает DROP COLUMN напрямую, поэтому нужно создать новую таблицу
                # Получаем список всех столбцов кроме старого столбца статуса
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                all_columns = [col[1] for col in self.cursor.fetchall() if col[1] != status_column]
                
                # Создаем новую таблицу
                columns_sql = ", ".join([f"{col} INTEGER" if col == temp_column else "BLOB" for col in all_columns])
                self.cursor.execute(f"CREATE TABLE {table_name}_new ({columns_sql})")
                
                # Копируем данные
                columns_str = ", ".join(all_columns)
                self.cursor.execute(f"INSERT INTO {table_name}_new ({columns_str}) SELECT {columns_str} FROM {table_name}")
                
                # Удаляем старую таблицу и переименовываем новую
                self.cursor.execute(f"DROP TABLE {table_name}")
                self.cursor.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
                
                # Переименовываем столбец
                self.cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN {temp_column} TO {status_column}")
                
            else:  # postgres
                # PostgreSQL поддерживает DROP COLUMN и RENAME COLUMN
                self.cursor.execute(
                    sql.SQL("ALTER TABLE {} DROP COLUMN {}").format(
                        sql.Identifier(table_name),
                        sql.Identifier(status_column)
                    )
                )
                self.cursor.execute(
                    sql.SQL("ALTER TABLE {} RENAME COLUMN {} TO {}").format(
                        sql.Identifier(table_name),
                        sql.Identifier(temp_column),
                        sql.Identifier(status_column)
                    )
                )
            
            # Проверяем, сколько записей стало после обновления
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            new_total = self.cursor.fetchone()[0]
            
            print(f"Нормализация завершена. Было {total_records} записей, стало {new_total} записей.")
            print(f"Рабочих ячеек: {self.count_working_cells(table_name, status_column)}")
            
            # Сохраняем изменения
            self.conn.commit()
            return True
        
        except Exception as e:
            print(f"Ошибка при нормализации статуса: {e}")
            import traceback
            traceback.print_exc()
            # Отменяем изменения
            self.conn.rollback()
            return False
    
    def count_working_cells(self, table_name, status_column):
        """Подсчет количества рабочих ячеек"""
        try:
            if self.db_type == 'sqlite':
                self.cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {status_column} = 1")
            else:  # postgres
                self.cursor.execute(
                    sql.SQL("SELECT COUNT(*) FROM {} WHERE {} = 1").format(
                        sql.Identifier(table_name),
                        sql.Identifier(status_column)
                    )
                )
            return self.cursor.fetchone()[0]
        except Exception as e:
            print(f"Ошибка при подсчете рабочих ячеек: {e}")
            return 0

def main():
    """Основная функция для запуска из командной строки"""
    if len(sys.argv) < 2:
        print("Использование: python DB_man.py [sqlite|postgres] [файл_БД или строка_подключения]")
        print("Например: python DB_man.py sqlite mydatabase.db")
        print("Или: python DB_man.py postgres 'host=localhost dbname=mydb user=postgres password=pass'")
        return
    
    db_type = sys.argv[1].lower()
    
    if db_type == 'sqlite':
        if len(sys.argv) < 3:
            print("Не указан файл SQLite базы данных")
            return
        db_file = sys.argv[2]
        postgres_conn_string = None
    elif db_type == 'postgres':
        if len(sys.argv) < 3:
            print("Не указана строка подключения к PostgreSQL")
            return
        db_file = None
        postgres_conn_string = sys.argv[2]
    else:
        print(f"Неподдерживаемый тип БД: {db_type}")
        return
    
    normalizer = DBNormalizer(db_file, db_type, postgres_conn_string)
    
    if normalizer.connect():
        try:
            # Нормализуем таблицу cells
            normalizer.normalize_status_column('cells')
        finally:
            normalizer.disconnect()

if __name__ == "__main__":
    main() 