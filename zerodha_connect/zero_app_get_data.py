## read the json file and get the tradingsymbol
from pathlib import Path
import json
from typing import Dict, List, Union


output_dir = Path(__file__).resolve().parent / "data"
output_path = output_dir / "portfolio.json"

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


