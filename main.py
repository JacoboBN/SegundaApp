#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import messagebox
import requests
import json
import os
import sys
import subprocess
import tempfile
import threading
import shutil
import time
from pathlib import Path

# Configuración de la aplicación
APP_NAME = "SegundaApp"
VERSION = "1.0.15"
GITHUB_REPO = "JacoboBN/SegundaApp"
UPDATE_CHECK_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"

class UpdateChecker:
    def __init__(self, current_version):
        self.current_version = current_version
        
    def check_for_updates(self):
        """Verifica si hay actualizaciones disponibles"""
        try:
            response = requests.get(UPDATE_CHECK_URL, timeout=10)
            response.raise_for_status()
            release_info = response.json()
            
            latest_version = release_info['tag_name'].lstrip('v')
            
            if self.is_newer_version(latest_version, self.current_version):
                return {
                    'available': True,
                    'version': latest_version,
                    'download_url': self.get_exe_download_url(release_info),
                    'release_notes': release_info.get('body', 'Sin notas de versión')
                }
            else:
                return {'available': False}
                
        except Exception as e:
            print(f"Error verificando actualizaciones: {e}")
            return {'available': False, 'error': str(e)}
    
    def get_exe_download_url(self, release_info):
        """Obtiene la URL de descarga del archivo .exe"""
        for asset in release_info.get('assets', []):
            if asset['name'].endswith('.exe'):
                return asset['browser_download_url']
        return None
    
    def is_newer_version(self, latest, current):
        """Compara versiones (formato x.y.z)"""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            
            # Normalizar longitud
            max_len = max(len(latest_parts), len(current_parts))
            latest_parts.extend([0] * (max_len - len(latest_parts)))
            current_parts.extend([0] * (max_len - len(current_parts)))
            
            return latest_parts > current_parts
        except:
            return False
    
    def download_update(self, download_url, progress_callback=None):
        """Descarga la actualización"""
        try:
            response = requests.get(download_url, stream=True)
            response.raise_for_status()
            
            # Crear archivo temporal con nombre único
            temp_dir = tempfile.gettempdir()
            timestamp = int(time.time())
            temp_file = os.path.join(temp_dir, f"{APP_NAME}_update_{timestamp}.exe")
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress = (downloaded / total_size) * 100
                            progress_callback(progress)
            
            return temp_file
            
        except Exception as e:
            print(f"Error descargando actualización: {e}")
            return None

class MainApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{VERSION}")
        self.root.geometry("400x200")
        self.root.resizable(False, False)
        
        # Centrar ventana
        self.center_window()
        
        # Crear interfaz
        self.create_widgets()
        
        # Verificar actualizaciones al iniciar
        self.check_updates_on_startup()
    
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (200 // 2)
        self.root.geometry(f"400x200+{x}+{y}")
    
    def create_widgets(self):
        """Crea la interfaz de usuario"""
        # Título principal
        title_label = tk.Label(
            self.root, 
            text="Holaaaaaaa Mundo!", 
            font=("Arial", 24, "bold"),
            fg="blue"
        )
        title_label.pack(pady=40)
        
        # Información de versión
        version_label = tk.Label(
            self.root, 
            text=f"Versión {VERSION}", 
            font=("Arial", 10),
            fg="gray"
        )
        version_label.pack()
        
        # Botón para verificar actualizaciones manualmente
        update_button = tk.Button(
            self.root,
            text="Verificar Actualizaciones",
            command=self.manual_update_check,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10),
            padx=20,
            pady=5
        )
        update_button.pack(pady=20)
    
    def check_updates_on_startup(self):
        """Verifica actualizaciones al iniciar (en hilo separado)"""
        def check_in_background():
            checker = UpdateChecker(VERSION)
            update_info = checker.check_for_updates()
            
            if update_info.get('available'):
                # Programar el diálogo en el hilo principal
                self.root.after(0, lambda: self.show_update_dialog(update_info))
        
        # Ejecutar en hilo separado para no bloquear la UI
        thread = threading.Thread(target=check_in_background, daemon=True)
        thread.start()
    
    def manual_update_check(self):
        """Verificación manual de actualizaciones"""
        checker = UpdateChecker(VERSION)
        update_info = checker.check_for_updates()
        
        if update_info.get('available'):
            self.show_update_dialog(update_info)
        elif update_info.get('error'):
            messagebox.showerror(
                "Error", 
                f"No se pudo verificar actualizaciones:\n{update_info['error']}"
            )
        else:
            messagebox.showinfo(
                "Sin Actualizaciones", 
                "Ya tienes la versión más reciente."
            )
    
    def show_update_dialog(self, update_info):
        """Muestra el diálogo de actualización"""
        version = update_info['version']
        notes = update_info.get('release_notes', 'Sin notas')
        
        message = f"Nueva versión disponible: v{version}\n\n"
        message += "¿Deseas descargar y ejecutar la nueva versión?\n\n"
        message += "NOTA: Se descargará el nuevo ejecutable y se abrirá automáticamente."
        
        result = messagebox.askyesno(
            "Actualización Disponible",
            message,
            icon="question"
        )
        
        if result:
            self.perform_simple_update(update_info)
    
    def perform_simple_update(self, update_info):
        """Descarga la nueva versión, reemplaza el ejecutable y reinicia la app usando un .bat temporal"""
        download_url = update_info.get('download_url')
        if not download_url:
            messagebox.showerror("Error", "No se encontró el archivo de actualización.")
            return

        progress_window = tk.Toplevel(self.root)
        progress_window.title("Descargando actualización...")
        progress_window.geometry("350x120")
        progress_window.resizable(False, False)
        progress_window.transient(self.root)
        progress_window.grab_set()

        x = self.root.winfo_x() + 25
        y = self.root.winfo_y() + 40
        progress_window.geometry(f"350x120+{x}+{y}")

        progress_label = tk.Label(progress_window, text="Descargando nueva versión...")
        progress_label.pack(pady=10)

        progress_var = tk.DoubleVar()
        progress_bar = tk.ttk.Progressbar(
            progress_window,
            variable=progress_var,
            maximum=100
        )
        progress_bar.pack(pady=10, padx=20, fill=tk.X)

        status_label = tk.Label(progress_window, text="Preparando descarga...", fg="gray")
        status_label.pack()

        def update_progress(percentage):
            progress_var.set(percentage)
            status_label.config(text=f"Descargado: {percentage:.1f}%")
            progress_window.update()

        def download_and_replace():
            try:
                checker = UpdateChecker(VERSION)
                new_exe_path = checker.download_update(download_url, update_progress)
                if new_exe_path:
                    status_label.config(text="Descarga completada. Preparando actualización...")
                    progress_window.update()
                    time.sleep(1)
                    progress_window.destroy()

                    # Ruta del ejecutable actual
                    current_exe = sys.executable
                    # Ruta destino (donde está el .exe actual)
                    dest_exe = current_exe
                    # Ruta temporal del nuevo exe descargado
                    temp_new_exe = new_exe_path

                    # Crear script .bat temporal SOLO para reemplazar el exe, con log y mensaje de error
                    bat_content = f'''@echo off
setlocal
set LOGFILE="%TEMP%\\segundaapp_update.log"
timeout /t 2 > nul
:loop
tasklist | find /i "{os.path.basename(current_exe)}" > nul
if not errorlevel 1 (
    timeout /t 1 > nul
    goto loop
)
echo Intentando reemplazar el exe... > %LOGFILE%
move /y "{temp_new_exe}" "{dest_exe}" >> %LOGFILE% 2>&1
if errorlevel 1 (
    echo ERROR: No se pudo reemplazar el exe. >> %LOGFILE%
    echo. >> %LOGFILE%
    echo No se pudo actualizar SegundaApp. >> %LOGFILE%
    msg * "No se pudo actualizar SegundaApp. Cierra todos los procesos y vuelve a intentarlo." 2>nul
    exit /b 1
) else (
    echo Actualización completada correctamente. >> %LOGFILE%
)
endlocal
'''
                    bat_fd, bat_path = tempfile.mkstemp(suffix='.bat', text=True)
                    with os.fdopen(bat_fd, 'w', encoding='utf-8') as f:
                        f.write(bat_content)

                    # Mensaje final antes de cerrar
                    messagebox.showinfo(
                        "Actualización Lista",
                        f"La nueva versión se ha descargado y reemplazado correctamente.\n\n"
                        f"Por favor, cierra la aplicación y vuelve a abrirla manualmente para completar la actualización."
                    )

                    # Ejecutar el .bat y salir
                    subprocess.Popen([bat_path], shell=True, close_fds=True)
                    self.root.after(500, self.root.destroy)
                    sys.exit(0)
                else:
                    progress_window.destroy()
                    messagebox.showerror("Error", "No se pudo descargar la actualización.")
            except Exception as e:
                progress_window.destroy()
                messagebox.showerror("Error", f"Error durante la descarga: {e}")

        thread = threading.Thread(target=download_and_replace, daemon=True)
        thread.start()
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    # Log de arranque para depuración
    try:
        log_path = os.path.join(os.path.dirname(sys.executable), "arranque_segundaapp.log")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"Arranque: {time.strftime('%Y-%m-%d %H:%M:%S')} | PID: {os.getpid()}\n")
    except Exception as e:
        pass

    # Importar ttk para la barra de progreso
    try:
        from tkinter import ttk
    except ImportError:
        import tkinter.ttk as ttk

    app = MainApp()
    app.run()