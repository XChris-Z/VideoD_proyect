"""
Configuración de colores, estilos y constantes globales de Universal Video Downloader.
Paleta rediseñada con tonos Azul y Verde oscuros de principales, y Rojos y Dorados de secundarios.
"""

# --- CONFIGURACIÓN DE COLORES Y ESTILO ---
# Principales (Azul y Verde oscuros)
COLOR_BG_MAIN = "#0A1118"       # Fondo general abismal (Azul marino muy oscuro / Deep Navy Slate)
COLOR_BG_CARD = "#0F1E2E"       # Fondo de las tarjetas principal (Azul oscuro profundo / Dark Blue Card)
COLOR_BORDER = "#1E3A5F"        # Color de los bordes estructurados (Azul marino luminoso)
COLOR_ACCENT = "#0D6E58"        # Verde oscuro esmeralda/bosque interactivo (Principal para botones y destacados)
COLOR_ACCENT_HOVER = "#0A5443"  # Verde oscuro intensificado al pasar el cursor (Hover Principal)

# Secundarios (Rojos, Dorados y acentos complementarios)
COLOR_GREEN = "#10B981"         # Verde claro de éxito y compatibilidad verificado
COLOR_RED = "#EF4444"           # Rojo secundario vivo para cancelaciones, errores y botón X
COLOR_YELLOW = "#F59E0B"        # Dorado / Amarillo secundario para procesamiento, advertencias y actualizaciones
COLOR_GOLD = "#F59E0B"          # Dorado para insignias, acentos especiales y estados activos
COLOR_BLUE_SEC = "#3B82F6"      # Azul secundario para detalles y selecciones

# Colores de Texto
COLOR_TEXT_MAIN = "#F8FAFC"     # Texto principal ultra claro
COLOR_TEXT_MUTED = "#94A3B8"    # Texto secundario/atenuado
COLOR_TEXT_PLACEHOLDER = "#64748B" # Color de placeholder en inputs

# --- TABLA DE DETECCIÓN DE REDES SOCIALES ---
# Expresiones regulares para identificar la plataforma y asignar su color distintivo
PLATFORMS = {
    r"youtube\.com|youtu\.be": ("YouTube", "#FF0000"),
    r"instagram\.com": ("Instagram", "#E1306C"),
    r"twitter\.com|x\.com": ("Twitter / X", "#1D9BF0"),
    r"facebook\.com|fb\.watch": ("Facebook", "#1877F2"),
    r"reddit\.com": ("Reddit", "#FF4500"),
    r"tiktok\.com": ("TikTok", "#000000"),
    r"pinterest\.com": ("Pinterest", "#E60023"),
    r"twitch\.tv": ("Twitch", "#9146FF"),
    r"vimeo\.com": ("Vimeo", "#1AB7EA"),
}

# --- CONFIGURACIÓN DE FUENTES ---
FONT_FAMILY = "Segoe UI"
