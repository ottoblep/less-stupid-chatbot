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
import asyncio

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
    tts_model.save_wav(ssml_text=silero_input, speaker='en_103', sample_rate=24000, audio_path=str(output_file)) # 99 25 38 103
    os.system("vlc -I dummy --dummy-quiet ./outputs/response.wav vlc://quit")

async def TTSAgent(response_queue):
    while True:
        print("TTSAgent Waiting for Responses")
        sentence = await response_queue.get()
        print("Producing Speech")
        TextToSpeech(sentence)
        response_queue.task_done()


async def STTAgent(query_queue, response_queue, stt_params):
    while True:
        print("Starting listening")
        os.system("vlc -I dummy --dummy-quiet ./sounds/button-41.mp3 vlc://quit")
        input_sentence = SpeechToText(stt_params) + "."
        await query_queue.put(input_sentence)
        await query_queue.join()
        await response_queue.join()


async def Main():
    query_queue = asyncio.Queue(maxsize=3)
    response_queue = asyncio.Queue(maxsize=20)
    stt_params = InitSTT()

    with open("marvin_prompt.txt", "r") as file:
        system_prompt = file.read()
    
    asyncio.create_task(TTSAgent(response_queue))
    asyncio.create_task(webui_api.Chatbot(query_queue,response_queue, system_prompt))
    asyncio.create_task(STTAgent(query_queue,response_queue,stt_params))

    while True:
        await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(Main())
