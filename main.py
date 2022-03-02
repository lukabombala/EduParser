from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import config
from collections import namedtuple

chrome_options = Options()
if config.background:
    chrome_options.add_argument("--headless")

mdriver = Chrome(options=chrome_options)


def messages_login(driver):
    driver.get('https://edukacja.pwr.wroc.pl/EdukacjaWeb/studia.do')
    driver.find_element(by=By.NAME, value='login').send_keys(config.username)
    driver.find_element(by=By.NAME, value='password').send_keys(config.password)
    driver.find_element(by=By.CLASS_NAME, value='BUTTON_ZALOGUJ').click()
    driver.find_element(by=By.XPATH, value="//a[@title='Wiadomości']").click()


def messages_parser(driver):
    while True:
        page_number = int(
            driver.find_element(by=By.CLASS_NAME, value="paging-numeric-btn-disabled").get_attribute('value'))
        elements = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "BIALA")))
        identifiers = create_identifiers(elements)
        for elem in identifiers:
            yield elem
        pages = driver.find_elements(by=By.CLASS_NAME, value='paging-numeric-btn')
        [page for page in pages if page.get_attribute('value') == f"{page_number + 1}"][0].click()


def create_identifiers(lst):
    indices = [(1, 2, 4), (6, 7, 9), (11, 12, 14), (16, 17, 19), (21, 22, 24)]
    Message = namedtuple('Message', 'sender topic date link')
    messages = []
    for ind in indices:
        m = Message(lst[ind[0]].text,
                    lst[ind[1]].find_element(by=By.TAG_NAME, value='a').get_attribute('text'),
                    lst[ind[2]].text,
                    lst[ind[1]].find_element(by=By.TAG_NAME, value='a').get_attribute('href'))
        messages.append(m)
    return messages


def check_identifier(message):
    pass


def main():
    try:
        messages_login(mdriver)
        parser = messages_parser(mdriver)
        for _ in range(15):
            print(next(parser))
    finally:
        if config.background:
            mdriver.quit()


if __name__ == '__main__':
    main()
