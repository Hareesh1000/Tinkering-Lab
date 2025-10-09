import cx_Oracle
import requests
import time
import keyboard

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class DataImport:
    def __init__(self):
        self.data_processed = 1
        self.driver = webdriver.Chrome()
        self.stop_requested = False   # Flag for ESC stop
    # ------------------ Database Connection ------------------ #
    def connect_to_database(self):
        try:
            return cx_Oracle.connect('dev/dev@localhost:1521/xe')
        except cx_Oracle.Error as e:
            print(f"Oracle database error: {e}")
            return None

    # ------------------ Web Scraping Process ------------------ #
    def scrap_the_web(self):
        try:
            url = "https://www.tickertape.in/stocks"
            self.driver.get(url)

            stock_list = self.get_the_list()

            for stock in stock_list:
                if keyboard.is_pressed("esc"):
                    print("ESC pressed! Stopping the scraping process...")
                    self.stop_requested = True
                    break

                self.search_the_stock(stock)
                self.wait_for_seconds(2)

                print('Press Enter to process data OR Esc to stop process.')
                manual_enter = self.check_enter_key()
                
                if self.stop_requested:   # If ESC pressed inside check_enter_key
                    break

                if manual_enter == 1:
                    self.extract_data(stock)
                else:
                    self.driver.implicitly_wait(15)
                    print("Data not processed")

        except Exception as e:
            print(f"An error occurred: {e}")

        finally:
            if self.driver:
                self.driver.quit()
                print('Calling the procedure from the Finally block')
                self.call_the_procedure()

    # ------------------ Stock Search ------------------ #
    def search_the_stock(self, stock_name):
        try:
            search_box = WebDriverWait(self.driver, 1).until(
                EC.element_to_be_clickable((By.ID, "search-stock-input"))
            )
            search_box.clear()
            print(f'Entering stock name: {stock_name}')
            search_box.send_keys(stock_name)
            search_box.send_keys(Keys.RETURN)

        except Exception as e:
            print(f"An error occurred during search for {stock_name}: {e}")

    # ------------------ Fetch Stock List ------------------ #
    def get_the_list(self):
        connection = self.connect_to_database()
        if not connection:
            print("Unable to connect to the database.")
            return []

        try:
            cursor = connection.cursor()
            cursor.execute("SELECT stock_name FROM nse_stock_list")
            return [row[0] for row in cursor.fetchall()]
        except cx_Oracle.Error as e:
            print(f"Oracle database error: {e}")
            return []

    # ------------------ Extract Data ------------------ #
    def extract_data(self, stock):
        try:
            current_url = self.driver.current_url
            print(f"Extracting from URL: {current_url}")

            response = requests.get(current_url)
            soup = BeautifulSoup(response.content, 'html.parser')

            elements = soup.find_all(class_='cards-container')
            for element in elements:
                data = [child.text.strip() for child in element.find_all(['p', 'span'])]

                organized_data = {}
                current_category = None
                for item in data:
                    if item.isalpha() or ' ' in item:
                        current_category = item
                        organized_data[current_category] = []
                    else:
                        organized_data[current_category].append(item)

                print(organized_data)

                collected_item = [
                    f"{category}: {', '.join(statements)}"
                    for category, statements in organized_data.items()
                ]

                numbered_item = self.add_numbering(collected_item)

                db_data = [[1, stock, line] for line in numbered_item]

                print('Data collected, storing in DB...')
                self.store_to_database(db_data)

        except Exception as e:
            print(f"An error occurred in extract_data: {e}")

    # ------------------ Keyboard Check ------------------ #
    # ------------------ Keyboard Check ------------------ #
    def check_enter_key(self):
        try:
            start_time = time.time()
            while True:
                if keyboard.is_pressed("enter"):
                    return 1
                elif keyboard.is_pressed("esc"):
                    print("ESC pressed! Stopping process...")
                    self.stop_requested = True
                    return 0
                elif time.time() - start_time >= 5:  # 5-second timeout
                    print("Auto Enter triggered after 5 seconds")
                    keyboard.press_and_release("enter")
                    return 1
        except Exception as e:
            print(f"Error in check_enter_key: {e}")
            return 0


    # ------------------ Store Data ------------------ #
    def store_to_database(self, stock_data):
        connection = self.connect_to_database()
        if not connection:
            return

        try:
            cursor = connection.cursor()
            cursor.executemany(
                '''INSERT INTO sp_raw_data 
                   (series_no, nse_name, raw_data, CREATED_DATE) 
                   VALUES (:count_value, :name, :data, sysdate)''',
                stock_data
            )
            connection.commit()
            print('Data Inserted')
            self.data_processed = 1

        except cx_Oracle.Error as e:
            print(f"Oracle database error: {e}")

    # ------------------ Numbering Function ------------------ #
    def add_numbering(self, input_lines):
        lines = input_lines.copy()
        current_keyword = None

        for i in range(len(lines)):
            if lines[i].startswith(('Performance', 'Valuation', 'Growth',
                                    'Profitability', 'Entry point', 'Red flags')):
                current_keyword = lines[i]
            elif current_keyword is not None:
                lines[i] = f"{current_keyword} {i - lines.index(current_keyword) + 1}): {lines[i]}"

        return [
            line if line.startswith(('Performance', 'Valuation', 'Growth',
                                     'Profitability', 'Entry point', 'Red flags'))
            else line.replace('\n', ' ')
            for line in lines
        ]

    # ------------------ Utility Functions ------------------ #
    def wait_for_seconds(self, seconds):
        print(f"Waiting for {seconds} seconds...")
        time.sleep(seconds)
        print("Done waiting!")

    def call_the_procedure(self):
        connection = self.connect_to_database()
        if not connection:
            return

        try:
            cursor = connection.cursor()
            out_param1 = cursor.var(cx_Oracle.NUMBER)
            out_param2 = cursor.var(cx_Oracle.STRING)
            cursor.callproc("PKG_STOCK_PULSE_ANALYSE.PRC_SP_TICKER_DATA_ANALYSE",
                            [out_param1, out_param2])
            print("Procedure executed successfully.")

        except cx_Oracle.Error as e:
            print(f"Oracle database error: {e}")


# ------------------ Main Execution ------------------ #
if __name__ == "__main__":
    ticker = DataImport()
    ticker.scrap_the_web()
    print('Final call to procedure...')
    ticker.call_the_procedure()
