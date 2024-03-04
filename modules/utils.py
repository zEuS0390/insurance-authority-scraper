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

def generateCSV(header: list, row: dict, output_filename: str) -> None:

    output_file_path = os.path.dirname(output_filename)

    if not os.path.exists(output_file_path):
        os.makedirs(output_file_path)

    # Write data
    with open(os.path.join(output_filename), "a", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=header)
        if file.tell() == 0: writer.writeheader()
        writer.writerow(row)

def populateCSVRowDict(
        license_no: str, 
        csv_header_list: list, 
        csv_row_dict: dict, 
        rows: list, 
        is_multirow: bool = False) -> None:
    """
    Populates the given dictionary to prepare for CSV generation.

    Args:
        csv_header_list (list): A list of header column names needed for the fieldnames when generating CSV.
        csv_row_dict (dict): A dictionary that holds the final row for generating CSV.
        rows (list): A list of rows containing values for the columns.
        is_multirow (bool): Flag indicating whether the current table row spans multiple rows in the CSV.

    Returns:
        None: The function updates the given dictionary directly.
    """

    # Include license number in the csv row dictionary
    column = csv_header_list[0]
    csv_row_dict[column] = license_no

    # Set the loop at index 3 if the current row in the table has multiple rows
    start_loop_index = 3 if is_multirow else 0

    # A flag for multiple rows
    multirow_flag = False

    # Iterate through the list of row values in tuples
    for row_values in rows:

        if is_multirow:
            # Add license number in the row values
            row_values = (license_no,) + row_values
            # The flag will be True if the columns at the beginning are blank strings
            multirow_flag = all(map(lambda index: row_values[index] == '', range(start_loop_index-1, 0, -1)))
            if multirow_flag is not True: 
                # If the current row does not have multple rows within it, directly populate the csv row dictionary with row values
                csv_row_dict.update(dict(zip(csv_header_list, row_values)))

        for index in range(start_loop_index, len(row_values)):
            # Increment the index by 1 if the current row does not have multiple rows
            column = csv_header_list[index + (1 if not is_multirow else 0)]
            value = row_values[index]
            csv_row_dict[column] += f"{value}\n" if multirow_flag or not is_multirow else "\n"
