#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Простой скрипт для сборки exe-файлов системы мониторинга нефтепровода
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
            __import__(package)
            print(f"{package} уже установлен")
        except ImportError:
            print(f"Устанавливаем {package}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def prepare_main_app():
    """Подготовка главного приложения для exe"""
    print("Готовим главное приложение...")
    
    # Читаем оригинальный файл
    with open('MonOilStudy.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Функция для определения пути exe
    exe_path_code = '''
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
        content = content[:import_end] + '\n' + exe_path_code + content[import_end:]
    
    # Модифицируем ReportDatabase для работы с exe
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
    
    # В главном приложении нет создания txt файлов, они только в модулях
    # Поэтому не нужно ничего дополнительно патчить
    
    # Сохраняем модифицированную версию
    with open('MonOilStudy_exe.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Создана exe-версия MonOilStudy_exe.py")

def build_main_app():
    """Сборка главного приложения"""
    print("Собираем главное приложение...")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=MonOilStudy',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=build',
        'MonOilStudy_exe.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Главное приложение собрано успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при сборке главного приложения: {e}")
        return False

def build_db_manager():
    """Сборка менеджера БД"""
    print("Собираем менеджер БД...")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=DB_Manager',
        '--distpath=dist',
        '--workpath=build',
        '--specpath=build',
        'DB man.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("Менеджер БД собран успешно!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при сборке менеджера БД: {e}")
        return False

def copy_required_files():
    """Копирование необходимых файлов в dist"""
    print("Копируем необходимые файлы...")
    
    if not os.path.exists('dist'):
        os.makedirs('dist')
    
    # Копируем базы данных
    for file in os.listdir('.'):
        if file.endswith('.db'):
            try:
                shutil.copy(file, 'dist/')
                print(f"Скопирован: {file}")
            except:
                pass
    
    # Копируем инструкции для БД
    if os.path.exists('db_instructions.txt'):
        try:
            shutil.copy('db_instructions.txt', 'dist/')
            print("Скопированы инструкции БД")
        except:
            pass
    
    # Создаем папку reports в dist
    reports_dist = os.path.join('dist', 'reports')
    if not os.path.exists(reports_dist):
        os.makedirs(reports_dist)
        print("Создана папка reports в dist")
    
    # Копируем существующие отчеты если есть
    if os.path.exists('reports'):
        try:
            for file in os.listdir('reports'):
                if file.endswith('.txt'):
                    shutil.copy(os.path.join('reports', file), reports_dist)
            print("Скопированы существующие отчеты")
        except:
            pass

def cleanup():
    """Очистка временных файлов"""
    print("Очищаем временные файлы...")
    
    # Удаляем временную exe-версию
    if os.path.exists('MonOilStudy_exe.py'):
        os.remove('MonOilStudy_exe.py')
    
    # Удаляем папку build если есть
    if os.path.exists('build'):
        try:
            shutil.rmtree('build')
        except:
            pass

def main():
    """Основная функция сборки"""
    print("=== СБОРКА EXE-ФАЙЛОВ СИСТЕМЫ МОНИТОРИНГА НЕФТЕПРОВОДА ===\n")
    
    # Устанавливаем пакеты
    install_required_packages()
    
    # Подготавливаем файлы
    prepare_main_app()
    
    success = True
    
    # Собираем приложения
    if not build_main_app():
        success = False
    
    if not build_db_manager():
        success = False
    
    if success:
        # Копируем файлы
        copy_required_files()
        
        print("\n=== СБОРКА ЗАВЕРШЕНА УСПЕШНО! ===")
        print("\nСозданные exe-файлы:")
        print("📁 dist/MonOilStudy.exe - основная программа мониторинга")
        print("📁 dist/DB_Manager.exe - программа управления БД")
        print("\n📋 Инструкции:")
        print("1. Скопируйте всю папку 'dist' в нужное место")
        print("2. Запускайте exe-файлы прямо из этой папки")
        print("3. Папка 'reports' будет создана автоматически рядом с exe")
        print("4. Базы данных уже скопированы в папку dist")
        
    else:
        print("\n❌ Сборка завершилась с ошибками!")
    
    # Очищаем временные файлы
    cleanup()
    
    return success

if __name__ == "__main__":
    main() 