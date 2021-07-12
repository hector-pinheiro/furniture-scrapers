import io
import json
import os

import requests
from PIL import Image
from bs4 import BeautifulSoup

from scrapers import LIGHTING, CHAIR, TABLE, BED, SOFA
from util.utils import mkdir, generate_id


# https://www.ikea.com/gb/en/cat/sofa-beds-10663/
# https://www.ikea.com/gb/en/cat/fabric-sofas-10661/
# https://www.ikea.com/gb/en/cat/modular-sofas-16238/
# https://www.ikea.com/gb/en/cat/footstools-pouffes-20926/
# https://www.ikea.com/gb/en/cat/leather-coated-fabric-sofas-10662/

# https://www.ikea.com/gb/en/cat/double-beds-16284/
# https://www.ikea.com/gb/en/cat/beds-with-storage-25205/
# https://www.ikea.com/gb/en/cat/divan-beds-28433/
# https://www.ikea.com/gb/en/cat/single-beds-16285/
# https://www.ikea.com/gb/en/cat/guest-beds-day-beds-19037/
# https://www.ikea.com/gb/en/cat/upholstered-beds-49096/
# https://www.ikea.com/gb/en/cat/childrens-beds-18723/
# https://www.ikea.com/gb/en/cat/loft-beds-bunk-beds-19039/

# https://www.ikea.com/gb/en/cat/table-desk-systems-47423/
# https://www.ikea.com/gb/en/cat/desks-computer-desks-20649/
# https://www.ikea.com/gb/en/cat/bedside-tables-20656/
# https://www.ikea.com/gb/en/cat/coffee-side-tables-10705/
# https://www.ikea.com/gb/en/cat/dining-table-sets-19145/
# https://www.ikea.com/gb/en/cat/dining-tables-21825/
# https://www.ikea.com/gb/en/cat/changing-tables-45783/
# https://www.ikea.com/gb/en/cat/dressing-tables-20657/
# https://www.ikea.com/gb/en/cat/childrens-tables-18768/
# https://www.ikea.com/gb/en/cat/bar-tables-20862/
# https://www.ikea.com/gb/en/cat/meeting-conference-tables-54173/
# https://www.ikea.com/gb/en/cat/cafe-tables-19143/
# https://www.ikea.com/gb/en/cat/console-tables-16246/

# https://www.ikea.com/gb/en/cat/fabric-armchairs-10687/
# https://www.ikea.com/gb/en/cat/fabric-chaise-longues-10679/
# https://www.ikea.com/gb/en/cat/chair-beds-16296/
# https://www.ikea.com/gb/en/cat/lounge-chairs-53257/
# https://www.ikea.com/gb/en/cat/rattan-armchairs-20907/
# https://www.ikea.com/gb/en/cat/recliners-47359/
# https://www.ikea.com/gb/en/cat/coated-fabric-armchairs-35186/
# https://www.ikea.com/gb/en/cat/leather-armchairs-10696/
# https://www.ikea.com/gb/en/cat/leather-coated-fabric-armchairs-35184/
# https://www.ikea.com/gb/en/cat/leather-coated-fabric-chaise-longues-10694/
# https://www.ikea.com/gb/en/cat/desk-chairs-20652/
# https://www.ikea.com/gb/en/cat/dining-chairs-25219/
# https://www.ikea.com/gb/en/cat/stools-benches-10728/
# https://www.ikea.com/gb/en/cat/dining-table-sets-19145/
# https://www.ikea.com/gb/en/cat/bar-stools-chairs-20864/
# https://www.ikea.com/gb/en/cat/childrens-armchairs-20483/
# https://www.ikea.com/gb/en/cat/small-chairs-18769/
# https://www.ikea.com/gb/en/cat/childrens-desk-chairs-24715/
# https://www.ikea.com/gb/en/cat/childrens-stools-benches-45816/
# https://www.ikea.com/gb/en/cat/junior-dining-chairs-45815/
# https://www.ikea.com/gb/en/cat/cafe-chairs-19144/
# https://www.ikea.com/gb/en/cat/baby-chairs-highchairs-45782/

# https://www.ikea.com/gb/en/cat/table-lamps-10732/
# https://www.ikea.com/gb/en/cat/floor-lamps-10731/
# https://www.ikea.com/gb/en/cat/led-lights-20515/
# https://www.ikea.com/gb/en/cat/ceiling-lights-18750/
# https://www.ikea.com/gb/en/cat/work-lamps-20502/
# https://www.ikea.com/gb/en/cat/wall-lights-20503/
# https://www.ikea.com/gb/en/cat/childrens-lighting-18773/
# https://www.ikea.com/gb/en/cat/spotlights-20506/
# https://www.ikea.com/gb/en/cat/led-light-bulbs-10744/
# https://www.ikea.com/gb/en/cat/decorative-lighting-14971/
# https://www.ikea.com/gb/en/cat/bathroom-cabinet-lighting-55010/
# https://www.ikea.com/gb/en/cat/kitchen-lighting-16282/
# https://www.ikea.com/gb/en/cat/bookcase-lighting-16281/
# https://www.ikea.com/gb/en/cat/wardrobe-lighting-16283/
# https://www.ikea.com/gb/en/cat/smart-lighting-36812/
# https://www.ikea.com/gb/en/cat/outdoor-lighting-17897/
# https://www.ikea.com/gb/en/cat/bathroom-lighting-10736/

class IkeaScraper:
    def __init__(self):
        self.search_urls = {
            "url_format": "https://sik.search.blue.cdtapps.com/gb/en/product-list-page?category={}&size=1000",
            SOFA: ["10663", "10661", "16238", "20926", "10662"],
            BED: ["16284", "25205", "28433", "16285", "19037", "49096", "18723", "19039"],
            TABLE: ["47423", "20649", "20656", "10705", "19145", "21825", "45783", "20657", "18768", "20862", "54173",
                    "19143", "16246"],
            CHAIR: ["10687", "10679", "16296", "53257", "20907", "47359", "35186", "10696", "35184", "10694", "20652",
                    "25219", "10728", "19145", "20864", "20483", "18769", "24715", "45816", "45815", "19144",
                    "45782"],
            LIGHTING: ["10732", "10731", "20515", "18750", "20502", "20503", "18773", "20506", "10744", "14971",
                       "55010", "16282", "16281", "16283", "36812", "17897", "10736"]
        }

    def collect_product_urls(self, furniture_type):
        product_urls = [("product_id", "product_url")] * 0
        url_format = self.search_urls['url_format']
        search_categories = self.search_urls[furniture_type]
        for search_category in search_categories:
            json_response = requests.get(url_format.format(search_category)).text
            dict_response = json.loads(json_response)
            products = dict_response['productListPage']["productWindow"]
            for product in products:
                product_urls.append((generate_id(), product['id'], product['pipUrl']))
                # variants
                for variant in product['gprDescription']['variants']:
                    product_urls.append((generate_id(), variant['id'], variant['pipUrl']))
        return product_urls

    def get_images_urls(self, soup):
        images_containers = soup.find_all("div", {"class": "range-revamp-media-grid__media-container"})
        urls = []
        for container in images_containers:
            img = container.find("img")
            if img is not None:
                urls.append(img.get('src').replace("f=s", "f=xl"))
        return urls

    def persist_images(self, folder, id, urls):
        for i, url in enumerate(urls):
            for trials in range(0, 3):
                try:
                    image_content = requests.get(url).content
                except Exception as e:
                    print(f"ERROR - Could not download {url} - {e}")
                    continue

                try:
                    image_file = io.BytesIO(image_content)
                    image = Image.open(image_file).convert('RGB')
                    file_path = os.path.join(folder, id + '_' + str(i) + '.jpg')
                    with open(file_path, 'wb') as f:
                        image.save(f, "JPEG", quality=90)
                except Exception as e:
                    print(f"ERROR - Could not save {url} - {e}")
                    continue

                break

    def get_details(self, soup, url):
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

    def scrap_product(self, product, output_folder):
        id, product_id, url = product
        product_folder = os.path.join(output_folder, id)
        mkdir(product_folder)
        response = requests.get(url).text
        soup = BeautifulSoup(response, 'html.parser')
        # product details
        details = self.get_details(soup, url)
        with open(os.path.join(product_folder, id + '.json'), "w") as outfile:
            json.dump(details, outfile, indent=4)
        # product images
        images_urls = self.get_images_urls(soup)
        self.persist_images(product_folder, id, images_urls)
