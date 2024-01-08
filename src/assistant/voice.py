import azure.cognitiveservices.speech as speechsdk


speech_key, service_region = "9f490b1316b54e07aa923fdc8b3a07eb", "eastus"

def keyword_function_mic():
    """runs keyword spotting locally, with direct access to the result audio"""

    # Creates an instance of a keyword recognition model. Update this to
    # point to the location of your keyword recognition model.
    model = speechsdk.KeywordRecognitionModel(
        "resources/models/computer.table")

    # Create a local keyword recognizer with the default microphone device for input.
    keyword_recognizer = speechsdk.KeywordRecognizer()

    done = False

    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        result = evt.result
        nonlocal done
        done = True

    # def canceled_cb(evt: speechsdk.SpeechRecognitionCanceledEventArgs):
    #     result = evt.result
    #     if result.reason == speechsdk.ResultReason.Canceled:
    #         print('CANCELED: {}'.format(result.cancellation_details.reason))
    #     nonlocal done
    #     done = True

    # Connect callbacks to the events fired by the keyword recognizer.
    keyword_recognizer.recognized.connect(recognized_cb)
    # keyword_recognizer.canceled.connect(canceled_cb)

    # Start keyword recognition.
    result_future = keyword_recognizer.recognize_once_async(model)
    # print('Say something starting with "{}" followed by whatever you want...'.format(keyword))
    result = result_future.get()

    stop_future = keyword_recognizer.stop_recognition_async()
    # print('Stopping...')
    stopped = stop_future.get()

    return True


def speech_recognize_once_from_mic():
    """performs one-shot speech recognition from the default microphone"""
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region, speech_recognition_language="es-MX")

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    result = speech_recognizer.recognize_once()

    # Check the result
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
