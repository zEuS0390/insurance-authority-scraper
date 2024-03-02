# Import necessary modules
from selenium.webdriver.support.ui import WebDriverWait  # For waiting until a condition is met
from selenium.common.exceptions import TimeoutException  # Exception for timeout
import logging  # For logging
import cv2  # OpenCV library for image processing
import base64  # For base64 encoding and decoding
import numpy as np  # NumPy library for numerical computations

# Initialize logger
logger = logging.getLogger()

# Function to wait until a condition is met
def wait_until(instance, condition, timeout, error_message=None):
    try:
        return WebDriverWait(instance, timeout).until(condition)
    except TimeoutException:
        # Log error message if timeout occurs
        if isinstance(error_message, str): logger.error(error_message)

# Generator function to generate sequential license numbers
def generate_sequential_license_numbers(prefix1_range, prefix2_range, suffix_range):
    for prefix1 in range(ord(prefix1_range[0]), ord(prefix1_range[1])+1):  # Iterate over uppercase letters from 'F' to 'G'
        for prefix2 in range(ord(prefix2_range[0]), ord(prefix2_range[1])+1):  # Iterate over uppercase letters from 'A' to 'Z'
            for suffix in range(suffix_range[0], suffix_range[1]+1):  # Iterate over numbers from 1001 to 9999
                yield f"{chr(prefix1)}{chr(prefix2)}{suffix}"  # Yield license number combining prefix and suffix

# Function to convert base64 encoded image to OpenCV image
def base64ToImage(img_base64: str):
    # Convert base64 image to NumPy array
    buffer = base64.b64decode(img_base64)
    npimg = np.frombuffer(buffer, dtype=np.uint8)
    decoded_image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)  # Decode image using OpenCV
    return decoded_image  # Return decoded image as NumPy array
