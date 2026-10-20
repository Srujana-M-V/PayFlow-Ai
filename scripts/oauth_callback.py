import base64
import hashlib
import os
import secrets
import threading
import urllib.parse
import webbrowser
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse
from urllib.request import Request, urlopen

from dotenv import load_dotenv

# Project configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

CLIENT_ID = "Smc5bXs0gwPJvgPZDgFHfXYSX1rq7nD7UxWtUTXU"
CLIENT_SECRET = os.getenv("OAUTH_CLIENT_SECRET")

REDIRECT_URI = "http://127.0.0.1:8080/callback"
AUTHORIZATION_URL = "http://127.0.0.1:8001/o/authorize/"
TOKEN_URL = "http://127.0.0.1:8001/o/token/"

# PKCE security values
STATE = secrets.token_urlsafe(32)
CODE_VERIFIER = secrets.token_urlsafe(64)

CODE_CHALLENGE = base64.urlsafe_b64encode(
    hashlib.sha256(CODE_VERIFIER.encode()).digest()
).rstrip(b"=").decode()


class OAuthCallbackHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        parsed_url = urlparse(self.path)
        params = parse_qs(parsed_url.query)

        if parsed_url.path != "/callback":
            self.send_error(404)
            return

        # Validate OAuth state
        if params.get("state", [""])[0] != STATE:
            self.send_error(400, "Invalid OAuth state")
            return

        # Handle OAuth errors
        if params.get("error"):
            error = params["error"][0]
            print("OAuth authorization failed:", error)
            self.send_error(400, "OAuth authorization failed")
            return

        # Retrieve authorization code
        code = params.get("code", [""])[0]

        if not code:
            self.send_error(400, "Authorization code missing")
            return

        # Require the confidential client's secret
        if not CLIENT_SECRET:
            print(
                "Token exchange failed: "
                "OAUTH_CLIENT_SECRET is missing from .env"
            )
            self.send_error(
                500,
                "OAuth client secret is not configured"
            )
            return

        try:
            # Prepare token exchange request
            form_data = urllib.parse.urlencode({
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "code_verifier": CODE_VERIFIER,
            }).encode()

            # Authenticate the confidential OAuth client
            credentials = base64.b64encode(
                f"{CLIENT_ID}:{CLIENT_SECRET}".encode()
            ).decode()

            request = Request(
                TOKEN_URL,
                data=form_data,
                headers={
                    "Content-Type": (
                        "application/x-www-form-urlencoded"
                    ),
                    "Authorization": f"Basic {credentials}",
                },
                method="POST",
            )

            with urlopen(request, timeout=10) as response:
                token_data = response.read().decode()

            # Never print access or refresh tokens
            print("Token exchange succeeded.")
            print("Token response received; values are hidden.")

            message = "OAuth token exchange succeeded."

        except HTTPError as exc:
            print("Token exchange failed. HTTP status:", exc.code)
            print(
                exc.read().decode(errors="replace")
            )
            message = (
                f"Token exchange failed (HTTP {exc.code}). "
                "Check the terminal."
            )

        except Exception as exc:
            print("Token exchange error:", type(exc).__name__)
            message = "Token exchange failed. Check the terminal."

        # Return the result to the browser
        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>PayFlow AI OAuth</title>
        </head>
        <body>
            <h2>{message}</h2>
            <p>You may close this browser tab.</p>
        </body>
        </html>
        """

        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":

    if not CLIENT_SECRET:
        raise SystemExit(
            "OAUTH_CLIENT_SECRET is missing from the project-root .env file."
        )

    # Build OAuth authorization URL
    query = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "read",
        "state": STATE,
        "code_challenge": CODE_CHALLENGE,
        "code_challenge_method": "S256",
    })

    authorization_url = f"{AUTHORIZATION_URL}?{query}"

    # Start callback server
    server = HTTPServer(
        ("127.0.0.1", 8080),
        OAuthCallbackHandler
    )

    print("OAuth callback server listening on port 8080.")

    threading.Timer(
        1,
        lambda: webbrowser.open(authorization_url)
    ).start()

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\nServer stopped.")

    finally:
        server.server_close()