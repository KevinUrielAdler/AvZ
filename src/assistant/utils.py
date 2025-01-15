"""
Este módulo contiene funciones auxiliares para el funcionamiento del asistente.

Es importado por el módulo de habilidades del asistente virtual, `src/assistant/skills.py`
"""
from time import sleep
import requests
import json
import re

from scipy.io.wavfile import write
from elevenlabs import set_api_key
from unidecode import unidecode
from bs4 import BeautifulSoup
from numpy.linalg import norm
from openai import OpenAI
import sounddevice as sd
import numpy as np
import tempfile
import pygame

import config
from config import SPOTIFY_TOKEN as TOKEN

# constantes
client = OpenAI(api_key=config.OPEN_AI_API_KEY)
set_api_key(config.TTS_API_KEY)


def getLinks(query: str, n=5) -> list:
    """
    Obtiene una lista de enlaces de búsqueda de Google para una consulta dada.

    Parámetros:
    - query (str): Consulta a buscar en Google.
    - n (int, opcional): Número de enlaces a obtener. Por defecto 2.

    Retorna:
    - links (list): Lista de enlaces.
    """
    links = []
    query = "+".join(query.lower().split())
    query = unidecode(query)
    # se obtienen los enlaces de la búsqueda
    page = requests.get('https://www.google.com/search?q=' + query)
    soup = BeautifulSoup(page.content, features='html.parser')
    # se filtran los enlaces
    for link in soup.find_all("a", href=re.compile("(?<=/url\\?q=)(https://.)")):
        token = re.split(":(?=http)", link["href"].replace("/url?q=", ""))[0]
        token = token.split("&sa=")
        if not token[0].endswith('.xml') and not token[0].endswith('.pdf') and not token[0].startswith('https://www.google') and not token[0].startswith('https://maps.google.com') and not token[0].startswith('https://es.wikipedia.org/'):
            links.append(token[0])

    return links[:n]


def getWebText(url: str) -> list:
    """
    Obtiene el texto de un sitio web.

    Parámetros:
    - url (str): URL del sitio web.

    Retorna:
    - res (list): Lista de párrafos del sitio web.
    """
    text = ''
    # se obtiene el texto del sitio web
    result = requests.get(url, timeout=1)
    # se filtra el texto
    soup = BeautifulSoup(result.content, features="html.parser")
    # se obtienen los párrafos
    article = soup.find_all('p')
    # se filtran los párrafos
    for e in article:
        text += f'\n' + ''.join(e.findAll(string=True))
    res = text.split("\n")
    res = [e + "\n" for e in res if len(e) > 50]

    return res


def get_embedding(text: str, model="text-embedding-ada-002") -> any:
    """
    Obtiene el embedding de un texto.

    Parámetros:
    - text (str): Texto a obtener el embedding.
    - model (str, opcional): Modelo de OpenAI para obtener el embedding. Por defecto "text-embedding-ada-002".

    Retorna:
    - (embedding): Embedding del texto.
    """
    text = text.replace("\n", " ")

    return client.embeddings.create(input=[text], model=model).data[0].embedding


def cosine_similarity(A: any, B: any) -> float:
    """
    Obtiene la similitud coseno entre dos vectores.

    Parámetros:
    - A (embedding): Primer vector.
    - B (embedding): Segundo vector.

    Retorna:
    - (float): Similitud coseno entre los vectores.
    """
    return np.dot(A, B)/(norm(A)*norm(B))


def euclidean_distance(A: any, B: any) -> float:
    """
    Obtiene la distancia euclidiana entre dos vectores.

    Parámetros:
    - A (embedding: Primer vector.
    - B (embedding): Segundo vector.

    Retorna:
    - distance (float): Distancia euclidiana entre los vectores.
    """
    A = np.array(A)
    B = np.array(B)
    squared_diff = np.square(A - B)
    sum_squared_diff = np.sum(squared_diff)
    distance = np.sqrt(sum_squared_diff)
    if distance == 0:
        return 0.1

    return distance


def getContext(embedd: any, links: list, n=3) -> dict:
    """
    Obtiene el contexto de un texto.

    Parámetros:
    - embedd (embedding): Embedding del texto.
    - links (list): Lista de enlaces de sitios web.
    - n (int, opcional): Número de párrafos a obtener. Por defecto 3.

    Retorna:
    - context (dict): Diccionario de párrafos con su similitud coseno con el texto.
    """
    context = {}
    text = []
    # se obtiene el texto de los enlaces
    for link in links:
        try:
            text += getWebText(link)
        except Exception as e:
            pass
    # se obtiene la similitud coseno de cada párrafo con el texto
    for t in text:
        t_embedd = get_embedding(t)
        score = cosine_similarity(embedd, t_embedd)
        context[t] = score
    # se ordena el diccionario de mayor a menor
    context = dict(
        sorted(context.items(), key=lambda item: item[1], reverse=True))
    # se obtienen los n párrafos con mayor similitud coseno
    top = {}
    keys = list(context.keys())
    for key in keys[:n]:
        top[key] = context[key]

    return top


def play_audio(filename: str):
    """
    Reproduce un archivo de audio.

    Parámetros:
    - filename (str): Nombre del archivo de audio.
    """
    try:
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play()
    except Exception as e:
        print(e)


def generate_audio(text: str, idx: int, events=None):
    """
    Genera un archivo de audio a partir de un texto.

    Parámetros:
    - text (str): Texto a convertir a audio.
    - idx (int): Índice del evento.
    - events (list, opcional): Lista de eventos. Por defecto None.
    """
    print(f"Audio thread {idx} Started.")
    # Se obtiene la clave de Eleven Labs
    with open("src/assistant/files/vkey.txt", "r") as archivo:
        vkey = archivo.read()
    CHUNK_SIZE = 1024
    # Se obtiene el audio de Eleven Labs
    url = "https://api.elevenlabs.io/v1/text-to-speech/" + vkey.strip()
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": config.TTS_API_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.75,
            "similarity_boost": 0.5,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }
    response = requests.post(url, json=data, headers=headers)
    # Se guarda el audio en un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
        f.flush()
        temp_filename = f.name
    # Si hay eventos, se espera a que termine el audio anterior
    if idx > 0:
        print(f"Waiting for audio event {idx-1} to finish...")
        events[idx-1].wait()
    # Se reproduce el audio
    print(f"Playing audio {idx}...")
    play_audio(temp_filename)
    # Se elimina el archivo temporal
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    if events != None:
        print(f"Audio event {idx} finished.")
        events[idx].set()


def timer_timer(seconds: int):
    """
    Reproduce un archivo de audio de alarma después de un tiempo determinado.

    Parámetros:
    - seconds (int): Tiempo en segundos para reproducir el audio.
    """
    sleep(seconds)
    play_audio("src/assistant/sounds/timer.mp3")


def alarm_timer(seconds: int):
    """
    Reproduce un archivo de audio de alarma en el tiempo asignado.

    Parámetros:
    - seconds (int): Tiempo en segundos para reproducir el audio.
    """
    sleep(seconds)
    play_audio("src/assistant/sounds/alarm.mp3")


def getVkey(archivo: str, nombre_buscado: str) -> any:
    """
    Obtiene la clave de Eleven Labs de un archivo JSONL.

    Parámetros:
    - archivo (str): Nombre del archivo JSONL.
    - nombre_buscado (str): Nombre de la voz buscada.

    Retorna:
    - (any): Clave de Eleven Labs.
    """
    # Se lee el archivo JSONL
    with open(archivo, "r") as archivo_jsonl:
        lineas_jsonl = archivo_jsonl.readlines()
    # Se busca la clave de la voz
    for linea_jsonl in lineas_jsonl:
        dato = json.loads(linea_jsonl)
        # Si se encuentra la voz, se retorna la clave
        if dato.get("voz") == nombre_buscado:
            return dato.get("clave")

    return None


def record_audio(duration: int) -> (any, int):
    """
    Graba un audio.

    Parámetros:
    - duration (int): Duración del audio en segundos.

    Retorna:
    - (any, int): Audio grabado y frecuencia de muestreo.
    """
    # se coloca la frecuencia de muestreo y la duración deseada
    fs = 44100  # 44.1 kHz
    seconds = duration
    # se graba el audio
    print(f"Recording for {seconds} seconds...")
    play_audio("src/assistant/sounds/blink_a.mp3")
    audio_data = sd.rec(int(fs * seconds), samplerate=fs,
                        channels=2, dtype='int16')
    sd.wait()
    play_audio("src/assistant/sounds/blink_a.mp3")
    print("Recording complete.")
    return audio_data, fs


def save_audio(data: any, fs: int, filename='output.wav'):
    """
    Guarda un audio en un archivo WAV.

    Parámetros:
    - data (any): Audio a guardar.
    - fs (int): Frecuencia de muestreo.
    - filename (str, opcional): Nombre del archivo WAV. Por defecto 'output.wav'.
    """
    write(filename, fs, data)
