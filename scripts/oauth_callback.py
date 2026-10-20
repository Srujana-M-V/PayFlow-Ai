from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_url = urlparse(self.path)

        if parsed_url.path != "/callback":
            self.send_error(404)
            return

        params = parse_qs(parsed_url.query)
        error = params.get("error", [None])[0]
        code = params.get("code", [None])[0]
        state = params.get("state", [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()

        if error:
            message = f"OAuth authorization failed: {error}"
        elif code:
            message = "OAuth authorization code received successfully."
        else:
            message = "No authorization code received."

        self.wfile.write(
            f"<html><body><h2>{message}</h2></body></html>".encode()
        )

        print("OAuth callback received.")
        print("Authorization code received:", bool(code))
        print("State received:", bool(state))

    def log_message(self, format, *args):
        print(format % args)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 8080), OAuthCallbackHandler)
    print("OAuth callback server listening at http://127.0.0.1:8080/callback")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nCallback server stopped.")
    finally:
        server.server_close()