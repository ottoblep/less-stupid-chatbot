import requests
import json
import re

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
    #print("PROMPT\n", history + "\nEND PROMPT")
    response = requests.post("http://127.0.0.1:7860/run/textgen", json={
    	"data": [
    		history, 100, True, 0.5, 0.9, 1, 1.1, 1, 0, 0, 0, 1, 0,
    		1, False, -1,
        ]
    }).json()
    return response["data"][0]