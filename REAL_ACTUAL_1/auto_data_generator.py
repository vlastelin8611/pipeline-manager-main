import sqlite3
import random
import time
import threading

class DataGenerator:
    def __init__(self, db_path='new_database.db'):
        self.db_path = db_path
        self.running = False
        self.thread = None
        
    def start(self, interval=5):
        """Запускает генератор данных с указанным интервалом (в секундах)"""
        if self.running:
            print("Генератор уже запущен")
            return
            
        self.running = True
        self.interval = interval
        self.thread = threading.Thread(target=self._generate_loop)
        self.thread.daemon = True
        self.thread.start()
        print(f"Генератор данных запущен с интервалом {interval} секунд")
        
    def stop(self):
        """Останавливает генератор данных"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("Генератор данных остановлен")
        
    def _generate_loop(self):
        """Основной цикл генерации данных"""
        while self.running:
            try:
                self._update_data()
                time.sleep(self.interval)
            except Exception as e:
                print(f"Ошибка в генераторе: {e}")
                time.sleep(1)
                
    def _update_data(self):
        """Обновляет данные в БД"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Получаем текущие данные
            cursor.execute('''
                SELECT cell_pressure, cell_temperature, cell_pumping_speed, 
                       cell_vibrations, cell_tilt_angle, outdoor_temperature, 
                       outdoor_pressure, outdoor_wind, outdoor_humidity 
                FROM raw_data ORDER BY id DESC LIMIT 1
            ''')
            current = cursor.fetchone()
            
            if current:
                # Генерируем новые значения с небольшими изменениями
                new_pressure = max(40.0, min(60.0, current[0] + random.uniform(-0.5, 0.5)))
                new_temperature = max(15.0, min(25.0, current[1] + random.uniform(-0.3, 0.3)))
                new_pumping_speed = max(3.0, min(7.0, current[2] + random.uniform(-0.2, 0.2)))
                new_vibrations = max(0.01, min(0.2, current[3] + random.uniform(-0.02, 0.02)))
                new_tilt_angle = max(8.0, min(12.0, current[4] + random.uniform(-0.2, 0.2)))
                
                # Данные окружающей среды
                new_outdoor_temp = max(-5.0, min(35.0, current[5] + random.uniform(-0.5, 0.5)))
                new_outdoor_pressure = max(99.0, min(103.0, current[6] + random.uniform(-0.1, 0.1)))
                new_wind = max(0.0, min(10.0, current[7] + random.uniform(-0.3, 0.3)))
                new_humidity = max(30.0, min(90.0, current[8] + random.uniform(-1.0, 1.0)))
                
                # Обновляем данные
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute('''
                    UPDATE raw_data 
                    SET cell_pressure = ?, 
                        cell_temperature = ?, 
                        cell_pumping_speed = ?, 
                        cell_vibrations = ?, 
                        cell_tilt_angle = ?,
                        outdoor_temperature = ?,
                        outdoor_pressure = ?,
                        outdoor_wind = ?,
                        outdoor_humidity = ?,
                        timestamp = ?
                    WHERE id = (SELECT MAX(id) FROM raw_data)
                ''', (new_pressure, new_temperature, new_pumping_speed, new_vibrations, 
                      new_tilt_angle, new_outdoor_temp, new_outdoor_pressure, new_wind, 
                      new_humidity, timestamp))
                
                conn.commit()
                print(f"[{timestamp}] Обновлено: P={new_pressure:.2f}, T={new_temperature:.2f}, S={new_pumping_speed:.2f}")
                
            conn.close()
            
        except Exception as e:
            print(f"Ошибка обновления данных: {e}")

def main():
    generator = DataGenerator()
    
    try:
        generator.start(interval=3)  # Обновление каждые 3 секунды
        
        print("Генератор запущен. Нажмите Ctrl+C для остановки...")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nПолучен сигнал остановки...")
        generator.stop()
        print("Программа завершена")

if __name__ == "__main__":
    main() 