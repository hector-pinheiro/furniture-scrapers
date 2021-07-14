import os
from multiprocessing.pool import ThreadPool
from threading import Lock

import pandas as pd
import requests
from bs4 import BeautifulSoup

from scrapers.john_lewis.scraper_v1 import JohnLewisScraperV1
from scrapers.john_lewis.scraper_v2 import JohnLewisScraperV2
from util.utils import mkdir, get_web_driver, persist_details, persist_images, generate_id, print_update_progress


class JohnLewisScraper:
    def __scrap_products_urls(self, search_url):
        category, sub_category, url_format, n_pages = search_url
        products_urls = []
        for page in range(1, n_pages + 1):
            page_url = url_format.format(page)
            soup = BeautifulSoup(requests.get(page_url).text, 'html.parser')
            products_grid = soup.find("div", {"data-test": "component-grid-container"})
            scraper = JohnLewisScraperV1 if products_grid is not None else JohnLewisScraperV2
            urls = scraper.scrap_product_urls(page_url)
            products_urls.extend(urls)
        product_urls = [(generate_id(), product_id, category, sub_category, product_url) for product_id, product_url in
                        products_urls]
        return product_urls

    def scrap_products_urls(self, searches_file_path, output_scraper_folder):
        mkdir(output_scraper_folder)
        search_urls = pd.read_csv(searches_file_path)
        products_urls = [("cadeera_id", "product_id", "category", "sub_category", "product_url")] * 0
        for search_url in search_urls.iloc:
            category, sub_category, _, _ = search_url
            urls = self.__scrap_products_urls(search_url)
            products_urls.extend(urls)
            print('\t{}/{} done, {} products'.format(category, sub_category, len(urls)))
        products_urls_path = os.path.join(output_scraper_folder, 'products.csv')
        df = pd.DataFrame(products_urls,
                          columns=['cadeera_id', 'product_id', 'category', 'sub_category', 'product_url'])
        df.to_csv(products_urls_path, index=False)
        print("\tdone, total {} products".format(len(df)))

    def __scrap_product(self, product, output_folder):
        id, product_id, _, _, url = product
        product_folder = os.path.join(output_folder, id)
        mkdir(product_folder)
        driver = get_web_driver(url)
        response = driver.page_source
        driver.close()
        soup = BeautifulSoup(response, 'html.parser')
        if len(soup.find_all("li", {"data-carousel": "productCarousel"})) > 0:
            scraper = JohnLewisScraperV1
        else:
            scraper = JohnLewisScraperV2

        details = scraper.scrap_details(soup, url)
        images_urls = scraper.scrap_images_urls(soup)
        persist_details(product_folder, id, details)
        persist_images(product_folder, id, images_urls)

        self.mutex.acquire()
        self.done += 1
        print_update_progress('\t', self.done, self.total)
        self.mutex.release()

    def scrap_products(self, output_scraper_folder, n_threads):
        products_urls_path = os.path.join(output_scraper_folder, 'products.csv')
        all_products = pd.read_csv(products_urls_path)
        categories = pd.unique(all_products['category'])
        sub_categories = pd.unique(all_products['sub_category'])
        print('{} products, {} categories, {} sub-categories'
              .format(len(all_products), len(categories), len(sub_categories)))
        for category in categories:
            for sub_category in sub_categories:
                idxs = (all_products['category'] == category) & (all_products['sub_category'] == sub_category)
                products = all_products[idxs]
                if len(products) > 0:
                    print('scraping {}/{}'.format(category, sub_category))
                    product_folder = os.path.join(output_scraper_folder, category, sub_category)
                    mkdir(product_folder)
                    self.total = len(products)
                    self.done = 0
                    self.mutex = Lock()
                    pool = ThreadPool(n_threads)
                    pool.map(lambda x: self.__scrap_product(x, product_folder), products.iloc)
                    print('')
