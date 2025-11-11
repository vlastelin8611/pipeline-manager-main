@echo off
echo === УСТАНОВКА И СБОРКА СИСТЕМЫ МОНИТОРИНГА НЕФТЕПРОВОДА ===
echo.

echo Устанавливаем необходимые пакеты...
pip install pyinstaller --no-proxy
if %errorlevel% neq 0 (
    echo Попытка установки без прокси...
    pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pyinstaller
    if %errorlevel% neq 0 (
        echo Не удалось установить pyinstaller. Попробуйте вручную:
        echo pip install pyinstaller
        pause
        exit /b 1
    )
)

pip install PyQt5 --no-proxy
if %errorlevel% neq 0 (
    pip install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org PyQt5
)

echo.
echo Готовим файлы для сборки...
python build_exe.py
if %errorlevel% neq 0 (
    echo Ошибка при сборке!
    pause
    exit /b 1
)

echo.
echo === СБОРКА ЗАВЕРШЕНА ===
echo Ваши exe-файлы находятся в папке dist/
echo.
pause 