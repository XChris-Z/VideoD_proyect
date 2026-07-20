"""
Gestor de dependencias e instalación del motor (yt-dlp y ffmpeg).
Maneja comprobaciones de versión, descarga directa desde GitHub Releases e instalación en segundo plano.
"""

import os
import sys
import platform
import subprocess
import zipfile
import requests
from src.utils import get_app_dir, get_ytdlp_bin, get_ffmpeg_bin, download_file_with_progress


def check_ffmpeg_available():
    """
    Verifica si ffmpeg está accesible tanto en la ruta local de la aplicación como en el PATH global.
    Retorna True si está disponible, False en caso contrario.
    """
    # 1. Verificar binario en carpeta local
    local_ffmpeg = get_ffmpeg_bin()
    if os.path.exists(local_ffmpeg):
        try:
            startupinfo = None
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE

            res = subprocess.run(
                [local_ffmpeg, "-version"],
                capture_output=True,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0,
                timeout=10
            )
            if res.returncode == 0:
                return True
        except Exception:
            pass

    # 2. Verificar en el PATH del sistema
    try:
        startupinfo = None
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        res = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            startupinfo=startupinfo,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0,
            timeout=10
        )
        if res.returncode == 0:
            return True
    except Exception:
        pass

    return False


def download_ytdlp_sync(progress_callback=None):
    """Descarga el binario yt-dlp desde GitHub Releases de forma síncrona."""
    target_asset_name = "yt-dlp.exe" if platform.system() == "Windows" else "yt-dlp"
    dest_file = get_ytdlp_bin()

    # Intentar primero descarga directa sin usar la API de GitHub (evita rate limits)
    direct_url = f"https://github.com/yt-dlp/yt-dlp/releases/latest/download/{target_asset_name}"
    try:
        download_file_with_progress(direct_url, dest_file, "yt-dlp", progress_callback)
        if platform.system() != "Windows":
            os.chmod(dest_file, 0o755)
        return
    except Exception as direct_err:
        print(f"[Direct Download Failed] {direct_err}. Probando a través de la API de GitHub...")

    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get("https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest", headers=headers, timeout=10)
    r.raise_for_status()
    release_data = r.json()

    download_url = None
    for asset in release_data.get("assets", []):
        if asset.get("name") == target_asset_name:
            download_url = asset.get("browser_download_url")
            break

    if not download_url:
        for asset in release_data.get("assets", []):
            name = asset.get("name", "")
            if "yt-dlp" in name:
                if platform.system() == "Windows" and name.endswith(".exe"):
                    download_url = asset.get("browser_download_url")
                    break
                elif platform.system() != "Windows" and not name.endswith(".exe") and not name.endswith(".tar.gz") and not name.endswith(".zip"):
                    download_url = asset.get("browser_download_url")
                    break

    if not download_url:
        raise Exception("No se pudo encontrar un binario de yt-dlp compatible en GitHub.")

    download_file_with_progress(download_url, dest_file, "yt-dlp", progress_callback)

    if platform.system() != "Windows":
        os.chmod(dest_file, 0o755)


def download_ffmpeg_sync(progress_callback=None):
    """Descarga y extrae el binario ffmpeg desde repositorio estático confiable."""
    sys_platform = platform.system()
    if sys_platform == "Windows":
        url = "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v6.1/ffmpeg-6.1-win-64.zip"
        binary_filename = "ffmpeg.exe"
    elif sys_platform == "Darwin":
        url = "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v6.1/ffmpeg-6.1-macos-64.zip"
        binary_filename = "ffmpeg"
    else:
        url = "https://github.com/ffbinaries/ffbinaries-prebuilt/releases/download/v6.1/ffmpeg-6.1-linux-64.zip"
        binary_filename = "ffmpeg"

    app_dir = get_app_dir()
    zip_path = os.path.join(app_dir, "ffmpeg.zip")

    download_file_with_progress(url, zip_path, "ffmpeg", progress_callback)

    dest_binary_path = os.path.join(app_dir, binary_filename)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        extracted_name = None
        for name in zip_ref.namelist():
            if os.path.basename(name).lower() == binary_filename.lower():
                extracted_name = name
                break

        if not extracted_name:
            extracted_name = zip_ref.namelist()[0]

        temp_extracted = zip_ref.extract(extracted_name, app_dir)

        if os.path.abspath(temp_extracted) != os.path.abspath(dest_binary_path):
            if os.path.exists(dest_binary_path):
                os.remove(dest_binary_path)
            os.rename(temp_extracted, dest_binary_path)

    try:
        os.remove(zip_path)
    except Exception:
        pass

    if platform.system() != "Windows":
        os.chmod(dest_binary_path, 0o755)


def check_local_version():
    """
    Verifica si yt-dlp y ffmpeg están en el sistema y retorna una tupla (status_ok, version_str, ffmpeg_ok).
    """
    bin_path = get_ytdlp_bin()
    ffmpeg_ok = check_ffmpeg_available()

    if not os.path.exists(bin_path):
        return False, "Incompleto", ffmpeg_ok

    try:
        startupinfo = None
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE

        res = subprocess.run(
            [bin_path, "--version"],
            capture_output=True,
            text=True,
            startupinfo=startupinfo,
            timeout=30,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        if res.returncode == 0:
            version_str = res.stdout.strip()
            return True, version_str, ffmpeg_ok
    except Exception:
        pass

    return False, "Error de motor", ffmpeg_ok


def check_latest_release_version(local_version):
    """
    Consulta silenciosamente a la API de GitHub si existe una versión superior de yt-dlp.
    Retorna la versión (str) si hay nueva actualización, o None en caso contrario.
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.get("https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest", headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            latest_version = data.get("tag_name", "")
            clean_latest = latest_version.lstrip('v')
            clean_local = local_version.lstrip('v')

            if clean_local != clean_latest and local_version not in ("Desconocida", "Incompleto", "Error de motor"):
                return clean_latest
    except Exception:
        pass
    return None
