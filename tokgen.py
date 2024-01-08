import webbrowser
import random
import string


def generate_random_string(length):
    """Genera una cadena aleatoria de longitud especificada."""
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


def ObtenerToken():
    client_id = 'f7437e968c8c4620a587c6f32246a5bd'
    redirect_uri = 'http://localhost:8888/callback'
    state = generate_random_string(16)
    scope = 'user-read-private user-read-email user-read-playback-state user-modify-playback-state user-read-currently-playing'

    auth_url = f'https://accounts.spotify.com/authorize?response_type=token&client_id={client_id}&scope={scope}&redirect_uri={redirect_uri}&state={state}'

    webbrowser.open(auth_url)

ObtenerToken()
