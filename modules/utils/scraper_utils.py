# Import necessary modules
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait  # For waiting until a condition is met
from selenium.common.exceptions import TimeoutException  # Exception for timeout
import logging, cv2, base64, csv, os
from typing import Union, Generator
import numpy as np  # NumPy library for numerical computations

# Initialize logger
logger = logging.getLogger()

# Function to wait until a condition is met
def waitUntil(instance, condition, timeout, error_message = None) -> Union[WebElement, None]:
    try: return WebDriverWait(instance, timeout).until(condition)
    except TimeoutException:
        # Log error message if timeout occurs
        if isinstance(error_message, str): logger.error(error_message)

# Generator function to generate sequential license numbers
def generateSequentialLicenseNumbers(prefix1_range: tuple, prefix2_range: tuple, suffix_range: tuple) -> Generator[str, None, None]:
    for prefix1 in range(ord(prefix1_range[0]), ord(prefix1_range[1])+1):  # Iterate over uppercase letters from 'F' to 'G'
        for prefix2 in range(ord(prefix2_range[0]), ord(prefix2_range[1])+1):  # Iterate over uppercase letters from 'A' to 'Z'
            for suffix in range(suffix_range[0], suffix_range[1]+1):  # Iterate over numbers from 1001 to 9999
                yield f"{chr(prefix1)}{chr(prefix2)}{suffix}"  # Yield license number combining prefix and suffix

# Function to convert base64 encoded image to OpenCV image
def base64ToImage(img_base64: str) -> np.ndarray:
    # Convert base64 image to NumPy array
    buffer = base64.b64decode(img_base64)
    npimg = np.frombuffer(buffer, dtype=np.uint8)
    decoded_image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)  # Decode image using OpenCV
    return decoded_image  # Return decoded image as NumPy array
