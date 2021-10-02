#!/usr/bin/env python3
__author__ = "Claudio Bottari"
__version__ = "0.2.0"
__license__ = "MIT"

# target prices for each GPU
ths = {'3060 ti': 450, '3070 ti': 650, '3060': 350, '3070': 550, '3080': 800}
# how many seconds betweens checks   
sleep_time = 60
# selenium edge driver path (can run with Chrome or Firefox with few code updates)
driver_path = 'edgedriver/msedgedriver.exe'

import time
import webbrowser
import os
from time import sleep

from playsound import playsound
from datetime import datetime, timedelta

from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from msedge.selenium_tools import Edge, EdgeOptions

class GPU:
    def __init__(self, x, origin):
        (self.id, self.title, self.url, self.price, self.availability) = x
        self.origin = origin
    
    def __repr__(self):
        return f'{self.origin} [{self.title}] {self.price}'

def get_driver(driver_path):
    driverOptions = EdgeOptions()
    driverOptions.use_chromium = True
    driverOptions.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    driverOptions.add_argument('log-level=3')
    driverOptions.add_experimental_option("excludeSwitches", ["enable-logging"])

    DRIVER_PATH = str(Path(driver_path).resolve())
    return Edge(executable_path=DRIVER_PATH, options=driverOptions)

def clear_screen():
    _ = os.system('clear' if os.name == 'posix' else 'cls')
    
def alarm():
    for i in range (30):
        playsound('siren.wav')
        time.sleep(5)

def get_time_str(s=0):
    delta = timedelta(0, s)
    return (datetime.now() + delta).strftime("%H:%M:%S")

def get_data_ldlc(driver):
    driver.get('https://www.ldlc.com/it-it/informatica/componenti/scheda-video/c4684/')
    uids = [x.get_attribute("id") for x in driver.find_elements_by_xpath('//li[@class="pdt-item"]')]
    urls = [x.get_attribute("href") for x in driver.find_elements_by_xpath('//li[@class="pdt-item"]/div[@class="pic"]/a')]
    titles = [x.text.lower() for x in driver.find_elements_by_xpath('//h3[@class="title-3"]/a')]
    prices = [float(x.text.replace(' ', '').replace('€', '.')) for x in driver.find_elements_by_xpath('//div[@class="price"]/div')]
    availabilities = ['disabled' not in x.get_attribute("class") for x in driver.find_elements_by_xpath('//div[@class="basket"]/a')]
    return [GPU(x, 'LDLC') for x in zip(uids, titles, urls, prices, availabilities) if x[4]] #return only the available GPUs

def get_data_next(driver):
    driver.get('https://www.nexths.it//Products/getSkuFromLev/page/1/l0/Hardware%20Software/l1/Schede%20Video/sort/Dispo/rpp/48')
    uids = [x.get_attribute("id") for x in driver.find_elements_by_xpath('//div[@class="thumbnailx pcbox"]/a/img')]
    urls = [x.get_attribute("href") for x in driver.find_elements_by_xpath('//div[@class="thumbnailx pcbox"]/a')]
    titles = [x.text.lower() for x in driver.find_elements_by_xpath('//p[@class="gallery-descrbreve"]')]
    prices = [float(x.text.replace('.', '').replace(' ', '').replace(',', '.').replace('€', '')) for x in driver.find_elements_by_xpath('//span[@class="lista-prezzo oswald"]')]
    availabilities = ['NON' not in x.text for x in driver.find_elements_by_xpath('//p[@class="lista-dispo"]/a')]
    return [GPU(x, 'Next') for x in zip(uids, titles, urls, prices, availabilities) if x[4]] #return only the available GPUs

def check_price(driver, data, ths, min_prices):
    for card in data:
        print(card)
        for th in ths:
            if th in card.title:
                min_prices[th] = min(min_prices[th], card.price)
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
    print('GPU BOT by Claudio')
    # for th in ths:
    #     print(f'\t[{th}] for less than {ths[th]}')
    print(f'The BOT will keep running until manually stopped, current time: {get_time_str()}\n\n')

def print_footer(ths, min_prices, sleep_time):
    print('\nResults:')
    for th in min_prices:
        price = min_prices[th]
        price = str(price) + ' €' if price < 99999 else '-'
        print(f'\t[{th}] target {ths[th]} €, current best price {price}')
    print(f'\nNext run at: {get_time_str(sleep_time)}\n\n')

def main(driver_path, ths, sleep_time):
    driver = get_driver(driver_path)
    min_prices = {x: 99999 for x in ths.keys()}
    while True:
        clear_screen()
        print_header(ths)

        try:
            check_price(driver, get_data_ldlc(driver), ths, min_prices)
            check_price(driver, get_data_next(driver), ths, min_prices)
        except Exception as e: print(e)

        print_footer(ths, min_prices, sleep_time)
        sleep(sleep_time)
 
if __name__ == "__main__":
    """ This is executed when run from the command line """
    main(driver_path, ths, sleep_time)
