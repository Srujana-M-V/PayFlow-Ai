import hashlib
import base64
import secrets
import threading
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

CLIENT_ID = "Smc5bXs0gwPJvgPZDgFHfXYSX1rq7nD7UxWtUTXU"
REDIRECT_URI = "http://127.0.0.1:8080/callback"
AUTHORIZATION_URL = "http://127.0.0.1:8001/o/authorize/"
TOKEN_URL = "http://127.0.0.1:8001/o/token/"

SCOPE = "read"
STATE = secrets.token_urlsafe(32)
CODE_VERIFIER = secrets.token_urlsafe(64)
CODE_CHALLENGE = base64.urlsafe_b64encode(
    hashlib.sha256(CODE_VERIFIER.encode()).digest()
).rstrip(b"=").decode()


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)

        if urlparse(self.path).path != "/callback":
            self.send_error(404)
            return

        if params.get("state", [""])[0] != STATE:
            self.send_error(400, "Invalid OAuth state")
            return

        if params.get("error"):
            message = "OAuth authorization failed."
        else:
            code = params.get("code", [""])[0]
            if not code:
                self.send_error(400, "Authorization code missing")
                return

            message = (
                "Authorization code received. "
                "Token exchange will be implemented next."
            )
            print("Authorization code received successfully.")
            print("Do not share the authorization code.")

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(
            f"<html><body><h2>{message}</h2></body></html>".encode()
        )

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    query = urllib.parse.urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPE,
        "state": STATE,
        "code_challenge": CODE_CHALLENGE,
        "code_challenge_method": "S256",
    })

    server = HTTPServer(("127.0.0.1", 8080), OAuthCallbackHandler)
    print("Starting OAuth callback server...")
    threading.Timer(
        1, lambda: webbrowser.open(f"{AUTHORIZATION_URL}?{query}")
    ).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()