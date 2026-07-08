import json
from pathlib import Path

from zerodha_client import ZerodhaClient


def main():
    client = ZerodhaClient()

    # Authenticate (opens browser if required)
    client.login()

    # Get all portfolio information
    portfolio = client.get_personal_portfolio()

    # Print as formatted JSON
    print(json.dumps(portfolio, indent=4))

    # Save the portfolio data as JSON in the local data folder
    output_dir = Path(__file__).resolve().parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "portfolio.json"
    saved_path = client.save_portfolio_json(portfolio, output_path=output_path)
    print(f"Saved portfolio JSON to: {saved_path}")


if __name__ == "__main__":
    main()
