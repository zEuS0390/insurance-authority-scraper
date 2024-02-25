from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time, base64, time, logging, json
from modules.constants import *
from modules.firm import *

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
    license_status_all_checkbox = WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located((By.ID, 'licenseStatusc'))
    )
    search_criteria_license_number_checkbox = WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located((By.ID, 'searchBy3'))
    )
    search_criteria_input_txt = WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located((By.NAME, 'searchInputTxt'))
    )
    search_button = WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[7]/div[1]/div/div/div/button'))
    )
    captcha_code_input = WebDriverWait(driver, 3).until(
            expected_conditions.presence_of_element_located((By.XPATH, '/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[6]/fieldset/div/div[2]/div[3]/input'))
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

captcha_image = driver.find_element(By.ID, "stickyImg")

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
    timeout = 10,
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

with open(r"captcha_image.jpg", "wb") as f:
    f.write(base64.b64decode(img_base64))

# Detect and read the captcha image ...

# This is temporary
captcha_code = input("Enter Captcha Code: ")
captcha_code_input.send_keys(captcha_code)


for license_no in ["FA1001", "FA1002", "FA1003", "FA1004", "FA1005", "FA1006", "FB1360", "FB1468", "FB1552"]:
    
    logger.info("-"*15)

    search_criteria_input_txt.clear()
    search_criteria_input_txt.send_keys(license_no)
    logger.info(f"Entered license number '{license_no}'")

    # Click 'Search' button
    search_button.click()
    logger.info("Clicked 'Search' button")

    # Get the element containing a text of 'Captcha code does not match.'
    locator = (By.XPATH, ".//*[contains(text(), 'Captcha code does not match.')]")
    captcha_does_not_match_error = wait_until(
        instance = driver,
        condition = expected_conditions.presence_of_element_located(locator),
        timeout = 2
    )
    if captcha_does_not_match_error:
        logger.error("Captcha code does not match.")
        # This is temporary
        input("Press enter to quit...")
        driver.quit()
        exit()

    # Get the element container a text of 'Please fill in the captcha code'
    locator = (By.XPATH, ".//*[contains(text(), 'Please fill in the captcha code')]")
    captcha_empty_error = wait_until(
        instance = driver,
        condition = expected_conditions.presence_of_element_located(locator),
        timeout = 2,
    )
    if captcha_empty_error:
        logger.error("Please fill in the captcha code")
        # This is temporary
        input("Press enter to quit...")
        driver.quit()
        exit()

    search_result_buttons = []

    # Get all the firms in the search result
    locator = (By.XPATH, "/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[9]/div/div[1]/table")
    table = wait_until(
        instance = driver, 
        condition = expected_conditions.presence_of_element_located(locator), 
        timeout = 10,
        error_message = "The table does not exist!"
    )
    if table:
        rows = table.find_elements(By.TAG_NAME, "tr")
        for row in rows:
            col = row.find_elements(By.TAG_NAME, "td")
            if len(col) > 0: search_result_buttons.append(col[-1])

    # Skip if the search result is empty
    if len(search_result_buttons) == 0: continue

    # Before clicking the button to open popup, store the current window handle
    main_window = driver.current_window_handle

    # Click the 'Click for details' button
    search_result_buttons[0].click()

    logger.info("Clicked 'See for details'")

    # Switch to the popup window
    for handle in driver.window_handles:
        if handle != main_window:
            popup = handle
            driver.switch_to.window(popup)

    logger.info("Scrapping data...")

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
        timeout = 10,
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
    logger.info(json.dumps(details, indent=4))

    # Close the popup window and switch back to the main window
    driver.close()
    driver.switch_to.window(main_window)

# This is temporary
input("Press enter to quit...")

# Quit Web Driver
driver.quit()
