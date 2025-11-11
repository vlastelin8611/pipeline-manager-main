#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка exe через Nuitka (альтернатива PyInstaller)
"""

import os
import subprocess
import sys

def check_nuitka():
    """Проверка доступности Nuitka"""
    try:
        subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_nuitka():
    """Установка Nuitka"""
    print("Устанавливаем Nuitka...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "nuitka"])
        return True
    except subprocess.CalledProcessError:
        print("Не удалось установить Nuitka через pip")
        return False

def build_with_nuitka():
    """Сборка через Nuitka"""
    print("=== СБОРКА ЧЕРЕЗ NUITKA ===\n")
    
    if not check_nuitka():
        print("Nuitka не найдена, пытаемся установить...")
        if not install_nuitka():
            print("❌ Не удалось установить Nuitka")
            return False
    
    print("✅ Nuitka доступна")
    
    # Подготавливаем файлы
    if not os.path.exists('MonOilStudy_portable.py'):
        print("❌ Файл MonOilStudy_portable.py не найден. Запустите сначала simple_build.py")
        return False
    
    try:
        # Сборка главного приложения
        print("Собираем главное приложение...")
        cmd_main = [
            sys.executable, "-m", "nuitka",
            "--onefile",
            "--windows-disable-console",
            "--output-filename=MonOilStudy.exe",
            "--output-dir=dist_nuitka",
            "MonOilStudy_portable.py"
        ]
        
        subprocess.run(cmd_main, check=True)
        print("✅ Главное приложение собрано!")
        
        # Сборка менеджера БД
        print("Собираем менеджер БД...")
        cmd_db = [
            sys.executable, "-m", "nuitka",
            "--onefile",
            "--windows-disable-console",
            "--output-filename=DB_Manager.exe",
            "--output-dir=dist_nuitka",
            "DB man.py"
        ]
        
        subprocess.run(cmd_db, check=True)
        print("✅ Менеджер БД собран!")
        
        # Копируем файлы в дистрибутив
        import shutil
        dist_dir = "MonOilStudy_Distribution"
        
        if os.path.exists(os.path.join("dist_nuitka", "MonOilStudy.exe")):
            shutil.copy(os.path.join("dist_nuitka", "MonOilStudy.exe"), dist_dir)
            print("✅ MonOilStudy.exe скопирован в дистрибутив")
        
        if os.path.exists(os.path.join("dist_nuitka", "DB_Manager.exe")):
            shutil.copy(os.path.join("dist_nuitka", "DB_Manager.exe"), dist_dir)
            print("✅ DB_Manager.exe скопирован в дистрибутив")
        
        # Создаем bat-файлы для exe
        exe_launcher_main = '''@echo off
cd /d "%~dp0"
echo Запуск системы мониторинга нефтепровода (EXE)...
MonOilStudy.exe
'''
        
        exe_launcher_db = '''@echo off
cd /d "%~dp0"
echo Запуск менеджера БД (EXE)...
DB_Manager.exe
'''
        
        with open(os.path.join(dist_dir, 'run_monitor_exe.bat'), 'w', encoding='cp1251') as f:
            f.write(exe_launcher_main)
        
        with open(os.path.join(dist_dir, 'run_db_manager_exe.bat'), 'w', encoding='cp1251') as f:
            f.write(exe_launcher_db)
        
        print("✅ Созданы bat-файлы для exe")
        
        print("\n=== СБОРКА NUITKA ЗАВЕРШЕНА ===")
        print("📁 EXE файлы добавлены в MonOilStudy_Distribution")
        print("📁 run_monitor_exe.bat - запуск exe основной программы")
        print("📁 run_db_manager_exe.bat - запуск exe менеджера БД")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при сборке: {e}")
        return False

def create_manual_instructions():
    """Создание инструкций для ручной сборки"""
    instructions = """=== РУЧНАЯ СБОРКА EXE ФАЙЛОВ ===

Если автоматическая сборка не работает, можете собрать вручную:

1. ЧЕРЕЗ PYINSTALLER:
   pip install pyinstaller
   pyinstaller --onefile --windowed --name=MonOilStudy MonOilStudy_portable.py
   pyinstaller --onefile --windowed --name=DB_Manager "DB man.py"

2. ЧЕРЕЗ NUITKA:
   pip install nuitka
   python -m nuitka --onefile --windows-disable-console MonOilStudy_portable.py
   python -m nuitka --onefile --windows-disable-console "DB man.py"

3. ЧЕРЕЗ CX_FREEZE:
   pip install cx_freeze
   cxfreeze MonOilStudy_portable.py --target-dir dist_cx
   cxfreeze "DB man.py" --target-dir dist_cx

4. ЧЕРЕЗ AUTO-PY-TO-EXE (GUI):
   pip install auto-py-to-exe
   auto-py-to-exe
   (выберите файлы в графическом интерфейсе)

ПОСЛЕ СБОРКИ:
- Скопируйте .exe файлы в папку MonOilStudy_Distribution
- Скопируйте также все .db файлы и папку reports
- Готово к использованию!
"""
    
    with open('РУЧНАЯ_СБОРКА.txt', 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("Созданы инструкции для ручной сборки: РУЧНАЯ_СБОРКА.txt")

if __name__ == "__main__":
    success = build_with_nuitka()
    if not success:
        print("\nСоздаем инструкции для ручной сборки...")
        create_manual_instructions() 