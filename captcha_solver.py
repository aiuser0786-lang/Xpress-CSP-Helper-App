import cv2
import numpy as np
import ddddocr
import easyocr
import pytesseract
import logging
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Set up logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s:%(levelname)s:%(message)s')

# Method 1: Using ddddocr

def solve_captcha_with_ddddocr(image_path):
    ocr = ddddocr.DdddOcr()
    result = ocr.classification(image_path)
    return result

# Method 2: Using easyocr

def solve_captcha_with_easyocr(image_path):
    reader = easyocr.Reader(['en'])
    image = cv2.imread(image_path)
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    upscaled_image = cv2.resize(gray_image, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    contrast_enhanced_image = cv2.convertScaleAbs(upscaled_image, alpha=1.5, beta=0)
    result = reader.readtext(contrast_enhanced_image)
    return ' '.join([text[1] for text in result])

# Method 3: Using pytesseract with multiple PSM modes

def solve_captcha_with_pytesseract(image_path):
    for psm in [8, 7, 6]:
        custom_config = f'--psm {psm}'
        result = pytesseract.image_to_string(image_path, config=custom_config)
        if result.strip():
            return result.strip()
    return None

# Main function to solve captcha

def solve_captcha(driver):
    retries = 3
    for attempt in range(retries):
        try:
            # Find all image tags with 'captcha' in src/alt
            images = driver.find_elements(By.TAG_NAME, 'img')
            captcha_images = [img for img in images if 'captcha' in img.get_attribute('src') or 'captcha' in img.get_attribute('alt')]
            if not captcha_images:
                logging.info('No captcha image found.')
                return None
            # Process the first captcha image
            captcha_image = captcha_images[0]
            captcha_image.screenshot('captcha.png')
            
            # Try each method of solving the captcha
            result = solve_captcha_with_ddddocr('captcha.png')
            if result:
                return result
            result = solve_captcha_with_easyocr('captcha.png')
            if result:
                return result
            result = solve_captcha_with_pytesseract('captcha.png')
            if result:
                return result
            logging.info('Failed to solve captcha on attempt %d', attempt + 1)
            driver.find_element(By.ID, 'refreshButton').click()  # Click refresh button
        except Exception as e:
            logging.error(f'Error during captcha solving: {e}')
            break
    return None

# Example usage: Set up Chrome WebDriver and navigate to a page
# options = Options()
# options.add_argument('--headless')  # Uncomment to run headless
# service = Service('/path/to/chromedriver')
# driver = webdriver.Chrome(service=service, options=options)
# driver.get('URL_TO_CAPTCHA_PAGE')
# captcha_solution = solve_captcha(driver)
# print('Captcha solved:', captcha_solution)

