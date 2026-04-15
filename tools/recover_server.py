"""Slide recovery receiver server.

Start this server, then paste the recovery script into the browser console.
The browser script will POST each cached slide's HTML content to this server.
"""
import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

SAVE_DIR = '/private/tmp/slides/recovered'
os.makedirs(SAVE_DIR, exist_ok=True)

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length)
        data = json.loads(body)

        filename = os.path.basename(data['filename'])
        content = data['content']

        path = os.path.join(SAVE_DIR, filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        resp = json.dumps({'saved': filename, 'bytes': len(content)})
        self.wfile.write(resp.encode())
        print(f'  Saved: {filename} ({len(content)} bytes)')

    def log_message(self, fmt, *args):
        pass

print(f'Recovery server listening on http://127.0.0.1:9876')
print(f'Saving to: {SAVE_DIR}')
print('Waiting for browser to send slides...')
print('Press Ctrl+C to stop.')
HTTPServer(('127.0.0.1', 9876), Handler).serve_forever()
