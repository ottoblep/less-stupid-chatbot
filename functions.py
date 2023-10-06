import os
import socket
import time
import re


def context_adder(question):
    additional_info = ""
    if any(re.findall(r'clock|soon|late|time|day|date|hour|second|minute',question, re.IGNORECASE)):
        additional_info = ". The current time and date is " + get_time()
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