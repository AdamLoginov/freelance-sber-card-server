import json
import time
import random
import os

import requests

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

os.chdir(os.path.dirname(os.path.abspath(__file__)))

URL = 'https://www.sberbank.com/ru/person/bank_cards/debit/sberkarta'

URL_HOST = "http://89.104.67.76:8999"
# URL_HOST = "http://127.0.0.1:8000"



def get_user_agent():
    with open('user-agent.txt', 'r', encoding='utf-8') as file:
        return(file.read().split('\n')[random.randint(0,1000)])

def click_button(driver, path):
    js_command = f"""
        document.evaluate('{path}', 
                            document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()
    """
    driver.execute_script(js_command)

def find_button(driver, path):
    js_command = f"""
        clickButton = document.evaluate('{path}', 
                            document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue
    """
    driver.execute_script(js_command)

def click_button_test(driver):
    js_command = """
        clickButton.click()
    """
    driver.execute_script(js_command)

def get_ChromeOptions():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument("--incognito")
    options.add_argument('--no-sandbox')


    options.add_argument('--remote-debugging-address=0.0.0.0')
    options.add_argument(f"--remote-debugging-port=9222")
    options.add_argument("--remote-allow-origins=*")

    device_emulation = {
        "deviceMetrics": {"width": 360, "height": 640, "pixelRatio": 3.0},
        "userAgent": f"{get_user_agent()}",
    }
    options.add_experimental_option("mobileEmulation", device_emulation)

    options.add_argument('--disable-logging')

    return options

def go_form_1(wait, driver, data):
    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//button[@class="do-kit-button do-kit-button_type_primary do-kit-button_size_md do-home__step-button"]')))
    
    driver.find_element(By.XPATH, '//input[@id="do-form__lastName"]').send_keys(data['data']['lastName'])
    driver.find_element(By.XPATH, '//input[@id="do-form__firstName"]').send_keys(data['data']['firstName'])
    driver.find_element(By.XPATH, '//input[@id="do-form__middleName"]').send_keys(data['data']['sureName'])

def go_form_2(wait, driver, data):
    wait.until(EC.presence_of_all_elements_located((By.XPATH, '//button[@class="do-kit-button do-kit-button_type_primary do-kit-button_size_md do-personal__step-button"]')))
    
    ActionChains(driver).click(
        driver.find_element(By.XPATH, '//input[@id="do-form__seriesNumber"]')
        ).send_keys(data['data']['pasport']).perform()
    
    ActionChains(driver).click(
        driver.find_element(By.XPATH, '//input[@id="do-form__issueDate"]')
    ).send_keys(data['data']['dateOfIssue']).perform()

    ActionChains(driver).click(
        driver.find_element(By.XPATH, '//input[@id="do-form__birthDate"]')
    ).send_keys(data['data']['dateOfBorn']).perform()

def post_host(status, message):
    response = requests.post(f'{URL_HOST}/post/', json={
        "data": {
            "status": status,
            "message": message
        } 
    })
    print(message)
    print(f'Code: {response.status_code}, Answer: {response.json()}')

if __name__ == "__main__":
    try:
        post_host('wait', 'start listen')

        while json.loads(requests.get(f'{URL_HOST}/get-command/').content.decode('utf-8'))['command'] == 'wait': time.sleep(5)
        post_host('wait', 'Start script')

        data = json.loads(requests.get(f'{URL_HOST}/get-data/').content.decode('utf-8'))
        post_host('wait', 'Data received successfully')
        
        with webdriver.Chrome(options=get_ChromeOptions()) as driver:
            wait = WebDriverWait(driver, 120)
            wait_map = WebDriverWait(driver, 1200)

            driver.get(URL)
            post_host('wait', 'Get sber Successfully')

            go_form_1(wait=wait, driver=driver, data=data)
            post_host('wait', 'Form №1 Successfully')
            # click_button(driver=driver,
            #                 path='//button[@class="do-kit-button do-kit-button_type_primary do-kit-button_size_md do-home__step-button"]')
            # post_host('wait', 'Form №1 press button Successfully')
            # go_form_2(wait=wait, driver=driver, data=data)
            # post_host('debag-url', 'Form №2 Successfully debag-url')
            
            # wait_map.until(EC.presence_of_all_elements_located((By.XPATH, '//button[@class="do-kit-button do-kit-button_type_primary do-kit-button_size_md do-office__step-button"]')))

            # find_button(driver=driver,
            #     path='//button[@class="do-kit-button do-kit-button_type_primary do-kit-button_size_md do-office__step-button"]')
            find_button(driver=driver,
                path='//button[@class="do-kit-button do-kit-button_type_primary do-kit-button_size_md do-home__step-button"]')

            post_host('ready', 'Host ready to press button')

            commandHost = None
            while commandHost != 'press':
                responseHost = json.loads(requests.get(f'{URL_HOST}/get-command/').content.decode('utf-8'))
                commandHost =  responseHost['command']
                timeHost = responseHost['time']
                time.sleep(5)

            post_host('ready', 'Host waits time')
            
            while (time.time() < timeHost): pass
            click_button_test(driver=driver)
            timePressButton = time.time()
            post_host('finish', f'Button press time: {timePressButton}')

            time.sleep(10)
            try:
                content = driver.find_element(By.XPATH, '//h2[@class="do-kit-heading do-kit-heading_size_lg do-kit-heading_grey do-final__heading"]').text
                post_host('finish', f'{content}, time: {timePressButton}')
            except Exception as ex:
                post_host('finish', f'Error finish page, time: {timePressButton}')



    except KeyboardInterrupt:
        post_host('error', 'Script terminated ahead of schedule ctrl + C')
    except Exception as ex:
        post_host('error', 'Script ERROR')