from datetime import datetime
import requests
import threading
import os

from elevenlabs import clone
from docx import Document
import pandas as pd
import spotipy

from assistant.utils import TOKEN
import assistant.utils as utils


def CrearDocumentoTxt(nombreArchivo, contenido, ruta=''):
    try:
        with open(ruta + nombreArchivo, 'w') as archivo:
            archivo.write(contenido)
    except:
        return False
    return True


def LeerDocumentoTxt(nombreArchivo, ruta=''):
    contenido = ''
    try:
        with open(ruta + nombreArchivo, 'r') as archivo:
            contenido = archivo.read()
    except:
        return False, contenido
    return True, contenido


def AgregarContenidoDocumentoTxt(nombreArchivo, contenido, ruta=''):
    try:
        with open(ruta + nombreArchivo, 'a') as archivo:
            archivo.write(contenido)
    except:
        return False
    return True


def AgregarContenidoWord(Tit, contenido, document):
    document.add_heading(Tit, level=1)
    while '[tit|' in contenido:
        inicomand = contenido.index('[tit|')

        document.add_paragraph(contenido[:inicomand])

        contenido = contenido.replace("[tit|", "", 1)
        fincomand = contenido.find(']', inicomand)
        if fincomand == -1:
            break
        subtit = contenido[inicomand:fincomand]
        contenido = contenido[:fincomand]+contenido[fincomand+1:]

        document.add_heading(subtit, level=2)

    document.add_paragraph(contenido)


def CrearDocAux(topic):
    links = utils.getLinks(topic, 2)
    utils.generate_audio(
        "Dame un momento para conseguir la información y crear tu documento", 0)
    context = ""
    links = utils.getLinks(topic)
    print(links)
    embedd = utils.get_embedding(topic)
    webContext = utils.getContext(embedd, links, 10)
    for i in webContext:
        context += i
    messages = [{"role": "user", "content": "information:"+context}]
    tools = [
        {
            "type": "function",
            "function": {
                    "name": "CrearDocumentoWord",
                    "description": "Creates a word document about the given information",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "nombreArchivo": {
                                "type": "string",
                                "description": "A single-word name for the file",
                            },
                            "tema": {
                                "type": "string",
                                "description": "An adecuate title for the document",
                            },
                            "introduccion": {
                                "type": "string",
                                "description": "An adecuate introduction for the investigation",
                            },
                            "desarrollo": {
                                "type": "string",
                                "description": "An adecuate development for the investigation",
                            },
                            "conclusion": {
                                "type": "string",
                                "description": "An adecuate conclusion for the investigation",
                            }
                        },
                        "required": ["nombreArchivo", "tema", "introduccion", "desarrollo", "conclusion"],
                    }
            },
        }
    ]
    response = utils.client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    f_name = tool_calls[0].function.name
    if f_name == 'CrearDocumentoWord':
        CrearDocumentoWord(utils.json.loads(
            tool_calls[0].function.arguments).get('nombreArchivo'), utils.json.loads(
            tool_calls[0].function.arguments).get('tema'), utils.json.loads(
            tool_calls[0].function.arguments).get('introduccion'), utils.json.loads(
            tool_calls[0].function.arguments).get('desarrollo'), utils.json.loads(
            tool_calls[0].function.arguments).get('conclusion'))


def CrearDocumentoWord(nombreArchivo, tema, introduccion, desarrollo, conclusion, ruta=''):
    document = Document()
    document.add_heading(tema, 0)

    AgregarContenidoWord("Introducción", introduccion, document)
    AgregarContenidoWord("Desarrollo", desarrollo, document)
    AgregarContenidoWord("Conclusión", conclusion, document)

    document.save(ruta + nombreArchivo+'.docx')

    os.startfile(ruta + nombreArchivo+'.docx')


def research(query):
    utils.generate_audio("Dame un momento para conseguir la información", 0)
    context = ""
    links = utils.getLinks(query)
    print(links)
    embedd = utils.get_embedding(query)
    webContext = utils.getContext(embedd, links)
    for i in webContext:
        context += i
    completion = utils.client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Responde muy brevemente."},
            {"role": "user", "content": "Dado el siguiente contexto: " +
                context + "Responde: " + query}
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
        print(chunk_message)
        if chunk_message == '.' or chunk_message == None or chunk_message == ". \n" or chunk_message == ".\n":
            collected_messages = [
                m for m in collected_messages if m is not None]
            reply_content = ''.join([m for m in collected_messages])
            reply_content = reply_content.replace('.', '')

            if (idx != 0):
                reply_content = reply_content[1:]
            # print("Reply:" + reply_content)
            c = ". "
            if chunk_message == None:
                c = ""
            output = output + reply_content + c
            collected_messages = []
            print(reply_content)

            if reply_content != "":

                events.append(threading.Event())
                threads.append(threading.Thread(
                    target=utils.generate_audio, args=(reply_content, idx)))

                idx = idx+1
        collected_messages.append(chunk_message)

    for thread in threads:
        thread.daemon = True
        thread.start()

    return output


def PlayInSpotify(sec=0, song="spotify:track:4UOt0ObZ4Oqi7LSU1Gzzkq"):
    url = 'https://api.spotify.com/v1/me/player/play'
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        'Content-Type': 'application/json'
    }
    data = {
        # "context_uri": play,
        "uris": [
            song
        ],
        "offset": {
            "position": 0
        },
        "position_ms": sec*1000
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 204:
        print("Solicitud exitosa.")
        print(response.text)
    else:
        print(f"Error en la solicitud: {response.status_code}")
        print(response.text)


def PreviousSong():
    sp = spotipy.Spotify(auth=TOKEN)
    try:
        sp.previous_track(device_id=None)
    except:
        pass


def NextSong():
    sp = spotipy.Spotify(auth=TOKEN)
    try:
        sp.next_track()
    except:
        pass


def SearchASong(name):
    sp = spotipy.Spotify(auth=TOKEN)
    try:
        a = sp.search(q=name, limit=1, offset=0, type='track',
                      market=None)['tracks']['items'][0]['uri']
        PlayInSpotify(0, a)
    except:
        pass


def ResumeASong():
    sp = spotipy.Spotify(auth=TOKEN)
    try:
        sp.start_playback(device_id=None)
    except:
        pass


def PauseASong():
    sp = spotipy.Spotify(auth=TOKEN)
    try:
        sp.pause_playback(device_id=None)
    except:
        pass


def set_timer(seconds):
    utils.generate_audio(f"Timer de {seconds} segundos establecida", 0)
    timer_thread = threading.Thread(
        target=utils.timer_timer, args=(int(seconds), ))
    timer_thread.daemon = True
    timer_thread.start()


def set_alarm(hour):
    utils.generate_audio(f"Alarma establecida a las {hour}", 0)

    hours_a, minutes_a = map(int, hour.split(':'))

    hours_b, minutes_b, secs_b = map(
        int, datetime.now().strftime("%H:%M:%S").split(":"))

    hours = hours_a - hours_b
    minutes = minutes_a - minutes_b

    seconds = hours*3600 + minutes*60 - secs_b

    if seconds < 0:
        seconds = 24*3600 + seconds

    timer_thread = threading.Thread(
        target=utils.alarm_timer, args=(seconds, ))
    timer_thread.daemon = True
    timer_thread.start()


def clone_voice(name):
    audio_data, fs = utils.record_audio(20)
    utils.save_audio(audio_data, fs)
    voice = clone(
        name=name,
        description="A test for creating a voice",  # Optional
        files=["output.wav"]
    )
    with open("src/assistant/files/vkey.txt", "w") as archivo:
        archivo.write(voice.voice_id)
    with open("src/assistant/files/voces.jsonl", 'a') as archivo:
        utils.json.dump(
            {"voz": voice.name, voice.voice_id: "ynvBVrXc205UzwgmRbNS"}, archivo)
    # Añade un salto de línea al final para mantener el formato JSON Lines
        archivo.write('\n')
    utils.generate_audio(f"Listo, ahora puedes utilizar esta voz bajo el nombre {
        voice.name}", 0)
    os.remove("output.wav")


def select_voice(name):
    name = name.lower()

    events = [threading.Event()]

    vkey = utils.getVkey("src/assistant/files/voces.jsonl", name)

    if vkey is not None:

        with open("src/assistant/files/vkey.txt", "w") as archivo:
            archivo.write(vkey)

        utils.generate_audio("Listo, esta es mi nueva voz", 0)

    else:
        utils.generate_audio(
            "Lo siento, la voz seleccionada no existe, puedo clonar una voz si me lo pides, recuerda especificar un nombre para la voz!", 0)


def Salir():
    utils.generate_audio("Hasta luego", 0)
    exit()


def brain(content, stm):
    content = content[:-1]
    df_skills = pd.read_csv("src/assistant/files/skills.csv")
    embedd = utils.get_embedding(content)

    df_skills['EMBEDDINGS'] = df_skills.EMBEDDINGS.apply(
        eval).apply(utils.np.array)
    df_skills['SCORE'] = df_skills.EMBEDDINGS.apply(
        lambda x: (1/utils.euclidean_distance(x, embedd))**(6))

    print(df_skills['SCORE'].max())

    if df_skills['SCORE'].max() > 20:
        print("Se va a ejecutar una función")
        messages = [{"role": "user", "content": content}]
        tools = [
            {
                "type": "function",
                "function": {
                        "name": "set_timer",
                        "description": "Creates a timer",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "duration": {
                                    "type": "string",
                                    "description": "The duration of the timer in seconds",
                                }
                            },
                            "required": ["duration"],
                        },
                },
            },
            {
                "type": "function",
                "function": {
                        "name": "CrearDocAux",
                        "description": "Activates when words like create, crea, genera are used",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "topic": {
                                    "type": "string",
                                    "description": "The topic of the document",
                                }
                            },
                            "required": ["topic"],
                        }
                }
            },
            {
                "type": "function",
                "function": {
                        "name": "set_alarm",
                        "description": "Creates an alarm using the hour",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "hour": {
                                    "type": "string",
                                    "description": "The hour of the alarm in format HH:MM, the hour should be in 24h format",
                                }
                            },
                            "required": ["hour"],
                        },
                },
            },

            {
                "type": "function",
                "function": {
                        "name": "select_voice",
                        "description": "Select a voice by name",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "single-word name for selecting the voice",
                                }
                            },
                            "required": ["name"],
                        },
                },
            },

            {
                "type": "function",
                "function": {
                        "name": "clone_voice",
                        "description": "Starts a procces that record and clone voice",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "single-word name",
                                }
                            },
                            "required": ["name"],
                        },
                },
            },
            {
                "type": "function",
                "function": {
                        "name": "SearchASong",
                        "description": "used when request a song in spotify, a name should be provided",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "name of the requested song",
                                }
                            },
                            "required": ["name"],
                        },
                },
            },
            {
                "type": "function",
                "function": {
                        "name": "research",
                        "description": "activated when words like busca, investiga, averigua, busca en internet are used",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "what is going to be researched",
                                }
                            },
                            "required": ["query"],
                        },
                },
            },
            {
                "type": "function",
                "function": {
                        "name": "ResumeASong",
                        "description": "used for resume or continue the music, instructions like play, continuar, resumir, sigue",
                }
            },
            {
                "type": "function",
                "function": {
                        "name": "PauseASong",
                        "description": "used for pause or quit the music, instructions like para, quita la musica, detente",

                }
            },
            {
                "type": "function",
                "function": {
                        "name": "NextSong",
                        "description": "used for skip a song or go next, instructions like siguiente, reproduce la siguiente canción",

                }
            },
            {
                "type": "function",
                "function": {
                        "name": "PreviousSong",
                        "description": "used for go back a song or play previous, instructions like anterior, regresa, reproduce la canción anterior",
                }
            },
            {
                "type": "function",
                "function": {
                        "name": "Salir",
                        "description": "used for quit the program, instructions like salir, termina, cierra",
                }
            }
        ]
        response = utils.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            tools=tools,
            tool_choice="auto",  # auto is default, but we'll be explicit
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        f_name = tool_calls[0].function.name
        out = ""
        if f_name == 'set_timer':
            set_timer(utils.json.loads(
                tool_calls[0].function.arguments).get('duration'))
        if f_name == 'CrearDocAux':
            hilo = threading.Thread(target=CrearDocAux, args=(
                utils.json.loads(
                    tool_calls[0].function.arguments).get('topic'),))
            hilo.daemon = True
            hilo.start()
        if f_name == 'set_alarm':
            set_alarm(utils.json.loads(
                tool_calls[0].function.arguments).get('hour'))
        if f_name == 'select_voice':
            select_voice(utils.json.loads(
                tool_calls[0].function.arguments).get('name'))
        if f_name == 'research':
            out = utils.research(utils.json.loads(
                tool_calls[0].function.arguments).get('query'))
        if f_name == 'clone_voice':
            clone_voice(utils.json.loads(
                tool_calls[0].function.arguments).get('name'))
        if f_name == 'SearchASong':
            SearchASong(utils.json.loads(
                tool_calls[0].function.arguments).get('name'))
        if f_name == 'ResumeASong':
            ResumeASong()
        if f_name == 'PauseASong':
            PauseASong()
        if f_name == 'NextSong':
            NextSong()
        if f_name == 'PreviousSong':
            PreviousSong()
        if f_name == 'Salir':
            Salir()

        if out == "":
            return f"Se ejecutó la función {f_name}"
        return out.strip()

    else:
        print("Se va a conversar")
        completion = utils.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Responde amigablemente en máximo 3 oraciones"},
                {"role": "user", "content": "Te llamas Zaid y eres un asistente virtual"},
                {"role": "user", "content": stm[0]},
                {"role": "assistant", "content": stm[1]},
                {"role": "user", "content": stm[2]},
                {"role": "assistant", "content": stm[3]},
                {"role": "user", "content": stm[4]},
                {"role": "assistant", "content": stm[5]},
                {"role": "user", "content": stm[6]},
                {"role": "assistant", "content": stm[7]},
                {"role": "user", "content": stm[8]},
                {"role": "assistant", "content": stm[9]},
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
            # extract the message
            chunk_message = chunk.choices[0].delta.content

            if chunk_message == '.' or chunk_message == None or chunk_message == ". \n" or chunk_message == ".\n":

                collected_messages = [
                    m for m in collected_messages if m is not None]
                reply_content = ''.join([m for m in collected_messages])
                reply_content = reply_content.replace('.', '')
                if (idx != 0):
                    reply_content = reply_content[1:]
                output = output + reply_content + ". "
                collected_messages = []

                reply_content = reply_content.strip()
                if reply_content != "":
                    print("Reply:" + reply_content)

                    events.append(threading.Event())
                    threads.append(threading.Thread(
                        target=utils.generate_audio, args=(reply_content, idx, events)))

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
