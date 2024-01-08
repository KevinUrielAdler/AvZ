"""
Este módulo contiene funciones auxiliares relacionadas con la detección de voz.

Es importado por el módulo principal del asistente virtual, 'src/main.py'
"""
import azure.cognitiveservices.speech as speechsdk

# constantes
speech_key, service_region = "9f490b1316b54e07aa923fdc8b3a07eb", "eastus"


def keyword_function_mic() -> bool:
    """
        Ejecuta el reconocimiento de voz de una palabra clave en un período de tiempo indefinido.

        Retorna:
        - (bool): Cuando se detecta la palabra clave.
    """
    # Crea una instancia del modelo de reconocimiento de voz con la palabra clave.
    model = speechsdk.KeywordRecognitionModel(
        "resources/models/computer.table")
    # Crea un keyword recognizer local con el micrófono como entrada predeterminada.
    keyword_recognizer = speechsdk.KeywordRecognizer()
    done = False

    # Agrega el modelo al reconocedor.
    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        result = evt.result
        nonlocal done
        done = True
    keyword_recognizer.recognized.connect(recognized_cb)
    # Empieza el reconocimiento de voz.
    result_future = keyword_recognizer.recognize_once_async(model)
    # Espera a que se detecte la palabra clave.
    stop_future = keyword_recognizer.stop_recognition_async()
    stop_future.get()

    return True


def speech_recognize_once_from_mic() -> str:
    """
        Ejecuta el reconocimiento de voz desde el micrófono.

        Retorna:
        - (str): Texto reconocido.
    """
    print("Escuchando...")
    # Crea una instancia del modelo de reconocimiento de voz con la palabra clave.
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region, speech_recognition_language="es-MX")
    # Crea un reconocedor de voz con el micrófono como entrada predeterminada.
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
    # Reconoce la entrada de voz.
    result = speech_recognizer.recognize_once()
    # Comprueba el resultado.
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))

        return result.text

    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")

        return ""

    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(
                cancellation_details.error_details))

        return ""
