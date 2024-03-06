from selenium.webdriver.support import expected_conditions
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from modules.ocr import ocr_with_color_filtering
from selenium import webdriver
from modules.details import Details
from modules.utils import *
from modules.constants import *
import time

class Scraper:

    # Methods:
    #     select                    (name: str)
    #     _decode_captcha_image      (captcha_image: np.ndarray) -> str
    #     _enter_captcha_code        (captcha_code: str)
    #     _solve_captcha             ()
    #     _scrap_details             ()
    #     scrap                     (license_no: str)
    #     quit                      ()

    def __init__(self, output_dir):
        # Initialize Web Driver Options
        self._options = Options()
        # self._options.add_argument("-headless")

        # Initialize Web Driver with FireFox
        self._driver = webdriver.Firefox(options = self._options)

        self._is_firm = False
        self._output_dir = output_dir

    def select(self, name: str):

        self._driver.get(BASE_URL)

        # Wait till the page is fully loaded before clicking 'Search for Firm' link
        if name == 'firm': self._is_firm = True
        elif name == 'individual': self._is_firm = False
        else: raise ValueError("name parameter must be 'firm' or 'individual'")

        locator = (By.LINK_TEXT, 'Search for Firm' if self._is_firm else 'Search for Individual')
        select_button = waitUntil(self._driver, expected_conditions.presence_of_element_located(locator), 20)

        if select_button is None:
            logger.debug("Loading took too much time!")
            self._driver.quit()
            # This is temporary
            logger.info("Press enter to quit...")
            exit()

        logger.debug("Page is ready!")

        # Click 'Search for Firm' link
        select_button.click()

        # Wait till the page is fully loaded before filling up the form
        locator = (By.ID, 'licenseStatusc')
        license_status_all_checkbox = waitUntil(self._driver, expected_conditions.presence_of_element_located(locator), 20)

        locator = (By.ID, 'searchBy3' if self._is_firm else 'searchByI3')
        search_criteria_license_number_checkbox = waitUntil(self._driver, expected_conditions.presence_of_element_located(locator), 20)

        locator = (By.NAME, 'searchInputTxt' if self._is_firm else 'searchInputLicNo')
        self.search_criteria_input_txt = waitUntil(self._driver, expected_conditions.presence_of_element_located(locator), 20)

        locator = (By.XPATH, '/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[7]/div[1]/div/div/div/button')
        self.search_button = waitUntil(self._driver, expected_conditions.presence_of_element_located(locator), 20)

        if any(map(lambda element: element is None, [
                license_status_all_checkbox, 
                search_criteria_license_number_checkbox, 
                self.search_criteria_input_txt, 
                self.search_button
            ])):
            logger.debug("Loading took too much time!")
            self._driver.quit()
            # This is temporary
            input("Press enter to quit...")
            exit()

        license_status_all_checkbox.click()
        logger.debug("Selected 'All' in License Status section")

        search_criteria_license_number_checkbox.click()
        logger.debug("Selected 'License Number' in Search Criteria section")

    def _decode_captcha_image(self, captcha_image: np.ndarray) -> str:
        capture_catpcha_image_jscode = """
            let ele = arguments[0];
            let cnv = document.createElement('canvas');
            cnv.width = ele.width; 
            cnv.height = ele.height;
            cnv.getContext('2d').drawImage(ele, 0, 0);
        """

        waitUntil(
            instance = self._driver,
            condition = lambda _driver: self._driver.execute_script(
                capture_catpcha_image_jscode + "return cnv.toDataURL('image/jpeg').substring(22).length > 0;",
                captcha_image),
            timeout = 20,
            error_message = "Took too much time to load"
        )

        img_base64 = self._driver.execute_script(
            capture_catpcha_image_jscode + "return cnv.toDataURL('image/jpeg').substring(22);",
            captcha_image
        )
        
        # Read and solve the captcha image
        decoded_image = base64ToImage(img_base64)
        captcha_code = ocr_with_color_filtering(decoded_image)
        return captcha_code
    
    def _enter_captcha_code(self, captcha_code):

        locator = (
            By.XPATH, 
            '/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[6]/fieldset/div/div[2]/div[3]/input',
        )
        captcha_code_input = waitUntil(self._driver, expected_conditions.element_to_be_clickable(locator), 3)

        # This is temporary
        captcha_code_input.clear()
        captcha_code_input.send_keys(captcha_code)

        # Click 'Search' button
        self.search_button.click()
        logger.debug("Clicked 'Search' button")

    def _solve_captcha(self):
        captcha_image = self._driver.find_element(By.ID, "stickyImg")
        # locator = (By.XPATH, '/html/body/div/div/div/div/div[1]/form/div/div/div/div/div/div[6]/fieldset/div/div[2]/div[3]/input')
        # captcha_code_input = waitUntil(self._driver, expected_conditions.presence_of_element_located(locator), 20)

        while captcha_image.is_displayed():

            captcha_code = self._decode_captcha_image(captcha_image)

            logger.info("Entered Captcha Code: "+ captcha_code)
            self._enter_captcha_code(captcha_code)

            time.sleep(3)

            # Get the element containing a text of 'Captcha code does not match.'
            locator = (By.XPATH, ".//*[contains(text(), 'Captcha code does not match.')]")
            captcha_does_not_match_error = waitUntil(
                instance = self._driver,
                condition = expected_conditions.presence_of_element_located(locator),
                timeout = 3
            )
            if captcha_does_not_match_error:
                logger.debug("Captcha code does not match.")
                captcha_image.click()
                continue

            # Get the element container a text of 'Please fill in the captcha code'
            locator = (By.XPATH, ".//*[contains(text(), 'Please fill in the captcha code')]")
            captcha_empty_error = waitUntil(
                instance = self._driver,
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
            self.search_button.click()
            logger.debug("Clicked 'Search' button")
            time.sleep(3)

    def _scrap_details(self):

        search_result_buttons = []

        # Get all in the search result
        locator = (By.TAG_NAME, "table")
        table = waitUntil(
            instance = self._driver, 
            condition = expected_conditions.presence_of_element_located(locator), 
            timeout = 20,
            error_message = "The table does not exist!"
        )
        if table:
            rows = WebDriverWait(table, 60).until(
                    expected_conditions.presence_of_all_elements_located((By.TAG_NAME, "tr"))
            )
            if len(rows) > 1: 
                data_row = WebDriverWait(rows[1], 60).until(
                        expected_conditions.presence_of_all_elements_located((By.TAG_NAME, "td"))
                )
                if len(data_row) > 0: search_result_buttons.append(data_row[-1])

        # Skip if the search result is empty
        if len(search_result_buttons) == 0: return

        # Before clicking the button to open popup, store the current window handle
        main_window = self._driver.current_window_handle

        # Click the 'Click for details' button
        search_result_buttons[0].click()

        logger.debug("Clicked 'See for details'")

        # Switch to the popup window
        for handle in self._driver.window_handles:
            if handle != main_window:
                popup = handle
                self._driver.switch_to.window(popup)

        logger.debug("Scraping data...")

        locator = (By.XPATH, "//div[contains(@class, 'containerSearch')]")
        container_search = waitUntil(
            instance = self._driver, 
            condition = expected_conditions.presence_of_element_located(locator),
            timeout = 20,
            error_message = "Took too much time to load"
        )

        if container_search:
            details = Details()
            details.get(container_search)
            details.saveCSV(self._output_dir)

        # Close the popup window and switch back to the main window
        self._driver.close()
        self._driver.switch_to.window(main_window)

    def scrap(self, license_no):

        logger.debug("-"*15)

        self.search_criteria_input_txt.click() # The form will get an error if you did not include this in the process
        self.search_criteria_input_txt.clear()
        self.search_criteria_input_txt.send_keys(license_no)

        logger.info(f"Entered license number '{license_no}'")

        self._solve_captcha()
        self._scrap_details()

    def quit(self):
        self._driver.quit()