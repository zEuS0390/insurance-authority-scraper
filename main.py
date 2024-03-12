# Import necessary modules and functions
from modules.utils import generateSequentialLicenseNumbers
from configparser import ConfigParser
from modules.scraper import Scraper
import logging, threading

# Initialize logger configuration
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s [%(levelname)s] --- %(message)s", level=logging.INFO)

# Read configuration from config.cfg file
cfg = ConfigParser()
cfg.read("config.cfg")

def scrap(select: str, license_number_range: tuple):
    # Initialize Scraper object with configuration
    scraper = Scraper(cfg)
    # Select the appropriate category
    scraper.select(select)
    # Iterate through sequential license numbers and scrape data
    for license_no in generateSequentialLicenseNumbers(*license_number_range):
        scraper.scrap(license_no)
    # Quit the scraper instance
    scraper.quit()

# Create threads for scraping firms and individuals concurrently
scrapFirmsThread = threading.Thread(target=scrap, args=('firm', (('F', 'G'), ('A', 'Z'), (1001, 9999))))
scrapIndividualsThread = threading.Thread(target=scrap, args=('individual', (('I', 'J'), ('A', 'Z'), (1001, 9999))))

# Start execution of threads
scrapFirmsThread.start()
scrapIndividualsThread.start()

# Wait for threads to finish execution
scrapFirmsThread.join()
scrapIndividualsThread.join()
