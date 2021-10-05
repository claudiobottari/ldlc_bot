#!/usr/bin/env python3
__author__ = "Claudio Bottari"
__version__ = "0.3.0"
__license__ = "MIT"

# target prices for each GPU
ths = {'3060 ti': 450, '3070 ti': 650, '3080 ti': 850, '3060': 350, '3070': 550, '3080': 750, '3090': 1600  }
# how many seconds betweens checks   
sleep_time = 5
# selenium edge driver path (can run with Chrome or Firefox with few code updates)
driver_path = 'edgedriver/msedgedriver.exe'
# mininum price used to avoid accessories (such as coolers) and old cheap GPUs
low_th = 270
# how many time checks high/low speed sites
high_low_speed_ratio = 30

import time, os
from time import sleep
from tabulate import tabulate

import webbrowser
from playsound import playsound
from datetime import datetime, timedelta
from pathlib import Path

from msedge.selenium_tools import Edge, EdgeOptions

class GPU:
    def __init__(self, x, origin):
        (self.id, self.title, self.url, self.price, self.availability) = x
        self.origin = origin
        self.target = None
        self.uid = self.origin + self.id
        
    def set_target(self, target):
        self.target = target
        return self
    
    def __repr__(self):
        return f'{self.origin} [{self.title}] {self.price}'

    def to_array(self):
        if self.target != None:
            return [self.origin, self.title[:80], self.price if self.price != 99999 else '-', self.target]
        else:
            return [self.origin, self.title[:80], self.price if self.price != 99999 else '-', '']

def get_driver(driver_path):
    options = EdgeOptions()
    options.use_chromium = True
    options.binary_location = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    
    # avoid warnings
    options.add_argument('log-level=3')

    # headless
    options.add_argument("headless")
    options.add_argument("disable-gpu")

    # no images
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    # options.add_experimental_option("excludeSwitches", ["enable-logging"])

    DRIVER_PATH = str(Path(driver_path).resolve())
    return Edge(executable_path=DRIVER_PATH, options=options)

def clear_screen():
    _ = os.system('clear' if os.name == 'posix' else 'cls')
    
def alarm():
    for i in range (100):
        playsound('siren.wav')
        time.sleep(1)

def get_time_str(s=0):
    delta = timedelta(0, s)
    return (datetime.now() + delta).strftime("%H:%M:%S")

def read_and_check_ldlc(driver, ths, min_gpus):
    uids = [x.get_attribute('data-product-id') for x in driver.find_elements_by_xpath('//a[@class="button picto-seul color2 add-to-cart"]')]
    titles = [x.text.lower() for x in driver.find_elements_by_xpath('//a[@class="button picto-seul color2 add-to-cart"]/ancestor::node()[2]//h3[@class="title-3"]/a')]
    urls = [x.get_attribute('href') for x in driver.find_elements_by_xpath('//a[@class="button picto-seul color2 add-to-cart"]/ancestor::node()[2]//h3[@class="title-3"]/a')]
    prices = [float(x.text.replace(' ', '').replace('€', '.')) for x in driver.find_elements_by_xpath('//a[@class="button picto-seul color2 add-to-cart"]/ancestor::node()[1]/div[@class="price"]/div')]
    availabilities = [True for x in range(len(prices))]
    data = [GPU(x, 'LDLC') for x in zip(uids, titles, urls, prices, availabilities) if x[4] and x[3] > low_th] #return only the available GPUs        
    check_price(driver, data, ths, min_gpus)

def get_data_ldlc(driver, ths, min_gpus):
    driver.get("https://www.ldlc.com/it-it/informatica/componenti/scheda-video/c4684/+fv1026-5801+fv121-19183,19184,19185,19365,19509,19800,19801+fv134-1339.html")
    read_and_check_ldlc(driver, ths, min_gpus)

    # other pages
    for url in [x.get_attribute('href') for x in driver.find_elements_by_xpath('//ul[@class="pagination"]/li/a')][:-1]:
        driver.get(url)
        read_and_check_ldlc(driver, ths, min_gpus)

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
    urls = [x.get_attribute("href") for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[9]//h2/a')]
    titles = [x.text.lower() for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[9]//h2')]
    prices = [float(x.text.replace('.', '').replace(' ', '').replace(',', '.').replace('€', '')) for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]')]
    availabilities = [True for x in range(len(prices))]
    return [GPU(x, 'Amazon.it') for x in zip(uids, titles, urls, prices, availabilities)if x[3] > low_th]

def get_data_amazon_es(driver):
    driver.get('https://www.amazon.es/s?i=computers&bbn=937935031&rh=n%3A667049031%2Cn%3A937912031%2Cn%3A17478031031%2Cn%3A937935031%2Cp_n_feature_seven_browse-bin%3A16069169031%2Cp_n_condition-type%3A15144009031&s=price-desc-rank&dc&fs=true&qid=1633341030&rnid=15144007031&ref=sr_st_price-desc-rank')
    uids = [x.get_attribute("data-asin") for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[11]')]
    urls = [x.get_attribute("href") for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[9]//h2/a')]
    titles = [x.text.lower() for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[9]//h2')]
    prices = [float(x.text.replace('.', '').replace(' ', '').replace(',', '.').replace('€', '')) for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]')]
    availabilities = [True for x in range(len(prices))]
    return [GPU(x, 'Amazon.es') for x in zip(uids, titles, urls, prices, availabilities)if x[3] > low_th]

def get_data_amazon_fr(driver):
    driver.get('https://www.amazon.fr/s?keywords=Cartes+graphiques&i=computers&rh=n%3A430340031%2Cp_n_feature_seven_browse-bin%3A15941744031%2Cp_36%3A27000-100000%2Cp_n_shipping_option-bin%3A2019350031%2Cp_n_condition-type%3A15135266031&dc&_encoding=UTF8&c=ts&qid=1633350520&rnid=15135264031&ts_id=430340031&ref=sr_nr_p_n_condition-type_1')
    uids = [x.get_attribute("data-asin") for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[17]')]
    urls = [x.get_attribute("href") for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[9]//h2/a')]
    titles = [x.text.lower() for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[9]//h2')]
    prices = [float(x.text.replace('.', '').replace(' ', '').replace(',', '.').replace('€', '')) for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]')]
    availabilities = [True for x in range(len(prices))]
    return [GPU(x, 'Amazon.fr') for x in zip(uids, titles, urls, prices, availabilities)if x[3] > low_th]

def get_data_amazon_de(driver, page):
    driver.get(f'https://www.amazon.de/-/en/s?k=Graphics+Cards&i=computers&rh=n%3A430161031%2Cp_n_feature_seven_browse-bin%3A15664227031%7C22756211031%2Cp_n_condition-type%3A776949031%2Cp_36%3A27000-200000&dc&page={page}&language=en&_encoding=UTF8&c=ts&qid=1633350892&rnid=428358031&ts_id=430161031')
    uids = [x.get_attribute("data-asin") for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[17]')]
    urls = [x.get_attribute("href") for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[9]//h2/a')]
    titles = [x.text.lower() for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]/ancestor::node()[9]//h2')]
    prices = [float(x.text.replace(' ', '').replace(',', '').replace('€', '')) for x in driver.find_elements_by_xpath('//div[@data-asin]//span[@class="a-price-whole"]')]
    availabilities = [True for x in range(len(prices))]
    return [GPU(x, 'Amazon.de') for x in zip(uids, titles, urls, prices, availabilities)if x[3] > low_th]

def check_price(driver, data, ths, min_gpus):
    if len(data) == 0: return

    print(tabulate([x.to_array() for x in data], headers=['Origin', 'Title', 'Price', ''], tablefmt="plain"))
    for card in data:
        track(card)
        for th in ths:
            if th in card.title or th in card.title.replace(' ', ''):
                if min_gpus[th].price > card.price:
                    min_gpus[th] = card.set_target(ths[th])
                if ths[th] > card.price and card.price > ths[th] / 2: # check threshold and also discard prices too low (can be GPU accessories and scams)
                    print('\n\nTARGET FOUND')
                    print(card)
                    print(f'Price is {card.price} while threshold was set to {ths[th]}\n\n')
                    print(card.url)
                    
                    # open default browser on the card
                    webbrowser.open(card.url)

                    alarm()
                    sleep(1000)
                break

history = {}
def track(card):
    if card.uid not in history.keys():
        history[card.uid] = card
        store(card)
    elif card.price != history[card.uid].price:
        store(card)

def store(card):
    with open('log.csv', 'a', encoding="utf-8") as f:
        f.write(f'{datetime.now().strftime("%d/%m/%Y %H:%M:%S")}, {card.origin}, {card.id}, "{card.title}", {card.url}, {card.price}')
        f.write('\n')

def print_header(counter, min_gpus):
    print(f'GPU BOT by Claudio, it will keep running until manually stopped, run {counter}, current time: {get_time_str()}\n\n')
    print(tabulate([x.to_array() for x in min_gpus.values()], headers=['Origin', 'Title', 'Price', 'Target'], tablefmt="plain"))
    print()

def print_footer(elapsed, sleep_time):
    print(f'\nDone. Completion time {elapsed} seconds, next run at: {get_time_str(sleep_time)}\n\n')

def main(driver, ths, sleep_time):
    min_gpus = {x: GPU(('-', x, '#', 99999, False), '-') for x in ths.keys()}
    actual_sleep_time = 0
    counter = 0
    while True:
        # start job
        start = time.time()
        clear_screen()  
        print_header(counter, min_gpus)
        if actual_sleep_time == 1:
            print('WARNING: it seems there are too many things to do for the desiderate polling time! Please check...\n')

        # read and check data
        try:
            # high speed polling
            get_data_ldlc(driver, ths, min_gpus)

            #low speed polling
            if counter % high_low_speed_ratio == 0:
                check_price(driver, get_data_amazon_it(driver), ths, min_gpus)
                check_price(driver, get_data_amazon_fr(driver), ths, min_gpus)
                check_price(driver, get_data_amazon_es(driver), ths, min_gpus)
                for page in range(1, 5):
                    check_price(driver, get_data_amazon_de(driver, page), ths, min_gpus)
                check_price(driver, get_data_next(driver), ths, min_gpus)
        except Exception as e: print(e)

        # calc time and schedule next run 
        end = time.time()
        elapsed = int(end - start)
        actual_sleep_time = max(1, sleep_time - elapsed) # to avoid negative sleep time 
        print_footer(elapsed, actual_sleep_time)
        sleep(actual_sleep_time)

        counter = counter + 1
        
 
if __name__ == "__main__":
    driver = get_driver(driver_path)
    
    try:
        main(driver, ths, sleep_time)
    except KeyboardInterrupt:
        print('Interrupted')
    
    driver.quit()