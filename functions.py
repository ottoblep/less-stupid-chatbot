import os
import socket
import time
import re
import requests
from bs4 import BeautifulSoup
import random


def context_adder():
    # Add horoscope personality
    additional_info = get_random_horoscope()
    # Add time
    additional_info += "The current time and date is " + get_time() + "."
    # Add weather
    LOCATION = os.getenv("LOCATION")
    weather_format = "Conditions are %C. The temperature is %t. There will be %p of rain. The humidity is %h\n"
    weather = "The current local weather is: " + requests.get("http://wttr.in/"+LOCATION+"?format=" + weather_format).text + "."
    additional_info += weather 
    # Add news
    headlines = get_news_headlines(3)
    additional_info += ". Some current events and news headlines are: " + headlines[0] + ". " + headlines[1] + ". " + headlines[2] + ". "
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


def get_news_headlines(amount):
    url='https://apnews.com/hub/breaking-news'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.find_all("a", class_="Link")
    headlines = []
    for tag in links:
        if tag.has_attr("aria-label") and len(headlines)<=amount: 
            headlines.append(tag['aria-label'])
    return headlines


def get_random_horoscope():
    url = "https://cafeastrology.com/dailyhoroscopesall.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    box = soup.find_all("div", class_="content-box-green")
    signs = box[0].contents
    horoscopes = []
    for hor in signs:
        if len(hor.text) > 100: horoscopes.append(hor.text)
    return random.choice(horoscopes)