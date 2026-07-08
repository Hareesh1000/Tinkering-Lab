import os
import html
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv

load_dotenv()

def generate_html_table(data):
    if not isinstance(data, list) or not data:
        return "<p>No data available to generate table.</p>"

    first_row = data[0]

    if isinstance(first_row, dict):
        headers = list(first_row.keys())
        rows = [
            [item.get(key, "") if isinstance(item, dict) else "" for key in headers]
            for item in data
        ]
    else:
        rows = [
            list(item) if isinstance(item, (list, tuple)) else [item]
            for item in data
        ]
        headers = [f"Column {i + 1}" for i in range(len(rows[0]))]

    table_html = """
    <table style="border-collapse:collapse;width:100%;font-family:Arial,sans-serif;color:#333;">
      <thead>
        <tr style="background-color:#1f77b4;color:#fff;text-align:left;">
    """

    for header in headers:
        table_html += (
            f'<th style="padding:10px;border:1px solid #c8c8c8;">'
            f"{html.escape(str(header))}</th>"
        )

    table_html += "</tr></thead><tbody>"

    for index, row in enumerate(rows):
        row_style = "background-color:#f8f9fb;" if index % 2 else "background-color:#fff;"
        table_html += f'<tr style="{row_style}">'

        for cell in row:
            table_html += (
                '<td style="padding:10px;border:1px solid #c8c8c8;vertical-align:top;">'
                f"{html.escape(str(cell))}</td>"
            )

        table_html += "</tr>"

    table_html += "</tbody></table>"
    return table_html


def get_required_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def send_automail(data):
    print("Process to send auto mail has started")

    sender_email = get_required_env("EMAIL_SENDER")
    receiver_email = get_required_env("EMAIL_RECEIVER")
    email_password = get_required_env("EMAIL_PASSWORD")

    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))

    subject = "[SP] Automated Mail - Zerodha Portfolio Data"
    plain_body = "New announcement about the Zerodha Portfolio Data"
    table_html = generate_html_table(data)

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(plain_body, "plain"))
    message.attach(MIMEText(table_html, "html"))

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(sender_email, email_password)
        server.send_message(message)

    print("Email sent successfully.")