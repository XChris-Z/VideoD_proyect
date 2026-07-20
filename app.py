"""
Punto de entrada principal de Universal Video Downloader.
Mantiene compatibilidad al 100% con scripts de ejecución y compilación de PyInstaller (app.py).
"""

import sys
import platform

# Asegurar soporte de alta definición en Windows (DPI awareness)
if platform.system() == "Windows":
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

from src.gui.app_window import DownloaderApp


def main():
    app = DownloaderApp()
    app.mainloop()


if __name__ == "__main__":
    main()
