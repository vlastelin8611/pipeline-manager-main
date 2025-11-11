#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ПРАВИЛЬНАЯ сборка exe на основе актуальной версии системы
"""

import os
import subprocess
import sys
import shutil

def install_required_packages():
    """Установка необходимых пакетов"""
    packages = ['pyinstaller', 'PyQt5']
    
    for package in packages:
        try:
            __import__(package.replace('-', '_').lower())
            print(f"✅ {package} уже установлен")
        except ImportError:
            print(f"Устанавливаем {package}...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} установлен")
            except subprocess.CalledProcessError:
                print(f"❌ Не удалось установить {package}")
                return False
    return True

def prepare_for_exe():
    """Подготовка файлов для компиляции в exe"""
    print("Подготавливаем файлы для exe...")
    
    # Проверяем наличие портативной версии
    if not os.path.exists('MonOilStudy_portable.py'):
        print("❌ Сначала запустите build_correct.py для создания портативной версии")
        return False
    
    # Проверяем наличие всех модулей
    missing_modules = []
    for i in range(1, 10):
        module_file = f'module{i}.py'
        if not os.path.exists(module_file):
            missing_modules.append(module_file)
    
    if missing_modules:
        print(f"❌ Отсутствуют модули: {missing_modules}")
        return False
    
    print("✅ Все файлы готовы для сборки")
    return True

def build_main_app_exe():
    """Сборка главного приложения в exe"""
    print("Собираем главное приложение в exe...")
    
    # Команда для PyInstaller
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=MonOilStudy',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=build',
        # Добавляем все модули как дополнительные файлы
        '--add-data=module1.py;.',
        '--add-data=module2.py;.',
        '--add-data=module3.py;.',
        '--add-data=module4.py;.',
        '--add-data=module5.py;.',
        '--add-data=module6.py;.',
        '--add-data=module7.py;.',
        '--add-data=module8.py;.',
        '--add-data=module9.py;.',
        # Добавляем базы данных
        '--add-data=*.db;.',
        'MonOilStudy_portable.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Главное приложение собрано!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сборке главного приложения: {e}")
        return False

def build_db_manager_exe():
    """Сборка менеджера БД в exe"""
    print("Собираем менеджер БД в exe...")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=DB_Manager',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=build',
        # Добавляем базы данных и инструкции
        '--add-data=*.db;.',
        '--add-data=db_instructions.txt;.',
        'DB man.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Менеджер БД собран!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сборке менеджера БД: {e}")
        return False

def create_exe_distribution():
    """Создание дистрибутива с exe"""
    print("Создаем дистрибутив с exe...")
    
    dist_dir = "MonOilStudy_EXE_Distribution"
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    os.makedirs(dist_dir)
    
    # Копируем exe файлы
    exe_files = ['MonOilStudy.exe', 'DB_Manager.exe']
    for exe_file in exe_files:
        exe_path = os.path.join('dist', exe_file)
        if os.path.exists(exe_path):
            shutil.copy(exe_path, dist_dir)
            print(f"✅ Скопирован: {exe_file}")
        else:
            print(f"❌ Не найден: {exe_file}")
    
    # Копируем базы данных
    db_count = 0
    for file in os.listdir('.'):
        if file.endswith('.db'):
            shutil.copy(file, dist_dir)
            db_count += 1
    print(f"✅ Скопировано БД: {db_count}")
    
    # Создаем папку reports
    reports_dist = os.path.join(dist_dir, 'reports')
    os.makedirs(reports_dist, exist_ok=True)
    
    # Копируем отчеты
    if os.path.exists('reports'):
        report_count = 0
        for file in os.listdir('reports'):
            if file.endswith('.txt'):
                shutil.copy(os.path.join('reports', file), reports_dist)
                report_count += 1
        print(f"✅ Скопировано отчетов: {report_count}")
    
    # Создаем bat-файлы для exe
    exe_launcher_main = '''@echo off
cd /d "%~dp0"
echo Запуск системы мониторинга нефтепровода (EXE)...
MonOilStudy.exe
if %errorlevel% neq 0 (
    echo Произошла ошибка при запуске программы.
    pause
)
'''
    
    exe_launcher_db = '''@echo off
cd /d "%~dp0"
echo Запуск менеджера БД (EXE)...
DB_Manager.exe
if %errorlevel% neq 0 (
    echo Произошла ошибка при запуске менеджера БД.
    pause
)
'''
    
    with open(os.path.join(dist_dir, 'run_monitor_exe.bat'), 'w', encoding='cp1251') as f:
        f.write(exe_launcher_main)
    
    with open(os.path.join(dist_dir, 'run_db_manager_exe.bat'), 'w', encoding='cp1251') as f:
        f.write(exe_launcher_db)
    
    # Создаем README для exe версии
    readme_exe = """=== EXE ВЕРСИЯ СИСТЕМЫ МОНИТОРИНГА НЕФТЕПРОВОДА ===

ОСОБЕННОСТИ EXE ВЕРСИИ:
- Не требует установки Python
- Все модули встроены в exe файл
- Готова к работе сразу после распаковки

ЗАПУСК:
- run_monitor_exe.bat - основная программа мониторинга
- run_db_manager_exe.bat - программа управления БД

ФАЙЛЫ:
- MonOilStudy.exe - основная программа (включает все модули)
- DB_Manager.exe - менеджер баз данных
- *.db - файлы баз данных
- reports/ - папка с отчетами

ПРЕИМУЩЕСТВА:
- Быстрый запуск
- Не зависит от Python окружения
- Портативность
- Все в одном файле

СИСТЕМНЫЕ ТРЕБОВАНИЯ:
- Windows 7/8/10/11
- Минимум 1 ГБ RAM
- 100 МБ свободного места

ТЕХПОДДЕРЖКА: Зубенко Михаил Петрович
"""
    
    with open(os.path.join(dist_dir, 'README_EXE.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_exe)
    
    print(f"✅ EXE дистрибутив создан: {dist_dir}")
    return dist_dir

def main():
    """Основная функция сборки exe"""
    print("=== СБОРКА EXE ВЕРСИИ АКТУАЛЬНОЙ СИСТЕМЫ ===\n")
    
    # Проверяем и устанавливаем пакеты
    if not install_required_packages():
        print("❌ Не удалось установить необходимые пакеты")
        return False
    
    # Подготавливаем файлы
    if not prepare_for_exe():
        return False
    
    # Собираем exe файлы
    main_success = build_main_app_exe()
    db_success = build_db_manager_exe()
    
    if main_success and db_success:
        # Создаем дистрибутив
        dist_dir = create_exe_distribution()
        
        print("\n=== EXE СБОРКА ЗАВЕРШЕНА УСПЕШНО! ===")
        print(f"\n✅ EXE версия готова: {dist_dir}")
        print("\n📦 Содержимое:")
        print("- MonOilStudy.exe (основная программа с модулями)")
        print("- DB_Manager.exe (менеджер БД)")
        print("- run_monitor_exe.bat (запуск основной программы)")
        print("- run_db_manager_exe.bat (запуск менеджера БД)")
        print("- *.db (базы данных)")
        print("- reports/ (папка отчетов)")
        print("- README_EXE.txt (инструкции)")
        
        print(f"\n🚀 Для запуска: run_monitor_exe.bat в папке {dist_dir}")
        print("🎯 EXE версия не требует установки Python!")
        
        return True
    else:
        print("\n❌ Сборка exe завершилась с ошибками!")
        if not main_success:
            print("- Не удалось собрать основную программу")
        if not db_success:
            print("- Не удалось собрать менеджер БД")
        return False

if __name__ == "__main__":
    main() 