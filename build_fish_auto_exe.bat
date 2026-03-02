@echo off
setlocal

REM Build script para generar fish_auto.exe en Windows
REM Uso:
REM   build_fish_auto_exe.bat

where py >nul 2>&1
if errorlevel 1 (
  echo [ERROR] No se encontro el launcher de Python ^("py"^).
  echo Instala Python 3.8+ y vuelve a intentar.
  exit /b 1
)

py -m pip install --upgrade pip
if errorlevel 1 exit /b 1

py -m pip install -r requirements-fish-auto.txt
if errorlevel 1 exit /b 1

py -m PyInstaller --noconfirm --clean --onefile --name fish_auto fish_auto.py
if errorlevel 1 exit /b 1

echo.
echo [OK] Ejecutable generado en: dist\fish_auto.exe
endlocal
