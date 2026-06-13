from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.request
import os
from urllib.parse import urlparse, parse_qs

ASSOCIATIONS = {
    'mosquee_vaureal': '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',
}

APP_VERSION = {
    "versionCode": 5,
    "apkUrl": "https://github.com/alaouims69/stripe-server/releases/download/V5/app-release.apk"
}

class Handler(BaseHTTPRequestHandler):

    def _cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def do_OPTIONS(self):
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == '/app-version':
            self.send_response(200)
            self._cors_headers()
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(APP_VERSION).encode())
            return

        self.send_response(200)
        self._cors_headers()
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"status": "ok"}')

    def do_POST(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if parsed.path == '/connection_token':
            asso = params.get('asso', ['mosquee_vaureal'])[0]
            stripe_key = ASSOCIATIONS.get(asso)

            if not stripe_key:
                self.send_response(404)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(b'Association not found')
                return

            try:
                req = urllib.request.Request(
                    'https://api.stripe.com/v1/terminal/connection_tokens',
                    data=b'',
                    headers={
                        'Authorization': f'Bearer {stripe_key}',
                        'Content-Type': 'application/x-www-form-urlencoded'
                    },
                    method='POST'
                )
                with urllib.request.urlopen(req) as response:
                    result = json.loads(response.read())
                    token = result['secret']
                    self.send_response(200)
                    self._cors_headers()
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'secret': token}).encode())
            except Exception as e:
                self.send_response(500)
                self._cors_headers()
                self.end_headers()
                self.wfile.write(str(e).encode())
        else:
            self.send_response(404)
            self._cors_headers()
            self.end_headers()

    def log_message(self, format, *args):
        print(f'[SERVER] {args[0]} {args[1]}')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    print(f'Serveur démarré sur le port {port}')
    HTTPServer(('0.0.0.0', port), Handler).serve_forever()
