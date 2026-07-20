"""
Componentes visuales reutilizables, generador de miniaturas ilustradas premium y estilos de la UI.
"""

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
