#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для сборки exe-файлов системы мониторинга нефтепровода
"""

import os
import subprocess
import sys

def install_pyinstaller():
    """Установка PyInstaller если не установлен"""
    try:
        import PyInstaller
        print("PyInstaller уже установлен")
    except ImportError:
        print("Устанавливаем PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def create_main_app_spec():
    """Создание spec файла для главного приложения"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['MonOilStudy.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('reports', 'reports'),
        ('*.db', '.'),
        ('*.pkl', '.'),
        ('*.txt', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'pickle',
        'datetime',
        'os',
        'random'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MonOilStudy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
'''
    
    with open('MonOilStudy.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("Создан MonOilStudy.spec")

def create_db_manager_spec():
    """Создание spec файла для управления БД"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['DB man.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('*.db', '.'),
        ('db_instructions.txt', '.'),
    ],
    hiddenimports=[
        'PyQt5',
        'PyQt5.QtWidgets',
        'PyQt5.QtCore',
        'sqlite3',
        'sys',
        'os',
        'time',
        'random'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DB_Manager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None
)
'''
    
    with open('DB_Manager.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    print("Создан DB_Manager.spec")

def patch_reports_path():
    """Патчим главное приложение для правильной работы с путями в exe"""
    # Читаем оригинальный файл
    with open('MonOilStudy.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Добавляем функцию для определения пути к exe
    path_detection = '''
import sys

def get_exe_dir():
    """Получает директорию exe файла"""
    if getattr(sys, 'frozen', False):
        # Если запущено как exe
        return os.path.dirname(sys.executable)
    else:
        # Если запущено как скрипт
        return os.path.dirname(os.path.abspath(__file__))
'''
    
    # Вставляем после импортов
    imports_end = content.find('class ReportDatabase:')
    if imports_end != -1:
        content = content[:imports_end] + path_detection + '\n\n' + content[imports_end:]
    
    # Патчим класс ReportDatabase для работы с путем exe
    old_init = '''class ReportDatabase:
    def __init__(self):
        self.db_filename = "reports_db.pkl"
        self.reports = []'''
    
    new_init = '''class ReportDatabase:
    def __init__(self):
        exe_dir = get_exe_dir()
        self.db_filename = os.path.join(exe_dir, "reports_db.pkl")
        self.reports = []
        
        # Создаем папку reports рядом с exe если её нет
        self.reports_dir = os.path.join(exe_dir, "reports")
        if not os.path.exists(self.reports_dir):
            os.makedirs(self.reports_dir)'''
    
    content = content.replace(old_init, new_init)
    
    # Сохраняем патченную версию
    with open('MonOilStudy_exe.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Создана патченная версия MonOilStudy_exe.py")

def build_executables():
    """Сборка exe файлов"""
    print("Начинаем сборку...")
    
    # Патчим главное приложение
    patch_reports_path()
    
    # Создаем spec файлы
    create_main_app_spec()
    create_db_manager_spec()
    
    try:
        # Собираем главное приложение
        print("Собираем главное приложение...")
        subprocess.run([
            'pyinstaller', 
            '--onefile',
            '--windowed', 
            '--name=MonOilStudy',
            '--add-data=reports;reports',
            '--add-data=*.db;.',
            '--add-data=*.pkl;.',
            'MonOilStudy_exe.py'
        ], check=True)
        
        # Собираем менеджер БД
        print("Собираем менеджер БД...")
        subprocess.run([
            'pyinstaller', 
            '--onefile',
            '--windowed',
            '--name=DB_Manager', 
            '--add-data=*.db;.',
            '--add-data=db_instructions.txt;.',
            'DB man.py'
        ], check=True)
        
        print("Сборка завершена успешно!")
        print("Exe файлы находятся в папке dist/")
        
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при сборке: {e}")
        return False
    
    return True

if __name__ == "__main__":
    install_pyinstaller()
    success = build_executables()
    
    if success:
        print("\n=== ГОТОВО ===")
        print("Exe файлы созданы:")
        print("- dist/MonOilStudy.exe - основная программа мониторинга")
        print("- dist/DB_Manager.exe - программа управления БД")
        print("\nПапка reports будет создана автоматически рядом с exe файлом")
    else:
        print("Сборка не удалась!") 