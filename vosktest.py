from vosk import Model, KaldiRecognizer
import pyaudio
import json
import threading

def listenloop():
    model = Model("vosk-model-small")
    rec = KaldiRecognizer(model, 44100)
    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=22050)
    stream.start_stream()
    while True:
            data = stream.read(11025, exception_on_overflow = False)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                res = json.loads(rec.Result())
                t = threading.Thread(target=actionthread, args=(res['text'],))
                t.start()

def actionthread(command):
    print(command)

listenloop()