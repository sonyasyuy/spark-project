import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.keys import Keys

"""
Парсер, с помощью которого можно выгрузить данные из https://spark-interfax.ru/
Нужно загрузить из .env SPARK_LOGIN и SPARK_PASSWORD
"""

class SparkParser:
    def __init__(self):
        load_dotenv()
        self.LOGIN = os.getenv("SPARK_LOGIN")
        self.PASSWORD = os.getenv("SPARK_PASSWORD")
        self.COOKIES_PATH = "cookies.pkl"
        self.driver = self.create_driver()

        self.load_or_login()
        time.sleep(2)
        self.go()

    def create_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        return webdriver.Chrome(options=options)

    def save_cookies(self, path):
        with open(path, "wb") as file:
            pickle.dump(self.driver.get_cookies(), file)

    def load_cookies(self, path):
        with open(path, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def login_and_save_cookies(self):
        self.driver.get("https://spark-interfax.ru/")
        time.sleep(2)

        login_input = self.driver.find_element(By.CSS_SELECTOR, "body > header > div > div.header__first-row > div.header__login.hidden-xs > div.login-form > div.js-login-form-container > form > div.login-form__group.js-login-credentials > input:nth-child(1)")
        login_input.send_keys(self.LOGIN)
        time.sleep(1)

        password_input = self.driver.find_element(By.CSS_SELECTOR, "body > header > div > div.header__first-row > div.header__login.hidden-xs > div.login-form > div.js-login-form-container > form > div.login-form__group.js-login-credentials > input:nth-child(2)")
        password_input.send_keys(self.PASSWORD)

        password_input.send_keys(Keys.ENTER)
        time.sleep(1)

        time.sleep(30)
        self.save_cookies(self.COOKIES_PATH)

    def is_logged_in(self):
        print("Проверяем актуальны ли куки")
        html = BeautifulSoup(self.driver.page_source, "html.parser")

        continue_btn = html.find("a", string="Продолжить работу")

        if continue_btn:
            print("continue_btn найдена")
            print("Авторизация через куки прошла успешно")

            try:
                button = self.driver.find_element(By.LINK_TEXT, "Продолжить работу")
                button.click()
                time.sleep(3)
                return True
            except Exception as e:
                print(f"Не удалось нажать кнопку 'Продолжить работу': {e}")
                return False
        else:
            return False

    def load_or_login(self):
        self.driver.get("https://spark-interfax.ru/")
        print('Инициализация драйвера')
        time.sleep(2)

        try:
            if not os.path.exists(self.COOKIES_PATH) or os.stat(self.COOKIES_PATH).st_size == 0:
                raise FileNotFoundError

            self.load_cookies(self.COOKIES_PATH)
            print("Подтягиваем куки")

            self.driver.get("https://spark-interfax.ru/")
            time.sleep(3)

            if not self.is_logged_in():
                print("Cookies устарели или не сработали. Повторная авторизация...")
                self.login_and_save_cookies()
            else:
                print("Авторизация по cookies прошла успешно, не было повторного входа")
        except (FileNotFoundError, EOFError):
            print("Файл cookies не найден или повреждён. Логинимся впервые...")
            self.login_and_save_cookies()

    def parse_by_inn(self, inn):
        print(f"Парсим инн={inn}")

        self.driver.get("https://spark-interfax.ru/system/#/dashboard")
        time.sleep(0.5)

        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input.form-control"))
        )
        search_input = self.driver.find_element(By.CSS_SELECTOR, "input.form-control")

        # Вставляем ИНН через JavaScript с правильной реакцией React
        self.driver.execute_script("""
            const input = arguments[0];
            const inn = arguments[1];
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
            nativeInputValueSetter.call(input, inn);
            input.dispatchEvent(new Event('input', { bubbles: true }));
        """, search_input, inn)

        time.sleep(0.5)

        # Нажимаем Enter (лучше, чем кликать по кнопке)
        search_input.send_keys(Keys.ENTER)

        link = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.sp-summary__title-link"))
        )
        href = link.get_attribute("href")
        print(href)
        return href

    def get_ido_from_link(self, company_url):
        self.driver.get(company_url)
        time.sleep(0.6)

        try:
            text_element = self.driver.find_element(By.CSS_SELECTOR,
                "#Indexes > table > tbody > tr > td.company-indicators-list__content > table > tbody > tr > td:nth-child(2) > div > div.card-index__icon > svg > text"
            )
            return text_element.text.strip()
        except:
            return None

    def parse_company_metrics(self, company_url):
        self.driver.get(company_url)
        time.sleep(0.5)

        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "td.company-stats-item__label"))
        )
        time.sleep(1)
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        needed_fields = [
            "Выручка от продажи",
            "Чистая прибыль",
            "Чистые активы",
            "Основные средства",
            "Денежный поток",
            "«Кредитный лимит»",
        ]
        metrics = {field: "-" for field in needed_fields}

        for label_td in soup.select("td.company-stats-item__label"):
            label = label_td.get_text(strip=True)

            if label in needed_fields:
                # В случае обычных метрик значение в следующем <td> или <td class="money-currency ...">
                value_td = label_td.find_parent("tr").find_next_sibling("tr")
                if value_td:
                    value = value_td.get_text(strip=True)
                    if value:
                        metrics[label] = value
        print(metrics)
        return metrics

    def parse_company_daughters(self, daughter_url):
        self.driver.get(daughter_url)
        time.sleep(0.5)

        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#card-partition-content"))
        )
        time.sleep(1)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        result = []

        # Ищем только активные компании — они находятся в tr без класса "not-acting"
        table = soup.select_one("#card-partition-content table.new-table")
        if not table:
            return []

        for row in table.select("tr"):
            if "not-acting" in row.get("class", []):
                continue  # пропускаем неактивные

            name_tag = row.select_one("td.col-25 a")
            if name_tag:
                href = name_tag.get("href")
                name = name_tag.get_text(strip=True)
                full_link = f"https://spark-interfax.ru{href}"

                result.append({
                    "Название": name,
                    "Ссылка": full_link
                })

        print(f"Найдено активных компаний: {len(result)}")
        return result

    def go(self): # можем изменять функцию в зависимости от того, чего хотим
        df = pd.read_excel("main_companies.xlsx")
        df["Ссылка на компанию"] = ""
        try:
            for idx, row in df.iterrows():
                inn = str(row["ИНН основной компаний"]).strip()
                try:
                    href_ = self.parse_by_inn(inn)

                    print(f"успешно нашли ссылку на компанию: idx={idx}, inn={inn}")
                    df.at[idx, "Ссылка на компанию"] = href_
                except Exception as e:
                    print(f"❌ Не удалось найти ссылку для ИНН {inn}, idx={idx}: {e}")
                    df.at[idx, "Ссылка на компанию"] = "Ошибка"
                    time.sleep(2)
            df.to_excel("data.xlsx")
        finally:
            print("на блоке файнали")
            time.sleep(2)
            df.to_excel("data.xlsx")
            self.driver.quit()


