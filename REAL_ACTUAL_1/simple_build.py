#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая сборка exe без PyInstaller - создание готовых скриптов для запуска
"""

import os
import shutil
import subprocess
import sys

def create_launcher_scripts():
    """Создание скриптов-запускателей"""
    print("Создаем скрипты-запускатели...")
    
    # Скрипт запуска главного приложения
    main_launcher = '''@echo off
cd /d "%~dp0"
echo Запуск системы мониторинга нефтепровода...
python MonOilStudy_portable.py
if %errorlevel% neq 0 (
    echo Ошибка запуска! Убедитесь что Python установлен.
    pause
)
'''
    
    # Скрипт запуска менеджера БД
    db_launcher = '''@echo off
cd /d "%~dp0"
echo Запуск менеджера баз данных...
python "DB man.py"
if %errorlevel% neq 0 (
    echo Ошибка запуска! Убедитесь что Python и PyQt5 установлены.
    echo Для установки PyQt5 выполните: pip install PyQt5
    pause
)
'''
    
    with open('run_monitor.bat', 'w', encoding='cp1251') as f:
        f.write(main_launcher)
    
    with open('run_db_manager.bat', 'w', encoding='cp1251') as f:
        f.write(db_launcher)
    
    print("Созданы скрипты запуска:")
    print("- run_monitor.bat")
    print("- run_db_manager.bat")

def prepare_portable_version():
    """Подготовка портативной версии главного приложения"""
    print("Готовим портативную версию...")
    
    # Читаем АКТУАЛЬНЫЙ файл
    with open('MonOilStudy test.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Функция для определения пути приложения
    portable_path_code = '''
import sys
import os

def get_application_path():
    """Получает путь к директории приложения"""
    return os.path.dirname(os.path.abspath(__file__))
'''
    
    # Вставляем функцию после импортов, перед первым классом
    import_end = content.find('\nclass')
    if import_end != -1:
        content = content[:import_end] + '\n' + portable_path_code + content[import_end:]
    
    # Модифицируем ReportDatabase для работы с локальными путями
    old_db_init = '''    def __init__(self):
        self.db_filename = "reports_db.pkl"
        self.reports = []

        if not os.path.exists(self.db_filename):
            self._save_db()

        self._load_db()'''
    
    new_db_init = '''    def __init__(self):
        app_path = get_application_path()
        self.db_filename = os.path.join(app_path, "reports_db.pkl")
        self.reports_dir = os.path.join(app_path, "reports")
        self.reports = []

        # Создаем папку reports если её нет
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)

        if not os.path.exists(self.db_filename):
            self._save_db()

        self._load_db()'''
    
    content = content.replace(old_db_init, new_db_init)
    
    # Сохраняем портативную версию
    with open('MonOilStudy_portable.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Создана портативная версия: MonOilStudy_portable.py")

def create_distribution():
    """Создание готовой сборки"""
    print("Создаем дистрибутив...")
    
    # Создаем папку дистрибутива
    dist_dir = "MonOilStudy_Distribution"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Копируем основные файлы
    files_to_copy = [
        'MonOilStudy_portable.py',
        'DB man.py',
        'run_monitor.bat',
        'run_db_manager.bat'
    ]
    
    for file in files_to_copy:
        if os.path.exists(file):
            shutil.copy(file, dist_dir)
            print(f"Скопирован: {file}")
    
    # Копируем базы данных
    for file in os.listdir('.'):
        if file.endswith('.db'):
            shutil.copy(file, dist_dir)
            print(f"Скопирована БД: {file}")
    
    # Копируем инструкции
    if os.path.exists('db_instructions.txt'):
        shutil.copy('db_instructions.txt', dist_dir)
        print("Скопированы инструкции БД")
    
    # Создаем папку reports
    reports_dist = os.path.join(dist_dir, 'reports')
    os.makedirs(reports_dist, exist_ok=True)
    
    # Копируем существующие отчеты
    if os.path.exists('reports'):
        for file in os.listdir('reports'):
            if file.endswith('.txt'):
                shutil.copy(os.path.join('reports', file), reports_dist)
        print("Скопированы отчеты")
    
    # Создаем README
    readme_content = """=== СИСТЕМА МОНИТОРИНГА НЕФТЕПРОВОДА ===

УСТАНОВКА И ЗАПУСК:

1. ТРЕБОВАНИЯ:
   - Python 3.7 или выше
   - Для менеджера БД: PyQt5 (pip install PyQt5)

2. ЗАПУСК:
   - run_monitor.bat - запуск основной программы мониторинга
   - run_db_manager.bat - запуск программы управления БД

3. ФАЙЛЫ:
   - MonOilStudy_portable.py - основная программа мониторинга
   - DB man.py - программа управления базами данных
   - *.db - файлы баз данных
   - reports/ - папка с отчетами (создается автоматически)

4. ОСОБЕННОСТИ:
   - Папка reports создается автоматически рядом с программой
   - Все данные сохраняются в той же папке где находится программа
   - Программа полностью портативная

5. ПРОБЛЕМЫ:
   - Если не запускается - проверьте установку Python
   - Если не работает менеджер БД - установите PyQt5: pip install PyQt5

ТЕХПОДДЕРЖКА: Зубенко Михаил Петрович, оператор промежуточной станции
"""
    
    with open(os.path.join(dist_dir, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"Дистрибутив создан в папке: {dist_dir}")
    return dist_dir

def try_pyinstaller_build():
    """Попытка создания exe через PyInstaller если доступен"""
    try:
        import PyInstaller
        print("PyInstaller найден, пробуем создать exe...")
        
        # Собираем главное приложение
        cmd_main = [
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--name=MonOilStudy',
            'MonOilStudy_portable.py'
        ]
        
        subprocess.run(cmd_main, check=True, capture_output=True)
        print("Exe главного приложения создан!")
        
        # Собираем менеджер БД
        cmd_db = [
            'pyinstaller',
            '--onefile',
            '--windowed',
            '--name=DB_Manager',
            'DB man.py'
        ]
        
        subprocess.run(cmd_db, check=True, capture_output=True)
        print("Exe менеджера БД создан!")
        
        return True
        
    except (ImportError, subprocess.CalledProcessError, FileNotFoundError):
        print("PyInstaller недоступен или произошла ошибка")
        return False

def main():
    """Основная функция"""
    print("=== СБОРКА ПОРТАТИВНОЙ СИСТЕМЫ МОНИТОРИНГА НЕФТЕПРОВОДА ===\n")
    
    # Подготавливаем портативную версию
    prepare_portable_version()
    
    # Создаем скрипты запуска
    create_launcher_scripts()
    
    # Пробуем создать exe
    exe_created = try_pyinstaller_build()
    
    # Создаем дистрибутив
    dist_dir = create_distribution()
    
    if exe_created and os.path.exists('dist'):
        print("\nКопируем exe файлы в дистрибутив...")
        for file in os.listdir('dist'):
            if file.endswith('.exe'):
                shutil.copy(os.path.join('dist', file), dist_dir)
                print(f"Скопирован exe: {file}")
    
    print("\n=== СБОРКА ЗАВЕРШЕНА ===")
    print(f"\nГотовая система находится в папке: {dist_dir}")
    print("\nСодержимое:")
    print("📁 run_monitor.bat - запуск основной программы")
    print("📁 run_db_manager.bat - запуск менеджера БД")
    print("📁 MonOilStudy_portable.py - портативная версия")
    print("📁 DB man.py - менеджер баз данных")
    print("📁 *.db - базы данных")
    print("📁 reports/ - папка отчетов")
    print("📁 README.txt - инструкции")
    
    if exe_created:
        print("📁 *.exe - готовые исполняемые файлы")
    
    print(f"\nПросто скопируйте папку '{dist_dir}' куда нужно и запускайте программы!")

if __name__ == "__main__":
    main() 