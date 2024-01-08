from unidecode import unidecode
import requests
from bs4 import BeautifulSoup
import re
import os
from openai import OpenAI
import numpy as np
from numpy.linalg import norm
import tiktoken
import pygame
from elevenlabs import set_api_key
import tempfile
import threading
import pandas as pd

import config

client = OpenAI(api_key=config.OPEN_AI_API_KEY)
set_api_key(config.TTS_API_KEY)
# %%MODULO DE OBTENCIÓN DE INFORMACIÓN


def getLinks(query):
    links = []
    query = "+".join(query.lower().split())
    query = unidecode(query)
    page = requests.get('https://www.google.com/search?q=' + query)
    soup = BeautifulSoup(page.content, features='html.parser')
    for link in soup.find_all("a", href=re.compile("(?<=/url\?q=)(https://.)")):
        token = re.split(":(?=http)", link["href"].replace("/url?q=", ""))[0]
        token = token.split("&sa=")
        if not token[0].endswith('.xml') and not token[0].endswith('.pdf') and not token[0].startswith('https://www.google.comhttps://support') and not token[0].startswith('https://maps.google.com'):
            links.append(token[0])
    return links[:4]

# %%Obtener información de los links


def getWebText(url):
    text = ''
    result = requests.get(url, timeout=1)
    content = result.content
    soup = BeautifulSoup(result.content, features="html.parser")
    article = soup.find_all('p')
    for e in article:
        text += ' \n' + ''.join(e.findAll(string=True))
    res = text.split("\n")
    res = [e + "\n" for e in res if len(e) > 50]
    return res

# %%


def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def cosine_similarity(A, B):
    return np.dot(A, B)/(norm(A)*norm(B))

# %%


def getContext(embedd, links):
    context = {}
    text = []
    for link in links:
        try:
            text += getWebText(link)
        except Exception as e:
            pass

    # Estimación de costos con tiktoken.
    num_tokens = 0
    for t in text:
        encoding = tiktoken.get_encoding('cl100k_base')
        num_tokens = num_tokens + len(encoding.encode(t))

    # if(True):#input() == 'y'):
    for t in text:
        t_embedd = get_embedding(t)
        score = cosine_similarity(embedd, t_embedd)
        context[t] = score
    context = dict(
        sorted(context.items(), key=lambda item: item[1], reverse=True))
    top = {}
    keys = list(context.keys())
    for key in keys[:2]:
        top[key] = context[key]
    return top
# %%


def play_audio(filename):
    pygame.mixer.init()

    # Cargar el archivo de audio
    pygame.mixer.music.load(filename)

    # Reproducir el audio
    pygame.mixer.music.play()

# %%


def generate_audio(text, idx, events):
    print("Se ha llamado a generar audio")
    CHUNK_SIZE = 1024
    url = "https://api.elevenlabs.io/v1/text-to-speech/8ccqPwgP8jhKZ8CvbXQo"

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

    # Save audio data to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)
        f.flush()
        temp_filename = f.name

    if idx > 0:
        events[idx-1].wait()

    play_audio(temp_filename)
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    events[idx].set()


# %% CONVERSATIONAL CHATBOT

# %%stream responses
# ltm = pd.read_csv("ltm.csv")
# ltm['EMBEDDINGS'] = ltm.EMBEDDINGS.apply(eval).apply(np.array)
# %%


def brain(content, stm):
    embedd = get_embedding(content)
    # Modulo para elección de acción

    # Long Term Memory Read
    # ltm['SCORE'] = ltm.EMBEDDINGS.apply(lambda x: cosine_similarity(x, embedd))

    # df_asst = ltm[ltm['ROLE'] == 'Assistant']
    # df_user = ltm[ltm['ROLE'] == 'User']

    # ltm_a = ""
    # ltm_u = ""

    # if df_asst['SCORE'].max() > .8:
    #    ltm_a = "En alguna conversación pasada mencionaste que: " + df_asst.at[df_asst['SCORE'].idxmax(), 'CONTENT']
    # if df_user['SCORE'].max() > .8:
    #   ltm_u = "En alguna conversación pasada mencioné: " + df_user.at[df_user['SCORE'].idxmax(), 'CONTENT']

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Responde muy brevemente."},
            # Long-term Memory

            #   {"role": "user", "content": ltm_u},
            #  {"role": "user", "content": ltm_a},

            # Short-term Memory
            {"role": "user", "content": stm[0]},
            {"role": "assistant", "content": stm[1]},
            {"role": "user", "content": stm[2]},
            {"role": "assistant", "content": stm[3]},
            {"role": "user", "content": stm[4]},
            {"role": "assistant", "content": stm[5]},

            # Question
            {"role": "user", "content": content}
        ],
        temperature=0.3,
        max_tokens=100,
        stream=True
    )

    audio_fn = []
    collected_chunks = []
    collected_messages = []
    output = ""
    idx = 0

    threads = []
    events = []

    for chunk in completion:

        collected_chunks.append(chunk)  # save the event response
        chunk_message = chunk.choices[0].delta.content  # extract the message

        if chunk_message == '.' or chunk_message == None or chunk_message == ". \n" or chunk_message == ".\n":

            collected_messages = [
                m for m in collected_messages if m is not None]
            reply_content = ''.join([m for m in collected_messages])
            reply_content = reply_content.replace('.', '')
            if (idx != 0):
                reply_content = reply_content[1:]
            output = output + reply_content + ". "
            collected_messages = []

            if reply_content != "":
                events.append(threading.Event())
                threads.append(threading.Thread(
                    target=generate_audio, args=(reply_content, idx, events)))
                idx = idx+1

        collected_messages.append(chunk_message)  # save the message

    for thread in threads:
        thread.daemon = True
        thread.start()

    stm.pop(0)
    stm.pop(0)
    stm.append(content)
    stm.append(output)
    return output

    # Long term memory update
    # u_emb = get_embedding(content)
    # ass_emb = get_embedding(output)

    # ltm.loc[len(ltm.index)] = ['User', content, u_emb, 0]

    # ltm.loc[len(ltm.index)] = ['Assistant', output, ass_emb, 0]

    # ltm.to_csv('ltm.csv', index=False)


# %%
# audio_fn

# %%
