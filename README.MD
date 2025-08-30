# SegundaApp - Sistema de Actualizaciones Automáticas

Una aplicación de ejemplo que demuestra cómo implementar un sistema de actualizaciones automáticas usando GitHub Releases.

## 🚀 Características

- ✅ Interfaz gráfica simple con "Hello World!"
- ✅ Verificación automática de actualizaciones al iniciar
- ✅ Descarga e instalación automática de updates
- ✅ Distribución via GitHub Releases
- ✅ Construcción automática con GitHub Actions

## 📋 Requisitos

- Python 3.8 o superior
- Windows 10 o superior (para el ejecutable final)
- Cuenta de GitHub

## 🛠️ Configuración Inicial

### 1. Preparar el código

1. **Clona tu repositorio localmente:**
   ```bash
   git clone https://github.com/JacoboBN/SegundaApp.git
   cd SegundaApp
   ```

2. **Crea los archivos necesarios:**
   - Copia `main.py` en la raíz del proyecto
   - Crea `requirements.txt` en la raíz
   - Crea la carpeta `.github/workflows/` y añade `release.yml`
   - Opcionalmente, añade `build.bat` para pruebas locales

3. **Sube todo a GitHub:**
   ```bash
   git add .
   git commit -m "Inicial: App con sistema de actualizaciones"
   git push origin main
   ```

### 2. Probar localmente (Opcional)

Para probar antes de subir:

1. **Ejecuta `build.bat`** o manualmente:
   ```bash
   pip install -r requirements.txt
   pyinstaller --onefile --windowed --name SegundaApp main.py
   ```

2. **Ejecuta el .exe generado** en `dist/SegundaApp.exe`

### 3. Crear tu primera release

1. **Crear y subir un tag:**
   ```bash
   git tag v1.0.0
   git push origin v1.0.0
   ```

2. **GitHub Actions se ejecutará automáticamente** y:
   - Construirá el ejecutable
   - Creará un Release
   - Subirá el .exe

3. **Descarga el .exe** desde la página de Releases y pruébalo

## 🔄 Cómo hacer actualizaciones

### Para actualizar a versión 1.0.1:

1. **Modifica el código** (por ejemplo, cambia "Hello World!" por "Hello World v2!")

2. **Actualiza la versión** en `main.py`:
   ```python
   VERSION = "1.0.1"  # Cambiar aquí
   ```

3. **Commit y crea nuevo tag:**
   ```bash
   git add .
   git commit -m "v1.0.1: Actualización de mensaje"
   git tag v1.0.1
   git push origin main
   git push origin v1.0.1
   ```

4. **GitHub Actions creará automáticamente** el nuevo release

5. **Los usuarios existentes** recibirán notificación de actualización al abrir su app

## 📁 Estructura del proyecto

```
SegundaApp/
├── main.py                 # Aplicación principal
├── requirements.txt        # Dependencias
├── build.bat              # Script de construcción local
├── .github/
│   └── workflows/
│       └── release.yml    # GitHub Actions
└── README.md              # Este archivo
```

## 🔧 Personalización

### Cambiar información de la app:

En `main.py`, modifica estas constantes:

```python
APP_NAME = "SegundaApp"      # Nombre de la aplicación
VERSION = "1.0.0"            # Versión actual
GITHUB_REPO = "JacoboBN/SegundaApp"  # Tu repositorio
```

### Modificar la interfaz:

La interfaz está en el método `create_widgets()`. Puedes:
- Cambiar el texto "Hello World!"
- Añadir más botones o elementos
- Modificar colores y fuentes

## 🐛 Solución de problemas

### La app no encuentra actualizaciones:
- Verifica que `GITHUB_REPO` esté correctamente configurado
- Asegúrate de que el repositorio sea público
- Revisa que los releases tengan archivos .exe adjuntos

### GitHub Actions falla:
- Revisa los logs en la pestaña "Actions" de GitHub
- Asegúrate de que `requirements.txt` esté bien formateado
- Verifica que el tag siga el formato `vX.Y.Z`

### El ejecutable no se crea:
- Verifica que tienes Python 3.8+ instalado
- Ejecuta `pip install pyinstaller` manualmente
- Revisa que no haya errores en `main.py`

## 📈 Siguientes pasos

Una vez que funcione básicamente, puedes añadir:

1. **Configuración persistente** (guardar preferencias)
2. **Logs de actualización** (historial de cambios)
3. **Actualizaciones diferenciales** (solo cambios)
4. **Interfaz más compleja** (más funcionalidades)
5. **Firma digital** (certificados de seguridad)

## 🤝 Contribuir

1. Haz fork del proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo LICENSE para detalles.

---

**¡Tu app está lista para actualizaciones automáticas!** 🎉