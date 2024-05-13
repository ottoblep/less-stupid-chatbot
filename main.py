import os
import time
import argparse
import json
import threading
import queue
import re
from pathlib import Path
import chatbot
import asyncio
from dotenv import load_dotenv

load_dotenv()

def TextToSpeech(sentence):
    print("echo \"" + sentence.replace("\n","") + "\" | piper -m " + os.environ['MODELFILE'] + " -c " + os.environ['MODELCONFIG'] + " -f out.wav")
    os.system("echo \"" + sentence.replace("\n","").replace("\"","'") + "\" | piper -m " + os.environ['MODELFILE'] + " -c " + os.environ['MODELCONFIG'] + " -f out.wav && play -q out.wav")

async def TTSAgent(response_queue):
    while True:
        print("TTSAgent Waiting for Responses")
        sentence = await response_queue.get()
        print("Producing Speech")
        TextToSpeech(sentence)
        response_queue.task_done()

async def STTAgent(query_queue, response_queue):
    while True:
        print("Input: ")
        input_sentence = input() 
        await query_queue.put(input_sentence)
        await query_queue.join()
        await response_queue.join()

async def Main():
    query_queue = asyncio.Queue(maxsize=3)
    response_queue = asyncio.Queue(maxsize=20)

    with open("marvin_prompt.txt", "r") as file:
        system_prompt = file.read()
    
    asyncio.create_task(TTSAgent(response_queue))
    asyncio.create_task(chatbot.Chatbot(query_queue,response_queue, system_prompt))
    asyncio.create_task(STTAgent(query_queue,response_queue))

    while True:
        await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(Main())
