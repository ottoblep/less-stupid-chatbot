import os
import time
import argparse
import pyaudio
import json
import threading
import queue
import speech_recognition as sr 
import torch
from pathlib import Path
from vosk import Model, KaldiRecognizer # STT
import webui_api

table = str.maketrans({
    "<": "&lt;",
    ">": "&gt;",
    "&": "&amp;",
    "'": "&apos;",
    '"': "&quot;",
})


def xmlesc(txt):
    return txt.translate(table)


def InitSTT():
    stt_params = []
    stt_params.append(Model("vosk-model-small"))
    stt_params.append(KaldiRecognizer(stt_params[0], 44100))
    stt_params.append(pyaudio.PyAudio())
    return stt_params


def SpeechToText(stt_params):
    model = stt_params[0]
    rec = stt_params[1]
    p = stt_params[2]
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=22050)
    stream.start_stream()
    while True:
        data = stream.read(11025, exception_on_overflow = False)
        if len(data) == 0: continue
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            if len(res['text'])==0: continue
            return res['text']


def LoadModels():
    tts_model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models', model='silero_tts', language='en', speaker='v3_en')
    tts_model.to('cpu')
    return tts_model
tts_model = LoadModels()


def TextToSpeech(text):
    global tts_model
    output_file = Path(f'outputs/response.wav')
    prosody = '<prosody rate="{}" pitch="{}">'.format('medium', 'medium')
    silero_input = f'<speak>{prosody}{xmlesc(text)}</prosody></speak>'
    tts_model.save_wav(ssml_text=silero_input, speaker='en_106', sample_rate=48000, audio_path=str(output_file))
    os.system("vlc -I dummy --dummy-quiet ./outputs/response.wav vlc://quit")
    tts_model = LoadModels()


def Main():
    query_queue = queue.LifoQueue(maxsize=3)
    stt_params = InitSTT()

    with open("startertext2.txt", "r") as file:
        startertext = file.read()
    history = startertext + "\n"
    name1 = "You:"
    name2 = "Hel:"

    while True:
        input_sentence = SpeechToText(stt_params) + "."
        print("Processing "+input_sentence)
        if 'reset' in input_sentence:
            history = startertext + "\n"
            print("Reset history!")
            TextToSpeech("Reset conversation.")
            continue

        response_sentence, history = webui_api.Chatbot(input_sentence, history, name1, name2)
        #print("Responding "+response_sentence)
        TextToSpeech(response_sentence)

if __name__ == "__main__":
    Main() 
