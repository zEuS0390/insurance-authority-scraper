from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from modules.utils.scraper_utils import *
import time, logging

# Getting the root logger for logging messages.
logger = logging.getLogger()

# Definition of a class named 'Details'
class Details:

    # Methods:
    #     _get_table_content    (title: str, panel: WebElement) -> None
    #     _get_polii            (panel: WebElement) -> None
    #     _get_r                (panel: WebElement) -> None
    #     fetch                 (container_search: WebElement) -> Nnoe
    #     saveCSV               (output_dir: str) -> None
    
    # Constructor method to initialize instances of the class
    def __init__(self):
        # Initializing private attributes for different sections with 'None'
        self.POLII, self.AWCAP, self.PL, self.COL, self.PDAL5, self.N, self.R = None, None, None, None, None, None, None

    # Function to extract content from a table within a panel.
    def _get_table_content(self, title: str, panel: WebElement) -> None:

        try: getattr(self, title)
        except AttributeError: 
            # Log an error if the requested attribute doesn't exist within 'details'.
            logger.error(f"Invalid requested attribute '{title}' from Details")
            return
        
        # Set a new dictionary for the requested title within 'details'.
        setattr(self, title, {
            "header_columns": [],
            "data_rows": []
        })

        # Access the newly set dictionary.
        table = getattr(self, title)

        # Find the panel's heading.
        panel_heading = panel.find_element(By.CLASS_NAME, "panel-heading")

        # Expand the panel to view content, if it's necessary.
        if title == 'PL': panel_heading.click()

        try:
            # Attempt to find the table within the panel.
            panel_table = panel.find_element(By.CLASS_NAME, "table")
        except NoSuchElementException: 
            # Log a debug message if no table is found in the panel.
            logger.debug(f"No table found in '{title}'")
            return None
        
        # Retrieve all rows within the table.
        rows = panel_table.find_elements(By.TAG_NAME, "tr")

        # Extract header columns from the table.
        for header_row in rows:
            header_columns = header_row.find_elements(By.TAG_NAME, "th")
            if len(header_columns) > 0: table['header_columns'] = [header_column.text for header_column in header_columns]

        # Extract data cells from the table.
        for data_row in rows:
            data_cells = data_row.find_elements(By.TAG_NAME, "td")
            if len(data_cells) > 0: table["data_rows"].append([data_cell.text for data_cell in data_cells])

    # Function to extract content for 'Particulars of Licensed Insurance Intermediary' (POLII) section.
    def _get_polii(self, panel: WebElement):
        # Initialize a dictionary for POLII within 'details'.
        self.POLII = {"items": []}

        # Find panel's heading and body.
        panel_heading = panel.find_element(By.CLASS_NAME, "panel-heading")  
        panel_body = panel.find_element(By.CLASS_NAME, "panel-body")
        
        # Wait until the body content is fully loaded.
        while True:
            time.sleep(1)
            logger.debug("Trying...")
            try:
                rows = WebDriverWait(panel_body, 20).until(
                    expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "row"))
                )
                break
            except TimeoutException:
                continue

        # Populate items with rows.
        for row in rows:
            panel_body_label = row.find_element(By.TAG_NAME, "label")
            while True:
                try:
                    panel_body_value = waitUntil(
                        instance = row,
                        condition = expected_conditions.presence_of_element_located((By.TAG_NAME, "div")),
                        timeout = 20
                    )
                    if not panel_body_value: continue
                    waitUntil(
                        instance = panel_body_value,
                        condition = lambda _driver: panel_body_value.text != "",
                        timeout = 20
                    )
                    break
                except NoSuchElementException: continue
                except StaleElementReferenceException: continue
            self.POLII["items"].append((panel_body_label.text, panel_body_value.text))

    # Function to extract content for 'Remarks' (R) section.
    def _get_r(self, panel: WebElement):
        # Initialize a dictionary for R within 'details'.
        self.R = {"items": []}

        # Find div elements within the panel.
        div_elements = panel.find_elements(By.TAG_NAME, "div")

        # Get panel's heading and ordered list.
        panel_heading = div_elements[0].text
        panel_ordered_list = div_elements[1].find_element(By.TAG_NAME, "ol")

        # Retrieve items from the ordered list and append them to 'details.R["items"]'.
        items = panel_ordered_list.find_elements(By.TAG_NAME, "li")
        for item in items: self.R["items"].append(item.text)

    def fetch(self, container_search):
        container_search_panels = container_search.find_elements(By.CLASS_NAME, "panel")

        self._get_polii(container_search_panels[0])
        for index, title in enumerate(['AWCAP', 'PL', 'PDAL5', 'COL', 'N'], start=1):
            self._get_table_content(title, container_search_panels[index])

        # Load panel elements again. For some reason, the last panel gets 'StaleElementException' when it is not reloaded.
        container_search_panels = container_search.find_elements(By.CLASS_NAME, "panel")
        self._get_r(container_search_panels[6])

    def get(self) -> dict[str, any]:
        return {
            "POLII": self.POLII, 
            "AWCAP": self.AWCAP, 
            "PL": self.PL, 
            "COL": self.COL, 
            "PDAL5": self.PDAL5, 
            "N": self.N, 
            "R": self.R
        }
