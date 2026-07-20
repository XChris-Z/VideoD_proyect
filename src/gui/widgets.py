"""
Componentes visuales reutilizables, generador de miniaturas ilustradas premium y estilos de la UI.
"""

import os
import tkinter as tk
from PIL import Image, ImageDraw, ImageFont
import customtkinter as ctk
from src.config import (
    COLOR_BG_MAIN,
    COLOR_BG_CARD,
    COLOR_BORDER,
    COLOR_ACCENT,
    COLOR_GOLD,
    COLOR_TEXT_MAIN,
    COLOR_TEXT_MUTED
)


def create_default_placeholder_image():
    """
    Genera y retorna una imagen placeholder de 160x90 con diseño ilustrado premium en PIL.
    Combina fondo Azul oscuro (#0F1E2E), marco Verde esmeralda (#0D6E58) / Dorado (#F59E0B)
    y un ícono/texto digital estilizado.
    """
    width, height = 160, 90
    img = Image.new("RGB", (width, height), color=COLOR_BG_CARD)
    draw = ImageDraw.Draw(img)

    # 1. Dibujar un borde exterior sutil en color azul marino brillante
    draw.rectangle([0, 0, width - 1, height - 1], outline=COLOR_BORDER, width=2)

    # 2. Dibujar esquineras o detalles geométricos en Verde Esmeralda y Dorado
    margin = 8
    # Marco interior verde oscuro
    draw.rectangle([margin, margin, width - margin - 1, height - margin - 1], outline=COLOR_ACCENT, width=1)
    
    # Acentos dorados en las 4 esquinas del marco interior
    corner_len = 8
    # Superior izquierda
    draw.line([(margin, margin + corner_len), (margin, margin), (margin + corner_len, margin)], fill=COLOR_GOLD, width=2)
    # Superior derecha
    draw.line([(width - margin - corner_len, margin), (width - margin, margin), (width - margin, margin + corner_len)], fill=COLOR_GOLD, width=2)
    # Inferior izquierda
    draw.line([(margin, height - margin - corner_len), (margin, height - margin), (margin + corner_len, height - margin)], fill=COLOR_GOLD, width=2)
    # Inferior derecha
    draw.line([(width - margin - corner_len, height - margin), (width - margin, height - margin), (width - margin, height - margin - corner_len)], fill=COLOR_GOLD, width=2)

    # 3. Dibujar ícono simbólico de video/play en el centro
    center_x, center_y = width // 2, (height // 2) - 6
    tri_size = 10
    triangle_coords = [
        (center_x - tri_size + 2, center_y - tri_size),
        (center_x - tri_size + 2, center_y + tri_size),
        (center_x + tri_size + 2, center_y)
    ]
    draw.polygon(triangle_coords, fill=COLOR_ACCENT, outline=COLOR_GOLD)

    # 4. Dibujar texto inferior
    text = "U V D   •   L I S T O"
    try:
        # Intentar cargar fuente por defecto del sistema
        font = ImageFont.truetype("arial.ttf", 10)
    except Exception:
        font = ImageFont.load_default()

    try:
        # Calcular ancho de texto con el método moderno o clásico
        if hasattr(draw, "textbbox"):
            bbox = draw.textbbox((0, 0), text, font=font)
            text_w = bbox[2] - bbox[0]
        else:
            text_w, _ = draw.textsize(text, font=font)
        draw.text(((width - text_w) / 2, center_y + 16), text, fill=COLOR_TEXT_MAIN, font=font)
    except Exception:
        # Si falla el cálculo exacto, aproximar posición centrándolo
        draw.text((35, center_y + 16), text, fill=COLOR_TEXT_MAIN)

    return ctk.CTkImage(light_image=img, dark_image=img, size=(width, height))


def attach_context_menu(widget):
    """
    Agrega un menú contextual con clic derecho (Cortar, Copiar, Pegar, Seleccionar Todo)
    a campos de entrada (CTkEntry, CTkTextbox, etc.).
    """
    menu = tk.Menu(
        widget,
        tearoff=0,
        bg=COLOR_BG_CARD,
        fg=COLOR_TEXT_MAIN,
        activebackground=COLOR_ACCENT,
        activeforeground="#FFFFFF",
        relief="flat",
        borderwidth=1,
        font=("Segoe UI", 10)
    )

    def do_cut():
        try:
            widget.event_generate("<<Cut>>")
        except Exception:
            pass

    def do_copy():
        try:
            widget.event_generate("<<Copy>>")
        except Exception:
            pass

    def do_paste():
        try:
            widget.event_generate("<<Paste>>")
        except Exception:
            pass

    def do_select_all():
        try:
            widget.select_range(0, 'end')
            widget.icursor('end')
        except Exception:
            try:
                widget.event_generate("<<SelectAll>>")
            except Exception:
                pass

    menu.add_command(label="Cortar", command=do_cut)
    menu.add_command(label="Copiar", command=do_copy)
    menu.add_command(label="Pegar", command=do_paste)
    menu.add_separator()
    menu.add_command(label="Seleccionar todo", command=do_select_all)

    def show_popup(event):
        try:
            if hasattr(widget, "cget") and widget.cget("state") == "disabled":
                return
        except Exception:
            pass
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    widget.bind("<Button-3>", show_popup)


def setup_app_icon(window, app_dir):
    """
    Genera dinámicamente un ícono .ico elegante con PIL (si no existe) y lo aplica a la ventana principal.
    """
    try:
        icon_path = os.path.join(app_dir, "icon.ico")
        if not os.path.exists(icon_path):
            size = 256
            img = Image.new("RGBA", (size, size), color=(0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            # Fondo con bordes redondeados en Azul Abismal e interior Verde Esmeralda/Oro
            draw.rounded_rectangle([10, 10, size - 10, size - 10], radius=50, fill=COLOR_BG_MAIN, outline=COLOR_GOLD, width=8)
            draw.rounded_rectangle([30, 30, size - 30, size - 30], radius=35, outline=COLOR_ACCENT, width=6)

            # Triángulo (Play) de video centrado
            center = size // 2
            tri_size = 50
            triangle = [
                (center - tri_size + 15, center - tri_size),
                (center - tri_size + 15, center + tri_size),
                (center + tri_size + 18, center)
            ]
            draw.polygon(triangle, fill=COLOR_ACCENT, outline=COLOR_GOLD)

            img.save(icon_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])

        if os.path.exists(icon_path):
            try:
                window.iconbitmap(icon_path)
            except Exception:
                pass
    except Exception as e:
        print(f"[Icon Setup Error] {e}")


def show_app_notification(window, title, message, notif_type="info"):
    """
    Muestra un cuadro de notificación modal premium e insonoro (sin ruido de Windows)
    dentro de la misma estética de la aplicación.
    """
    try:
        notif = ctk.CTkToplevel(window)
        notif.title(title)
        notif.resizable(False, False)
        notif.configure(fg_color=COLOR_BG_MAIN)
        notif.transient(window)
        notif.grab_set()

        if notif_type == "success":
            accent_color = "#10B981"  # Verde esmeralda brillante
            icon_str = "✔"
        elif notif_type == "error":
            accent_color = "#EF4444"  # Rojo vibrante
            icon_str = "✖"
        else:
            accent_color = COLOR_GOLD  # Dorado / Advertencia / Info
            icon_str = "ℹ"

        card = ctk.CTkFrame(notif, fg_color=COLOR_BG_CARD, border_color=accent_color, border_width=2, corner_radius=12)
        card.pack(fill="both", expand=True, padx=15, pady=15)

        header_frame = ctk.CTkFrame(card, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(15, 5))

        icon_lbl = ctk.CTkLabel(header_frame, text=icon_str, font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"), text_color=accent_color)
        icon_lbl.pack(side="left", padx=(0, 10))

        title_lbl = ctk.CTkLabel(header_frame, text=title, font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"), text_color=COLOR_TEXT_MAIN)
        title_lbl.pack(side="left")

        msg_lbl = ctk.CTkLabel(card, text=message, font=ctk.CTkFont(family="Segoe UI", size=13), text_color=COLOR_TEXT_MUTED, wraplength=380, justify="left")
        msg_lbl.pack(fill="both", expand=True, padx=20, pady=10)

        ok_btn = ctk.CTkButton(
            card,
            text="ACEPTAR",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            width=130,
            height=34,
            fg_color=accent_color,
            hover_color=accent_color,
            text_color="#FFFFFF" if notif_type in ["error", "success"] else COLOR_TEXT_MAIN,
            corner_radius=8,
            command=notif.destroy
        )
        ok_btn.pack(pady=(5, 15))

        try:
            window.update_idletasks()
            notif.update_idletasks()
            w = notif.winfo_reqwidth()
            h = notif.winfo_reqheight()
            x = window.winfo_x() + (window.winfo_width() // 2) - (w // 2)
            y = window.winfo_y() + (window.winfo_height() // 2) - (h // 2)
            notif.geometry(f"{w}x{h}+{x}+{y}")
        except Exception:
            notif.geometry("440x220")
    except Exception as e:
        print(f"[Notification Error] {e}")


