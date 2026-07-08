"""
token_manager.py

Handles reading and updating tokens stored in the .env file.
"""

import os
from dotenv import dotenv_values


class TokenManager:
    """
    Reads and updates ACCESS_TOKEN and REQUEST_TOKEN
    from the .env file.
    """

    def __init__(self, env_file=".env"):
        self.env_file = env_file

    def _read_env(self):
        """Read all variables from .env"""
        return dotenv_values(self.env_file)

    def _write_env(self, values):
        """Write all variables back to .env"""

        with open(self.env_file, "w") as file:

            for key, value in values.items():

                if value is None:
                    value = ""

                file.write(f"{key}={value}\n")

    # ---------------------------------------------------

    def get_access_token(self):

        data = self._read_env()

        return data.get("ACCESS_TOKEN")

    # ---------------------------------------------------

    def save_access_token(self, token):

        data = self._read_env()

        data["ACCESS_TOKEN"] = token

        self._write_env(data)

    # ---------------------------------------------------

    def get_request_token(self):

        data = self._read_env()

        return data.get("REQUEST_TOKEN")

    # ---------------------------------------------------

    def save_request_token(self, token):

        data = self._read_env()

        data["REQUEST_TOKEN"] = token

        self._write_env(data)

    # ---------------------------------------------------

    def clear_tokens(self):

        data = self._read_env()

        data["ACCESS_TOKEN"] = ""

        data["REQUEST_TOKEN"] = ""

        self._write_env(data)

    # ---------------------------------------------------

    def has_access_token(self):

        token = self.get_access_token()

        return bool(token)

    # ---------------------------------------------------

    def has_request_token(self):

        token = self.get_request_token()

        return bool(token)