from kiteconnect import KiteConnect

from config import Config

config = Config()

kite = KiteConnect(api_key=config.API_KEY)
kite.set_access_token(config.ACCESS_TOKEN)

holdings = kite.holdings()

for stock in holdings:
    print(stock["tradingsymbol"])
    print(stock["quantity"])
    print(stock["average_price"])
    print(stock["last_price"])
    print(stock["pnl"])
    print("----------------")

    from kiteconnect import KiteConnect


# Retrieve full quotes
full_quote = kite.quote(["NSE:INFY", "NSE:RELIANCE"])
print(full_quote["NSE:INFY"]["last_price"])
print(full_quote["NSE:INFY"]["depth"]["buy"])  # Top 5 bids