from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from modules.utils import wait_until
import time, logging

logger = logging.getLogger()

# POLII - Particulars of Licensed Insurance Intermediary
def get_polii(details, panel):

    # Prepare a dictionary for POLII

    details.POLII = {
        "items": []
    }

    # Get panel's heading and body
    panel_heading = panel.find_element(By.CLASS_NAME, "panel-heading")  
    panel_body = panel.find_element(By.CLASS_NAME, "panel-body")
    
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

    # Populate items with rows
    for row in rows:
        panel_body_label = row.find_element(By.TAG_NAME, "label")
        while True:
            try:
                panel_body_value = wait_until(
                    instance = row,
                    condition = expected_conditions.presence_of_element_located((By.TAG_NAME, "div")),
                    timeout = 20
                )
                wait_until(
                    instance = panel_body_value,
                    condition = lambda _driver: panel_body_value.text != "",
                    timeout = 20
                )
                break
            except NoSuchElementException: continue
            except StaleElementReferenceException: continue
        details.POLII["items"].append((panel_body_label.text, panel_body_value.text))

# ---------------------------------------------------------------------------------------------
# AWCAP - Particulars of Licensed Insurance Intermediary's Appointment with Current Appointing Principal(s)
def get_awcap(details, panel):

    # Prepare a dictionary for AWCAP
    details.AWCAP = {
        "header_columns": [],
        "data_cells": []
    }

    # Get panel's heading and table
    panel_heading = panel.find_element(By.CLASS_NAME, "panel-heading")

    # Skip when the panel's content shows 'Nil' (The word 'Nil' means nothing or zero)
    try:
        panel_table = panel.find_element(By.CLASS_NAME, "table")
    except NoSuchElementException: 
        logger.debug("No table found in 'Particulars of Licensed Insurance Intermediary's Appointment with Current Appointing Principal(s)'")
        return None
    
    rows = panel_table.find_elements(By.TAG_NAME, "tr")

    # Obtain header columns
    for header_row in rows:
        header_columns = header_row.find_elements(By.TAG_NAME, "th")
        if len(header_columns) > 0: details.AWCAP['header_columns'].append(tuple([header_column.text for header_column in header_columns]))

    # Iterate through the data cells
    for data_row in rows:
        data_cells = data_row.find_elements(By.TAG_NAME, "td")
        if len(data_cells) > 0: details.AWCAP["data_cells"].append(tuple([data_cell.text for data_cell in data_cells]))

# ---------------------------------------------------------------------------------------------
# PL - Details of Licensed Insurance Intermediary's Previous Licence
def get_pl(details, panel):

    # Prepare a dictionary for PL
    details.PL = {
        "header_columns": [],
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
        logger.debug("No table found in 'Details of Licensed Insurance Intermediary's Previous Licence'")
        return

    rows = panel_table.find_elements(By.TAG_NAME, "tr")
    
    # Obtain header columns
    for header_row in rows:
        header_columns = header_row.find_elements(By.TAG_NAME, "th")
        if len(header_columns) > 0: details.PL['header_columns'].append(tuple([header_column.text for header_column in header_columns]))

    # Iterate through the data cells
    for row in rows:
        data_cells = row.find_elements(By.TAG_NAME, "td")
        if len(data_cells) > 0: details.PL["data_cells"].append(tuple([data_cell.text for data_cell in data_cells]))

# ---------------------------------------------------------------------------------------------
# PDAL5 - Public Disciplinary Actions taken in the Last 5 Years
def get_pdal5(details, panel):

    # Prepare a dictionary for PDAL5
    details.PDAL5 = {
        "header_columns": [],
        "data_cells": []
    }

    # Get panel's heading and table
    panel_heading = panel.find_element(By.CLASS_NAME, "panel-heading")
    
    # Skip when the panel's content shows 'Nil' 
    try:
        panel_table = panel.find_element(By.CLASS_NAME, "table")
    except NoSuchElementException: 
        logger.debug("No table found in 'Public Disciplinary Actions taken in the Last 5 Years'")
        return

    rows = panel_table.find_elements(By.TAG_NAME, "tr")

    # Obtain header columns
    for header_row in rows:
        header_columns = header_row.find_elements(By.TAG_NAME, "th")
        if len(header_columns) > 0: details.PDAL5['header_columns'].append(tuple([header_column.text for header_column in header_columns]))

    # Iterate through the data cells
    for row in rows:
        data_cells = row.find_elements(By.TAG_NAME, "td")
        if len(data_cells) > 0: details.PDAL5["data_cells"].append(tuple([data_cell.text for data_cell in data_cells]))

# ---------------------------------------------------------------------------------------------
# N - Notes
def get_n(details, panel):
    
    # Prepare a dictionary for N
    details.N = {}

    # Get panel's heading and content
    panel_heading = panel.find_element(By.CLASS_NAME, "panel-heading")

# ---------------------------------------------------------------------------------------------
# R - Remarks
def get_r(details, panel):

    # Prepare a dictionary for R
    details.R = {"items": []}

    div_elements = panel.find_elements(By.TAG_NAME, "div")

    # Get panel's heading and ordered list
    panel_heading = div_elements[0].text
    panel_ordered_list = div_elements[1].find_element(By.TAG_NAME, "ol")

    items = panel_ordered_list.find_elements(By.TAG_NAME, "li")

    for item in items: details.R["items"].append(item.text)
