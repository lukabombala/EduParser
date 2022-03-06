from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from collections import namedtuple
import notifier
import sqlite3 as sl
import config


def database_init():
    con = sl.connect(config.database_name)

    with con:
        cur = con.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS MESSAGE (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                sender TEXT,
                date DATE,
                content TEXT
            );
        """)


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


def get_message_content(driver, message):
    driver.get(message.link)
    elements = WebDriverWait(driver, 20).until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "BIALA")))
    text = elements[15].text
    driver.find_element(by=By.NAME, value='event_refreshPost').click()
    return text


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


def check_identifier(driver, conn, message):
    with conn:
        cur = conn.cursor()
        cur.execute("""
        SELECT *
        FROM MESSAGE
        WHERE title=?
        AND sender=?
        AND date=?
        """, (message.topic, message.sender, message.date))
        rows = cur.fetchall()
        if not rows:
            text = get_message_content(driver, message)
            cur.execute("""INSERT INTO MESSAGE (title, sender, date, content)
                           VALUES (?, ?, ?, ?)""", (message.topic, message.sender, message.date, text))
            notifier.send(message, text)
            return True
        return False


def main():
    database_init()

    chrome_options = Options()
    if config.background:
        chrome_options.add_argument("--headless")

    mdriver = Chrome(options=chrome_options)
    con = sl.connect(config.database_name)

    try:
        messages_login(mdriver)
        parser = messages_parser(mdriver)
        ind = 0
        while ind < config.stop_value:
            mes = next(parser)
            check = check_identifier(mdriver, con, mes)
            if not check:
                break
            ind += 1

    finally:
        if config.background:
            mdriver.quit()


if __name__ == '__main__':
    main()
