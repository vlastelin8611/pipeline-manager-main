#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРАВИЛЬНАЯ сборка портативной системы на основе актуальной версии
"""

import os
import shutil
import subprocess
import sys

def create_portable_main_app():
    """Создание портативной версии основного приложения"""
    print("Готовим портативную версию актуального приложения...")
    
    # Читаем АКТУАЛЬНЫЙ файл
    with open('MonOilStudy test.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Функция для определения пути приложения  
    portable_path_code = '''
import sys

def get_application_path():
    """Получает путь к директории приложения (exe или скрипт)"""
    if getattr(sys, 'frozen', False):
        # Если запущено как exe
        application_path = os.path.dirname(sys.executable)
    else:
        # Если запущено как скрипт
        application_path = os.path.dirname(os.path.abspath(__file__))
    return application_path
'''
    
    # Вставляем функцию после импортов, перед первым классом
    import_end = content.find('\nclass')
    if import_end != -1:
        content = content[:import_end] + '\n' + portable_path_code + content[import_end:]
    
    # Сохраняем портативную версию
    with open('MonOilStudy_portable.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Создана портативная версия: MonOilStudy_portable.py")

def copy_modules():
    """Копирование всех модулей"""
    print("Копируем модули...")
    
    modules = []
    for i in range(1, 10):
        module_file = f'module{i}.py'
        if os.path.exists(module_file):
            modules.append(module_file)
    
    print(f"Найдено модулей: {len(modules)}")
    return modules

def create_launcher_scripts():
    """Создание скриптов-запускателей"""
    print("Создаем скрипты запуска...")
    
    # Скрипт запуска главного приложения
    main_launcher = '''@echo off
cd /d "%~dp0"
echo Запуск актуальной системы мониторинга нефтепровода...
python MonOilStudy_portable.py
if %errorlevel% neq 0 (
    echo Ошибка запуска! Убедитесь что Python установлен.
    echo Также проверьте наличие всех модулей (module1.py - module9.py)
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
    
    print("✅ Созданы скрипты запуска")

def create_distribution():
    """Создание правильного дистрибутива"""
    print("Создаем правильный дистрибутив...")
    
    # Создаем папку дистрибутива
    dist_dir = "MonOilStudy_Distribution"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Копируем основные файлы
    main_files = [
        'MonOilStudy_portable.py',
        'DB man.py',
        'run_monitor.bat',
        'run_db_manager.bat'
    ]
    
    for file in main_files:
        if os.path.exists(file):
            shutil.copy(file, dist_dir)
            print(f"✅ Скопирован: {file}")
    
    # Копируем ВСЕ модули
    modules_copied = 0
    for i in range(1, 10):
        module_file = f'module{i}.py'
        if os.path.exists(module_file):
            shutil.copy(module_file, dist_dir)
            print(f"✅ Скопирован модуль: {module_file}")
            modules_copied += 1
    
    print(f"✅ Всего скопировано модулей: {modules_copied}")
    
    # Копируем базы данных
    db_count = 0
    for file in os.listdir('.'):
        if file.endswith('.db'):
            shutil.copy(file, dist_dir)
            print(f"✅ Скопирована БД: {file}")
            db_count += 1
    
    print(f"✅ Всего скопировано БД: {db_count}")
    
    # Копируем дополнительные файлы
    extra_files = ['db_instructions.txt']
    for file in extra_files:
        if os.path.exists(file):
            shutil.copy(file, dist_dir)
            print(f"✅ Скопирован: {file}")
    
    # Создаем папку reports
    reports_dist = os.path.join(dist_dir, 'reports')
    os.makedirs(reports_dist, exist_ok=True)
    
    # Копируем существующие отчеты
    if os.path.exists('reports'):
        report_count = 0
        for file in os.listdir('reports'):
            if file.endswith('.txt'):
                shutil.copy(os.path.join('reports', file), reports_dist)
                report_count += 1
        print(f"✅ Скопировано отчетов: {report_count}")
    
    # Создаем README
    readme_content = """=== АКТУАЛЬНАЯ СИСТЕМА МОНИТОРИНГА НЕФТЕПРОВОДА ===

УСТАНОВКА И ЗАПУСК:

1. ТРЕБОВАНИЯ:
   - Python 3.7 или выше
   - Для менеджера БД: PyQt5 (pip install PyQt5)

2. ЗАПУСК:
   - run_monitor.bat - запуск основной программы мониторинга
   - run_db_manager.bat - запуск программы управления БД

3. ФАЙЛЫ:
   - MonOilStudy_portable.py - основная программа (актуальная версия)
   - DB man.py - программа управления базами данных
   - module1.py - module9.py - модули системы
   - *.db - файлы баз данных
   - reports/ - папка с отчетами

4. ОСОБЕННОСТИ:
   - Включает ВСЕ 9 модулей системы
   - Модульная архитектура с системой авторизации
   - Автоматическое подключение к БД
   - Полная система мониторинга

5. МОДУЛИ:
   - Модуль 1: Визуализация ячеек трубопровода
   - Модуль 2: Графики и диаграммы
   - Модуль 3: Система отчетов
   - Модуль 4: Авторизация пользователей
   - Модуль 5: Контроль параметров
   - Модуль 6: Просмотр отчетов
   - Модуль 7: Мониторинг состояния БД  
   - Модуль 8: Выбор БД
   - Модуль 9: Подключение к БД

6. ПРОБЛЕМЫ:
   - Если не запускается - проверьте Python и наличие всех модулей
   - Если модуль не работает - проверьте файлы module1.py-module9.py
   - Для БД менеджера нужен PyQt5: pip install PyQt5

ТЕХПОДДЕРЖКА: Зубенко Михаил Петрович, оператор промежуточной станции
"""
    
    with open(os.path.join(dist_dir, 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"✅ Дистрибутив создан в папке: {dist_dir}")
    return dist_dir

def test_distribution(dist_dir):
    """Тестирование созданного дистрибутива"""
    print("\nПроверяем содержимое дистрибутива...")
    
    required_files = [
        'MonOilStudy_portable.py',
        'DB man.py',
        'run_monitor.bat',
        'run_db_manager.bat',
        'README.txt'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(os.path.join(dist_dir, file)):
            missing_files.append(file)
    
    # Проверяем модули
    missing_modules = []
    for i in range(1, 10):
        module_file = f'module{i}.py'
        if not os.path.exists(os.path.join(dist_dir, module_file)):
            missing_modules.append(module_file)
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {missing_files}")
        return False
    
    if missing_modules:
        print(f"⚠️ Отсутствуют модули: {missing_modules}")
        print("Это может вызвать ошибки при запуске!")
    
    print("✅ Основные файлы на месте")
    
    # Проверяем наличие БД
    db_files = [f for f in os.listdir(dist_dir) if f.endswith('.db')]
    print(f"✅ Найдено БД файлов: {len(db_files)}")
    
    return True

def main():
    """Основная функция правильной сборки"""
    print("=== ПРАВИЛЬНАЯ СБОРКА АКТУАЛЬНОЙ СИСТЕМЫ МОНИТОРИНГА ===\n")
    
    # Проверяем наличие актуального файла
    if not os.path.exists('MonOilStudy test.py'):
        print("❌ Файл 'MonOilStudy test.py' не найден!")
        return False
    
    # Подготавливаем портативную версию
    create_portable_main_app()
    
    # Создаем скрипты запуска
    create_launcher_scripts()
    
    # Создаем дистрибутив
    dist_dir = create_distribution()
    
    # Тестируем дистрибутив
    if test_distribution(dist_dir):
        print("\n=== ПРАВИЛЬНАЯ СБОРКА ЗАВЕРШЕНА ===")
        print(f"\n✅ Готовая актуальная система: {dist_dir}")
        print("\n📋 Содержимое:")
        print("- MonOilStudy_portable.py (актуальная версия с модулями)")
        print("- module1.py - module9.py (все модули системы)")
        print("- DB man.py (менеджер БД)")
        print("- *.db (базы данных)")
        print("- .bat файлы для запуска")
        print("- README.txt с инструкциями")
        
        print(f"\n🚀 ЗАПУСК: cd {dist_dir} && run_monitor.bat")
        return True
    else:
        print("\n❌ Сборка завершилась с ошибками!")
        return False

if __name__ == "__main__":
    main() 