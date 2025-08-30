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
from pathlib import Path

# Configuración de la aplicación
APP_NAME = "SegundaApp"
VERSION = "1.0.3"
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
            
            # Crear archivo temporal
            temp_dir = tempfile.gettempdir()
            temp_file = os.path.join(temp_dir, f"{APP_NAME}_update.exe")
            
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
            text="HOLA MUNDO!", 
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
        message += "¿Deseas actualizar ahora?\n\n"
        message += f"Notas de la versión:\n{notes[:200]}..."
        
        result = messagebox.askyesno(
            "Actualización Disponible",
            message,
            icon="question"
        )
        
        if result:
            self.perform_update(update_info)
    
    def perform_update(self, update_info):
        """Realiza la actualización"""
        download_url = update_info.get('download_url')
        if not download_url:
            messagebox.showerror("Error", "No se encontró el archivo de actualización.")
            return
        
        # Ventana de progreso
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Actualizando...")
        progress_window.geometry("300x100")
        progress_window.resizable(False, False)
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        # Centrar ventana de progreso
        x = self.root.winfo_x() + 50
        y = self.root.winfo_y() + 50
        progress_window.geometry(f"300x100+{x}+{y}")
        
        progress_label = tk.Label(progress_window, text="Descargando actualización...")
        progress_label.pack(pady=10)
        
        progress_var = tk.DoubleVar()
        progress_bar = tk.ttk.Progressbar(
            progress_window, 
            variable=progress_var, 
            maximum=100
        )
        progress_bar.pack(pady=10, padx=20, fill=tk.X)
        
        def update_progress(percentage):
            progress_var.set(percentage)
            progress_window.update()
        
        def download_and_install():
            try:
                checker = UpdateChecker(VERSION)
                temp_file = checker.download_update(download_url, update_progress)
                
                if temp_file:
                    progress_label.config(text="Instalando actualización...")
                    progress_window.update()
                    
                    # Obtener la ruta del ejecutable actual
                    current_exe = sys.executable if getattr(sys, 'frozen', False) else __file__
                    
                    # Crear script de actualización
                    self.create_update_script(temp_file, current_exe)
                    
                    messagebox.showinfo(
                        "Actualización Lista",
                        "La actualización se instalará al cerrar la aplicación."
                    )
                    progress_window.destroy()
                    self.root.quit()
                else:
                    messagebox.showerror("Error", "No se pudo descargar la actualización.")
                    progress_window.destroy()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error durante la actualización: {e}")
                progress_window.destroy()
        
        # Ejecutar descarga en hilo separado
        thread = threading.Thread(target=download_and_install, daemon=True)
        thread.start()
    
    def create_update_script(self, temp_file, current_exe):
        """Crea un script para reemplazar el ejecutable"""
        script_content = f'''
import time
import shutil
import subprocess
import os
import sys

# Esperar a que se cierre la aplicación principal
time.sleep(2)

try:
    # Reemplazar el ejecutable
    shutil.move(r"{temp_file}", r"{current_exe}")
    
    # Reiniciar la aplicación
    subprocess.Popen([r"{current_exe}"])
    
except Exception as e:
    print(f"Error durante actualización: {{e}}")

# Autodestrucción del script
try:
    os.remove(sys.argv[0])
except:
    pass
'''
        
        script_path = os.path.join(tempfile.gettempdir(), "update_script.py")
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Ejecutar script de actualización
        subprocess.Popen([sys.executable, script_path], 
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
    
    def run(self):
        """Ejecuta la aplicación"""
        self.root.mainloop()

if __name__ == "__main__":
    # Importar ttk para la barra de progreso
    try:
        from tkinter import ttk
    except ImportError:
        import tkinter.ttk as ttk
    
    app = MainApp()
    app.run()