import argparse
import json
import requests


def get_quote(symbol: str):
    symbol = symbol.strip().upper()
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1mo"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()

    payload = response.json()
    result = payload.get("chart", {}).get("result", [{}])[0]
    meta = result.get("meta", {})

    return {
        "symbol": meta.get("symbol", symbol),
        "currency": meta.get("currency"),
        "exchangeName": meta.get("exchangeName"),
        "marketState": meta.get("marketState"),
        "regularMarketPrice": meta.get("regularMarketPrice"),
        "previousClose": meta.get("previousClose"),
        "chartPreviousClose": meta.get("chartPreviousClose"),
        "timezone": meta.get("timezone"),
    }


def main():
    parser = argparse.ArgumentParser(description="Fetch public market data without login")
    parser.add_argument("--symbol", default="AAPL", help="Stock symbol to query")
    args = parser.parse_args()

    try:
        quote = get_quote(args.symbol)
        print(json.dumps(quote, indent=2))
    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
