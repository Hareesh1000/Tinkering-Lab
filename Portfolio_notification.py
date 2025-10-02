####################################################################

# Last modified: 02/10/2025
# DB: dev
# Description:
####################################################################


def send_mail():
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

def read_thepassword():
    file_path = r"C:\Users\91812\Documents\all_codes\config.txt.txt"

    with open(file_path, "r") as f:
        for line in f:
            if line.startswith("PWD"):
                pwd = line.split("=", 1)[1].strip()

    print("Password is:", pwd)   # use pwd in your code

def get_sender_recevier_email():
    pass

def connect_with_database():
    pass

def compute_the_portfolio():
    pass

def get_the_data():
    pass

def main():
    print('Portfolio Notification')
    read_thepassword()

main()
    