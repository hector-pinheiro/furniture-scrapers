from scrapers.john_lewis.scraper import JohnLewisScraper

SEARCH_URLS_FILE_PATH = 'resources/john_lewis.csv'
OUTPUT_FOLDER = '/home/hector/Documents/hector/cadeera/git/cadeera-scrapers/scraping_result/john-lewis-test'
N_THREADS = 12

scraper = JohnLewisScraper()

print("collecting products urls")
scraper.scrap_products_urls(SEARCH_URLS_FILE_PATH, OUTPUT_FOLDER)
print("scraping products")
scraper.scrap_products(OUTPUT_FOLDER, N_THREADS)
