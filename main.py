from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time, base64, time, logging, json, csv, os
from modules.constants import *
from modules.firm import *
from modules.captcha import solve_captcha
import numpy as np
import cv2

# Initialize logger
logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s [%(levelname)s] --- %(message)s", level=logging.INFO)

options = Options()
options.add_argument("-headless")

# Initialize Web Driver with FireFox
driver = webdriver.Firefox(options=options)
driver.get(BASE_URL)

# This is for the 'Licensed Insurance Agency/Licensed Insurance Broker Company'

def wait_until(instance, condition, timeout, error_message=None):
    try:
        return WebDriverWait(instance, timeout).until(condition)
    except TimeoutException:
        if isinstance(error_message, str): logger.error(error_message)

# Wait till the page is fully loaded before clicking 'Search for Firm' link
try:
    # search_for_firm_button = driver.find_element(By.LINK_TEXT, 'Search for Firm')
    search_for_firm_button = WebDriverWait(driver, 3).until(
        expected_conditions.presence_of_element_located((By.LINK_TEXT, 'Search for Firm'))
    )
    logger.info("Page is ready!")
except TimeoutException:
    logger.error("Loading took too much time!")
    driver.quit()
    # This is temporary
    logger.info("Press enter to quit...")
    exit()

# Click 'Search for Firm' link
search_for_firm_button.click()

# Wait till the page is fully loaded before filling up the form
try:
    license_status_all_checkbox = WebDriverWait(driver, 20).until(
            expected_conditions.presence_of_element_located((By.ID, 'licenseStatusc'))
    )
    search_criteria_license_number_checkbox = WebDriverWait(driver, 20).until(
            expected_conditions.presence_of_element_located((By.ID, 'searchBy3'))
    )
    search_criteria_input_txt = WebDriverWait(driver, 20).until(
            expected_conditions.presence_of_element_located((By.NAME, 'searchInputTxt'))
    )
    search_button = WebDriverWait(driver, 20).until(
            expected_conditions.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[7]/div[1]/div/div/div/button'))
    )
except TimeoutException:
    logger.error("Loading took too much time!")
    driver.quit()
    # This is temporary
    input("Press enter to quit...")
    exit()

license_status_all_checkbox.click()
logger.info("Selected 'All' in License Status section")

search_criteria_license_number_checkbox.click()
logger.info("Selected 'License Number' in Search Criteria section")

firms_dir = os.path.join(DATA_DIR, "firms")

def generate_sequential_license_numbers():
    for prefix1 in range(ord('F'), ord('G')+1):
        for prefix2 in range(ord('A'), ord('Z')+1):
            for suffix in range(1001, 10000):
                yield f"{chr(prefix1)}{chr(prefix2)}{suffix}"

for license_no in generate_sequential_license_numbers():

    logger.info("-"*15)
    search_criteria_input_txt.clear()
    search_criteria_input_txt.send_keys(license_no)
    logger.info(f"Entered license number '{license_no}'")
    # logger.info(f"LICENSE NUMBER: '{license_no}'")

    captcha_image = driver.find_element(By.ID, "stickyImg")
    locator = (By.XPATH, '/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[6]/fieldset/div/div[2]/div[3]/input')
    captcha_code_input = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located(locator))


    while captcha_image.is_displayed():

        wait_until(
            instance = driver,
            condition = lambda _driver: driver.execute_script("""
                let ele = arguments[0];
                let cnv = document.createElement('canvas');
                cnv.width = ele.width; 
                cnv.height = ele.height;
                cnv.getContext('2d').drawImage(ele, 0, 0);
                return cnv.toDataURL('image/jpeg').substring(22).length > 0;
            """, captcha_image),
            timeout = 20,
            error_message = "Took too much time to load"
        )

        img_base64 = driver.execute_script("""
            let ele = arguments[0];
            let cnv = document.createElement('canvas');
            cnv.width = ele.width; 
            cnv.height = ele.height;
            cnv.getContext('2d').drawImage(ele, 0, 0);
            return cnv.toDataURL('image/jpeg').substring(22);
        """, captcha_image)

        # Convert base64 image to NumPy array
        buffer = base64.b64decode(img_base64)
        npimg = np.frombuffer(buffer, dtype=np.uint8)
        decoded_image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)

        # Detect and read the captcha image ...
        captcha_code = solve_captcha(decoded_image)

        logger.info("Entered Captcha Code: "+ captcha_code)

        # if captcha_image.is_displayed(): logger.info(f"SOLVING CAPTCHA: {captcha_code}")

        try:
            locator = (By.XPATH, '/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[6]/fieldset/div/div[2]/div[3]/input')
            captcha_code_input = WebDriverWait(driver, 3).until(expected_conditions.element_to_be_clickable(locator))
        except TimeoutException:
            break

        # This is temporary
        captcha_code_input.send_keys(captcha_code)

        # Click 'Search' button
        search_button.click()
        logger.info("Clicked 'Search' button")

        # time.sleep(2)

        # driver.implicitly_wait(3)

        # Get the element containing a text of 'Captcha code does not match.'
        locator = (By.XPATH, ".//*[contains(text(), 'Captcha code does not match.')]")
        captcha_does_not_match_error = wait_until(
            instance = driver,
            condition = expected_conditions.presence_of_element_located(locator),
            timeout = 3
        )

        # driver.implicitly_wait(5)
        
        if captcha_does_not_match_error:
            logger.error("Captcha code does not match.")
            captcha_image.click()
            continue

        # Get the element container a text of 'Please fill in the captcha code'
        locator = (By.XPATH, ".//*[contains(text(), 'Please fill in the captcha code')]")
        captcha_empty_error = wait_until(
            instance = driver,
            condition = expected_conditions.presence_of_element_located(locator),
            timeout = 3,
        )
        if captcha_empty_error:
            logger.error("Please fill in the captcha code")
            captcha_image.click()
            continue

        break

    else:
        # Click 'Search' button
        search_button.click()
        logger.info("Clicked 'Search' button")
        time.sleep(3)

    search_result_buttons = []

    # Get all the firms in the search result
    locator = (By.TAG_NAME, "table")
    table = wait_until(
        instance = driver, 
        condition = expected_conditions.presence_of_element_located(locator), 
        timeout = 20,
        error_message = "The table does not exist!"
    )
    if table:
        rows = WebDriverWait(table, 60).until(
                expected_conditions.presence_of_all_elements_located((By.TAG_NAME, "tr"))
        )
        if len(rows) > 1: 
            data_cells = WebDriverWait(rows[1], 60).until(
                    expected_conditions.presence_of_all_elements_located((By.TAG_NAME, "td"))
            )
            if len(data_cells) > 0: search_result_buttons.append(data_cells[-1])

    # Skip if the search result is empty
    if len(search_result_buttons) == 0: continue

    # Before clicking the button to open popup, store the current window handle
    main_window = driver.current_window_handle

    # driver.execute_script("arguments[0].scrollIntoView();", search_result_buttons[0])

    # Click the 'Click for details' button
    search_result_buttons[0].click()

    logger.info("Clicked 'See for details'")

    # Switch to the popup window
    for handle in driver.window_handles:
        if handle != main_window:
            popup = handle
            driver.switch_to.window(popup)

    logger.info("Scraping data...")

    # ---------------------------------------------------------------------------------------------
    # Register of Licensed Insurance Intermediaries (Firm)

    # Prepare a dictionary for overall
    details = {
        "POLII": None,
        "AWCAP": None,
        "PL": None,
        "PDAL5": None,
        "N": None,
        "R": None,
    } 

    locator = (By.XPATH, "//div[contains(@class, 'containerSearch')]")
    container_search = wait_until(
        instance = driver, 
        condition = expected_conditions.presence_of_element_located(locator),
        timeout = 20,
        error_message = "Took too much time to load"
    )

    if container_search:

        container_search_panels = container_search.find_elements(By.CLASS_NAME, "panel")
        details["POLII"] = get_polii(details, container_search_panels[0])
        details["AWCAP"] = get_awcap(details, container_search_panels[1])
        details["PL"] = get_pl(details, container_search_panels[2])
        details["PDAL5"] = get_pdal5(details, container_search_panels[4])
        details["N"] = get_n(details, container_search_panels[5])

        # Load panel elements again. For some reason, the last panel gets 'StaleElementException' when it is not reloaded.
        container_search_panels = container_search.find_elements(By.CLASS_NAME, "panel")
        details["R"] = get_r(details, container_search_panels[6])

    # Temporarily show the retrieved details
    # logger.info(json.dumps(details, indent=4))

    # Save data

    # Create directory if not exists
    output_dir = os.path.join(firms_dir, license_no)
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    header = [item[0] for item in details["POLII"]["items"]]
    row = dict(details["POLII"]["items"])
    if not os.path.exists("firms_polii.csv"):
        with open(os.path.join("firms_polii.csv"), "w") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writeheader()
            writer.writerow(row)
    else:
        with open(os.path.join("firms_polii.csv"), "a") as file:
            writer = csv.DictWriter(file, fieldnames=header)
            writer.writerow(row)

    logger.info("Done.")

    # Close the popup window and switch back to the main window
    driver.close()
    driver.switch_to.window(main_window)

# This is temporary
input("Press enter to quit...")

# Quit Web Driver
driver.quit()
