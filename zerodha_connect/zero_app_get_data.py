## read the json file and get the tradingsymbol
from pathlib import Path
import json
from datetime import date, datetime
from typing import Dict, List, Union
from zerodha_client import ZerodhaClient

output_dir = Path(__file__).resolve().parent / "data"
output_path = output_dir / "portfolio.json"
watchlist_json_path = output_dir / "watchlist.json"

def _parse_authorised_date(value: Union[str, datetime, date, None]) -> Union[date, None]:
    """Return a date object from common Zerodha date formats."""
    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None

    normalized = text.replace("Z", "+00:00")

    try:
        return datetime.fromisoformat(normalized).date()
    except ValueError:
        pass

    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S%z",
    ):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue

    return None

## zero app connect
def connect_and_save_portfolio_json():
    

    client = ZerodhaClient()

    # Authenticate (opens browser if required)
    client.login()

    # Get all portfolio information
    portfolio = client.get_personal_portfolio()

    # Save the portfolio data as JSON in the local data folder
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_path = client.save_portfolio_json(portfolio, output_path=output_path)
    print(f"Saved portfolio JSON to: {saved_path}")



## get trading symbols from the json file along with last_price,average_price and difference between last_price and average_price in percentage
def get_tradingsymbols_from_portfolio_json() -> List[Dict[str, Union[str, float]]]:

    path = output_path
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return []

    items = []
    positions = data.get("positions")
    holdings = data.get("holdings")
    authorised_date = None

    if isinstance(holdings, list) and holdings:
        first_holding = holdings[0]
        if isinstance(first_holding, dict):
            authorised_date = first_holding.get("authorised_date")

    ## if authorised_date is not today then connect to zerodha and get the latest data and save it to the json file
    today = datetime.now().date()
    authorised_date_obj = _parse_authorised_date(authorised_date)
    if authorised_date_obj is None or authorised_date_obj != today:
        print("Authorised date is not today or missing. Fetching latest data from Zerodha...")
        connect_and_save_portfolio_json()
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        positions = data.get("positions")
        holdings = data.get("holdings")


    if isinstance(positions, list) and positions:
        items = positions
    elif isinstance(holdings, list):
        items = holdings
    elif isinstance(positions, list):
        items = positions

    if not isinstance(items, list):
        return []

    result = []
    for item in items:
        if not isinstance(item, dict):
            continue

        symbol = item.get("tradingsymbol") or item.get("trading_symbol")
        if not isinstance(symbol, str):
            continue

        last_price = item.get("last_price")
        average_price = item.get("average_price")

        if not isinstance(last_price, (int, float)) or not isinstance(average_price, (int, float)):
            continue

        if average_price == 0:
            percentage_diff = 0.0
        else:
            percentage_diff = round((last_price - average_price) / average_price, 2) * 100.0

        result.append({
            "tradingsymbol": symbol,
            "last_price": float(last_price),
            "average_price": float(average_price),
            "difference_percentage": percentage_diff,
        })

    return result


def get_watchlist_symbols_from_watchlist_json(watchlist_json_path: Path) -> List[str]:
    """Extract trading symbols from a watchlist JSON file."""
    if not watchlist_json_path.exists():
        print(f"Watchlist JSON file does not exist: {watchlist_json_path}")
        return []

    with watchlist_json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, dict):
        return []

    items = data.get("watchlist")
    if not isinstance(items, list):
        return []

    symbols: List[str] = []
    for item in items:
        if isinstance(item, str) and item.strip():
            symbols.append(item.strip())

    return symbols

def fetch_watchlist_symbols_from_zerodha():
    """Fetch watchlist symbols from Zerodha or the local watchlist JSON file."""
    client = ZerodhaClient()
    client.login()

    
  
    if watchlist_json_path.exists():
        watchlist = get_watchlist_symbols_from_watchlist_json(watchlist_json_path)
        print(f"Watchlist symbols retrieved from local JSON: {watchlist}")
    else:
        print("No watchlist symbols available from Zerodha or local JSON.")
        return {}

    try:
        quotes = client.get_quotes(watchlist)
    except Exception as exc:
        print(f"Unable to fetch quotes: {exc}")
        return {}

    prices = {}
    for symbol in watchlist:
        quote = quotes.get(symbol) if isinstance(quotes, dict) else None
        if quote:
            last_price = quote.get("last_price")
            prices[symbol] = last_price
            print(f"Symbol: {symbol}, Last Price: {last_price}")
        else:
            print(f"No quote data available for symbol: {symbol}")

    return prices