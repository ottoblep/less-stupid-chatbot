import os
import time
import torch
from transformers import pipeline, set_seed 
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration # T2T
import whisper # STT
from vosk import KaldiRecognizer # word recognition
from gtts import gTTS # TTS

ONLINE = True
SAVE_MODELS = False
TEXT_ONLY = False

if (SAVE_MODELS==True and ONLINE==False):
    raise Exception("To SAVE_MODELS for offline use, program must be ONLINE.") 

def init_models():
    """ Initializes all required models """
    if ONLINE:
        mname = "facebook/blenderbot-400M-distill"
        model = BlenderbotForConditionalGeneration.from_pretrained(mname)
        tokenizer = BlenderbotTokenizer.from_pretrained(mname)
        if SAVE_MODELS:
            model.save_pretrained('offline_model')  # Saves for Offline
            tokenizer.save_pretrained('offline_tokenizer')  # Saves for Offline
    else:
        tokenizer = AutoTokenizer.from_pretrained("offline_tokenizer")
        model = AutoModelForCausalLM.from_pretrained("offline_model")
    whisper_model = whisper.load_model("tiny.en") 


def main():
    while True:
        # input logic
        if TEXT_ONLY:
            input_sentence = input(">> User:")
        else:
            start_time = time.time()
            SpeechToText("input.mp3")
            print("input processing time: ", time.time() - start_time)
        print("input is: ", input_sentence)

        start_time = time.time()
        response_sentence = GenerateResponse(input_sentence)
        print("response generation time: ", time.time() - start_time)
        print("response is : ", response_sentence)

        if ONLINE and not TEXT_ONLY: # Google TTS requires network connection
            start_time = time.time()
            TextToSpeech(response_sentence)
            print("output processing time: ", time.time() - start_time)


def SpeechToText(path: str):
    return whisper_model.transcribe(path)["text"]


def GenerateResponse(prompt: str):
    inputs = tokenizer([prompt], return_tensors="pt")
    reply_ids = model.generate(**inputs)
    response_sentence = tokenizer.batch_decode(reply_ids)[0]
    response_sentence = response_sentence.replace('<s>','').replace('</s>','')
    return response_sentence


def TextToSpeech(input: str):
    tts_sound = gTTS(input)
    tts_sound.save('resp.mp3')
    os.system("vlc -I dummy --dummy-quiet ./resp.mp3 vlc://quit")


if __name__ == "__main__":
    main() 
