@echo off
echo === УСТАНОВКА СИСТЕМЫ МОНИТОРИНГА НЕФТЕПРОВОДА ===
echo.

set INSTALL_DIR=%~dp0MonOilStudy
echo Устанавливаем в: %INSTALL_DIR%

if exist "%INSTALL_DIR%" (
    echo Папка уже существует. Удаляем старую версию...
    rmdir /s /q "%INSTALL_DIR%"
)

echo Создаем папку установки...
mkdir "%INSTALL_DIR%"

echo Копируем файлы...
xcopy /s /e /q MonOilStudy_Distribution\* "%INSTALL_DIR%\"

echo.
echo === УСТАНОВКА ЗАВЕРШЕНА ===
echo.
echo Программа установлена в: %INSTALL_DIR%
echo.
echo Для запуска:
echo - %INSTALL_DIR%\run_monitor.bat (основная программа)
echo - %INSTALL_DIR%\run_db_manager.bat (менеджер БД)
echo.
echo ВНИМАНИЕ: Для работы требуется Python 3.7+ и PyQt5
echo Для установки PyQt5: pip install PyQt5
echo.
pause
