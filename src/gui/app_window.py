"""
Ventana principal de la aplicación y controlador gráfico (CustomTkinter).
Implementa la interfaz en tonos Azul y Verde oscuros (principales) y Rojo y Dorado (secundarios).
"""

import os
import re
import threading
import queue
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image

from src.config import (
    COLOR_BG_MAIN,
    COLOR_BG_CARD,
    COLOR_BORDER,
    COLOR_ACCENT,
    COLOR_ACCENT_HOVER,
    COLOR_GREEN,
    COLOR_RED,
    COLOR_YELLOW,
    COLOR_GOLD,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED,
    PLATFORMS,
    FONT_FAMILY
)
from src.utils import get_app_dir, get_default_download_dir, get_ytdlp_bin, get_ffmpeg_bin
from src.engine import (
    check_local_version,
    check_latest_release_version,
    download_ytdlp_sync,
    download_ffmpeg_sync,
    check_ffmpeg_available
)
from src.downloader import VideoDownloader
from src.gui.widgets import create_default_placeholder_image, attach_context_menu, setup_app_icon


class DownloaderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Inicializar cola de comunicación para hilos y bucle de procesamiento
        self.queue = queue.Queue()
        self.process_queue()

        # Configuración básica de la ventana
        self.title("Universal Video Downloader - Motor yt-dlp")
        self.geometry("780x760")
        self.resizable(True, True)
        self.minsize(780, 760)
        self.configure(fg_color=COLOR_BG_MAIN)
        setup_app_icon(self, get_app_dir())

        # Variables de estado
        self.download_path = ctk.StringVar(value=get_default_download_dir())
        self.local_version = "Desconocida"
        self.is_updating = False
        self.use_cookies = ctk.BooleanVar(value=False)
        self.cookies_path = ctk.StringVar(value="")
        self.preview_timer_id = None
        self.last_preview_url = ""
        self.preview_thumb_image = None

        # Instanciar el gestor de descargas con enrutador de UI thread-safe
        self.downloader = VideoDownloader(ui_dispatcher=self.ui_after)

        # Configurar la grid de la ventana principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Encabezado
        self.grid_rowconfigure(1, weight=1)  # Panel Central
        self.grid_rowconfigure(2, weight=0)  # Panel de Actualización

        # Construir interfaz gráfica
        self.create_widgets()

        # Enlazar protocolo de cierre seguro de ventana y eventos de URL
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.url_entry.bind("<KeyRelease>", self.on_url_change)

        # Iniciar verificación e instalación automática de dependencias
        self.ui_after(100, self.check_and_install_dependencies_async)

    def ui_after(self, ms, func=None, *args):
        """Método seguro para ejecutar funciones en el hilo de la UI o programar vía cola."""
        if threading.current_thread() is threading.main_thread():
            return super().after(ms, func, *args)
        else:
            if func is not None:
                self.queue.put((func, args))
            return None

    def process_queue(self):
        """Procesa todas las tareas pendientes en la cola desde el hilo principal."""
        try:
            while True:
                func, args = self.queue.get_nowait()
                try:
                    func(*args)
                except Exception as e:
                    print(f"[Queue Execution Error] {e}")
                self.queue.task_done()
        except queue.Empty:
            pass
        super().after(50, self.process_queue)

    def create_widgets(self):
        # ----------------------------------------------------
        # 1. ENCABEZADO (Header Frame)
        # ----------------------------------------------------
        self.header_frame = ctk.CTkFrame(self, fg_color=COLOR_BG_MAIN, height=80, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(20, 10))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="UNIVERSAL VIDEO DOWNLOADER",
            font=ctk.CTkFont(family=FONT_FAMILY, size=24, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        self.title_label.grid(row=0, column=0, sticky="w")

        self.subtitle_label = ctk.CTkLabel(
            self.header_frame,
            text="Descarga videos, audio o imágenes de YouTube, Instagram, X/Twitter, Facebook y más.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLOR_TEXT_MUTED
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", pady=(2, 0))

        # ----------------------------------------------------
        # 2. PANEL CENTRAL (Tarjeta principal de trabajo)
        # ----------------------------------------------------
        self.card_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_CARD,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=12
        )
        self.card_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        self.card_frame.grid_columnconfigure(0, weight=1)
        for r in range(9):
            self.card_frame.grid_rowconfigure(r, weight=1 if r == 3 else 0)

        # Selector de Navegador para Cookies (Fila 0)
        self.browser_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.browser_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=(15, 0))
        self.browser_frame.grid_columnconfigure(0, weight=0)
        self.browser_frame.grid_columnconfigure(1, weight=1)

        self.browser_lbl = ctk.CTkLabel(
            self.browser_frame,
            text="Navegador para extraer sesión:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        self.browser_lbl.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.browser_menu = ctk.CTkOptionMenu(
            self.browser_frame,
            values=["Ninguno", "chrome", "edge", "firefox", "brave"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=30,
            width=150,
            fg_color=COLOR_BG_MAIN,
            button_color=COLOR_BORDER,
            button_hover_color=COLOR_ACCENT,
            dropdown_fg_color=COLOR_BG_CARD,
            dropdown_text_color=COLOR_TEXT_MAIN,
            dropdown_hover_color=COLOR_ACCENT
        )
        self.browser_menu.grid(row=0, column=1, sticky="w")
        self.browser_menu.set("Ninguno")

        # Entrada de URL (Fila 1 & 2)
        self.url_title_lbl = ctk.CTkLabel(
            self.card_frame,
            text="Enlace de descarga (Video / Imagen / Galería):",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        self.url_title_lbl.grid(row=1, column=0, sticky="w", padx=25, pady=(10, 5))

        self.url_input_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.url_input_frame.grid(row=2, column=0, sticky="ew", padx=25, pady=(0, 8))
        self.url_input_frame.grid_columnconfigure(0, weight=1)
        self.url_input_frame.grid_columnconfigure(1, weight=0)
        self.url_input_frame.grid_columnconfigure(2, weight=0)

        self.url_entry = ctk.CTkEntry(
            self.url_input_frame,
            placeholder_text="Pega la URL aquí...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            height=40,
            fg_color=COLOR_BG_MAIN,
            border_color=COLOR_BORDER,
            text_color=COLOR_TEXT_MAIN,
            placeholder_text_color="#64748B"
        )
        self.url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        attach_context_menu(self.url_entry)

        self.clear_btn = ctk.CTkButton(
            self.url_input_frame,
            text="X",
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            width=40,
            height=40,
            fg_color=COLOR_BORDER,
            hover_color=COLOR_RED,
            text_color=COLOR_TEXT_MAIN,
            corner_radius=6,
            command=self.clear_url_entry
        )
        self.clear_btn.grid(row=0, column=1, sticky="e", padx=(0, 8))

        self.platform_badge = ctk.CTkLabel(
            self.url_input_frame,
            text="Esperando enlace...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11, weight="bold"),
            text_color=COLOR_TEXT_MUTED,
            fg_color=COLOR_BORDER,
            height=40,
            width=140,
            corner_radius=6
        )
        self.platform_badge.grid(row=0, column=2, sticky="e")

        # Tarjeta de Vista Previa (Fila 3)
        self.preview_card = ctk.CTkFrame(
            self.card_frame,
            fg_color=COLOR_BG_MAIN,
            border_color=COLOR_BORDER,
            border_width=1,
            corner_radius=8
        )
        self.preview_card.grid(row=3, column=0, sticky="nsew", padx=25, pady=(5, 8))
        self.preview_card.grid_columnconfigure(0, weight=0)
        self.preview_card.grid_columnconfigure(1, weight=1)

        self.preview_thumb_lbl = ctk.CTkLabel(
            self.preview_card,
            text="",
            width=160,
            height=90
        )
        self.preview_thumb_lbl.grid(row=0, column=0, padx=12, pady=10, sticky="w")

        self.preview_info_frame = ctk.CTkFrame(self.preview_card, fg_color="transparent")
        self.preview_info_frame.grid(row=0, column=1, padx=(0, 12), pady=10, sticky="nsew")
        self.preview_info_frame.grid_columnconfigure(0, weight=1)
        self.preview_info_frame.grid_rowconfigure(0, weight=1)
        self.preview_info_frame.grid_rowconfigure(1, weight=0)

        self.preview_title_lbl = ctk.CTkLabel(
            self.preview_info_frame,
            text="Vista previa no cargada",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_MAIN,
            wraplength=480,
            anchor="w",
            justify="left"
        )
        self.preview_title_lbl.grid(row=0, column=0, sticky="nw")

        self.preview_meta_lbl = ctk.CTkLabel(
            self.preview_info_frame,
            text="Pega un enlace compatible para ver los detalles.",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
            justify="left"
        )
        self.preview_meta_lbl.grid(row=1, column=0, sticky="sw", pady=(4, 0))

        # Cargar miniatura ilustrada inicial
        self.set_default_placeholder_image()

        # Configuración de Opciones: Formato, Calidad y Destino (Fila 4)
        self.options_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.options_frame.grid(row=4, column=0, sticky="ew", padx=25, pady=8)
        self.options_frame.grid_columnconfigure(0, weight=1)
        self.options_frame.grid_columnconfigure(1, weight=1)
        self.options_frame.grid_columnconfigure(2, weight=1)

        # Columna 1: Formato
        self.format_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.format_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.format_frame.grid_columnconfigure(0, weight=1)

        self.format_lbl = ctk.CTkLabel(
            self.format_frame,
            text="Formato de salida:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        self.format_lbl.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.format_menu = ctk.CTkOptionMenu(
            self.format_frame,
            values=["Video: Automático", "Video: MP4", "Video: MKV", "Audio: MP3", "Audio: M4A"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=35,
            fg_color=COLOR_BG_MAIN,
            button_color=COLOR_BORDER,
            button_hover_color=COLOR_ACCENT,
            dropdown_fg_color=COLOR_BG_CARD,
            dropdown_text_color=COLOR_TEXT_MAIN,
            dropdown_hover_color=COLOR_ACCENT
        )
        self.format_menu.grid(row=1, column=0, sticky="ew")
        self.format_menu.set("Video: Automático")

        # Columna 2: Calidad
        self.quality_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.quality_frame.grid(row=0, column=1, sticky="nsew", padx=8)
        self.quality_frame.grid_columnconfigure(0, weight=1)

        self.quality_lbl = ctk.CTkLabel(
            self.quality_frame,
            text="Calidad:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        self.quality_lbl.grid(row=0, column=0, sticky="w", pady=(0, 5))

        self.quality_menu = ctk.CTkOptionMenu(
            self.quality_frame,
            values=["Máxima Calidad", "Mínima Calidad"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            height=35,
            fg_color=COLOR_BG_MAIN,
            button_color=COLOR_BORDER,
            button_hover_color=COLOR_ACCENT,
            dropdown_fg_color=COLOR_BG_CARD,
            dropdown_text_color=COLOR_TEXT_MAIN,
            dropdown_hover_color=COLOR_ACCENT
        )
        self.quality_menu.grid(row=1, column=0, sticky="ew")
        self.quality_menu.set("Máxima Calidad")

        # Columna 3: Destino
        self.dest_frame = ctk.CTkFrame(self.options_frame, fg_color="transparent")
        self.dest_frame.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        self.dest_frame.grid_columnconfigure(0, weight=1)
        self.dest_frame.grid_columnconfigure(1, weight=0)

        self.dest_lbl = ctk.CTkLabel(
            self.dest_frame,
            text="Guardar en:",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        self.dest_lbl.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 5))

        self.path_entry = ctk.CTkEntry(
            self.dest_frame,
            textvariable=self.download_path,
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            height=35,
            fg_color=COLOR_BG_MAIN,
            border_color=COLOR_BORDER,
            state="readonly",
            text_color=COLOR_TEXT_MUTED
        )
        self.path_entry.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        attach_context_menu(self.path_entry)

        self.browse_btn = ctk.CTkButton(
            self.dest_frame,
            text="Buscar...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            width=80,
            height=35,
            fg_color=COLOR_BORDER,
            hover_color=COLOR_ACCENT,
            text_color=COLOR_TEXT_MAIN,
            command=self.browse_directory
        )
        self.browse_btn.grid(row=1, column=1, sticky="e")

        # Cookies manuales (Fila 5)
        self.cookies_frame = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.cookies_frame.grid(row=5, column=0, sticky="ew", padx=25, pady=(5, 10))
        self.cookies_frame.grid_columnconfigure(0, weight=0)
        self.cookies_frame.grid_columnconfigure(1, weight=1)
        self.cookies_frame.grid_columnconfigure(2, weight=0)

        self.cookies_chk = ctk.CTkCheckBox(
            self.cookies_frame,
            text="Usar archivo de cookies (cookies.txt)",
            variable=self.use_cookies,
            command=self.toggle_cookies,
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MAIN,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER
        )
        self.cookies_chk.grid(row=0, column=0, sticky="w", padx=(0, 10))

        self.cookies_entry = ctk.CTkEntry(
            self.cookies_frame,
            textvariable=self.cookies_path,
            placeholder_text="No se ha seleccionado ningún archivo (.txt)",
            font=ctk.CTkFont(family=FONT_FAMILY, size=11),
            height=30,
            fg_color=COLOR_BG_MAIN,
            border_color=COLOR_BORDER,
            state="readonly",
            text_color=COLOR_TEXT_MUTED
        )
        self.cookies_entry.grid(row=0, column=1, sticky="ew", padx=(0, 8))
        attach_context_menu(self.cookies_entry)

        self.cookies_btn = ctk.CTkButton(
            self.cookies_frame,
            text="Examinar...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            width=90,
            height=30,
            fg_color=COLOR_BORDER,
            hover_color=COLOR_ACCENT,
            text_color=COLOR_TEXT_MAIN,
            state="disabled",
            command=self.browse_cookies
        )
        self.cookies_btn.grid(row=0, column=2, sticky="e")

        # Advertencia FFMpeg (Fila 6)
        self.ffmpeg_warning_lbl = ctk.CTkLabel(
            self.card_frame,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_YELLOW,
            wraplength=700
        )

        # Botón Principal de Descarga (Fila 7) - Verde Esmeralda Principal
        self.download_btn = ctk.CTkButton(
            self.card_frame,
            text="INICIAR DESCARGA",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            width=320,
            height=45,
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=8,
            command=self.start_download
        )
        self.download_btn.grid(row=7, column=0, pady=(10, 15))

        # Panel de Barra de Progreso y Estado (Fila 8)
        self.progress_container = ctk.CTkFrame(self.card_frame, fg_color="transparent")
        self.progress_container.grid(row=8, column=0, sticky="ew", padx=25, pady=(0, 15))
        self.progress_container.grid_columnconfigure(0, weight=1)

        self.progressbar = ctk.CTkProgressBar(
            self.progress_container,
            fg_color=COLOR_BG_MAIN,
            progress_color=COLOR_GOLD,  # Barra dorada sobre fondo azul oscuro
            height=10,
            corner_radius=5
        )
        self.progressbar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.progressbar.set(0)

        self.status_detail_frame = ctk.CTkFrame(self.progress_container, fg_color="transparent")
        self.status_detail_frame.grid(row=1, column=0, sticky="ew")
        self.status_detail_frame.grid_columnconfigure(0, weight=1)
        self.status_detail_frame.grid_columnconfigure(1, weight=1)

        self.status_lbl = ctk.CTkLabel(
            self.status_detail_frame,
            text="Listo para descargar",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED
        )
        self.status_lbl.grid(row=0, column=0, sticky="w")

        self.progress_lbl = ctk.CTkLabel(
            self.status_detail_frame,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        self.progress_lbl.grid(row=0, column=1, sticky="e")

        # ----------------------------------------------------
        # 3. PANEL DE ACTUALIZACIÓN (Footer Frame)
        # ----------------------------------------------------
        self.footer_frame = ctk.CTkFrame(
            self,
            fg_color=COLOR_BG_CARD,
            border_color=COLOR_BORDER,
            border_width=1,
            height=60,
            corner_radius=8
        )
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(10, 25))
        self.footer_frame.grid_columnconfigure(0, weight=1)
        self.footer_frame.grid_columnconfigure(1, weight=0)

        self.motor_status_frame = ctk.CTkFrame(self.footer_frame, fg_color="transparent")
        self.motor_status_frame.grid(row=0, column=0, sticky="w", padx=20, pady=10)

        self.motor_title_lbl = ctk.CTkLabel(
            self.motor_status_frame,
            text="Motor de Descarga (yt-dlp):",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            text_color=COLOR_TEXT_MAIN
        )
        self.motor_title_lbl.grid(row=0, column=0, sticky="w")

        self.motor_version_lbl = ctk.CTkLabel(
            self.motor_status_frame,
            text="Verificando...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12),
            text_color=COLOR_TEXT_MUTED
        )
        self.motor_version_lbl.grid(row=0, column=1, sticky="w", padx=(5, 0))

        self.update_btn = ctk.CTkButton(
            self.footer_frame,
            text="Actualizar Motor",
            font=ctk.CTkFont(family=FONT_FAMILY, size=12, weight="bold"),
            width=130,
            height=30,
            fg_color=COLOR_BORDER,
            hover_color=COLOR_ACCENT,
            text_color=COLOR_TEXT_MAIN,
            command=self.start_update
        )
        self.update_btn.grid(row=0, column=1, sticky="e", padx=20, pady=10)

    # --- MÉTODOS DE INTERFAZ Y VISTA PREVIA ---
    def set_default_placeholder_image(self):
        """Asigna la miniatura ilustrada premium producida por PIL en widgets.py."""
        try:
            ctk_img = create_default_placeholder_image()
            self.preview_thumb_lbl.configure(image=ctk_img, text="")
            self.preview_thumb_image = ctk_img
        except Exception as e:
            print(f"[Placeholder Error] {e}")

    def clear_preview(self):
        """Limpia los campos informativos de la tarjeta de vista previa."""
        self.preview_title_lbl.configure(text="Vista previa no cargada")
        self.preview_meta_lbl.configure(text="Pega un enlace compatible para ver los detalles.")
        self.set_default_placeholder_image()

    def set_preview_error(self, message):
        """Muestra un mensaje de error en la tarjeta de vista previa."""
        self.preview_title_lbl.configure(text="Error de Vista Previa")
        self.preview_meta_lbl.configure(text=message)
        self.set_default_placeholder_image()

    def on_url_change(self, event=None):
        """Supervisa los cambios en la entrada de URL y detecta la plataforma en tiempo real."""
        url = self.url_entry.get().strip()
        if not url:
            self.platform_badge.configure(
                text="Esperando enlace...",
                fg_color=COLOR_BORDER,
                text_color=COLOR_TEXT_MUTED
            )
            if self.preview_timer_id is not None:
                self.after_cancel(self.preview_timer_id)
                self.preview_timer_id = None
            self.clear_preview()
            self.last_preview_url = ""
            return

        detected = False
        for pattern, (name, color) in PLATFORMS.items():
            if re.search(pattern, url, re.IGNORECASE):
                self.platform_badge.configure(
                    text=name,
                    fg_color=color,
                    text_color="#FFFFFF"
                )
                detected = True
                break

        if not detected:
            if url.startswith("http://") or url.startswith("https://"):
                self.platform_badge.configure(
                    text="Compatible (yt-dlp)",
                    fg_color=COLOR_GREEN,
                    text_color="#FFFFFF"
                )
                detected = True
            else:
                self.platform_badge.configure(
                    text="URL no válida",
                    fg_color=COLOR_RED,
                    text_color="#FFFFFF"
                )

        if detected:
            if url != self.last_preview_url:
                if self.preview_timer_id is not None:
                    self.after_cancel(self.preview_timer_id)
                self.preview_timer_id = self.after(1000, self.trigger_preview_load)
        else:
            if self.preview_timer_id is not None:
                self.after_cancel(self.preview_timer_id)
                self.preview_timer_id = None
            self.clear_preview()
            self.last_preview_url = ""

    def clear_url_entry(self):
        """Borra la entrada de URL y limpia la vista previa."""
        self.url_entry.delete(0, 'end')
        self.on_url_change()
        self.clear_preview()
        self.last_preview_url = ""

    def trigger_preview_load(self):
        """Inicia la carga de metadatos del video en segundo plano (debounced)."""
        self.preview_timer_id = None
        url = self.url_entry.get().strip()
        if not url or url == self.last_preview_url:
            return

        self.last_preview_url = url
        self.preview_title_lbl.configure(text="Cargando información del video...")
        self.preview_meta_lbl.configure(text="Obteniendo metadatos desde yt-dlp...")

        browser_sel = self.browser_menu.get()
        use_cookies = self.use_cookies.get()
        cookies_path = self.cookies_path.get()

        threading.Thread(
            target=self.fetch_preview_info_worker,
            args=(url, browser_sel, use_cookies, cookies_path),
            daemon=True
        ).start()

    def fetch_preview_info_worker(self, url, browser_sel, use_cookies, cookies_path):
        """Worker en segundo plano para obtener metadatos y miniatura (sin tocar widgets UI)."""
        try:
            data, pil_img = self.downloader.fetch_preview_info(
                url=url,
                browser_sel=browser_sel,
                use_cookies=use_cookies,
                cookies_path=cookies_path
            )
            self.ui_after(0, self.update_preview_ui, data["title"], data["meta_text"], pil_img, url)
        except Exception as e:
            self.ui_after(0, self.set_preview_error, f"No se pudo cargar la vista previa: {str(e)}")

    def update_preview_ui(self, title, meta_text, pil_img, url):
        """Actualiza la interfaz de la tarjeta de vista previa con los datos obtenidos."""
        if self.url_entry.get().strip() != url:
            return

        self.preview_title_lbl.configure(text=title)
        self.preview_meta_lbl.configure(text=meta_text)

        if pil_img:
            try:
                resampling_method = getattr(Image, "Resampling", Image)
                resample_filter = getattr(resampling_method, "LANCZOS", getattr(Image, "ANTIALIAS", Image.BICUBIC))
                pil_img.thumbnail((160, 90), resample_filter)
                ctk_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=pil_img.size)
                self.preview_thumb_lbl.configure(image=ctk_img, text="")
                self.preview_thumb_image = ctk_img
            except Exception as e:
                print(f"[Image Render Error] {e}")
                self.set_default_placeholder_image()
        else:
            self.set_default_placeholder_image()

    def browse_directory(self):
        """Abre un diálogo para seleccionar la carpeta de descarga."""
        selected_dir = filedialog.askdirectory(initialdir=self.download_path.get())
        if selected_dir:
            self.download_path.set(selected_dir)

    def toggle_cookies(self):
        """Habilita o deshabilita los controles del archivo de cookies manual."""
        if self.use_cookies.get():
            self.cookies_btn.configure(state="normal")
            if not self.cookies_path.get():
                self.browse_cookies()
        else:
            self.cookies_btn.configure(state="disabled")

    def browse_cookies(self):
        """Abre un diálogo para seleccionar el archivo cookies.txt."""
        selected_file = filedialog.askopenfilename(
            title="Seleccionar archivo de cookies (Netscape)",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if selected_file:
            self.cookies_path.set(selected_file)
            self.use_cookies.set(True)
            self.cookies_btn.configure(state="normal")
        else:
            if not self.cookies_path.get():
                self.use_cookies.set(False)
                self.cookies_btn.configure(state="disabled")

    # --- VERIFICACIÓN E INSTALACIÓN DE DEPENDENCIAS ---
    def check_and_install_dependencies_async(self):
        """Inicia el chequeo e instalación de yt-dlp y ffmpeg en segundo plano."""
        threading.Thread(target=self.perform_dependencies_check_and_install, daemon=True).start()

    def perform_dependencies_check_and_install(self):
        """Worker en segundo plano para verificar y descargar binarios faltantes."""
        ok, version_str, ffmpeg_ok = check_local_version()

        if not ok or not ffmpeg_ok:
            self.ui_after(0, lambda: self.status_lbl.configure(text="Descargando dependencias iniciales en segundo plano...", text_color=COLOR_YELLOW))
            self.ui_after(0, lambda: self.download_btn.configure(state="disabled", fg_color="#374151"))
            self.ui_after(0, lambda: self.update_btn.configure(state="disabled"))

            try:
                if not ok:
                    self.ui_after(0, lambda: self.motor_version_lbl.configure(text="Instalando yt-dlp...", text_color=COLOR_YELLOW))
                    download_ytdlp_sync(self.on_component_download_progress)

                if not ffmpeg_ok:
                    self.ui_after(0, lambda: self.motor_version_lbl.configure(text="Instalando ffmpeg...", text_color=COLOR_YELLOW))
                    download_ffmpeg_sync(self.on_component_download_progress)

                self.ui_after(0, self.on_dependencies_install_success)
            except Exception as e:
                self.ui_after(0, lambda err=e: self.on_dependencies_install_error(err))
        else:
            self.ui_after(0, self.update_local_version_label)
            self.ui_after(0, self.check_ffmpeg_and_warn)

    def on_component_download_progress(self, percent, downloaded, total, name):
        """Reporta el progreso de descarga de un binario en la UI."""
        self.ui_after(0, lambda p=percent: self.progressbar.set(p))
        mb_dl = downloaded / (1024 * 1024)
        mb_tot = total / (1024 * 1024)
        self.ui_after(0, lambda p=percent: self.progress_lbl.configure(text=f"{p*100:.1f}%"))
        self.ui_after(0, lambda: self.status_lbl.configure(text=f"Descargando {name}: {mb_dl:.1f} MB de {mb_tot:.1f} MB", text_color=COLOR_YELLOW))

    def on_dependencies_install_success(self):
        """Callback ejecutado al instalar dependencias con éxito."""
        self.progressbar.set(0)
        self.progress_lbl.configure(text="")
        self.update_local_version_label()
        self.reset_ui_controls()
        self.status_lbl.configure(text="Dependencias instaladas y listas.", text_color=COLOR_GREEN)
        self.check_ffmpeg_and_warn()

    def on_dependencies_install_error(self, error):
        """Callback al ocurrir un error durante la descarga de dependencias."""
        self.progressbar.set(0)
        self.progress_lbl.configure(text="")
        self.reset_ui_controls()
        self.status_lbl.configure(text="Error al instalar dependencias iniciales.", text_color=COLOR_RED)
        messagebox.showerror("Error de Inicio", f"No se pudieron descargar los binarios requeridos:\n{str(error)}")

    def update_local_version_label(self):
        """Verifica los binarios locales y actualiza las etiquetas de motor."""
        ok, version_str, ffmpeg_ok = check_local_version()
        self.local_version = version_str

        if not ok or not ffmpeg_ok:
            self.motor_version_lbl.configure(text="Motor incompleto", text_color=COLOR_RED)
            self.status_lbl.configure(text="Faltan componentes. Haz clic en 'Actualizar Motor' para descargarlos.", text_color=COLOR_RED)
            self.download_btn.configure(state="disabled", fg_color="#374151")
            return False

        self.motor_version_lbl.configure(text=f"v{self.local_version} (FFmpeg OK)", text_color=COLOR_GREEN)
        self.download_btn.configure(state="normal", fg_color=COLOR_ACCENT)
        self.check_update_silently()
        return True

    def check_update_silently(self):
        """Consulta en segundo plano si hay una nueva versión de yt-dlp en GitHub."""
        threading.Thread(target=self.check_update_worker, daemon=True).start()

    def check_update_worker(self):
        """Worker silencioso para verificar la última versión del motor."""
        new_version = check_latest_release_version(self.local_version)
        if new_version:
            self.ui_after(0, lambda: self.motor_version_lbl.configure(
                text=f"v{self.local_version} (Actualización v{new_version} disponible!)",
                text_color=COLOR_YELLOW
            ))

    def check_ffmpeg_and_warn(self):
        """Verifica si ffmpeg está en el sistema y muestra la advertencia en caso negativo."""
        if not check_ffmpeg_available():
            self.ffmpeg_warning_lbl.grid(row=6, column=0, sticky="ew", padx=25, pady=(0, 10))
            self.ffmpeg_warning_lbl.configure(
                text="Advertencia: FFmpeg no detectado. Las descargas de alta calidad o conversión podrían fallar."
            )
        else:
            self.ffmpeg_warning_lbl.grid_forget()

    def start_update(self):
        """Inicia la actualización manual del motor en un hilo secundario."""
        if self.is_updating or self.downloader.is_downloading:
            return

        self.is_updating = True
        self.update_btn.configure(state="disabled", text="Actualizando...")
        self.download_btn.configure(state="disabled", fg_color="#374151")
        self.motor_version_lbl.configure(text="Conectando...", text_color=COLOR_YELLOW)

        threading.Thread(target=self.perform_engine_update, daemon=True).start()

    def perform_engine_update(self):
        """Descarga e instala yt-dlp y ffmpeg secuencialmente."""
        try:
            self.ui_after(0, lambda: self.motor_version_lbl.configure(text="Actualizando yt-dlp...", text_color=COLOR_YELLOW))
            download_ytdlp_sync(self.on_component_download_progress)

            self.ui_after(0, lambda: self.motor_version_lbl.configure(text="Actualizando ffmpeg...", text_color=COLOR_YELLOW))
            download_ffmpeg_sync(self.on_component_download_progress)

            self.ui_after(0, self.on_engine_update_success)
        except Exception as e:
            self.ui_after(0, lambda err=e: self.on_engine_update_error(err))

    def on_engine_update_success(self):
        """Restablece el estado de la UI al completarse la actualización del motor."""
        self.is_updating = False
        self.update_btn.configure(state="normal", text="Actualizar Motor")
        self.progressbar.set(0)
        self.progress_lbl.configure(text="")

        if self.update_local_version_label():
            self.status_lbl.configure(text="Componentes actualizados con éxito.", text_color=COLOR_GREEN)
            messagebox.showinfo("Éxito", "El motor yt-dlp y FFmpeg han sido descargados e instalados correctamente.")
            self.check_ffmpeg_and_warn()
        else:
            self.status_lbl.configure(text="Error al verificar componentes.", text_color=COLOR_RED)

    def on_engine_update_error(self, error):
        """Maneja los errores de actualización en la interfaz gráfica."""
        self.is_updating = False
        self.update_btn.configure(state="normal", text="Actualizar Motor")
        self.progressbar.set(0)
        self.progress_lbl.configure(text="")

        # Limpiar temporales
        for p in [get_ytdlp_bin(), get_ffmpeg_bin()]:
            temp_dest = p + ".tmp"
            if os.path.exists(temp_dest):
                try: os.remove(temp_dest)
                except Exception: pass
        zip_temp = os.path.join(get_app_dir(), "ffmpeg.zip")
        if os.path.exists(zip_temp):
            try: os.remove(zip_temp)
            except Exception: pass

        self.update_local_version_label()
        self.status_lbl.configure(text="Fallo al descargar componentes.", text_color=COLOR_RED)
        messagebox.showerror("Error de Actualización", f"Ocurrió un error al actualizar los componentes:\n{str(error)}")

    # --- CONTROL DE DESCARGA DE VIDEOS ---
    def start_download(self):
        """Inicia la descarga de video o cancela la descarga en curso si está activa."""
        if self.downloader.is_downloading:
            self.downloader.cancel()
            return

        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Falta Enlace", "Por favor, ingresa una URL válida antes de descargar.")
            return

        if self.is_updating:
            return

        if not os.path.exists(get_ytdlp_bin()):
            messagebox.showerror("Falta Motor", "El motor yt-dlp no está instalado.\nHaz clic en 'Actualizar Motor' para descargarlo.")
            return

        # Cambiar el botón principal a estado CANCELAR (Rojo Secundario)
        self.download_btn.configure(
            text="CANCELAR DESCARGA",
            fg_color=COLOR_RED,
            hover_color="#DC2626"
        )

        # Deshabilitar controles de opciones
        self.update_btn.configure(state="disabled")
        self.browse_btn.configure(state="disabled")
        self.quality_menu.configure(state="disabled")
        self.format_menu.configure(state="disabled")
        self.cookies_chk.configure(state="disabled")
        self.cookies_btn.configure(state="disabled")
        self.browser_menu.configure(state="disabled")

        self.progressbar.set(0)
        self.progress_lbl.configure(text="0%")
        self.status_lbl.configure(text="Analizando enlace...", text_color=COLOR_GOLD)

        dest_dir = self.download_path.get()
        format_sel = self.format_menu.get()
        quality_sel = self.quality_menu.get()
        browser_sel = self.browser_menu.get()
        use_cookies = self.use_cookies.get()
        cookies_path = self.cookies_path.get()

        threading.Thread(
            target=self.downloader.start_download,
            args=(
                url,
                dest_dir,
                format_sel,
                quality_sel,
                browser_sel,
                use_cookies,
                cookies_path,
                self.update_download_progress,
                self.update_download_status_message,
                self.on_download_success,
                self.on_download_error,
                self.on_download_canceled
            ),
            daemon=True
        ).start()

    def reset_ui_controls(self):
        """Restablece los botones y menús a su estado normal de reposo."""
        self.download_btn.configure(
            text="INICIAR DESCARGA",
            fg_color=COLOR_ACCENT,
            hover_color=COLOR_ACCENT_HOVER,
            state="normal"
        )
        self.update_btn.configure(state="normal")
        self.browse_btn.configure(state="normal")
        self.quality_menu.configure(state="normal")
        self.format_menu.configure(state="normal")
        self.cookies_chk.configure(state="normal")
        self.browser_menu.configure(state="normal")
        self.status_lbl.configure(text_color=COLOR_TEXT_MUTED)
        if self.use_cookies.get():
            self.cookies_btn.configure(state="normal")
        else:
            self.cookies_btn.configure(state="disabled")

    def update_download_progress(self, percent, size, speed, eta, status="Descargando..."):
        """Actualiza la barra de progreso dorada y el texto informativo."""
        self.progressbar.set(percent / 100.0)
        self.progress_lbl.configure(text=f"{percent:.1f}%")
        self.status_lbl.configure(
            text=f"{status} | Tamaño: {size} | Vel: {speed} | ETA: {eta}",
            text_color=COLOR_GOLD
        )

    def update_download_status_message(self, message):
        """Actualiza el texto de estado del subproceso."""
        self.status_lbl.configure(text=message, text_color=COLOR_GOLD)

    def on_download_success(self):
        """Maneja el fin exitoso de la descarga."""
        self.reset_ui_controls()
        self.progressbar.set(1.0)
        self.progress_lbl.configure(text="100%")
        self.status_lbl.configure(text="Descarga completada con éxito.", text_color=COLOR_GREEN)
        messagebox.showinfo("Descarga Exitosa", "El archivo se ha descargado y guardado correctamente en la ruta seleccionada.")

    def on_download_canceled(self):
        """Maneja la cancelación de la descarga por parte del usuario."""
        self.reset_ui_controls()
        self.progressbar.set(0)
        self.progress_lbl.configure(text="")
        self.status_lbl.configure(text="Descarga cancelada por el usuario.", text_color=COLOR_RED)
        messagebox.showinfo("Cancelado", "La descarga ha sido cancelada.")

    def on_download_error(self, error_message):
        """Maneja un error durante la descarga del video."""
        self.reset_ui_controls()
        self.progressbar.set(0)
        self.progress_lbl.configure(text="")
        self.status_lbl.configure(text="Ocurrió un error en la descarga.", text_color=COLOR_RED)

        if "ffmpeg" in error_message.lower():
            msg = ("Se requiere 'ffmpeg' para esta descarga (fusión de pistas o conversión de formato).\n\n"
                   "Por favor, asegúrate de que ffmpeg esté instalado o prueba con 'Video: Automático' y 'Mínima Calidad'.")
        else:
            msg = f"No se pudo completar la descarga.\nDetalle:\n{error_message}"

        messagebox.showerror("Error en Descarga", msg)

    def on_closing(self):
        """Pide confirmación si hay un proceso activo antes de cerrar la ventana."""
        if self.downloader.is_downloading and self.downloader.process:
            if messagebox.askyesno("Confirmar Salida", "Hay una descarga en curso. ¿Deseas cancelarla y cerrar la aplicación?"):
                self.downloader.cancel()
                self.destroy()
        elif self.is_updating:
            if messagebox.askyesno("Confirmar Salida", "Se está actualizando el motor. ¿Deseas abortar y cerrar la aplicación?"):
                self.destroy()
        else:
            self.destroy()
