# from modules.auto import execute
import threading
from modules.utils import generateSequentialLicenseNumbers
from modules.scraper import Scraper
from modules.constants import *
import logging, os

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s [%(levelname)s] --- %(message)s", level=logging.INFO)

def scrap(*args):
  output_dir = os.path.join(DATA_DIR, args[0])
  scraper = Scraper(output_dir)
  scraper.select(args[0])
  for license_no in generateSequentialLicenseNumbers(*args[1]): 
    scraper.scrap(license_no)
  scraper.quit()

scrapFirms = threading.Thread(target=scrap, args=('firm', (('F', 'G'), ('A', 'Z'), (1001, 9999))))
scrapIndividuals = threading.Thread(target=scrap, args=('individual', (('I', 'J'), ('A', 'Z'), (1001, 9999))))

scrapFirms.start()
scrapIndividuals.start()

scrapFirms.join()
scrapIndividuals.join()