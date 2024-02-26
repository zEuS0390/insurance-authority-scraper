from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import time, logging

logger = logging.getLogger()

def wait_until_element_text_changes(element, timeout):
    try:
       WebDriverWait(element, timeout).until(
            lambda _driver: element.text != ""
       )
       return True
    except TimeoutException: 
        logger.error(f"Text did not change")
        return False

def wait_until_panel_body_value_appears(element, timeout):
    while True:
        try:
            panel_body_value = WebDriverWait(element, timeout).until(
                    expected_conditions.presence_of_element_located((By.TAG_NAME, "div"))
            )
            wait_until_element_text_changes(panel_body_value, timeout)
            return panel_body_value
        except NoSuchElementException:
            continue
        except StaleElementReferenceException:
            continue

# ---------------------------------------------------------------------------------------------
# POLII - Particulars of Licensed Insurance Intermediary
def get_polii(details, panel):

    # Prepare a dictionary for POLII
    """
    POLII = {
        "name": None,                       # Name
        "license_no": None,                 # License No.
        "license_type": None,               # License Type
        "lines_of_business": None,          # Line(s) of Business the Licensed Insurace may carry on
        "license_period:": None,            # License Period
        "business_address": None,           # Business Address
        "telephone_number": None,           # Telephone Number
        "fax_number": None,                 # Fax Number
        "website": None,                    # Website
        "email_address": None,              # Email Address
        "responsible_officers": None        # Responsible Officer(s)
    }
    """

    POLII = {
        "items": []
    }

    # Get panel's heading and body
    panel_heading = panel.find_element(By.CLASS_NAME, "panel-heading")  
    panel_body = panel.find_element(By.CLASS_NAME, "panel-body")
   
    while True:
        time.sleep(1)
        logger.info("Trying...")
        try:
            rows = WebDriverWait(panel_body, 10).until(
                expected_conditions.presence_of_all_elements_located((By.CLASS_NAME, "row"))
            )

            if len(rows) != 11:
                continue

            break
        except TimeoutException:
            continue 

    # Populate items with rows
    for row in rows:
        panel_body_label = row.find_element(By.TAG_NAME, "label")
        panel_body_value = wait_until_panel_body_value_appears(row, 10)
        POLII["items"].append((panel_body_label.text, panel_body_value.text))

    return POLII

# ---------------------------------------------------------------------------------------------
# AWCAP - Particulars of Licensed Insurance Intermediary's Appointment with Current Appointing Principal(s)
def get_awcap(details, panel):

    # Prepare a dictionary for AWCAP
    AWCAP = {
        "column_headers": [
            "Name of Appointing Principal(s)", 
            "Line(s) of Business which the Licenced Insurance Intermediary is appointed by the Appointing Principal to carry on",
            "Date of Appointment"
        ],
        "data_cells": []
    }

    # Get panel's heading and table
    panel_heading = panel.find_element(By.CLASS_NAME, "panel-heading")

    # Skip when the panel's content shows 'Nil' (The word 'Nil' means nothing or zero)
    try:
        panel_table = panel.find_element(By.CLASS_NAME, "table")
    except NoSuchElementException: 
        logger.info("No table found in 'Particulars of Licensed Insurance Intermediary's Appointment with Current Appointing Principal(s)'")
        return None

    rows = panel_table.find_elements(By.TAG_NAME, "tr")

    # Iterate through the data cells
    for row in rows:
        data_cells = row.find_elements(By.TAG_NAME, "td")
        if len(data_cells) > 0:
            AWCAP["data_cells"].append(tuple([data_cell.text for data_cell in data_cells]))

    return AWCAP

# ---------------------------------------------------------------------------------------------
# PL - Details of Licensed Insurance Intermediary's Previous Licence
def get_pl(details, panel):

    # Prepare a dictionary for PL
    PL = {
        "column_headers": [
            "Licence Type",
            "Licence Period",
            "Name of Appointing Principal(s)",
            "Line(s) of Business which the Licensed Insurance Intermediary was (appointed by the Appointing Principal) or (granted by the Insurance Authority) to carry on",
            "Date of (Appointment) or (Granting) and Termination",
        ],
        "data_cells": []
    }

    # Get panel's heading and table
    panel_heading = panel.find_element(By.CLASS_NAME, "panel-heading")

    # Click the panel headng to open and view content (Reminder: data cells will not appear if the content is hidden)
    panel_heading.click()

    # Skip when the panel's content shows 'Nil'
    try:
        panel_table = panel.find_element(By.CLASS_NAME, "table")
    except NoSuchElementException: 
        logger.info("No table found in 'Details of Licensed Insurance Intermediary's Previous Licence'")
        return None

    rows = panel_table.find_elements(By.TAG_NAME, "tr")

    # Iterate through the data cells
    for row in rows:
        data_cells = row.find_elements(By.TAG_NAME, "td")
        if len(data_cells) > 0:
            PL["data_cells"].append(tuple([data_cell.text for data_cell in data_cells]))

    return PL

# ---------------------------------------------------------------------------------------------
# PDAL5 - Public Disciplinary Actions taken in the Last 5 Years
def get_pdal5(details, panel):

    # Prepare a dictionary for PDAL5
    PDAL5 = {
        "column_headers": [
            "Date of Action",
            "Action Taken",
            "Press Release"
        ],
        "data_cells": []
    }

    # Get panel's heading and table
    panel_heading = panel.find_element(By.CLASS_NAME, "panel-heading")
    
    # Skip when the panel's content shows 'Nil' 
    try:
        panel_table = panel.find_element(By.CLASS_NAME, "table")
    except NoSuchElementException: 
        logger.info("No table found in 'Public Disciplinary Actions taken in the Last 5 Years'")
        return None

    rows = panel_table.find_elements(By.TAG_NAME, "tr")

    # Iterate through the data cells
    for row in rows:
        data_cells = row.find_elements(By.TAG_NAME, "td")
        if len(data_cells) > 0:
            PDAL5["data_cells"].append(tuple([data_cell.text for data_cell in data_cells]))

    return PDAL5

# ---------------------------------------------------------------------------------------------
# N - Notes
def get_n(details, panel):
    
    # Prepare a dictionary for N
    details["N"] = {}

    # Get panel's heading and content
    panel_heading = panel.find_element(By.CLASS_NAME, "panel-heading")

    return None

# ---------------------------------------------------------------------------------------------
# R - Remarks
def get_r(details, panel):

    # Prepare a dictionary for R
    R = {"items": []}

    div_elements = panel.find_elements(By.TAG_NAME, "div")

    # Get panel's heading and ordered list
    panel_heading = div_elements[0].text
    panel_ordered_list = div_elements[1].find_element(By.TAG_NAME, "ol")

    items = panel_ordered_list.find_elements(By.TAG_NAME, "li")

    for item in items: R["items"].append(item.text)

    return R
