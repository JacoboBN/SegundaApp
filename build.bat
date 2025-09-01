@echo off
echo Construyendo SegundaApp...
echo.

REM Crear entorno virtual si no existe
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

REM Construir ejecutable
echo Construyendo ejecutable...
pyinstaller --onefile --windowed --name SegundaApp main.py

echo.
echo ¡Construcción completada!
echo El ejecutable está en: dist\SegundaApp.exe
echo.
pause