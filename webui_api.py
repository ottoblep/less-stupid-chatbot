import asyncio
import json
import sys
import functions

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
        'stopping_strings': [ "[", "]"]
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


async def Chatbot(query_queue, response_queue, system_prompt):
    initial_prompt = "[INST] «SYS»\n" + system_prompt + "\n«/SYS»\n" # Reset 
    history = initial_prompt
    print("Chatbot starting")
    while True:
        prompt = await query_queue.get()
        if 'reset' in prompt:
            print("Registered Reset")
            history = initial_prompt # Reset
            await response_queue.put("Reset history!")
        else:
            print("Processing input:", prompt)
            # Add information to prompt if necessary
            if "time" in prompt or "day" in prompt or "date" in prompt:
                additional_info = "The current time and date is " + functions.get_time()
                prompt += ". " + additional_info
                print("Adding information:" + additional_info)

            if history == initial_prompt:
                history += prompt + " [\INST] ";
            else:
                history += "[INST] "+ prompt + " [\INST] ";
            output_buffer = ""
            ignore_first = True
            async for response in run(history):
                if ignore_first: 
                    ignore_first = False
                    continue
                output_buffer = output_buffer + response
                if "lighton" in output_buffer.lower(): functions.light_on()
                if "lightoff" in output_buffer.lower(): functions.light_off()
                if '.' in output_buffer or '?' in output_buffer or '!' in output_buffer:
                    await response_queue.put(output_buffer)
                    history = history + output_buffer
                    print("Appended Sentence to outputs: ", output_buffer)
                    output_buffer = ""
        history = history + "\n"
        query_queue.task_done()