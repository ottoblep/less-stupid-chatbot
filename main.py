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


def SpeechToTextLoop(sentence_queue: queue.LifoQueue):
    """ Concurrent listening loop fills a queue """
    model = Model("vosk-model-small")
    rec = KaldiRecognizer(model, 44100)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=22050)
    stream.start_stream()
    while True:
        data = stream.read(11025, exception_on_overflow = False)
        if len(data) == 0: continue
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            if len(res['text'])==0: continue
            try: 
                sentence_queue.put(res['text'], block=False, timeout=None)
                print("Added to queue:",res['text'])
            except queue.Full:
                print("Queue is full. Input was discarded.")


def TextToSpeech(tts_model, text):
    output_file = Path(f'outputs/response.wav')
    prosody = '<prosody rate="{}" pitch="{}">'.format('medium', 'medium')
    silero_input = f'<speak>{prosody}{text}</prosody></speak>'
    tts_model.save_wav(ssml_text=silero_input, speaker='en_97', sample_rate=48000, audio_path=str(output_file))
    os.system("vlc -I dummy --dummy-quiet ./outputs/response.wav vlc://quit")


def LoadModels():
    tts_model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models', model='silero_tts', language='en', speaker='v3_en')
    tts_model.to('cpu')
    return tts_model


def Main():
    query_queue = queue.LifoQueue(maxsize=3)
    tts_model = LoadModels()
    STTthread = threading.Thread(target=SpeechToTextLoop, args=(query_queue,))
    STTthread.start()

    while True:
        print(query_queue)
        input_sentence = query_queue.get(block=True, timeout=None) # waits forever if necessary
        if 'shutdown' in input_sentence:
            STTthread.stop()
            print("shutting down")
            STTthread.join()
            break
        TextToSpeech(tts_model, input_sentence)

        #print("processing:", input_sentence)

        #start_time = time.time()
        #response_sentence = PromptWebuiAPI(input_sentence)
        #print("response generation time:", time.time() - start_time)
        #print("response is:", response_sentence)

        #start_time = time.time()
        #TextToSpeech(response_sentence)
        #print("output processing time:", time.time() - start_time)

if __name__ == "__main__":
    Main() 
