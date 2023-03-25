import requests
import json
import re

def TruncateAnswer(response, name1, name2):
    stop_response_index = response.find(name1)
    truncated = response[0:stop_response_index].replace('\n','')
    truncated = truncated.replace(name2, '')
    return truncated


def remove_surrounded_chars(string):
    # this expression matches to 'as few symbols as possible (0 upwards) between any asterisks' OR
    # 'as few symbols as possible (0 upwards) between an asterisk and the end of the string'
    return re.sub('\*[^\*]*?(\*|$)','',string)


def Chatbot(prompt, history, name1, name2):
    history += name1 + prompt + "\n"
    history += name2
    history = re.sub('[^A-z0-9 :.,\n]', '', history)
    new_history = Query(history)
    if new_history == None: 
        return
    response = new_history.replace(history,'')
    truncated_response = TruncateAnswer(response, name1, name2)
    truncated_response = remove_surrounded_chars(truncated_response)
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