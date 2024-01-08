# %%
import pandas as pd
from openai import OpenAI
client = OpenAI(api_key='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')
# %%


def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding


# %%
data = {'CONTENT': ["Siguiente"],
        'EMBEDDINGS': [get_embedding("Siguiente")]}

df = pd.DataFrame(data)
df
# %%
resultados = []
strings = ["Siguiente", "Anterior", "Parar", "Pausa", "Reproduce", "Reanuda", "Continua", "Spotify", "Musica", "Cancion",
           "Crea un Documento sobre", "Documento", "Word", "Generar", "Archivo", "Alarma", "pm", "am", "pon una alarma", "inicia",
           "Temporizador", "Segundos", "Timer", "Minutos", "Investiga", "Busca", "Google", "Averigua",
           "Habla", "Selecciona", "Voz", "Clona", "Salir", "Cerrar", "Terminar", "Finalizar", "Cierra"]


# %%
for string in strings:
    df.loc[len(df)] = [string, get_embedding(string)]

# %%
df.to_csv("skills.csv")
# %%
df
