import json
import sys
import functions
import requests
import os

def filter_characters(input):
    return input.replace("*", "")

def run(context):
    data = {
        "prompt": context,
        "n_predict": 128,
        "temperature": 1,
        "stop": [os.getenv("USER_NAME") + ":"]
    }
    headers = {
        "Authorization": "Bearer doesntmatter"
    }
    response = requests.post('http://localhost:8080/completion', headers=headers, json=data).json()
    return response['content']

async def Chatbot(query_queue, response_queue, system_prompt):
    history = system_prompt + "\n" + functions.context_adder() + "\n" # Reset 
    print("Chatbot starting")
    while True:
        prompt = await query_queue.get()
        if 'reset' in prompt:
            print("Registered Reset")
            history = initial_prompt # Reset
            await response_queue.put("Reset history!")
        elif 'shut off' in prompt:
            print("Shutting down.")
            history = initial_prompt # Reset
            await response_queue.put("Shutting Down!")
            sys.exit()
        else:
            print("Processing input:", prompt)
            history += "\n" + os.getenv("USER_NAME") + ": " + prompt + "\n" + os.getenv("BOT_NAME") + ": ";
            response = run(history)
            await response_queue.put(response)
            history += response
            print("Appended response to outputs: ", response)
        query_queue.task_done()