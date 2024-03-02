from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from modules.details import Details
from modules.captcha import solve_captcha
import time, time, logging, csv, os
from modules.constants import *
from modules.utils import *
from modules.getdetails import *

# Initialize logger
logger = logging.getLogger(__name__)

def execute(select):

    # Initialize Web Driver Options
    options = Options()
    options.add_argument("-headless")

    # Initialize Web Driver with FireFox
    driver = webdriver.Firefox(options=options)
    driver.get(BASE_URL)

    # This is for the 'Licensed Insurance Agency/Licensed Insurance Broker Company'

    # Wait till the page is fully loaded before clicking 'Search for Firm' link
    if select == 'firm': is_firm = True
    elif select == 'individual': is_firm = False
    else: raise ValueError("select parameter must be 'firm' or 'individual'")

    output_filename = 'firms.csv' if is_firm else 'individuals.csv'

    locator = (By.LINK_TEXT, 'Search for Firm' if is_firm else 'Search for Individual')
    search_for_individual_button = wait_until(driver, expected_conditions.presence_of_element_located(locator), 20)

    if search_for_individual_button is None:
        logger.debug("Loading took too much time!")
        driver.quit()
        # This is temporary
        logger.info("Press enter to quit...")
        exit()

    logger.debug("Page is ready!")

    # Click 'Search for Firm' link
    search_for_individual_button.click()

    # Wait till the page is fully loaded before filling up the form
    locator = (By.ID, 'licenseStatusc')
    license_status_all_checkbox = wait_until(driver, expected_conditions.presence_of_element_located(locator), 20)

    locator = (By.ID, 'searchBy3' if is_firm else 'searchByI3')
    search_criteria_license_number_checkbox = wait_until(driver, expected_conditions.presence_of_element_located(locator), 20)

    locator = (By.NAME, 'searchInputTxt' if is_firm else 'searchInputLicNo')
    search_criteria_input_txt = wait_until(driver, expected_conditions.presence_of_element_located(locator), 20)

    locator = (By.XPATH, '/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[7]/div[1]/div/div/div/button')
    search_button = wait_until(driver, expected_conditions.presence_of_element_located(locator), 20)

    if any(map(lambda element: element is None, [
            license_status_all_checkbox, 
            search_criteria_license_number_checkbox, 
            search_criteria_input_txt, 
            search_button
        ])):
        logger.debug("Loading took too much time!")
        driver.quit()
        # This is temporary
        input("Press enter to quit...")
        exit()

    license_status_all_checkbox.click()
    logger.debug("Selected 'All' in License Status section")

    search_criteria_license_number_checkbox.click()
    logger.debug("Selected 'License Number' in Search Criteria section")

    params = (('F', 'G'), ('A', 'Z'), (1001, 9999)) if is_firm else (('I', 'J'), ('A', 'Z'), (1001, 9999))
    for license_no in generate_sequential_license_numbers(*params):

        logger.debug("-"*15)

        search_criteria_input_txt.click() # The form will get an error if you did not include this in the process
        search_criteria_input_txt.clear()
        search_criteria_input_txt.send_keys(license_no)
        logger.info(f"Entered license number '{license_no}'")

        captcha_image = driver.find_element(By.ID, "stickyImg")
        locator = (By.XPATH, '/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[6]/fieldset/div/div[2]/div[3]/input')
        captcha_code_input = wait_until(driver, expected_conditions.presence_of_element_located(locator), 20)

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
            
            # Read and solve the captcha image
            decoded_image = base64ToImage(img_base64)
            captcha_code = solve_captcha(decoded_image)

            logger.info("Entered Captcha Code: "+ captcha_code)

            locator = (
                By.XPATH, 
                '/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[6]/fieldset/div/div[2]/div[3]/input',
            )
            captcha_code_input = wait_until(driver, expected_conditions.element_to_be_clickable(locator), 3)

            # This is temporary
            captcha_code_input.clear()
            captcha_code_input.send_keys(captcha_code)

            # Click 'Search' button
            search_button.click()
            logger.debug("Clicked 'Search' button")

            time.sleep(3)

            # Get the element containing a text of 'Captcha code does not match.'
            locator = (By.XPATH, ".//*[contains(text(), 'Captcha code does not match.')]")
            captcha_does_not_match_error = wait_until(
                instance = driver,
                condition = expected_conditions.presence_of_element_located(locator),
                timeout = 3
            )
            
            if captcha_does_not_match_error:
                logger.debug("Captcha code does not match.")
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
                logger.debug("Please fill in the captcha code")
                captcha_image.click()
                continue

            break

        else:
            # Click 'Search' button
            search_button.click()
            logger.debug("Clicked 'Search' button")
            time.sleep(3)

        search_result_buttons = []

        # Get all in the search result
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

        # Click the 'Click for details' button
        search_result_buttons[0].click()

        logger.debug("Clicked 'See for details'")

        # Switch to the popup window
        for handle in driver.window_handles:
            if handle != main_window:
                popup = handle
                driver.switch_to.window(popup)

        logger.debug("Scraping data...")

        # Prepare a dictionary for overall
        details = Details()

        locator = (By.XPATH, "//div[contains(@class, 'containerSearch')]")
        container_search = wait_until(
            instance = driver, 
            condition = expected_conditions.presence_of_element_located(locator),
            timeout = 20,
            error_message = "Took too much time to load"
        )

        if container_search:

            container_search_panels = container_search.find_elements(By.CLASS_NAME, "panel")
            get_polii(details, container_search_panels[0])
            get_awcap(details, container_search_panels[1])
            get_pl(details, container_search_panels[2])
            get_pdal5(details, container_search_panels[4])
            get_n(details, container_search_panels[5])

            # Load panel elements again. For some reason, the last panel gets 'StaleElementException' when it is not reloaded.
            container_search_panels = container_search.find_elements(By.CLASS_NAME, "panel")
            get_r(details, container_search_panels[6])

            # Save data

            header = [item[0] for item in details.POLII["items"]] + ["Remark",]
            polii = dict(details.POLII["items"])
            r = {"Remark": "\n".join([f"{no}. {item}" for no, item in enumerate(details.R["items"], start=1)])}
            row = {**polii, **r}

            # Write header columns if the file is newly created
            if not os.path.exists(output_filename):
                with open(os.path.join(output_filename), "a", newline='', encoding="utf-8") as file:
                    writer = csv.DictWriter(file, fieldnames=header)
                    writer.writeheader()

            # Write data
            with open(os.path.join(output_filename), "a", newline='', encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=header)
                writer.writerow(row)

            logger.debug("Done.")

        # Close the popup window and switch back to the main window
        driver.close()
        driver.switch_to.window(main_window)

    driver.quit()