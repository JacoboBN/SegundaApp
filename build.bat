@echo off
echo Construyendo SegundaApp...
echo.

REM Limpiar entorno virtual anterior si existe
if exist "venv" (
    echo Limpiando entorno virtual anterior...
    rmdir /s /q venv
)

REM Crear nuevo entorno virtual
echo Creando entorno virtual...
python -m venv venv

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Actualizar pip
echo Actualizando pip...
python -m pip install --upgrade pip

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

REM Verificar instalación de PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo Instalando PyInstaller específicamente...
    pip install pyinstaller==6.11.0
)

REM Limpiar directorio dist si existe
if exist "dist" (
    echo Limpiando builds anteriores...
    rmdir /s /q dist
)

REM Crear archivo de versión
echo Creando archivo de versión...
echo VSVersionInfo( > version.txt
echo     ffi=FixedFileInfo( >> version.txt
echo         filevers=(1,0,15,0), >> version.txt
echo         prodvers=(1,0,15,0), >> version.txt
echo         mask=0x3f, >> version.txt
echo         flags=0x0, >> version.txt
echo         OS=0x40004, >> version.txt
echo         fileType=0x1, >> version.txt
echo         subtype=0x0, >> version.txt
echo         date=(0, 0) >> version.txt
echo     ), >> version.txt
echo     kids=[ >> version.txt
echo         StringFileInfo( >> version.txt
echo             [ >> version.txt
echo                 StringTable( >> version.txt
echo                     u'040904B0', >> version.txt
echo                     [StringStruct(u'CompanyName', u'JacoboBN'), >> version.txt
echo                     StringStruct(u'FileDescription', u'SegundaApp - Aplicación de Ejemplo'), >> version.txt
echo                     StringStruct(u'FileVersion', u'1.0.15.0'), >> version.txt
echo                     StringStruct(u'InternalName', u'SegundaApp'), >> version.txt
echo                     StringStruct(u'LegalCopyright', u'Copyright (c) 2025 JacoboBN'), >> version.txt
echo                     StringStruct(u'OriginalFilename', u'SegundaApp.exe'), >> version.txt
echo                     StringStruct(u'ProductName', u'SegundaApp'), >> version.txt
echo                     StringStruct(u'ProductVersion', u'1.0.15.0')] >> version.txt
echo                 ) >> version.txt
echo             ] >> version.txt
echo         ), >> version.txt
echo         VarFileInfo([VarStruct(u'Translation', [1033, 1200])]) >> version.txt
echo     ] >> version.txt
echo ) >> version.txt

REM Construir ejecutable
echo Construyendo ejecutable...

REM Primero construir sin spec para generar uno si no existe
if not exist "SegundaApp.spec" (
    python -m PyInstaller --onefile --windowed --name SegundaApp --version-file=version.txt ^
        --clean ^
        --uac-admin ^
        --noconfirm ^
        main.py
) else (
    python -m PyInstaller SegundaApp.spec
)

if exist "dist\SegundaApp.exe" (
    echo.
    echo ¡Construcción completada correctamente!
    echo El ejecutable está en: dist\SegundaApp.exe
) else (
    echo.
    echo Error: No se pudo crear el ejecutable.
    echo Verifica los errores anteriores.
)

echo.
pause