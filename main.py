import os
import time
import argparse
import pyaudio
import json
import threading
import queue
import speech_recognition as sr 
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


def Main():
    query_queue = queue.LifoQueue(maxsize=3)
    STTthread = threading.Thread(target=SpeechToTextLoop, args=(query_queue,))
    STTthread.start()

    print(query_queue)

    while True:
        print(query_queue)
        input_sentence = query_queue.get(block=True, timeout=None) # waits forever if necessary
        if contains(input_sentence,'shutdown'):
            STTthread.stop()
            print("shutting down")
            break

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
