import os
import time
import argparse
import pyaudio
import json
import threading
import queue
from transformers import pipeline, set_seed 
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration # T2T
from gtts import gTTS # TTS
import speech_recognition as sr 
from vosk import Model, KaldiRecognizer # STT

parser = argparse.ArgumentParser()
parser.add_argument('--offline', action='store_true')
parser.add_argument('--save', action='store_true')
parser.add_argument('--text_only', action='store_true')
args = parser.parse_args()
OFFLINE = args.offline 
SAVE_MODELS = args.save
TEXT_ONLY = args.text_only
if (SAVE_MODELS and OFFLINE):
    raise Exception("To save models for offline use, program must be online.") 


def InitModels():
    """ Initializes all required models """
    print("Loading models...")
    if OFFLINE:
        conversation_tokenizer = AutoTokenizer.from_pretrained("offline_tokenizer")
        conversation_model = AutoModelForCausalLM.from_pretrained("offline_model")
    else:
        mname = "facebook/blenderbot-400M-distill"
        conversation_model = BlenderbotForConditionalGeneration.from_pretrained(mname)
        conversation_tokenizer = BlenderbotTokenizer.from_pretrained(mname)
        if SAVE_MODELS:
            conversation_model.save_pretrained('offline_model')  # Saves for Offline
            conversation_tokenizer.save_pretrained('offline_tokenizer')  # Saves for Offline
    return conversation_tokenizer, conversation_model


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


def PromptBlenderbot(prompt: str, tokenizer, model):
    inputs = tokenizer([prompt], return_tensors="pt")
    reply_ids = model.generate(**inputs)
    response_sentence = tokenizer.batch_decode(reply_ids)[0]
    response_sentence = response_sentence.replace('<s>','').replace('</s>','')
    return response_sentence


def TextToSpeech(input: str):
    tts_sound = gTTS(input)
    tts_sound.save('resp.mp3')
    os.system("vlc -I dummy --dummy-quiet ./resp.mp3 vlc://quit")


def Main():
    if not TEXT_ONLY:
        query_queue = queue.LifoQueue(maxsize=3)
        STTthread = threading.Thread(target=SpeechToTextLoop, args=(query_queue,))
        STTthread.start()

    conversation_tokenizer, conversation_model = InitModels()

    while True:
        if TEXT_ONLY:
            input_sentence = input(">> User: ")
        else: 
            input_sentence = query_queue.get(block=True, timeout=None) # waits forever if necessary
        print("processing: ", input_sentence)

        start_time = time.time()
        response_sentence = PromptBlenderbot(input_sentence, conversation_tokenizer, conversation_model)
        print("response generation time: ", time.time() - start_time)
        print("response is : ", response_sentence)

        if not OFFLINE and not TEXT_ONLY: # Google TTS requires network connection
            start_time = time.time()
            TextToSpeech(response_sentence)
            print("output processing time: ", time.time() - start_time)


if __name__ == "__main__":
    Main() 
