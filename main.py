import tkinter as tk
import validators
import threading
import yt_dlp
from tkinter import ttk
from playsound import playsound
import os


def descargar(url, modo):

    progress_bar["value"] = 0
    send_info("Iniciando descarga...")

    def progreso(d):
        if d['status'] == 'downloading':
            if 'total_bytes' in d and 'downloaded_bytes' in d:
                total = d['total_bytes']
                descargado = d['downloaded_bytes']
                porcentaje = descargado / total * 100
                progress_bar["value"] = porcentaje

        if d['status'] == 'finished':
            send_info("Procesando archivo...")

    def descarga():
        carpeta = r"C:\Proyectos\Python\Extractor_Youtube\folder"

        # Crear la carpeta si no existe
        os.makedirs(carpeta, exist_ok=True)

        try:

            if modo == "Audio":

                opciones = {
                    "format": "bestaudio/best",
                    "outtmpl": os.path.join(carpeta, "%(title)s.%(ext)s"),
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
                    "outtmpl": os.path.join(carpeta, "%(title)s.%(ext)s"),
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
            progress_bar["value"] = 100

        except Exception as e:
            send_info(f"Error: {e}")

    hilo = threading.Thread(target=descarga)
    hilo.start()


def cargar_portapapeles():

    texto_portapapeles = ventana.clipboard_get()

    reproducir_sonido()

    if not texto_portapapeles.startswith('https://www.youtube'):
        send_info("La URL no corresponde a Youtube")
        return

    elif es_dir_web(texto_portapapeles):

        entry.delete(0, tk.END)
        entry.insert(0, texto_portapapeles)

        send_info("URL pegada desde portapapeles")
        boton_descarga.config(state='normal')

    else:
        send_info("No es una dirección web")


def send_info(mensaje):
    label_info.config(text=mensaje)


def es_dir_web(url):
    return validators.url(url)


def play_sound(ruta):
    playsound(ruta)


def reproducir_sonido():

    hilo = threading.Thread(
        target=play_sound,
        args=(r'sonido\mixkit-water-sci-fi-bleep-902.wav',)
    )

    hilo.start()


# ---------------- GUI ----------------

ventana = tk.Tk()
ventana.title("Extractor Youtube")
ventana.geometry("420x260")

etiqueta = tk.Label(ventana, text="Ingrese URL")
etiqueta.pack()

entry = tk.Entry(ventana, width=55)
entry.pack(pady=5)

label_info = tk.Label(bg='#bde0fe', width=50)
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
    text='Pegar URL',
    command=cargar_portapapeles
)

boton_pegar.pack(side="left", padx=10)

boton_descarga = tk.Button(
    ventana,
    text='Descargar',
    command=lambda: descargar(entry.get(), modo.get())
)

boton_descarga.pack(side="left", padx=10)
boton_descarga.config(state='disabled')

ventana.mainloop()