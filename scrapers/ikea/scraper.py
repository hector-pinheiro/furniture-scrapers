import json
import os
from multiprocessing.pool import ThreadPool
from threading import Lock

import pandas as pd
import requests
from bs4 import BeautifulSoup

from util.utils import mkdir, generate_id, persist_details, persist_images, print_update_progress


class IkeaScraper:

    def __scrap_products_urls(self, search_codes):
        category, sub_category, category_code = search_codes
        products_urls = []
        url_format = "https://sik.search.blue.cdtapps.com/gb/en/product-list-page?category={}&size=1000"
        json_response = requests.get(url_format.format(category_code)).text
        dict_response = json.loads(json_response)
        products = dict_response['productListPage']["productWindow"]
        for product in products:
            products_urls.append((generate_id(), product['id'], category, sub_category, product['pipUrl']))
            # variants
            for variant in product['gprDescription']['variants']:
                products_urls.append((generate_id(), variant['id'], variant['pipUrl']))
        return products_urls

    def scrap_products_urls(self, searches_file_path, output_scraper_folder):
        mkdir(output_scraper_folder)
        searches_codes = pd.read_csv(searches_file_path)
        products_urls = [("cadeera_id", "product_id", "category", "sub_category", "product_url")] * 0
        for search_codes in searches_codes.iloc:
            category, sub_category, _ = search_codes
            urls = self.__scrap_products_urls(search_codes)
            products_urls.extend(urls)
            print('\t{}/{} done, {} products'.format(category, sub_category, len(urls)))
        products_urls_path = os.path.join(output_scraper_folder, 'products.csv')
        df = pd.DataFrame(products_urls,
                          columns=['cadeera_id', 'product_id', 'category', 'sub_category', 'product_url'])
        df.to_csv(products_urls_path, index=False)
        print("\tdone, total {} products".format(len(df)))

    def __scrap_images_urls(self, soup):
        images_containers = soup.find_all("div", {"class": "range-revamp-media-grid__media-container"})
        urls = []
        for container in images_containers:
            img = container.find("img")
            if img is not None:
                urls.append(img.get('src').replace("f=s", "f=xl"))
        return urls

    def __scrap_details(self, soup, url):
        details = dict()
        description = soup.find("span", {"class": "range-revamp-header-section__description-text"}).string
        materials = soup.find("div", {"id": "SEC_product-details-material-and-care"})
        details['description'] = description
        details['product_url'] = url
        if materials is not None:
            details_containers = materials.find_all("div", {"class": "range-revamp-product-details__container"})
            for c, container in enumerate(details_containers):
                detail_name = container.find("span", {"class": "range-revamp-product-details__header"})
                if detail_name is not None:
                    detail_name = detail_name.string
                else:
                    detail_name = "details_{}".format(c)
                detail_sections = container.find_all("div", {"class": "range-revamp-product-details__section"})
                if len(detail_sections) > 0:
                    sections_dict = dict()
                    for section in detail_sections:
                        att = section.find("span", {"class": "range-revamp-product-details__header"})
                        if att is not None:
                            att = att.string.replace(":", "")
                        else:
                            att = "value"
                        value = section.find("span", {"class": "range-revamp-product-details__label"}).string
                        sections_dict[att] = value
                    details[detail_name] = sections_dict
        return details

    def __scrap_product(self, product, output_folder):
        id, product_id, category, sub_category, url = product
        product_folder = os.path.join(output_folder, id)
        mkdir(product_folder)
        response = requests.get(url).text
        soup = BeautifulSoup(response, 'html.parser')
        # product details
        details = self.__scrap_details(soup, url)
        # product images
        images_urls = self.__scrap_images_urls(soup)
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
