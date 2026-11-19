
import tkinter as tk
import validators
import threading
import yt_dlp
from tkinter import ttk
from playsound import playsound
import os
import sys
from pathlib import Path


# --------------------------------------------------
# RUTAS DE ARCHIVOS
# --------------------------------------------------

def obtener_ruta(recurso):
    """
    Obtiene la ruta de un recurso tanto desde Python
    como desde un ejecutable generado con PyInstaller.
    """

    if hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent

    return base / recurso


def obtener_carpeta_descargas():
    """
    La carpeta de descargas se crea junto al EXE
    o en la carpeta del proyecto cuando se ejecuta Python.
    """

    if getattr(sys, "frozen", False):
        base = Path(sys.executable).resolve().parent
    else:
        base = Path(__file__).resolve().parent

    carpeta = base / "folder"
    carpeta.mkdir(parents=True, exist_ok=True)

    return str(carpeta)


# --------------------------------------------------
# FUNCIONES PRINCIPALES
# --------------------------------------------------

def descargar(url, modo):

    progress_bar["value"] = 0
    send_info("Iniciando descarga...")

    def progreso(d):

        if d["status"] == "downloading":

            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            descargado = d.get("downloaded_bytes", 0)

            if total:
                porcentaje = descargado / total * 100

                ventana.after(
                    0,
                    lambda p=porcentaje: progress_bar.config(value=p)
                )

        if d["status"] == "finished":
            send_info("Procesando archivo...")

    def descarga():

        carpeta = obtener_carpeta_descargas()

        try:

            if modo == "Audio":

                opciones = {
                    "format": "bestaudio/best",
                    "outtmpl": os.path.join(
                        carpeta, "%(title)s.%(ext)s"
                    ),
                    "progress_hooks": [progreso],
                    "extractor_args": {
                        "youtube": {
                            "player_client": ["android"]
                        }
                    },
                    "postprocessors": [{
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }]
                }

            else:

                opciones = {
                    "format": "bestvideo+bestaudio/best",
                    "outtmpl": os.path.join(
                        carpeta, "%(title)s.%(ext)s"
                    ),
                    "merge_output_format": "mkv",
                    "progress_hooks": [progreso],
                    "extractor_args": {
                        "youtube": {
                            "player_client": ["android"]
                        }
                    }
                }

            with yt_dlp.YoutubeDL(opciones) as ydl:
                ydl.download([url])

            send_info("Descarga completada")

            ventana.after(
                0,
                lambda: progress_bar.config(value=100)
            )

        except Exception as e:
            send_info(f"Error: {e}")

    hilo = threading.Thread(target=descarga)
    hilo.start()


def cargar_portapapeles():

    try:
        texto_portapapeles = ventana.clipboard_get().strip()

        reproducir_sonido()

        if not texto_portapapeles.startswith("https://www.youtube.com"):
            send_info("La URL no corresponde a Youtube")
            return

        elif es_dir_web(texto_portapapeles):

            entry.delete(0, tk.END)
            entry.insert(0, texto_portapapeles)

            send_info("URL pegada desde portapapeles")
            boton_descarga.config(state="normal")

        else:
            send_info("No es una dirección web")

    except tk.TclError:
        send_info("El portapapeles está vacío")


def send_info(mensaje):

    ventana.after(
        0,
        lambda: label_info.config(text=mensaje)
    )


def es_dir_web(url):

    return validators.url(url)


def play_sound(ruta):

    playsound(str(ruta))


def reproducir_sonido():

    ruta = obtener_ruta(
        "sonido/mixkit-water-sci-fi-bleep-902.wav"
    )

    if ruta.exists():

        hilo = threading.Thread(
            target=play_sound,
            args=(ruta,),
            daemon=True
        )

        hilo.start()


# --------------------------------------------------
# INTERFAZ GRÁFICA
# --------------------------------------------------

ventana = tk.Tk()
ventana.title("Extractor Youtube")
ventana.geometry("420x260")

etiqueta = tk.Label(
    ventana,
    text="Ingrese URL"
)
etiqueta.pack()

entry = tk.Entry(
    ventana,
    width=55
)
entry.pack(pady=5)

label_info = tk.Label(
    ventana,
    text="",
    bg="#bde0fe",
    width=50
)
label_info.pack(pady=5)

modo = tk.StringVar(value="Audio")

radio_audio = tk.Radiobutton(
    ventana,
    text="Audio",
    variable=modo,
    value="Audio"
)

radio_video = tk.Radiobutton(
    ventana,
    text="Video",
    variable=modo,
    value="Video"
)

radio_audio.pack(anchor="w", padx=10)
radio_video.pack(anchor="w", padx=10)

progress_bar = ttk.Progressbar(
    ventana,
    orient="horizontal",
    length=350,
    mode="determinate"
)

progress_bar.pack(pady=10)

boton_pegar = tk.Button(
    ventana,
    text="Pegar URL",
    command=cargar_portapapeles
)

boton_pegar.pack(side="left", padx=10)

boton_descarga = tk.Button(
    ventana,
    text="Descargar",
    command=lambda: descargar(entry.get(), modo.get())
)

boton_descarga.pack(side="left", padx=10)

boton_descarga.config(state="disabled")

ventana.mainloop()
