from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
from pathlib import Path
import logging
import time
import sys


path_to_log = Path(__file__).resolve().parent / 'app.log'

dummy_data = {
    'first-name' : "FIRSTNAME",
    'last-name' : "LASTNAME",
    'email' : "YOUREMAIL",
    'phone' : "YOURNUMBER",
    'others' : '',
    'cover-letter' : 'PATH/TO/FILE',
    'resume': 'PATH/TO/FILE',
    'job' : 'JOBTITLE'
    # Add more as needed
}

mapping = {
    'last-name': 'last-name',
    'family-name': 'last-name',
    'l-name': 'last-name',
    'first-name': 'first-name',
    'name' : 'first-name',
    'given-name': 'first-name',
    'f-name': 'first-name',
    'email' : 'email',
    'mail' : 'email',
    'e-mail' : 'email',
    'phone' : 'phone',
    'phone-number' : 'phone',
    'number' : 'phone',
    'resume' : 'resume',
    'cv' : 'resume',
    'curriculum-vitae' : 'resume',
    'application-letter' : 'cover-letter',
    'cover-letter' : 'cover-letter',
    'upload-resume' : 'resume',
    'application-for' : 'job'
    # Add more mappings as needed
}

# Set up logging
logging.basicConfig(level=logging.INFO,
                    filename=path_to_log,
                    filemode="a",
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define functions for getting field names, standardizing them, and getting values from dummy data
def get_field_name(field, soup):
    """Get the field name from the label associated with the field."""
    label = soup.find("label", {"for":field.attrs['id']})
    return label.get_text().strip().replace("*", "").replace(" ", "-").lower()

def standardize_field_name(name):
    """Standardize the field name according to the mapping."""
    return mapping.get(name, 'others')

def get_field_value(name):
    """Get the field value from the dummy data."""
    return dummy_data.get(name, '')

def fill_field(driver, field, soup):
    """Fill in the given form field with the appropriate value."""
    if 'id' in field.attrs:
        # Get the field name and value
        field_name = get_field_name(field, soup)
        standardized_name = standardize_field_name(field_name)
        field_value = get_field_value(standardized_name)
        
        # Fill in the field
        field_type = field.get('type', '')
        if field_type == 'select':
            # Handle select fields separately
            options = [option.string for option in field.find_all('option')]
            if field_value not in options:
                raise ValueError(f"{field_name} value '{field_value}' not found in options.")
            index = options.index(field_value)
            select_elem = driver.find_element(By.ID, field.attrs['id'])
            select = Select(select_elem)
            select.select_by_visible_text(options[index])
        else:
            driver.find_element(By.ID, field.attrs['id']).send_keys(field_value)
    elif 'name' in field.attrs:
        # Get the field name and value
        field_name = field.attrs['name'].strip().replace("*", "").replace(" ", "-").lower()
        standardized_name = standardize_field_name(field_name)
        field_value = get_field_value(standardized_name)
        
        # Fill in the field
        field_type = field.get('type', '')
        if field_type == 'select':
            # Handle select fields separately
            options = [option.string for option in field.find_all('option')]
            if field_value not in options:
                raise ValueError(f"{field_name} value '{field_value}' not found in options.")
            index = options.index(field_value)
            select_elem = driver.find_element(By.NAME, field.attrs['name'])
            select = Select(select_elem)
            select.select_by_visible_text(options[index])
        else:
            driver.find_element(By.NAME, field.attrs['name']).send_keys(field_value)

# Define the main function
def main():
    
    if len(sys.argv) != 2:
        logging.error(f"You must provide an URL")
        sys.exit
    url = sys.argv[1]
    # Set up the webdriver and navigate to the form
    driver = webdriver.Chrome()
    driver.get(url)
    content = driver.page_source

    # Parse the form using BeautifulSoup
    soup = BeautifulSoup(content, 'html.parser')
    fields = soup.select('input[required], select[required], input[type=file]')

    # Fill in the form fields
    try:
        for field in fields:
            fill_field(driver, field, soup)
    except Exception as e:
        logging.error(f"Error filling in form field: {e}")

    # Wait for a bit to ensure the form is filled in before closing the browser
    time.sleep(5)
    driver.close

if __name__ == '__main__':
    main()
