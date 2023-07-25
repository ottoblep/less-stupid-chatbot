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