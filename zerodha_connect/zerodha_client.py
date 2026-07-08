"""
zerodha_client.py

Main Zerodha Client
"""

import csv
import json
import time
import webbrowser
from pathlib import Path

from kiteconnect import KiteConnect

from config import Config
from auth_server import AuthServer
from token_manager import TokenManager


class ZerodhaClient:

    def __init__(self):

        self.config = Config()

        self.token_manager = TokenManager()

        self.kite = KiteConnect(
            api_key=self.config.API_KEY
        )

        self.server = None

    # -----------------------------------------------------

    def login(self):
        """
        Authenticate the user and create a Kite session.
        """

        access_token = self.token_manager.get_access_token()

        if access_token:

            self.kite.set_access_token(access_token)

            try:
                self.kite.profile()
                print("Using existing access token.")
                return

            except Exception:
                print("Existing access token has expired.")

        self._authenticate()

    # -----------------------------------------------------

    def _authenticate(self):

        self.server = AuthServer()

        self.server.start()

        print("Authentication server started.")

        login_url = self.kite.login_url()

        print("Opening browser...")

        webbrowser.open(login_url)

        print("Waiting for login...")

        request_token = None

        while request_token is None:

            request_token = self.server.get_request_token()

            time.sleep(1)

        print("Request token received.")

        self.server.stop()

        self.token_manager.save_request_token(
            request_token
        )

        session = self.kite.generate_session(
            request_token=request_token,
            api_secret=self.config.API_SECRET
        )

        access_token = session["access_token"]

        self.token_manager.save_access_token(
            access_token
        )

        self.kite.set_access_token(access_token)

        print("Authentication successful.")

    # -----------------------------------------------------

    def get_profile(self):

        return self.kite.profile()

    # -----------------------------------------------------

    def get_holdings(self):

        return self.kite.holdings()

    # -----------------------------------------------------

    def get_positions(self):

        return self.kite.positions()

    # -----------------------------------------------------

    def get_orders(self):

        return self.kite.orders()

    # -----------------------------------------------------

    def get_trades(self):

        return self.kite.trades()

    # -----------------------------------------------------

    def get_funds(self):

        return self.kite.margins()

    # -----------------------------------------------------

    def get_ltp(self, symbol):

        return self.kite.ltp(symbol)

    # -----------------------------------------------------

    def get_quote(self, symbol):

        return self.kite.quote(symbol)

    # -----------------------------------------------------

    def get_quotes(self, symbols):

        return self.kite.quote(symbols)

    # -----------------------------------------------------

    def logout(self):

        self.token_manager.clear_tokens()

        print("Tokens removed.")

    # -----------------------------------------------------

    def save_portfolio_csv(self, portfolio, output_path=None):
        """
        Save portfolio payload to a CSV file in a local data folder.
        """
        if output_path is None:
            output_path = Path(__file__).resolve().parent / "data" / "portfolio.csv"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", newline="", encoding="utf-8") as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(["section", "key", "value"])

            for section, data in portfolio.items():
                if isinstance(data, dict):
                    for key, value in data.items():
                        writer.writerow([section, key, json.dumps(value, default=str)])
                elif isinstance(data, list):
                    for index, item in enumerate(data):
                        if isinstance(item, dict):
                            writer.writerow([section, index, json.dumps(item, default=str)])
                        else:
                            writer.writerow([section, index, item])
                else:
                    writer.writerow([section, "value", data])

        return output_path

    # -----------------------------------------------------

    def save_portfolio_json(self, portfolio, output_path=None):
        """
        Save portfolio payload to a JSON file in a local data folder.
        """
        if output_path is None:
            output_path = Path(__file__).resolve().parent / "data" / "portfolio.json"
        else:
            output_path = Path(output_path)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(portfolio, indent=2, default=str), encoding="utf-8")
        return output_path

    # -----------------------------------------------------

    def get_personal_portfolio(self):
        """
        Returns everything related to the account
        in a single dictionary.
        """

        return {

            "profile": self.get_profile(),

            "holdings": self.get_holdings(),

            "positions": self.get_positions(),

            "orders": self.get_orders(),

            "trades": self.get_trades(),

            "funds": self.get_funds()

        }