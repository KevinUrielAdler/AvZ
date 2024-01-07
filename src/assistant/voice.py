"""
Esta madre esta bien mal editada, no c q desmadre hice, pero jala
Speech recognition samples for the Microsoft Cognitive Services Speech SDK
"""

import os
import time

try:
    import azure.cognitiveservices.speech as speechsdk
except ImportError:
    print("""
    Importing the Speech SDK for Python failed.
    Refer to
    https://docs.microsoft.com/azure/cognitive-services/speech-service/quickstart-python for
    installation instructions.
    """)
    import sys
    sys.exit(1)


# Set up the subscription info for the Speech Service:
# Replace with your own subscription key and service region (e.g., "westus").
speech_key, service_region = "9f490b1316b54e07aa923fdc8b3a07eb", "eastus"

# Specify the path to an audio file containing speech (mono WAV / PCM with a sampling rate of 16
# kHz).
# weatherfilename = "whatstheweatherlike.wav"
# weatherfilenamemp3 = "whatstheweatherlike.mp3"


def keyword_function_mic():
    """runs keyword spotting locally, with direct access to the result audio"""

    # Creates an instance of a keyword recognition model. Update this to
    # point to the location of your keyword recognition model.
    current_dir = os.path.dirname(os.path.realpath(__file__))
    # print(current_dir)
    file_path = os.path.join(
        current_dir, "models/assistant.table")
    model = speechsdk.KeywordRecognitionModel(
        file_path)

    # The phrase your keyword recognition model triggers on.
    keyword = "assistant"

    # Create a local keyword recognizer with the default microphone device for input.
    keyword_recognizer = speechsdk.KeywordRecognizer()

    done = False

    def recognized_cb(evt: speechsdk.SpeechRecognitionEventArgs):
        # Only a keyword phrase is recognized. The result cannot be 'NoMatch'
        # and there is no timeout. The recognizer runs until a keyword phrase
        # is detected or recognition is canceled (by stop_recognition_async()
        # or due to the end of an input file or stream).
        result = evt.result
        # if result.reason == speechsdk.ResultReason.RecognizedKeyword:
            # print("RECOGNIZED KEY_WORD: {}".format(result.text))
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
    return True

    # stop_future = keyword_recognizer.stop_recognition_async()
    # print('Stopping...')
    # stopped = stop_future.get()


# speech_recognize_keyword_locally_from_microphone()


def speech_recognize_once_from_mic():
    """performs one-shot speech recognition from the default microphone"""
    # <SpeechRecognitionWithMicrophone>
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region)
    # Creates a speech recognizer using microphone as audio input.
    # The default language is "en-us".
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    # Starts speech recognition, and returns after a single utterance is recognized. The end of a
    # single utterance is determined by listening for silence at the end or until a maximum of 15
    # seconds of audio is processed. It returns the recognition text as result.
    # Note: Since recognize_once() returns only a single utterance, it is suitable only for single
    # shot recognition like command or query.
    # For long-running multi-utterance recognition, use start_continuous_recognition() instead.
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
    # </SpeechRecognitionWithMicrophone>

# speech_recognize_once_from_mic()


def speech_recognize_keyword_from_microphone():
    """performs keyword-triggered speech recognition with input microphone"""
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region)

    # Creates an instance of a keyword recognition model. Update this to
    # point to the location of your keyword recognition model.
    current_dir = os.path.dirname(os.path.realpath(__file__))
    print(current_dir)
    file_path = os.path.join(
        current_dir, "models/Zayd Assistant.table")
    model = speechsdk.KeywordRecognitionModel(
        file_path)

    # The phrase your keyword recognition model triggers on.
    keyword = "Zayd Assistant"

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

    done = False

    def stop_cb(evt):
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""
        print('CLOSING on {}'.format(evt))
        nonlocal done
        done = True

    def recognizing_cb(evt):
        """callback for recognizing event"""
        if evt.result.reason == speechsdk.ResultReason.RecognizingKeyword:
            print('RECOGNIZING KEYWORD: {}'.format(evt))
        elif evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
            print('RECOGNIZING: {}'.format(evt))

    def recognized_cb(evt):
        """callback for recognized event"""
        if evt.result.reason == speechsdk.ResultReason.RecognizedKeyword:
            print('RECOGNIZED KEYWORD: {}'.format(evt))
        elif evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print('RECOGNIZED: {}'.format(evt))
        elif evt.result.reason == speechsdk.ResultReason.NoMatch:
            print('NOMATCH: {}'.format(evt))

    # Connect callbacks to the events fired by the speech recognizer
    speech_recognizer.recognizing.connect(recognizing_cb)
    speech_recognizer.recognized.connect(recognized_cb)
    speech_recognizer.session_started.connect(
        lambda evt: print('SESSION STARTED: {}'.format(evt)))
    speech_recognizer.session_stopped.connect(
        lambda evt: print('SESSION STOPPED {}'.format(evt)))
    speech_recognizer.canceled.connect(
        lambda evt: print('CANCELED {}'.format(evt)))
    # stop continuous recognition on either session stopped or canceled events
    speech_recognizer.session_stopped.connect(stop_cb)
    speech_recognizer.canceled.connect(stop_cb)

    # Start keyword recognition
    speech_recognizer.start_keyword_recognition(model)
    print('Say something starting with "{}" followed by whatever you want...'.format(keyword))
    while not done:
        time.sleep(.5)

    speech_recognizer.stop_keyword_recognition()


# speech_recognize_keyword_from_microphone()


def speech_recognize_once_with_auto_language_detection_from_mic():
    """performs one-shot speech recognition from the default microphone with auto language detection"""
    speech_config = speechsdk.SpeechConfig(
        subscription=speech_key, region=service_region)

    # create the auto detection language configuration with the potential source language candidates
    auto_detect_source_language_config = \
        speechsdk.languageconfig.AutoDetectSourceLanguageConfig(
            languages=["de-DE", "en-US"])
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, auto_detect_source_language_config=auto_detect_source_language_config)
    result = speech_recognizer.recognize_once()

    # Check the result
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        auto_detect_source_language_result = speechsdk.AutoDetectSourceLanguageResult(
            result)
        print("Recognized: {} in language {}".format(
            result.text, auto_detect_source_language_result.language))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(
            cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(
                cancellation_details.error_details))


# def speech_recognize_keyword_locally_from_microphone():
#     """runs keyword spotting locally, with direct access to the result audio"""

#     # Creates an instance of a keyword recognition model. Update this to
#     # point to the location of your keyword recognition model.
#     current_dir = os.path.dirname(os.path.realpath(__file__))
#     print(current_dir)
#     file_path = os.path.join(
#         current_dir, "models/Zayd Assistant.table")
#     model = speechsdk.KeywordRecognitionModel(
#         file_path)

#     # The phrase your keyword recognition model triggers on.
#     keyword = "Zayd Assistant"

#     # Create a local keyword recognizer with the default microphone device for input.
#     keyword_recognizer = speechsdk.KeywordRecognizer()

#     done = False

#     def recognized_cb(evt):
#         # Only a keyword phrase is recognized. The result cannot be 'NoMatch'
#         # and there is no timeout. The recognizer runs until a keyword phrase
#         # is detected or recognition is canceled (by stop_recognition_async()
#         # or due to the end of an input file or stream).
#         result = evt.result
#         if result.reason == speechsdk.ResultReason.RecognizedKeyword:
#             print("RECOGNIZED KEYWORD: {}".format(result.text))
#         nonlocal done
#         done = True

#     def canceled_cb(evt):
#         result = evt.result
#         if result.reason == speechsdk.ResultReason.Canceled:
#             print('CANCELED: {}'.format(result.cancellation_details.reason))
#         nonlocal done
#         done = True

#     # Connect callbacks to the events fired by the keyword recognizer.
#     keyword_recognizer.recognized.connect(recognized_cb)
#     keyword_recognizer.canceled.connect(canceled_cb)

#     # Start keyword recognition.
#     result_future = keyword_recognizer.recognize_once_async(model)
#     print('Say something starting with "{}" followed by whatever you want...'.format(keyword))
#     result = result_future.get()

#     # Read result audio (incl. the keyword).
#     if result.reason == speechsdk.ResultReason.RecognizedKeyword:
#         time.sleep(2)  # give some time so the stream is filled
#         result_stream = speechsdk.AudioDataStream(result)
#         result_stream.detach_input()  # stop any more data from input getting to the stream

#         save_future = result_stream.save_to_wav_file_async(
#             "AudioFromRecognizedKeyword.wav")
#         print('Saving file...')
#         saved = save_future.get()

    # If active keyword recognition needs to be stopped before results, it can be done with
    #
    #   stop_future = keyword_recognizer.stop_recognition_async()
    #   print('Stopping...')
    #   stopped = stop_future.get()


# speech_recognize_keyword_locally_from_microphone()
