import requests
from bs4 import BeautifulSoup

from util.utils import get_web_driver, tag_string_text


class JohnLewisScraperV2:
    @staticmethod
    def scrap_product_urls(page_url):
        product_urls = [("product_id", "product_url")] * 0
        soup = BeautifulSoup(requests.get(page_url).text, 'html.parser')
        product_cards = soup.find("a", {"class": "sofa-card-container"})
        if product_cards is not None:
            driver = get_web_driver(page_url)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            product_cards = soup.findAll("a", {"class": "sofa-card-container"})
            for product_card in product_cards:
                product_url = "https://www.johnlewis.com" + product_card.get("href")
                product_data = product_card.find("div", {"class": "sofa-card"})
                if product_data is not None:
                    product_id = product_data.get("data-pid")
                else:
                    product_id = ""
                product_urls.append((product_id, product_url))
        return product_urls

    @staticmethod
    def scrap_details(soup, url):
        details = dict()
        details['product_url'] = url
        # description
        description = ""
        description_tag = soup.find("h1", {"class": "pdp__title mb2"})
        if description_tag is not None:
            description = tag_string_text(description_tag)
        if description == "":
            print("\nv2 no desc", url)
        details['description'] = description
        # specifications
        specifications_container = soup.find("div", {"class": "sofa-grid product-specifications"})
        specs = specifications_container.findAll("li")
        specifications = dict()
        for spec in specs:
            label = spec.find("strong")
            value = spec.find("span")
            label = tag_string_text(label)
            value = tag_string_text(value)
            if label != "":
                specifications[label] = value
        details['specifications'] = specifications
        if len(specifications) == 0:
            print("\nv2 no specs", url)
        return details

    @staticmethod
    def scrap_images_urls(soup):
        images_track = soup.find("div", {"class": "slick-track"})
        images_containers = images_track.find_all("img")
        urls = []
        for container in images_containers:
            img_url = container.get('src')
            if "https:" not in img_url:
                img_url = "https:" + img_url
            urls.append(img_url)
        return urls
