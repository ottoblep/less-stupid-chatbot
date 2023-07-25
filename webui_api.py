import requests
import json
import re

HOST = 'localhost:5000'
URI = f'http://{HOST}/api/v1/generate'

def TruncateAnswer(response, name1, name2):
    truncated = response[0:response.find(name1)].replace('\n','')
    truncated = truncated.replace(name2, '')
    return truncated


def Chatbot(prompt, history, name1, name2):
    history += name1 + prompt + "\n"
    history += name2
    history = re.sub('[^A-z0-9 :.,?!\n]', '', history)
    new_history = Query(history)
    if new_history == None: 
        return
    response = new_history.replace(history,'')
    truncated_response = TruncateAnswer(response, name1, name2)
    truncated_response = truncated_response
    history += truncated_response + "\n"
    return truncated_response, history


def Query(history):
    print(history)
    request = {
        'prompt': history,
        'max_new_tokens': 250,
        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'Divine Intellect',
    }

    response = requests.post(URI, json=request)

    if response.status_code == 200:
        result = response.json()['results'][0]['text']
    else:
        print("ERROR: ", response)

    return result 


import asyncio
import json
import sys

try:
    import websockets
except ImportError:
    print("Websockets package not found. Make sure it's installed.")

# For local streaming, the websockets are hosted without ssl - ws://
HOST = 'localhost:5005'
URI = f'ws://{HOST}/api/v1/stream'

# For reverse-proxied streaming, the remote will likely host with ssl - wss://
# URI = 'wss://your-uri-here.trycloudflare.com/api/v1/stream'


async def run(context):
    # Note: the selected defaults change from time to time.
    request = {
        'prompt': context,
        'max_new_tokens': 250,

        # Generation params. If 'preset' is set to different than 'None', the values
        # in presets/preset-name.yaml are used instead of the individual numbers.
        'preset': 'Divine Intellect',
    }

    async with websockets.connect(URI, ping_interval=None) as websocket:
        await websocket.send(json.dumps(request))

        yield context  # Remove this if you just want to see the reply

        while True:
            incoming_data = await websocket.recv()
            incoming_data = json.loads(incoming_data)

            match incoming_data['event']:
                case 'text_stream':
                    yield incoming_data['text']
                case 'stream_end':
                    return


async def Chatbot(query_queue, response_queue, name1, name2, startertext):
    history = startertext + "\n"
    print("Chatbot starting")
    while True:
        prompt = await query_queue.get()
        if 'reset' in prompt:
            print("Registered Reset")
            history = startertext + "\n" # Reset 
            await response_queue.put("Reset history!")
        else:
            print("Processing input:", prompt)
            history += name1 + prompt + "\n";
            history += name2
            output_buffer = ""
            ignore_first = True
            async for response in run(history):
                if ignore_first: 
                    ignore_first = False
                    continue
                output_buffer = output_buffer + response
                if '.' in output_buffer or '?' in output_buffer or '!' in output_buffer:
                    await response_queue.put(output_buffer)
                    history = history + output_buffer
                    print("Appended Sentence to outputs: ", output_buffer)
                    output_buffer = ""
        query_queue.task_done()