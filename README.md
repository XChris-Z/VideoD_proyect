# 🚀 Universal Video Downloader (`UniversalVideoDownloader`)

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-0D6E58?style=for-the-badge&logo=windows&logoColor=white" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/Motor-yt--dlp-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="yt-dlp">
  <img src="https://img.shields.io/badge/Licencia-MIT-F59E0B?style=for-the-badge" alt="MIT License">
</p>

---

## 🌟 Descripción General

**Universal Video Downloader** es una aplicación de escritorio multiplataforma, visualmente deslumbrante y de alto rendimiento, diseñada para descargar videos, pistas de audio de alta fidelidad y galerías de imágenes desde las principales redes sociales y plataformas multimedia utilizando el robusto motor **yt-dlp** y la conversión avanzada de **FFmpeg**.

La interfaz ha sido rediseñada meticulosamente con una **paleta cromática académica y moderna**:
* **🎨 Colores Principales**: Tonos **Azules abismales** (`#0A1118` y `#0F1E2E`) combinados con un elegante **Verde Esmeralda/Bosque** (`#0D6E58`) para los elementos interactivos principales.
* **✨ Colores Secundarios**: Destellos **Dorados** (`#F59E0B`) para estados de procesamiento, insignias y acentos premium, y un **Rojo vibrante** (`#EF4444`) para botones de cancelación e indicadores de alerta.

---

## 🔥 Características Destacadas

1. **🌐 Detección Inteligente y Automática de Redes Sociales**
   Pega el enlace e instantáneamente el indicador identificará si corresponde a **YouTube, Instagram, X (Twitter), TikTok, Facebook, Reddit, Pinterest, Twitch o Vimeo**, cambiando dinámicamente de color y previsualizando los metadatos del video en tiempo real.

2. **🤖 Autogestión Cero Configuración (`Actualizar Motor`)**
   No necesitas instalar manualmente herramientas en la terminal. El programa detecta automáticamente la presencia de `yt-dlp` y `ffmpeg` al iniciar. Si faltan o están desactualizados, descárgalos e instálalos de forma nativa en segundo plano con un solo clic.

3. **🖼️ Tarjeta de Vista Previa con Miniaturas Ilustradas en PIL**
   Muestra el título del video, canal, duración e imagen original. Si no se puede obtener o mientras carga, presenta una **miniatura digital ilustrada premium** construida dinámicamente usando `Pillow`.

4. **🍪 Soporte Total de Sesiones y Cookies (Bypassing)**
   Permite extraer cookies directamente desde navegadores locales (**Chrome, Edge, Firefox, Brave**) o cargar un archivo `cookies.txt` en formato Netscape para descargar contenido que requiera inicio de sesión o verificación de edad.

5. **⚡ Descargas en Hilos sin Congelamientos**
   Toda la descarga, fusión de pistas y conversión ocurre en hilos secundarios asíncronos (`threading` + `queue`). La barra de progreso dorada y los detalles (MB, velocidad, ETA) se actualizan suavemente línea por línea. Además, incluye botón de **Cancelación Instantánea**.

---

## 📁 Estructura Modular del Proyecto (`src/`)

El proyecto está organizado como un paquete de software limpio, escalable y 100% compatible con entornos virtuales y compiladores como PyInstaller:

```text
VideoD_proyect/
├── app.py                     # Punto de entrada gráfico principal (compatible con pyinstaller app.py)
├── run.py                     # Script alternativo de desarrollo rápido
├── requirements.txt           # Dependencias Python (CustomTkinter, Requests, Pillow, PyInstaller)
├── build_instructions.md      # Guía detallada de compilación a ejecutable (.exe)
├── UniversalVideoDownloader.spec # Archivo de configuración optimizado de PyInstaller
├── .gitignore                 # Excluye binarios pesados (134MB+), cachés y carpetas de build
└── src/                       # Paquete de código fuente estructurado
    ├── __init__.py
    ├── config.py              # Paleta de colores, tipografía y tabla de redes sociales
    ├── utils.py               # Resolución de rutas multiplataforma y descargas por bloques
    ├── engine.py              # Verificación e instalación remota de yt-dlp y ffmpeg
    ├── downloader.py          # Lógica asíncrona de descarga (subprocess, regex progress y cancelación)
    └── gui/                   # Capa de interfaz gráfica (CustomTkinter)
        ├── __init__.py
        ├── widgets.py         # Miniaturas personalizadas PIL e interfaz modular
        └── app_window.py      # Ventana principal DownloaderApp
```

---

## 🚀 Guía de Instalación y Uso (Desarrollo)

### Requisitos Previos
* **Python 3.10 o superior** instalado en tu sistema (`Windows`, `macOS` o `Linux`).

### 1. Clonar el Repositorio
```powershell
git clone https://github.com/tu-usuario/UniversalVideoDownloader.git
cd UniversalVideoDownloader
```

### 2. Crear Entorno Virtual (Recomendado) e Instalar Dependencias
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación
```powershell
python app.py
```
> [!NOTE]
> La primera vez que abras el programa en un sistema limpio, hará una verificación rápida. Si no localiza `yt-dlp.exe` o `ffmpeg.exe` en la carpeta raíz, te sugerirá descargarlos automáticamente haciendo clic en **"Actualizar Motor"**.

---

## 📦 Compilación a Ejecutable `.exe` Portable (Sin Consola)

Para distribuir la aplicación como un único archivo `.exe` que se puede llevar en un USB o compartir sin necesidad de instalar Python, ejecuta:

```powershell
# Opción 1: Usando el archivo de configuración (.spec) preconfigurado (recomendado):
pyinstaller UniversalVideoDownloader.spec

# Opción 2: Comando directo con ícono personalizado:
pyinstaller --onefile --windowed --icon="icon.ico" --name="UniversalVideoDownloader" app.py
```
* Una vez finalizado el proceso, encontrarás tu ejecutable portable en la carpeta `dist/UniversalVideoDownloader.exe`.
* Al transferir este `.exe` a cualquier computadora limpia, la función autogestionada del motor descargará `yt-dlp.exe` y `ffmpeg.exe` en la carpeta donde se encuentre el programa. ¡Totalmente portable!

---

## ❓ Preguntas Frecuentes y Solución de Problemas

* **¿Por qué `ffmpeg.exe` (134 MB) y `yt-dlp.exe` no están incluidos en el repositorio de GitHub?**
  GitHub impone un límite estricto de 100 MB por archivo. Subir binarios pesados al repositorio aumenta innecesariamente el tamaño del historial de git. Gracias a nuestra arquitectura, el `.gitignore` excluye inteligentemente estos ejecutables y el programa los descarga automáticamente desde fuentes oficiales precompiladas al hacer clic en **Actualizar Motor**.

* **El programa indica que falta FFmpeg al intentar fusionar pistas MP4 de máxima calidad:**
  Asegúrate de haber hecho clic en el botón inferior **Actualizar Motor** para que el programa extraiga automáticamente `ffmpeg.exe` en la carpeta de ejecución, o instálalo globalmente en las variables de entorno de tu sistema.

---

## 📄 Licencia

Este software se distribuye bajo la **Licencia MIT**. Consulta el archivo `LICENSE` para más información.
# VideoD_proyect
