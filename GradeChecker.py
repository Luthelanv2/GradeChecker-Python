import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pushbullet import Pushbullet

API_TOKEN = ''

username = ''
password = ''

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options, service=ChromeService(ChromeDriverManager().install()))
driver.get('https://www3.primuss.de/cgi-bin/login/index.pl')
driver.maximize_window()


def navigate():
    select = Select(driver.find_element(By.ID, 'FH'))
    select.select_by_value('fhh')
    try:
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'username'))).send_keys(username)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, 'password'))).send_keys(password)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, '_eventId_proceed'))).click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'A6'))).click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(
            (By.XPATH, '/html[1]/body[1]/div[1]/div[2]/div[2]/div[2]/div[2]/form[1]/input[6]'))).click()
        WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.NAME, 'Accept'))).click()
    except NoSuchElementException or TimeoutException:
        driver.quit()


def extract_grades():
    try:
        table = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'table2'))).get_attribute('outerHTML')
        soup = BeautifulSoup(table, 'html.parser')
        dataframe = pd.read_html(str(soup))[0]

        grades = []
        for grade in dataframe.Ergebnis:
            if grade != 'nicht teilgenommen':
                grade = grade[:1] + ',' + grade[1:]
            grades.append(grade)

        return dict(zip(dataframe.Titel, grades))
    except NoSuchElementException or TimeoutException:
        driver.quit()


def send_notification():
    push_bullet = Pushbullet(API_TOKEN)
    for key, value in extract_grades().items():
        if value != 'Korrektur noch nicht abgeschlossen':
            push_bullet.push_note('Notenbekanntgabe', '{}: {}'.format(key, value))


if __name__ == '__main__':
    navigate()
    send_notification()
    driver.close()
