from zero_app_notification import send_automail
import zero_app_get_data

## get the data from the json file and send it to the email
def send_email_with_portfolio_data():
    data = zero_app_get_data.get_tradingsymbols_from_portfolio_json()
    send_automail(data)


if __name__ == "__main__":
    send_email_with_portfolio_data()


   
