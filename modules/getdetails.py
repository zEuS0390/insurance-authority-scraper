# Importing necessary exceptions and modules from Selenium for web scraping,
# and importing time and logging for handling delays and logging messages respectively.
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from modules.utils import wait_until
import time, logging

# Getting the root logger for logging messages.
logger = logging.getLogger()

# Function to extract content from a table within a panel.
def get_table_content(details, title, panel):

    try: getattr(details, title)
    except AttributeError: 
        # Log an error if the requested attribute doesn't exist within 'details'.
        logger.error(f"Invalid requested attribute '{title}' from Details")
        return
    
    # Set a new dictionary for the requested title within 'details'.
    setattr(details, title, {
        "header_columns": [],
        "data_rows": []
    })

    # Access the newly set dictionary.
    table = getattr(details, title)

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
        if len(data_cells) > 0: table["data_rows"].append(tuple([data_cell.text for data_cell in data_cells]))

# Function to extract content for 'Particulars of Licensed Insurance Intermediary' (POLII) section.
def get_polii(details, panel):
    # Initialize a dictionary for POLII within 'details'.
    details.POLII = {"items": []}

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
                panel_body_value = wait_until(
                    instance = row,
                    condition = expected_conditions.presence_of_element_located((By.TAG_NAME, "div")),
                    timeout = 20
                )
                if not panel_body_value: continue
                wait_until(
                    instance = panel_body_value,
                    condition = lambda _driver: panel_body_value.text != "",
                    timeout = 20
                )
                break
            except NoSuchElementException: continue
            except StaleElementReferenceException: continue
        details.POLII["items"].append((panel_body_label.text, panel_body_value.text))

# Function to extract content for 'Particulars of Licensed Insurance Intermediary's Appointment with Current Appointing Principal(s)' (AWCAP) section.
def get_awcap(details, panel): get_table_content(details, 'AWCAP', panel)

# Function to extract content for 'Details of Licensed Insurance Intermediary's Previous Licence' (PL) section.
def get_pl(details, panel): get_table_content(details, 'PL', panel)

# Function to extract content for 'Public Disciplinary Actions taken in the Last 5 Years' (PDAL5) section.
def get_pdal5(details, panel): get_table_content(details, 'PDAL5', panel)

# Function to extract content for 'Notes' (N) section.
def get_n(details, panel): get_table_content(details, 'N', panel)

# Function to extract content for 'Remarks' (R) section.
def get_r(details, panel):
    # Initialize a dictionary for R within 'details'.
    details.R = {"items": []}

    # Find div elements within the panel.
    div_elements = panel.find_elements(By.TAG_NAME, "div")

    # Get panel's heading and ordered list.
    panel_heading = div_elements[0].text
    panel_ordered_list = div_elements[1].find_element(By.TAG_NAME, "ol")

    # Retrieve items from the ordered list and append them to 'details.R["items"]'.
    items = panel_ordered_list.find_elements(By.TAG_NAME, "li")
    for item in items: details.R["items"].append(item.text)
