# Instrucciones de Compilación con PyInstaller

Para empaquetar la aplicación como un ejecutable portable independiente (un solo archivo `.exe` sin consola de fondo), sigue estos pasos:

## Requisitos Previos

Asegúrate de tener instaladas las dependencias del archivo `requirements.txt`. Si no lo has hecho, puedes instalarlas con:
```powershell
pip install -r requirements.txt
```

## Arquitectura del Proyecto

El proyecto está modularizado dentro del paquete `src/` (`src/config.py`, `src/utils.py`, `src/engine.py`, `src/downloader.py` y `src/gui/`). 
El archivo `app.py` ubicado en el directorio raíz funciona como el controlador principal que importa y arranca la interfaz `DownloaderApp`. Por lo tanto, PyInstaller detecta e incluye automáticamente todos los submódulos de `src/` al procesar `app.py`.

## Comando de Compilación

Ejecuta el siguiente comando en tu terminal (asegúrate de estar en el directorio raíz del proyecto `c:\Users\chris\OneDrive\Desktop\VideoD_proyect`):

```powershell
pyinstaller --onefile --windowed --name="UniversalVideoDownloader" app.py
```

### Explicación de los Argumentos del Comando:

* `--onefile`: Indica a PyInstaller que empaquete todo el código de Python y sus dependencias (incluyendo `src/`) en un único archivo ejecutable `.exe` (ubicado dentro de la carpeta `dist/` al finalizar).
* `--windowed` (o `--noconsole`): Evita que se abra una ventana de comandos de fondo (símbolo del sistema) al ejecutar la aplicación gráfica.
* `--name="UniversalVideoDownloader"`: Especifica el nombre de salida para el archivo `.exe`.
* `app.py`: El archivo de código fuente principal.

## Distribución de la Aplicación

1. Una vez termine la compilación con éxito, verás una carpeta llamada `dist` dentro de tu directorio de trabajo.
2. Dentro de `dist/` encontrarás el ejecutable portable `UniversalVideoDownloader.exe`.
3. **Lógica Portable y GitHub Ready**: El ejecutable es completamente independiente de Python. Puedes copiar este archivo `UniversalVideoDownloader.exe` y colocarlo en cualquier carpeta o llevarlo en un USB.
4. **Actualización del Motor**: Al iniciarse en cualquier computadora nueva, la aplicación detectará que no tiene los motores `yt-dlp.exe` ni `ffmpeg.exe` en esa carpeta específica y te sugerirá hacer clic en **"Actualizar Motor"**. Al hacerlo, descargará ambos binarios de forma nativa en la misma ruta de ejecución y estará listo para descargar videos en máxima calidad sin requerir configuraciones previas ni archivos adicionales.
