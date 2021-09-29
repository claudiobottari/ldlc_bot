#!/usr/bin/env python3
__author__ = "Claudio Bottari"
__version__ = "0.1.0"
__license__ = "MIT"

# target prices for each GPU
ths = {'3060 ti': 450, '3070 ti': 650, '3070': 550, '3080': 800}
# how many seconds betweens checks   
sleep_time = 60
# selenium edge driver path (can run with Chrome or Firefox with few code updates)
driver_path = 'edgedriver/msedgedriver.exe'

import time
import webbrowser
import os
from time import sleep

from playsound import playsound
from datetime import datetime

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

class GPU:
    def __init__(self, x):
        (self.id, self.title, self.url, self.price, self.availability) = x
    
    def __repr__(self):
        return f'[{self.title}] {self.price}'

def clear_screen():
    _ = os.system('clear' if os.name == 'posix' else 'cls')
    
def alarm():
    for i in range (30):
        playsound('siren.wav')
        time.sleep(5)

def current_time():
    return datetime.now().strftime("%H:%M:%S")

def get_data(driver):
    driver.get('https://www.ldlc.com/it-it/informatica/componenti/scheda-video/c4684/')
    uids = [x.get_attribute("id") for x in driver.find_elements_by_xpath('//li[@class="pdt-item"]')]
    urls = [x.get_attribute("href") for x in driver.find_elements_by_xpath('//li[@class="pdt-item"]/div[@class="pic"]/a')]
    titles = [x.text.lower() for x in driver.find_elements_by_xpath('//h3[@class="title-3"]/a')]
    prices = [float(x.text.replace(' ', '').replace('€', '.')) for x in driver.find_elements_by_xpath('//div[@class="price"]/div')]
    availabilities = ['disabled' not in x.get_attribute("class") for x in driver.find_elements_by_xpath('//div[@class="basket"]/a')]
    data = zip(uids, titles, urls, prices, availabilities)
    return [GPU(x) for x in list(data) if x[4]] #return only the available GPUs

def check_price(driver, data, ths):
    print('Those GPUs where found:')
    for card in data:
        print(card)
        for th in ths:
            if th in card.title:
                if ths[th] > card.price:
                    print('\n\nTARGET FOUND')
                    print(card)
                    print(f'Price is {card.price} while threshold was set to {ths[th]}\n\n')
                    print(card.url)
                    
                    driver.get(card.url)
                    alarm()
                    return
                break

def print_header(ths):
    print('GPU BOT by Claudio\n\nChecking on LDLC for these GPUs:')
    for th in ths:
        print(f'\t[{th}] for less than {ths[th]}')
    print(f'The BOT will keep running until manually stopped, current time: {current_time()}\n\n')

def main(driver_path, ths, sleep_time):
    driver = webdriver.Edge(executable_path=str(Path(driver_path).resolve()))
    while True:
        clear_screen()
        print_header(ths)
        data = get_data(driver)
        check_price(driver, data, ths)
        print()
        sleep(sleep_time)
 
if __name__ == "__main__":
    """ This is executed when run from the command line """
    main(driver_path, ths, sleep_time)
