import os
import socket
import time
import re
import requests


def context_adder(question):
    additional_info = "\nAdditional background information: \n"
    LOCATION = os.getenv("LOCATION")
    # Add time
    if any(re.findall(r'clock|soon|late|time|day|date|hour|week|second|minute',question, re.IGNORECASE)):
        additional_info += ". The current time and date is " + get_time()
    # Add weather
    if any(re.findall(r'weather|rain|sun|clouds|mist|fog|warm|cold|clothes|hot|heat',question, re.IGNORECASE)):
        print(LOCATION)
        weather_format = "Conditions are %C. The temperature is %t. There will be %p of rain. The humidity is %h.\n"
        weather = ". The current local weather is: " + requests.get("http://wttr.in/"+LOCATION+"?format=" + weather_format).text
        additional_info += weather 
    print("Adding information:" + additional_info)
    return additional_info

def trigger(sentence):
    if "lighton" in sentence.lower():
        print("Sending Light On Signal.")
        light_on()
    if "lightoff" in sentence.lower():
        print("Sending Light Off Signal.")
        light_off()

def light_on():
    MESSAGE = bytes(os.getenv('MESSAGE'), 'utf-8')
    UDP_IP = os.getenv('UDP_IP')
    UDP_PORT = int(os.getenv('UDP_PORT'))
    sock = socket.socket(socket.AF_INET, # Internet
                 socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


def light_off():
    MESSAGE = bytes(os.getenv('MESSAGE'), 'utf-8')
    UDP_IP = os.getenv('UDP_IP')
    UDP_PORT = int(os.getenv('UDP_PORT'))
    sock = socket.socket(socket.AF_INET, # Internet
                 socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))


def get_time():
    return time.ctime()