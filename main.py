from modules.auto import execute
import threading
import logging

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s [%(levelname)s] --- %(message)s", level=logging.INFO)

# Web scrap concurrently
firm_thread = threading.Thread(target=execute, args=('firm',))
individual_thread = threading.Thread(target=execute, args=('individual',))
firm_thread.start()
individual_thread.start()

firm_thread.join()
individual_thread.join()
