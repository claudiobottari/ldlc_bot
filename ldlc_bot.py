#!/usr/bin/env python3
__author__ = "Claudio Bottari"
__version__ = "0.2.0"
__license__ = "MIT"

# target prices for each GPU
ths = {'3060 ti': 450, '3070 ti': 650, '3080 ti': 850, '3060': 350, '3070': 550, '3080': 800, '3090': 1000}
# how many seconds betweens checks   
sleep_time = 60
# selenium edge driver path (can run with Chrome or Firefox with few code updates)
driver_path = 'edgedriver/msedgedriver.exe'
# mininum price used to avoid accessories (such as coolers) and old cheap GPUs
low_th = 250

import time
import os, sys
from time import sleep
from tabulate import tabulate

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

    def to_array(self):
        return [self.origin, self.title[:80], self.price]

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
    return [GPU(x, 'LDLC') for x in zip(uids, titles, urls, prices, availabilities) if x[4] and x[3] > low_th] #return only the available GPUs

def get_data_next(driver):
    driver.get('https://www.nexths.it//Products/getSkuFromLev/page/1/l0/Hardware%20Software/l1/Schede%20Video/sort/Dispo/rpp/48')
    uids = [x.get_attribute("id") for x in driver.find_elements_by_xpath('//div[@class="thumbnailx pcbox"]/a/img')]
    urls = [x.get_attribute("href") for x in driver.find_elements_by_xpath('//div[@class="thumbnailx pcbox"]/a')]
    titles = [x.text.lower() for x in driver.find_elements_by_xpath('//p[@class="gallery-descrbreve"]')]
    prices = [float(x.text.replace('.', '').replace(' ', '').replace(',', '.').replace('€', '')) for x in driver.find_elements_by_xpath('//span[@class="lista-prezzo oswald"]')]
    availabilities = ['NON' not in x.text for x in driver.find_elements_by_xpath('//p[@class="lista-dispo"]/a')]
    return [GPU(x, 'Next') for x in zip(uids, titles, urls, prices, availabilities) if x[4] and x[3] > low_th] #return only the available GPUs

def get_data_amazon_it(driver):
    driver.get('https://www.amazon.it/s?k=nvidia&i=computers&rh=n%3A460090031%2Cp_n_feature_seven_browse-bin%3A16067946031&dc&__mk_it_IT=%C3%85M%C3%85%C5%BD%C3%95%C3%91&qid=1633335342&rnid=8321625031&ref=sr_nr_p_n_feature_seven_browse-bin_2')
    uids = [x.get_attribute("data-asin") for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[17]')]
    urls = [x.get_attribute("href") for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[17]//h2/a')]
    titles = [x.text.lower() for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[9]//h2')]
    prices = [float(x.text.replace('.', '').replace(' ', '').replace(',', '.').replace('€', '')) for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]')]
    availabilities = [True for x in range(len(prices))]
    return [GPU(x, 'Amazon.it') for x in zip(uids, titles, urls, prices, availabilities)if x[3] > low_th]

def check_price(driver, data, ths, min_prices):
    if len(data) == 0: return

    print(tabulate([x.to_array() for x in data], headers=['Origin', 'Title', 'Price'], tablefmt="plain"))
    for card in data:
        for th in ths:
            if th in card.title:
                min_prices[th] = min(min_prices[th], card.price)
                if ths[th] > card.price and card.price > ths[th] / 2: # check threshold and also discard prices too low (can be GPU accessories and scams)
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

def print_footer(ths, min_prices, elapsed, sleep_time):
    print('\nResults:')
    for th in min_prices:
        price = min_prices[th]
        price = str(price) + ' €' if price < 99999 else '-'
        print(f'\t[{th}] target {ths[th]} €, current best price {price}')
    print(f'\nCompletion time {elapsed} seconds, next run at: {get_time_str(sleep_time)}\n\n')

def main(driver, ths, sleep_time):
    min_prices = {x: 99999 for x in ths.keys()}
    while True:
        # start job
        start = time.time()
        clear_screen()  
        print_header(ths)

        # read and check data
        try:
            check_price(driver, get_data_ldlc(driver), ths, min_prices)
            check_price(driver, get_data_amazon_it(driver), ths, min_prices)
            check_price(driver, get_data_next(driver), ths, min_prices)
        except Exception as e: print(e)

        # calc time and schedule next run 
        end = time.time()
        elapsed = int(end - start)
        actual_sleep_time = sleep_time - elapsed
        print_footer(ths, min_prices, elapsed, actual_sleep_time)
        sleep(actual_sleep_time)
        
 
if __name__ == "__main__":
    driver = get_driver(driver_path)
    
    try:
        main(driver, ths, sleep_time)
    except KeyboardInterrupt:
        print('Interrupted')
    
    driver.quit()