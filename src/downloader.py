"""
Motor de descarga de video y obtención de metadatos.
Gestiona la ejecución de subprocesos de yt-dlp, el análisis de progreso en tiempo real y la cancelación segura.
"""

import os
import re
import json
import io
import platform
import subprocess
import requests
from PIL import Image
from src.utils import get_app_dir, get_ytdlp_bin


class VideoDownloader:
    """Clase para ejecutar y supervisar descargas con yt-dlp y ffmpeg."""

    def __init__(self, ui_dispatcher):
        """
        Args:
            ui_dispatcher (callable): Función para programar callbacks en el hilo principal de la UI (ej. app.after).
        """
        self.ui_dispatcher = ui_dispatcher
        self.process = None
        self.is_downloading = False
        self.download_canceled = False

    def fetch_preview_info(self, url, browser_sel="Ninguno", use_cookies=False, cookies_path=""):
        """
        Obtiene metadatos (título, miniatura, uploader, duración) de la URL usando yt-dlp --dump-json.
        Retorna (data_dict, pil_img) o lanza Exception si falla.
        """
        bin_path = get_ytdlp_bin()
        if not os.path.exists(bin_path):
            raise Exception("Motor yt-dlp no disponible. Instálalo primero desde 'Actualizar Motor'.")

        cmd = [bin_path, "--dump-json", "--no-playlist", "--ffmpeg-location", get_app_dir()]

        if use_cookies and os.path.exists(cookies_path):
            cmd.extend(["--cookies", cookies_path])

        if browser_sel and browser_sel != "Ninguno":
            cmd.extend(["--cookies-from-browser", browser_sel])

        cmd.append(url)

        startupinfo = None
        creationflags = 0
        if platform.system() == "Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            creationflags = subprocess.CREATE_NO_WINDOW

        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            startupinfo=startupinfo,
            creationflags=creationflags,
            timeout=35
        )

        if proc.returncode != 0:
            err_log = proc.stderr.strip() if proc.stderr else "Error desconocido de yt-dlp"
            err_msg = err_log.split("\n")[0] if err_log else "Error al obtener info"
            if "ERROR:" in err_msg:
                err_msg = err_msg.replace("ERROR:", "").strip()
            raise Exception(err_msg)

        try:
            data = json.loads(proc.stdout)
        except Exception:
            data = None
            if proc.stdout:
                for line in proc.stdout.splitlines():
                    line_str = line.strip()
                    if line_str.startswith("{") and line_str.endswith("}"):
                        try:
                            data = json.loads(line_str)
                            break
                        except Exception:
                            pass
            if not data:
                raise Exception("No se pudo procesar la respuesta JSON de yt-dlp.")

        title = data.get("title", "Título desconocido")
        thumbnail_url = data.get("thumbnail")

        if not thumbnail_url and data.get("thumbnails"):
            thumbnail_url = data.get("thumbnails")[-1].get("url")

        uploader = data.get("uploader", "")
        duration_secs = data.get("duration")

        duration_str = ""
        if duration_secs is not None:
            mins, secs = divmod(int(duration_secs), 60)
            hours, mins = divmod(mins, 60)
            if hours > 0:
                duration_str = f"{hours:02d}:{mins:02d}:{secs:02d}"
            else:
                duration_str = f"{mins:02d}:{secs:02d}"

        meta_parts = []
        if uploader:
            meta_parts.append(f"Canal: {uploader}")
        if duration_str:
            meta_parts.append(f"Duración: {duration_str}")

        meta_text = " | ".join(meta_parts) if meta_parts else "Vista previa cargada"

        pil_img = None
        if thumbnail_url:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                }
                thumb_resp = requests.get(thumbnail_url, headers=headers, timeout=10)
                thumb_resp.raise_for_status()
                pil_img = Image.open(io.BytesIO(thumb_resp.content))
            except Exception as img_err:
                print(f"[Preview Image Download Error] {img_err}")

        return {
            "title": title,
            "meta_text": meta_text,
            "url": url
        }, pil_img

    def start_download(
        self,
        url,
        dest_dir,
        format_sel,
        quality_sel,
        browser_sel,
        use_cookies,
        cookies_path,
        on_progress,
        on_status,
        on_success,
        on_error,
        on_cancel
    ):
        """
        Ejecuta la descarga en el hilo actual (debe llamarse desde un subhilo).
        Reporta el progreso y estados a través de los callbacks proporcionados mediante self.ui_dispatcher.
        """
        bin_path = get_ytdlp_bin()
        self.is_downloading = True
        self.download_canceled = False

        args = [bin_path]

        # Configuración de Calidad y Formato
        is_audio = format_sel.startswith("Audio:")
        is_twitter = bool(re.search(r"twitter\.com|x\.com", url, re.IGNORECASE))
        if is_audio:
            if quality_sel == "Máxima Calidad":
                args.extend(["-f", "bestaudio/best"])
            else:
                args.extend(["-f", "worstaudio/worst"])
        elif is_twitter:
            if quality_sel == "Máxima Calidad":
                args.extend(["-f", "bestvideo[protocol^=http]+bestaudio[protocol^=http]/best[protocol^=http]/bestvideo+bestaudio/best"])
            else:
                args.extend(["-f", "worstvideo[protocol^=http]+worstaudio[protocol^=http]/worst[protocol^=http]/worstvideo+worstaudio/worst"])
        else:
            if quality_sel == "Máxima Calidad":
                args.extend(["-f", "bestvideo+bestaudio/best"])
            else:
                args.extend(["-f", "worstvideo+worstaudio/worst"])

        if is_audio:
            args.append("-x")
            if "MP3" in format_sel:
                args.extend(["--audio-format", "mp3"])
            elif "M4A" in format_sel:
                args.extend(["--audio-format", "m4a"])
        else:
            args.extend(["-S", "vcodec:h264,acodec:m4a"])
            if "MP4" in format_sel or is_twitter:
                args.extend(["--merge-output-format", "mp4"])
            elif "MKV" in format_sel:
                args.extend(["--merge-output-format", "mkv"])

        output_template = os.path.join(dest_dir, "%(title)s.%(ext)s")
        args.extend(["-o", output_template])

        if use_cookies and os.path.exists(cookies_path):
            args.extend(["--cookies", cookies_path])

        if browser_sel and browser_sel != "Ninguno":
            args.extend(["--cookies-from-browser", browser_sel])

        args.append("--newline")

        is_gallery_platform = False
        for pattern in [r"instagram\.com", r"twitter\.com", r"x\.com", r"tiktok\.com", r"reddit\.com", r"pinterest\.com"]:
            if re.search(pattern, url, re.IGNORECASE):
                is_gallery_platform = True
                break

        if not is_gallery_platform:
            args.append("--no-playlist")

        args.extend(["--ffmpeg-location", get_app_dir()])
        args.append(url)

        try:
            startupinfo = None
            creationflags = 0
            if platform.system() == "Windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW

            self.process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                startupinfo=startupinfo,
                creationflags=creationflags
            )

            progress_regex = re.compile(
                r"\[download\]\s+(?P<percent>[\d\.]+)%\s+of\s+(?P<size>\S+)\s+at\s+(?P<speed>\S+)\s+ETA\s+(?P<eta>\S+)"
            )
            finish_regex = re.compile(
                r"\[download\]\s+100%\s+of\s+(?P<size>\S+)\s+in\s+(?P<time>\S+)"
            )

            for line in iter(self.process.stdout.readline, ""):
                line_str = line.strip()
                if not line_str:
                    continue

                print(f"[yt-dlp] {line_str}")

                # 1. Analizar si es línea de progreso estándar
                prog_match = progress_regex.search(line_str)
                if prog_match:
                    pct = float(prog_match.group("percent"))
                    size = prog_match.group("size")
                    speed = prog_match.group("speed")
                    eta = prog_match.group("eta")

                    self.ui_dispatcher(0, lambda p=pct, s=size, sp=speed, e=eta: on_progress(p, s, sp, e))
                    continue

                # 2. Analizar finalización del fragmento
                fin_match = finish_regex.search(line_str)
                if fin_match:
                    size = fin_match.group("size")
                    self.ui_dispatcher(0, lambda s=size: on_progress(100.0, s, "N/A", "00:00", "Descargado"))
                    continue

                # 3. Estados especiales
                if "has already been downloaded" in line_str:
                    self.ui_dispatcher(0, lambda: on_status("El video ya se encuentra descargado."))
                    self.ui_dispatcher(0, lambda: on_progress(100.0, "Listo", "N/A", "00:00", "Completo"))
                    continue

                if "[merger]" in line_str or "Merging formats" in line_str:
                    self.ui_dispatcher(0, lambda: on_status("Fusionando pistas (requiere ffmpeg)..."))
                    continue

                if "[ExtractInfo]" in line_str or "Extracting URL" in line_str:
                    self.ui_dispatcher(0, lambda: on_status("Extrayendo metadatos..."))
                    continue

                if line_str.startswith("ERROR:"):
                    err_msg = line_str.replace("ERROR:", "").strip()
                    if ";" in err_msg:
                        err_msg = err_msg.split(";")[0]
                    self.ui_dispatcher(0, lambda m=err_msg: on_error(m))
                    return

            self.process.wait()
            rc = self.process.returncode

            self.is_downloading = False
            if self.download_canceled:
                self.ui_dispatcher(0, on_cancel)
                return

            if rc == 0:
                self.ui_dispatcher(0, on_success)
            else:
                self.ui_dispatcher(0, lambda: on_error(f"El proceso falló con código de salida {rc}"))

        except Exception as e:
            self.is_downloading = False
            if self.download_canceled:
                self.ui_dispatcher(0, on_cancel)
            else:
                self.ui_dispatcher(0, lambda err=e: on_error(str(err)))

    def cancel(self):
        """Cancela el proceso activo terminando la tarea en el sistema operativo."""
        if self.is_downloading and self.process:
            self.download_canceled = True
            try:
                if platform.system() == "Windows":
                    subprocess.run(
                        ["taskkill", "/F", "/T", "/PID", str(self.process.pid)],
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )
                else:
                    self.process.terminate()
            except Exception as e:
                print(f"[Cancel Error] {e}")
