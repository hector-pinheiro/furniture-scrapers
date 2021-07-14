import io
import json
import os
import time
import uuid

import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait


def mkdir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def print_update_progress(prefix, done, total):
    print('\r{}{}/{} done, {:.1f}%'.format(prefix, done, total, int(100 * float(done) / total)), end='', flush=True)


def generate_id():
    return uuid.uuid4().hex[:16]


def tag_string_text(tag):
    if tag is None:
        return ""

    str = tag.string
    if str is None or str == "":
        str = tag.text

    if str is None:
        str = ""

    return str.split("\n")[0].strip()


def persist_images(folder, id, urls):
    urls = list(set(urls))
    for i, url in enumerate(urls):
        for trials in range(0, 3):
            try:
                image_content = requests.get(url).content
            except Exception as e:
                # print(f"\nERROR - Could not download {url} - {e}")
                continue

            try:
                image_file = io.BytesIO(image_content)
                image = Image.open(image_file).convert('RGB')
                file_path = os.path.join(folder, id + '_' + str(i) + '.jpg')
                with open(file_path, 'wb') as f:
                    image.save(f, "JPEG", quality=90)
            except Exception as e:
                # print(f"\nERROR - Could not save {url} - {e}")
                continue
            break


def persist_details(product_folder, id, details):
    with open(os.path.join(product_folder, id + '.json'), "w") as outfile:
        json.dump(details, outfile, indent=4)


def get_web_driver(url):
    WINDOW_SIZE = "1920,1080"
    chrome_options = Options()
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.add_argument("headless")

    prefs = {'profile.managed_default_content_settings.images': 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get(url)

    return driver


def scroll_and_wait(driver, times, wait_segs):
    for i in range(0, times):
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)

        wait = WebDriverWait(driver, wait_segs)
        time.sleep(wait_segs)

    return driver
