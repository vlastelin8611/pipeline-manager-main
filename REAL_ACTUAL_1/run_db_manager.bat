@echo off
cd /d "%~dp0"
echo Запуск менеджера баз данных...
python "DB man.py"
if %errorlevel% neq 0 (
    echo Ошибка запуска! Убедитесь что Python и PyQt5 установлены.
    echo Для установки PyQt5 выполните: pip install PyQt5
    pause
)
