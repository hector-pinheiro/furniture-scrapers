import os
from multiprocessing.pool import ThreadPool
from threading import Lock

import pandas as pd

from scrapers import SOFA, BED, TABLE, CHAIR, LIGHTING
from scrapers.ikea import IkeaScraper
from util.utils import mkdir, print_update_progress

OUTPUT_FOLDER = '/home/hector/Documents/hector/cadeera/git/cadeera-scrapers/scraping_result/ikea-test'
N_THREADS = 8

mkdir(OUTPUT_FOLDER)

scraper = IkeaScraper()

print("collecting products urls")
for furniture_type in [SOFA, BED, TABLE, CHAIR, LIGHTING]:
    furniture_folder = os.path.join(OUTPUT_FOLDER, furniture_type)
    products_urls_path = os.path.join(furniture_folder, 'product_urls.csv')
    mkdir(furniture_folder)

    sofa_urls = scraper.collect_product_urls(furniture_type)
    df = pd.DataFrame(sofa_urls, columns=['id', 'product_id', 'product_url'])
    df.to_csv(products_urls_path, index=False)
    print('\t{} ok'.format(furniture_type))

print("scraping products")
for furniture_type in [SOFA, BED, TABLE, CHAIR, LIGHTING]:
    print('scraping {}'.format(furniture_type))
    furniture_folder = os.path.join(OUTPUT_FOLDER, furniture_type)
    products_urls_path = os.path.join(furniture_folder, 'product_urls.csv')
    products_folder = os.path.join(furniture_folder, 'products')
    mkdir(products_folder)

    df = pd.read_csv(products_urls_path)
    total = len(df)
    done = 0
    mutex = Lock()


    def execute(product):
        global done
        scraper.scrap_product(product, products_folder)
        mutex.acquire()
        done += 1
        print_update_progress('\t', done, total)
        mutex.release()


    pool = ThreadPool(N_THREADS)
    pool.map(execute, df.iloc)
    print('')
