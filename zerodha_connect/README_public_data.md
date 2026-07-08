# Public market data without login

This script fetches public market data from Yahoo Finance without requiring a Zerodha login.

## Run
```powershell
.
.venv\Scripts\python.exe .\public_market_data.py --symbol AAPL
```

## Notes
- This does not connect to your Zerodha account.
- It is suitable for public stock quotes and price history.
- It does not provide holdings, portfolio, or order data.
