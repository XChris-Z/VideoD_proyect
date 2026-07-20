"""
Utilidades del sistema, gestión de rutas multiplataforma y descargas con progreso.
Garantiza 100% de compatibilidad al ejecutar desde código fuente Python o compilado en PyInstaller (.exe).
"""

import os
import sys
import platform
import requests


def get_app_dir():
    """
    Retorna la ruta del directorio base del proyecto resuelta de forma inteligente.
    Si se ejecuta como ejecutable congelado (PyInstaller), retorna la carpeta del .exe.
    Si se ejecuta desde el código fuente Python modular (dentro de src/), retorna la carpeta raíz.
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    
    base_path = os.path.dirname(os.path.abspath(__file__))
    # Si este archivo está dentro de un subpaquete (como 'src' o 'gui'), apuntar a la raíz del proyecto
    parent_folder_name = os.path.basename(base_path).lower()
    if parent_folder_name in ("src", "gui", "utils", "core", "engine"):
        return os.path.dirname(base_path)
    return base_path


def get_ytdlp_bin():
    """Retorna la ruta absoluta al ejecutable binario yt-dlp."""
    ext = ".exe" if platform.system() == "Windows" else ""
    return os.path.join(get_app_dir(), f"yt-dlp{ext}")


def get_ffmpeg_bin():
    """Retorna la ruta absoluta al ejecutable binario ffmpeg."""
    ext = ".exe" if platform.system() == "Windows" else ""
    return os.path.join(get_app_dir(), f"ffmpeg{ext}")


def get_default_download_dir():
    """Obtiene la ruta de la carpeta de descargas del usuario (multiplataforma)."""
    if platform.system() == "Windows":
        try:
            import winreg
            sub_key = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
                return winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
        except Exception:
            pass
    return os.path.join(os.path.expanduser("~"), "Downloads")


def download_file_with_progress(url, dest_path, component_name, progress_callback=None):
    """
    Descarga un archivo remoto con reporte de progreso de bloques.
    
    Args:
        url (str): Enlace directo de descarga.
        dest_path (str): Ruta final donde se guardará el archivo.
        component_name (str): Nombre legible del componente para reportar progreso.
        progress_callback (callable, optional): Función callback(pct, downloaded, total, name).
    """
    temp_dest = dest_path + ".tmp"
    res_stream = requests.get(url, stream=True, timeout=15)
    res_stream.raise_for_status()

    total_size = int(res_stream.headers.get('content-length', 0))
    downloaded = 0
    block_size = 1024 * 64

    with open(temp_dest, 'wb') as f:
        for chunk in res_stream.iter_content(block_size):
            if not chunk:
                break
            f.write(chunk)
            downloaded += len(chunk)
            if total_size > 0 and progress_callback is not None:
                percent = downloaded / total_size
                progress_callback(percent, downloaded, total_size, component_name)

    if os.path.exists(dest_path):
        try:
            os.remove(dest_path)
        except OSError as e:
            raise Exception(f"No se puede reemplazar '{os.path.basename(dest_path)}' porque está en uso por otra aplicación o descarga activa.") from e
    try:
        os.rename(temp_dest, dest_path)
    except OSError as e:
        raise Exception(f"Error al renombrar el archivo temporal a '{os.path.basename(dest_path)}': {e}") from e
