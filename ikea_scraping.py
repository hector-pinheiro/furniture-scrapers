from scrapers.ikea.scraper import IkeaScraper

SEARCH_URLS_FILE_PATH = 'resources/ikea.csv'
OUTPUT_FOLDER = '/home/hector/Documents/hector/cadeera/git/cadeera-scrapers/scraping_result/ikea-test'
N_THREADS = 12

scraper = IkeaScraper()

print("collecting products urls")
scraper.scrap_products_urls(SEARCH_URLS_FILE_PATH, OUTPUT_FOLDER)
print("scraping products")
scraper.scrap_products(OUTPUT_FOLDER, N_THREADS)
