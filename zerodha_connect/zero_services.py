from zero_app_notification import send_automail
import zero_app_get_data

## get the data from the json file and send it to the email
def send_email_with_portfolio_data():
    #zero_app_get_data.connect_and_save_portfolio_json()
    data = zero_app_get_data.get_tradingsymbols_from_portfolio_json()
    print("Portfolio data retrieved from JSON file:")
    print(data)
    ## if any one of the stocks has difference_percentage greater than 0 then send the email
    for stock in data:
        if stock["difference_percentage"] > 0:
            print("Sending email with portfolio data...")
            send_automail(data)
        else:
            print("No stocks with positive difference percentage. Email not sent.")

if __name__ == "__main__":
    send_email_with_portfolio_data()
    
    prices = zero_app_get_data.fetch_watchlist_symbols_from_zerodha()
    print(prices)
    print("End of script.")



   
