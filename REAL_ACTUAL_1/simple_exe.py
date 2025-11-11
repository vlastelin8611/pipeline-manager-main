#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простая сборка exe без добавления файлов данных
Модули должны быть в той же папке что и exe
"""

import os
import subprocess
import sys
import shutil

def simple_build():
    """Простая сборка exe"""
    print("=== ПРОСТАЯ СБОРКА EXE ===\n")
    
    # Проверяем pyinstaller
    try:
        subprocess.run(['pyinstaller', '--version'], check=True, capture_output=True)
        print("✅ PyInstaller доступен")
    except:
        print("❌ PyInstaller не найден")
        return False
    
    # Очищаем старые папки
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    
    print("Собираем главное приложение...")
    
    # Простая команда без добавления файлов
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=MonOilStudy',
        'MonOilStudy_portable.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("✅ Главное приложение собрано!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    print("Собираем менеджер БД...")
    
    cmd_db = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=DB_Manager',
        'DB man.py'
    ]
    
    try:
        subprocess.run(cmd_db, check=True)
        print("✅ Менеджер БД собран!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка: {e}")
        return False
    
    # Создаем папку для готовой системы
    final_dir = "MonOilStudy_EXE_Ready"
    if os.path.exists(final_dir):
        shutil.rmtree(final_dir)
    os.makedirs(final_dir)
    
    # Копируем exe файлы
    shutil.copy('dist/MonOilStudy.exe', final_dir)
    shutil.copy('dist/DB_Manager.exe', final_dir)
    print("✅ Exe файлы скопированы")
    
    # Копируем ВСЕ модули рядом с exe
    module_count = 0
    for i in range(1, 10):
        module_file = f'module{i}.py'
        if os.path.exists(module_file):
            shutil.copy(module_file, final_dir)
            module_count += 1
    print(f"✅ Скопировано модулей: {module_count}")
    
    # Копируем базы данных
    db_count = 0
    for file in os.listdir('.'):
        if file.endswith('.db'):
            shutil.copy(file, final_dir)
            db_count += 1
    print(f"✅ Скопировано БД: {db_count}")
    
    # Создаем папку reports
    reports_dir = os.path.join(final_dir, 'reports')
    os.makedirs(reports_dir, exist_ok=True)
    
    # Копируем отчеты
    if os.path.exists('reports'):
        report_count = 0
        for file in os.listdir('reports'):
            if file.endswith('.txt'):
                shutil.copy(os.path.join('reports', file), reports_dir)
                report_count += 1
        print(f"✅ Скопировано отчетов: {report_count}")
    
    # Создаем bat файлы
    main_bat = '''@echo off
cd /d "%~dp0"
echo Запуск системы мониторинга нефтепровода...
MonOilStudy.exe
if %errorlevel% neq 0 (
    echo Ошибка запуска. Проверьте наличие всех файлов.
    pause
)
'''
    
    db_bat = '''@echo off
cd /d "%~dp0"
echo Запуск менеджера БД...
DB_Manager.exe
if %errorlevel% neq 0 (
    echo Ошибка запуска менеджера БД.
    pause
)
'''
    
    with open(os.path.join(final_dir, 'Запуск_мониторинга.bat'), 'w', encoding='cp1251') as f:
        f.write(main_bat)
    
    with open(os.path.join(final_dir, 'Запуск_менеджера_БД.bat'), 'w', encoding='cp1251') as f:
        f.write(db_bat)
    
    # README
    readme = """=== ГОТОВАЯ EXE СИСТЕМА МОНИТОРИНГА НЕФТЕПРОВОДА ===

ЗАПУСК:
• Запуск_мониторинга.bat - основная программа
• Запуск_менеджера_БД.bat - управление базами данных

ФАЙЛЫ:
• MonOilStudy.exe - основная программа
• DB_Manager.exe - менеджер БД
• module1.py - module9.py - модули системы (9 штук)
• *.db - базы данных
• reports/ - папка отчетов

ВАЖНО:
• Все модули должны быть в той же папке что и exe!
• НЕ перемещайте файлы по отдельности
• Копируйте всю папку целиком

СИСТЕМНЫЕ ТРЕБОВАНИЯ:
• Windows 7/8/10/11
• Не требует установки Python

ТЕХПОДДЕРЖКА: Зубенко Михаил Петрович
"""
    
    with open(os.path.join(final_dir, 'ПРОЧТИ_МЕНЯ.txt'), 'w', encoding='utf-8') as f:
        f.write(readme)
    
    print(f"\n=== ГОТОВО! ===")
    print(f"📁 Готовая система: {final_dir}")
    print("📋 Содержимое:")
    print("• MonOilStudy.exe + DB_Manager.exe")
    print("• Все 9 модулей рядом с exe")
    print("• Все базы данных")
    print("• Папка reports с отчетами")
    print("• Bat-файлы для запуска")
    print("\n🚀 Для запуска: Запуск_мониторинга.bat")
    print("✅ Готово к использованию!")
    
    return True

if __name__ == "__main__":
    simple_build() 