"""
auth_server.py

Starts a local HTTP server to receive the Zerodha
request_token automatically.
"""

from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import threading

from token_manager import TokenManager


class ZerodhaCallbackHandler(BaseHTTPRequestHandler):

    token_manager = TokenManager()

    request_token = None

    def do_GET(self):

        parsed = urlparse(self.path)

        params = parse_qs(parsed.query)

        if "request_token" in params:

            token = params["request_token"][0]

            self.token_manager.save_request_token(token)

            ZerodhaCallbackHandler.request_token = token

            self.send_response(200)

            self.send_header("Content-Type", "text/html")

            self.end_headers()

            self.wfile.write(b"""
            <html>
                <head>
                    <title>Zerodha Login</title>
                </head>
                <body>
                    <h2>Login Successful</h2>
                    <p>You may now close this window.</p>
                </body>
            </html>
            """)

        else:

            self.send_response(400)

            self.end_headers()

            self.wfile.write(b"Request token not found.")

    def log_message(self, format, *args):
        # Suppress default HTTP logging
        return


class AuthServer:

    def __init__(self, host="127.0.0.1", port=8000):

        self.host = host

        self.port = port

        self.server = HTTPServer(
            (self.host, self.port),
            ZerodhaCallbackHandler
        )

    def start(self):

        thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True
        )

        thread.start()

    def stop(self):

        self.server.shutdown()

        self.server.server_close()

    def get_request_token(self):

        return ZerodhaCallbackHandler.request_token