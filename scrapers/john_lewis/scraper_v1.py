from bs4 import BeautifulSoup

from util.utils import tag_string_text, get_web_driver, scroll_and_wait


class JohnLewisScraperV1:
    @staticmethod
    def scrap_product_urls(page_url):
        product_urls = [("product_id", "product_url")] * 0
        driver = get_web_driver(page_url)
        driver = scroll_and_wait(driver, 10, 2)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        products_grid = soup.find("div", {"data-test": "component-grid-container"})
        products_containers = products_grid.findAll("div", {"data-test": "component-grid-column"})
        driver.close()
        for container in products_containers:
            try:
                section = container.find("section")
                product_id = section.get("data-product-id")
                url_container = section.find("a")
                product_url = "https://www.johnlewis.com" + url_container.get("href")
                product_urls.append((product_id, product_url))
            except:
                continue
        return product_urls

    @staticmethod
    def scrap_details(soup, url):
        details = dict()
        details['product_url'] = url
        # description
        description_tag = soup.find("h1", {"class": "product-header__title"})
        if description_tag is None:
            description_tag = soup.find("h1", {"itemprop": "name"})
        description = tag_string_text(description_tag)
        if description == "":
            print("\nv1 no desc", url)
        details['description'] = description
        # materials
        materials = soup.find("dl", {"class": "product-specifications-list"})
        specifications = dict()
        if materials is not None:
            labels = materials.find_all("dt", {"class": "product-specification-list__label"})
            values = materials.find_all("dd", {"class": "product-specification-list__value"})
            for i, label in enumerate(labels):
                label = label.text.split("\n")[0].strip()
                value = values[i].text.split("\n")[0].strip()
                specifications[label] = value
        details['specifications'] = specifications
        if len(specifications) == 0:
            print("\nv1 no spec", url)
        return details

    @staticmethod
    def scrap_images_urls(soup):
        images_containers = soup.find_all("li", {"data-carousel": "productCarousel"})
        urls = []
        for container in images_containers:
            img = container.find("img")
            if img is not None:
                img_url = img.get('data-large-image')
                if img_url is None or img_url == "":
                    img_url = img.get('src')
                urls.append("https:" + img_url)
        return urls
