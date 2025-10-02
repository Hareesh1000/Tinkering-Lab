####################################################################

# Last modified: 02/10/2025
# DB: dev
# Description: Code retrofit
####################################################################
from bs4 import BeautifulSoup
from selenium import webdriver
import cx_Oracle
import requests

def get_data():
    print('Dividend stock extract process started')
    ## Connect to data base using beautiful soup
    driver = webdriver.Chrome()
    url = 'https://www.moneycontrol.com/stocks/marketinfo/dividends_declared/index.php'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find('table', class_='b_12 dvdtbl')
    ## Extracting the data from the soup  -------------------------------------------------------
    # company_data = []
    # for row in table.find_all('tr')[1:]:
    #     columns = row.find_all(['td', 'th'])

    #     # Check if the row has the expected number of columns
    #     if len(columns) == 6:
    #         try:
    #             # Extract data for each column in the row
    #             company_name = columns[0].text.strip()
    #             dividend_type = columns[1].text.strip()
    #             percentage = columns[2].text.strip()
    #             announcement_date = columns[3].text.strip()
    #             record_date = columns[4].text.strip()
    #             ex_dividend_date = columns[5].text.strip()

    #             # Store the data in a dictionary
    #             company_info = {
    #                 'company_name': company_name,
    #                 'dividend_type': dividend_type,
    #                 'percentage': percentage,
    #                 'announcement_date': announcement_date,
    #                 'record_date': record_date,
    #                 'ex_dividend_date': ex_dividend_date
    #             }

    #             # Append the dictionary to the list
    #             company_data.append(company_info)
    #         except Exception as e:
    #             print(f"Error processing row: {e}")
    #     else:
    #         print('skipped the header record')

        ## New exraction method ------------------------

    cards = soup.find_all('div', class_='lhsGrayCard_web_lhsGrayCard__RSkQw')

    company_data = []

    for card in cards:
        try:
            company_name = card.find('a', class_='lhsGrayCard_web_title__B2NJA').text.strip()
            dividend_value = card.find_all('span', class_='lhsGrayCard_web_values__DQOxi')[1].text.strip()
            announcement_date = card.find_all('span', class_='lhsGrayCard_web_values__DQOxi')[2].text.strip()
            ex_dividend_date = card.find_all('span', class_='lhsGrayCard_web_values__DQOxi')[3].text.strip()

            company_data.append({
                'company_name': company_name,
                'dividend_value': dividend_value,
                'announcement_date': announcement_date,
                'ex_dividend_date': ex_dividend_date
            })
        except Exception as e:
            print(f"Error processing card: {e}")

    driver.quit()


    ## End of the extraction   -------------------------------------------------------
    # Print the extracted data
    print('Data extracted')
    # Insert into the table from the extract into the table using SQL -------------------------------
    # Replace these with your actual Oracle database credentials
    db_user = "dev"
    db_password = "dev"
    db_dsn = "localhost:1521/xe"
    #con = cx_Oracle.connect('dev/dev@localhost:1521/xe')
    # Establish a connection to the Oracle database
    connection = cx_Oracle.connect(db_user, db_password, db_dsn)
    # Create a cursor
    cursor = connection.cursor()
    print('Inserting into the table')
    for company_info in company_data:
        # Data to be inserted
        data_to_insert = company_info
        # Prepare and execute the INSERT statement
     
        insert_sql = """
            INSERT INTO dividend_stocks (
                company_name,
                dividend_value,
                announcement_date,
                ex_dividend_date
            ) VALUES (
                :company_name,
                :dividend_value,
                TO_DATE(decode(:announcement_date,'-',null,:announcement_date), 'DD/MM/YYYY'),
                 TO_DATE(decode(:ex_dividend_date,'-',null,:ex_dividend_date), 'DD/MM/YYYY') 
            )
        """
        cursor.execute(insert_sql, data_to_insert)

    # Commit the transaction
    connection.commit()
    # Close the cursor and connection
    cursor.close()
    connection.close()
    print('closing the connection...')

def call_db_prc():
    import cx_Oracle

    try:
        # Establish a connection to the Oracle database
        connection = cx_Oracle.connect('dev/dev@localhost:1521/xe')

        # Create a cursor
        cursor = connection.cursor()

        # Define variables to capture the OUT parameters
        out_param1 = cursor.var(cx_Oracle.NUMBER)
        out_param2 = cursor.var(cx_Oracle.STRING)

        # Call the procedure with OUT parameters
        arg1_value = 123
        arg2_value = "example"

        cursor.callproc("PKG_MC_DATA_ANALYSIS.PRC_DIV_STOCKS", [out_param1, out_param2])

        # Retrieve the values of the OUT parameters
        result1 = out_param1.getvalue()
        result2 = out_param2.getvalue()

        print("OUT Parameter 1:", result1)
        print("OUT Parameter 2:", result2)

        # Close the cursor and connection
        cursor.close()
        connection.close()

    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print("Database Error:", error.message)


def send_automail():
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    # Email configuration
    sender_email = "ind.gameworld@gmail.com"
    receiver_email = "hareeshraj10@gmail.com"
    subject = "Subject of the Email"
    body = "Body of the email."

    # Create the MIME object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Attach the body to the email
    message.attach(MIMEText(body, "plain"))

    # Establish a connection to the SMTP server (in this case, Gmail's SMTP server)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Use TLS for security
        server.login(sender_email, "qiia dlkr hlrw tgkj")  # important app pwd
        server.sendmail(sender_email, receiver_email, message.as_string())

    print("Email sent successfully.")

def generate_html_table(data):
    # Generate the opening tag for the table
    table_html = "<table border='1'>\n"

    # Generate the header row
    table_html += "    <tr>\n"
    table_html += "        <th>Company</th>\n"
    table_html += "        <th>Status</th>\n"
    table_html += "        <th>Start Date</th>\n"
    table_html += "        <th>End Date</th>\n"
    table_html += "    </tr>\n"

    # Generate table rows based on the provided data
    for row in data:
        table_html += "    <tr>\n"
        for value in row:
            table_html += f"        <td>{value}</td>\n"
        table_html += "    </tr>\n"

    # Generate the closing tag for the table
    table_html += "</table>"

    return table_html

def send_automail():
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    print('Process to send auto mail has started')
    db_user = "dev"
    db_password = "dev"
    db_dsn = "localhost:1521/xe"
    connection = cx_Oracle.connect(db_user, db_password, db_dsn)
    # Create a cursor
    cursor = connection.cursor()
    ## Check for the data, If alreaady exisits then skip else do the insert
    query = "select COMPANY_NAME,NEW_ENTRY,To_char(ANNOUNCEMENT_DATE),to_char(record_date) from DIVIDEND_STOCKS_CONFIG where trunc(CREATED_DATE)>= trunc(sysdate)"
    cursor.execute(query)
    return_value = cursor.fetchall()


    # Email configuration
    sender_email = "ind.gameworld@gmail.com"
    receiver_email = "hareeshraj10@gmail.com"
    subject = "[SP] Automated Mail - Dividend stock List Latest"
    body = "New announcement about the Dividend Stocks"

    # Create the MIME object
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Attach the body to the email
    message.attach(MIMEText(body, "plain"))
    # Create an HTML table
    table_html = generate_html_table(return_value)

    # Attach the HTML content to the email
    body = MIMEText(table_html, "html")
    message.attach(body)

    # Establish a connection to the SMTP server (in this case, Gmail's SMTP server)
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()  # Use TLS for security
        server.login(sender_email, "qiia dlkr hlrw tgkj")  # important app pwd
        server.sendmail(sender_email, receiver_email, message.as_string())

    print("Email sent successfully.")

    # Close the cursor and connection
    cursor.close()
    connection.close()

def start():
    print('Process started')
    db_user = "dev"
    db_password = "dev"
    db_dsn = "localhost:1521/xe"
    connection = cx_Oracle.connect(db_user, db_password, db_dsn)
    # Create a cursor
    cursor = connection.cursor()
    ## Check for the data, If alreaady exisits then skip else do the insert
    query = "select 1 from (select max(CREATED_DATE) as CREATED_DATE from dividend_stocks) dv where trunc(dv.CREATED_DATE) = trunc(sysdate)"
    cursor.execute(query)
    return_value = cursor.fetchone()
    if return_value == None:  get_data();    call_db_prc();  send_automail()

    else:   print('Data already exists')
    # send_automail()
    # update_sql = ""
    # cursor.execute(update_sql)
    send_automail()
    # Commit the transaction
    connection.commit()
    # Close the cursor and connection
    cursor.close()
    connection.close()
    print('Closing the connection, End...')

start()

