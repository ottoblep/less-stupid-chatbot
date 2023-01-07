import os
import time
import argparse
from transformers import pipeline, set_seed 
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration # T2T
import whisper # STT
from vosk import KaldiRecognizer # word recognition
from gtts import gTTS # TTS

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
    whisper_model = whisper.load_model("tiny.en") 
    return conversation_tokenizer, conversation_model, whisper_model


def SpeechToText(path: str, whisper_model):
    return whisper_model.transcribe(path)["text"]


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


def main():
    conversation_tokenizer, conversation_model, whisper_model = InitModels()
    while True:
        if TEXT_ONLY:
            input_sentence = input(">> User: ")
        else:
            start_time = time.time()
            SpeechToText("input.mp3", whisper_model)
            print("input processing time: ", time.time() - start_time)
        print("input is: ", input_sentence)

        start_time = time.time()
        response_sentence = PromptBlenderbot(input_sentence, conversation_tokenizer, conversation_model)
        print("response generation time: ", time.time() - start_time)
        print("response is : ", response_sentence)

        if not OFFLINE and not TEXT_ONLY: # Google TTS requires network connection
            start_time = time.time()
            TextToSpeech(response_sentence)
            print("output processing time: ", time.time() - start_time)


if __name__ == "__main__":
    main() 
