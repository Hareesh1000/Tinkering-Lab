
# ====================================================================================
# Script Name : mc_scrap.py
# Purpose     : To automate the extraction of stock data from MoneyControl website,
#               parse it using BeautifulSoup, and store the details into Oracle DB.
# ------------------------------------------------------------------------------------
# Enhanced Version Includes:
# 1. Logging system that creates a log file with datetime stamp under:
#    C:\Users\91812\Documents\logs\mc_scrap_logs
# 2. Graceful handling of browser closure or crashes.
# 3. Procedure (PKG_MC_DATA_EXTRACT.PRC_DATA_EXT_MAIN) is called even if scraping fails.
# 4. Automatic ENTER key handling for robustness.
# 5. Proper cleanup of DB connections and browser sessions.
# ====================================================================================


import os
import sys
import cx_Oracle
import traceback
import requests
import logging
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup

# ----------------------------------------------------------------------------------
# Logging Configuration
# ----------------------------------------------------------------------------------
LOG_DIR = r"C:\Users\91812\Documents\logs\mc_scrap_logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(LOG_DIR, f"mc_scrap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

def log(msg):
    print(msg)
    logging.info(msg)

# ----------------------------------------------------------------------------------
# Initialize WebDriver
# ----------------------------------------------------------------------------------
try:
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 10)
except WebDriverException as e:
    log(f"Failed to initialize browser: {e}")
    sys.exit(1)

# ----------------------------------------------------------------------------------
# Main Functions
# ----------------------------------------------------------------------------------
def get_started(query):
    """Fetch stock names from DB and process each stock."""
    try:
        driver.get('https://www.moneycontrol.com')
        log('Opened MoneyControl website.')

        try:
            con = cx_Oracle.connect('dev/dev@localhost:1521/xe')
        except cx_Oracle.DatabaseError as er:
            log(f"Database connection error: {er}")
            return

        try:
            cur = con.cursor()
            cur.execute("update stock_list set SYNC_FLAG = NULL")
            cur.execute(query)
            con.commit()

            stock_rows = cur.fetchall()
            log(f"Fetched {len(stock_rows)} stock(s) from database.")

            series_num = 1
            for stock_list in stock_rows:
                for stock in stock_list:
                    try:
                        log(f"Processing stock: {stock}")
                        get_stock_attrs(series_num, stock)
                    except WebDriverException:
                        log("Browser closed unexpectedly.")
                        raise
                    except Exception as e:
                        log(f"Error processing {stock}: {e}")
                        cur.execute("update stock_list set SYNC_FLAG = 'N' where NAME = :v_stock", v_stock=stock)
                        con.commit()
                        continue
                series_num += 1

        finally:
            cur.close()
            con.close()

    except WebDriverException:
        log("WebDriver session ended unexpectedly.")
        raise
    except Exception as e:
        log(f"Exception in get_started: {e}")
        traceback.print_exc()


def get_stock_attrs(series_num, stock):
    """Extract data from MoneyControl for a specific stock."""
    driver.implicitly_wait(15)
    actions = ActionChains(driver)

    try:
        actions.send_keys(Keys.PAGE_UP).perform()
        search_box = driver.find_element('id', 'search_str')
        search_box.clear()
        search_box.send_keys(stock)
        search_box.send_keys(Keys.ENTER)
        log(f"Searching for {stock}.")

        driver.implicitly_wait(6)
        driver.execute_script("window.stop();")

        current_url = driver.current_url
        log(f"Extracting data from: {current_url}")

        response = requests.get(current_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find(attrs={"class": "name_left topsel_tab"})
        swot = soup.find(attrs={"class": "swot_feature"})

        if not title or not swot:
            log(f"Incomplete data for {stock}.")
            return

        strength = swot.find(attrs={"class": "kbyistrengths"})
        weakness = swot.find(attrs={"class": "swli2 swotliClass"})
        opportunities = swot.find(attrs={"class": "kbyiopportunities"})
        threat = swot.find(attrs={"class": "kbyithreats"})

        data_from_stock = [
            title.text.strip(),
            strength.text.strip() if strength else '',
            weakness.text.strip() if weakness else '',
            opportunities.text.strip() if opportunities else '',
            threat.text.strip() if threat else ''
        ]

        for table in soup.find_all(attrs={"class": "oview_table"}):
            data_from_stock.append(table.text.strip())

        cleaned_data = [d.replace('\n', '').strip() for d in data_from_stock if d.strip()]
        db_data = [[series_num, stock, d] for d in cleaned_data]

        con = cx_Oracle.connect('dev/dev@localhost:1521/xe')
        cur = con.cursor()
        cur.executemany('insert into temp_raw_data(series_no, nse_name, raw_data) values(:1,:2,:3)', db_data)
        cur.execute("UPDATE stock_list SET last_update = sysdate WHERE name = :stock", stock=stock)
        con.commit()
        log(f"Inserted data for {stock} successfully.")

    except WebDriverException as e:
        log(f"Browser closed or crashed while processing {stock}: {e}")
        raise
    except Exception as e:
        log(f"Error in get_stock_attrs for {stock}: {e}")
    finally:
        try:
            cur.close()
            con.close()
        except:
            pass


def call_db_prc():
    """Call stored procedure even if scraping fails."""
    try:
        con = cx_Oracle.connect('dev/dev@localhost:1521/xe')
        cur = con.cursor()
        out1 = cur.var(cx_Oracle.NUMBER)
        out2 = cur.var(cx_Oracle.STRING)
        cur.callproc("PKG_MC_DATA_EXTRACT.PRC_DATA_EXT_MAIN", [out1, out2])
        log(f"Procedure executed: OUT1={out1.getvalue()}, OUT2={out2.getvalue()}")
    except cx_Oracle.DatabaseError as e:
        log(f"Database Error in procedure call: {e}")
    finally:
        try:
            cur.close()
            con.close()
        except:
            pass


def check_the_table(query):
    try:
        con = cx_Oracle.connect('dev/dev@localhost:1521/xe')
        cur = con.cursor()
        cur.execute(query)
        result = cur.fetchall()
        return result
    finally:
        cur.close()
        con.close()


def main():
    log('Process started.')
    try:
        ActionChains(driver).send_keys('\ue00c').perform()
        query = ("select name from stock_list where active='Y' and created_date is not null "
                 "and trunc(last_update)!=trunc(sysdate) order by last_update")
        get_started(query)

        query = "select count(1) from stock_list where SYNC_FLAG='N'"
        count = check_the_table(query)
        if count and count[0][0] > 0:
            log(f"Retrying {count[0][0]} unsynced stocks.")
            query = "select name from stock_list where active='Y' and SYNC_FLAG='N'"
            get_started(query)

    except WebDriverException:
        log("Browser closed or crashed. Proceeding to call procedure.")
    except Exception as e:
        log(f"Error in main: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass
        log('Calling procedure before exit...')
        call_db_prc()
        log('Process ended.')

if __name__ == '__main__':
    main()
