@echo off
cd /d "%~dp0"
echo Запуск актуальной системы мониторинга нефтепровода...
python MonOilStudy_portable.py
if %errorlevel% neq 0 (
    echo Ошибка запуска! Убедитесь что Python установлен.
    echo Также проверьте наличие всех модулей (module1.py - module9.py)
    pause
)
