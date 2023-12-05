import json
import time
import random
import socket

from selenium import webdriver

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


HOST = '0.0.0.0'
PORT = 12345

URL = 'https://www.sberbank.com/ru/person/bank_cards/debit/sberkarta'

USER_AGENT = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.1 Mobile/15E148 Safari/604.1'

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



if __name__ == "__main__":
    with  socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((HOST, PORT))

        print('start listen')
        server_socket.listen(1)
        client_socket, addr = server_socket.accept()

        data = json.loads(client_socket.recv(1024).decode('utf-8'))
        print(data)
        print(data['data']['pasport'],data['data']['dateOfIssue'],data['data']['dateOfBorn'])
        try:
            with webdriver.Chrome(options=get_ChromeOptions()) as driver:
                wait = WebDriverWait(driver, 120)
                wait_map = WebDriverWait(driver, 600)

                driver.get(URL)
                client_socket.send(json.dumps({'command':'debag-url'}).encode('utf-8'))
                print(1)
                go_form_1(wait=wait, driver=driver, data=data)
                print(2)
                click_button(driver=driver,
                             path='//button[@class="do-kit-button do-kit-button_type_primary do-kit-button_size_md do-home__step-button"]')
                print(3)
                go_form_2(wait=wait, driver=driver, data=data)
                print(4)

                wait_map.until(EC.presence_of_all_elements_located((By.XPATH, '//button[@class="do-kit-button do-kit-button_type_primary do-kit-button_size_md do-office__step-button"]')))

                find_button(driver=driver,
                    path='//button[@class="do-kit-button do-kit-button_type_primary do-kit-button_size_md do-office__step-button"]')
                
                client_socket.send(json.dumps({'command':'ready'}).encode('utf-8'))

                command = None
                timeStart = None
                while command == None:
                    second_data = json.loads(client_socket.recv(1024).decode('utf-8'))
                    if second_data['command'] == 'press':
                        command = 'press'
                        timeStart = second_data['time'] 

                print('start time') 

                while (time.time() < timeStart): pass
                click_button_test(driver=driver)
                timePressButton = time.time()
                print(f'time press button {timePressButton}')

                command = None
                while command == None:
                    command_client = json.loads(client_socket.recv(1024).decode('utf-8'))['command']
                    if command_client == 'close':
                        command = 'close'

                client_socket.send(json.dumps({'command':'', 'message':'server-close'}).encode('utf-8'))
        
        except Exception as ex:
            print(ex)
        finally:
            client_socket.send(json.dumps({'command':'error'}).encode('utf-8'))
            

        
        