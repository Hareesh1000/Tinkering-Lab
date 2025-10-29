"""
====================================================================================
Script Name : mc_scrap.py
Purpose     : To automate the extraction of stock data from MoneyControl website,
              parse it using BeautifulSoup, and store the details into Oracle DB.
------------------------------------------------------------------------------------
Working Overview:
1. The script connects to an Oracle database and retrieves active stock names.
2. For each stock:
   - It uses Selenium to open MoneyControl, search the stock, and fetch its details.
   - The page source is parsed using BeautifulSoup to extract SWOT and overview data.
   - Extracted data is stored in the TEMP_RAW_DATA table in Oracle.
   - The last_update column of STOCK_LIST table is updated with the current date.
3. After processing, a stored procedure (PKG_MC_DATA_EXTRACT.PRC_DATA_EXT_MAIN)
   is invoked to finalize data processing.
------------------------------------------------------------------------------------
Functions:
- get_started(query): Fetches stock list from DB, iterates through stocks, and calls get_stock_attrs.
- get_stock_attrs(series_num, stock): Extracts data from MoneyControl for a given stock.
- delete_table(): Deletes data from TEMP_RAW_DATA table.
- call_db_prc(): Calls the Oracle stored procedure for data finalization.
- check_the_table(query): Executes a query and returns fetched values.
- main(): Entry point for the script execution.
====================================================================================
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import cx_Oracle
import traceback
import requests

# Initialize WebDriver (Chrome)
driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)

def get_started(query):
    """Fetch stock names from DB and process each stock."""
    try:
        # Open MoneyControl homepage
        url = 'https://www.moneycontrol.com'
        driver.get(url)
        print('Finding')

        # Connect to Oracle DB
        try:
            con = cx_Oracle.connect('dev/dev@localhost:1521/xe')
        except cx_Oracle.DatabaseError as er:
            print('Error connecting to Oracle database:', er)
            return

        try:
            cur = con.cursor()

            # Reset sync flag before new run
            cur.execute("update stock_list set SYNC_FLAG = NULL")
            cur.execute(query)
            con.commit()

            stock_rows = cur.fetchall()
            print(stock_rows)

            series_num = 1
            for stock_list in stock_rows:
                for stock in stock_list:
                    print(f"Processing stock: {stock}")
                    try:
                        get_stock_attrs(series_num, stock)
                    except Exception as e:
                        print(f"Error while searching for stock {stock}: {e}")
                        cur.execute("update stock_list set SYNC_FLAG = 'N' where NAME = :v_stock", v_stock=stock)
                        con.commit()
                        continue
                series_num += 1

        except cx_Oracle.DatabaseError as er:
            print('Database error:', er)
        except Exception as er:
            print('General error:', str(er))
        finally:
            cur.close()
            con.close()

    except Exception as e:
        print("Exception occurred in get_started:", str(e))
        traceback.print_exc()
        driver.quit()


def get_stock_attrs(series_num, stock):
    """Extracts data from MoneyControl for a specific stock and inserts into DB."""
    data_from_stock = []

    driver.implicitly_wait(15)
    actions = ActionChains(driver)

    # Scroll up to ensure search box is visible
    print('Scrolling up...')
    actions.send_keys(Keys.PAGE_UP).perform()

    # Locate search box and enter stock name
    search_box = driver.find_element('id', 'search_str')
    search_box.send_keys(stock)
    print('Search submitted')

    driver.implicitly_wait(6)
    search_box.send_keys(Keys.RETURN)

    # Stop page load to prevent dynamic reloads
    driver.implicitly_wait(6)
    driver.execute_script("window.stop();")

    # Get current page URL
    current_url = driver.current_url
    print(f'Started data extraction for {stock}')

    # Parse page using BeautifulSoup
    response = requests.get(current_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract stock title and SWOT details
    title = soup.find(attrs={"class": "name_left topsel_tab"})
    swot = soup.find(attrs={"class": "swot_feature"})

    if not title or not swot:
        print(f"Incomplete data for {stock}")
        return

    strength = swot.find(attrs={"class": "kbyistrengths"})
    weakness = swot.find(attrs={"class": "swli2 swotliClass"})
    opportunities = swot.find(attrs={"class": "kbyiopportunities"})
    threat = swot.find(attrs={"class": "kbyithreats"})

    # Collect data
    data_from_stock.extend([
        title.text.strip(),
        strength.text.strip() if strength else '',
        weakness.text.strip() if weakness else '',
        opportunities.text.strip() if opportunities else '',
        threat.text.strip() if threat else ''
    ])

    # Extract overview table data
    data = soup.find_all(attrs={"class": "oview_table"})
    for values in data:
        data_from_stock.append(values.text.strip())

    # Clean and prepare data for DB insert
    modified_data = [item.replace('\n', '').strip() for item in data_from_stock if item.strip()]
    db_data = [[series_num, stock, item] for item in modified_data]

    # Insert into Oracle DB
    try:
        con = cx_Oracle.connect('dev/dev@localhost:1521/xe')
        cur = con.cursor()
        print('Inserting data into DB...')

        cur.executemany(
            'insert into temp_raw_data(series_no, nse_name, raw_data) values(:1, :2, :3)', db_data
        )

        # Update last_update timestamp
        cur.execute("UPDATE stock_list SET last_update = sysdate WHERE name = :stock", stock=stock)

        con.commit()
        print(f'Data for {stock} inserted successfully.')

    except cx_Oracle.DatabaseError as er:
        print('Oracle database error:', er)
    except Exception as er:
        print('Error inserting data:', er)
    finally:
        if cur:
            cur.close()
        if con:
            con.close()


def delete_table():
    """Deletes data from TEMP_RAW_DATA table."""
    try:
        connection = cx_Oracle.connect('dev/dev@localhost:1521/xe')
        cursor = connection.cursor()
        cursor.execute("delete from TEMP_RAW_DATA")
        connection.commit()
        print('TEMP_RAW_DATA table cleared.')
    except cx_Oracle.DatabaseError as er:
        print('Error clearing TEMP_RAW_DATA:', er)
    finally:
        cursor.close()
        connection.close()


def call_db_prc():
    """Calls the stored procedure PKG_MC_DATA_EXTRACT.PRC_DATA_EXT_MAIN."""
    try:
        connection = cx_Oracle.connect('dev/dev@localhost:1521/xe')
        cursor = connection.cursor()

        # Define OUT parameters
        out_param1 = cursor.var(cx_Oracle.NUMBER)
        out_param2 = cursor.var(cx_Oracle.STRING)

        cursor.callproc("PKG_MC_DATA_EXTRACT.PRC_DATA_EXT_MAIN", [out_param1, out_param2])

        print("OUT Parameter 1:", out_param1.getvalue())
        print("OUT Parameter 2:", out_param2.getvalue())

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print("Database Error:", error.message)
    finally:
        cursor.close()
        connection.close()


def check_the_table(query):
    """Executes a query and returns fetched data."""
    connection = cx_Oracle.connect('dev/dev@localhost:1521/xe')
    cursor = connection.cursor()
    cursor.execute(query)
    value = cursor.fetchall()
    cursor.close()
    connection.close()
    return value


def main():
    """Main execution workflow."""
    print('Process started...')

    # Stop any current page load using ESC key
    ActionChains(driver).send_keys('\ue00c').perform()

    # First DB query to get stocks for today's run
    query = """
        select name from stock_list
        where active = 'Y'
        and created_date is not null
        and trunc(last_update) != trunc(sysdate)
        order by last_update
    """
    get_started(query)

    # Second run for failed syncs
    query = "select count(1) from stock_list where SYNC_FLAG = 'N'"
    count = check_the_table(query)
    print('Count is', count)

    if count and count[0][0] > 0:
        query = "select name from stock_list where active = 'Y' and SYNC_FLAG = 'N'"
        get_started(query)

    print('Calling Procedure...')
    call_db_prc()

    print('Process ended successfully.')


if __name__ == '__main__':
    main()