from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
import logging, cv2, base64
import numpy as np

logger = logging.getLogger()

def wait_until(instance, condition, timeout, error_message=None):
    try:
        return WebDriverWait(instance, timeout).until(condition)
    except TimeoutException:
        if isinstance(error_message, str): logger.error(error_message)

def generate_sequential_license_numbers():
    for prefix1 in range(ord('F'), ord('G')+1):
        for prefix2 in range(ord('A'), ord('Z')+1):
            for suffix in range(1001, 10000):
                yield f"{chr(prefix1)}{chr(prefix2)}{suffix}"

def base64ToImage(img_base64):
    # Convert base64 image to NumPy array
    buffer = base64.b64decode(img_base64)
    npimg = np.frombuffer(buffer, dtype=np.uint8)
    decoded_image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    return decoded_image

