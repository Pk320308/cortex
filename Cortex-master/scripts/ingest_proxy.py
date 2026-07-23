#!/usr/bin/env python3
"""
Simple ingestion proxy: receive incoming alert JSON, add a non-destructive alias/tag,
and forward to TheHive. This avoids changing source field and is safe for testing.

Usage:
  - Set THEHIVE_URL and THEHIVE_API_KEY environment variables.
  - Run: python scripts/ingest_proxy.py --host 0.0.0.0 --port 8080
  - Point your Wazuh/the connector webhook to http://PROXY_HOST:8080/ingest

Behavior:
  - Adds `source_alias: "Astra"` to the JSON payload if not present.
  - Ensures tag `astra` is present in `tags` list.
  - Forwards the modified payload to TheHive `/api/alert` endpoint.
  - Returns TheHive response to the caller.

This is intentionally non-destructive: the original `source` field is left unchanged.
"""
from http.server import BaseHTTPRequestHandler, HTTPServer
import argparse
import json
import os
import requests
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')


def transform(alert):
    # Add non-destructive alias and tag
    if not isinstance(alert, dict):
        return alert
    if 'source_alias' not in alert:
        alert['source_alias'] = 'Astra'
    tags = alert.get('tags')
    if tags is None:
        alert['tags'] = ['astra']
    elif isinstance(tags, list):
        if 'astra' not in tags:
            tags.append('astra')
    else:
        try:
            alert['tags'] = list(tags) + ['astra']
        except Exception:
            alert['tags'] = ['astra']
    return alert


class IngestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path != '/ingest':
            self.send_response(404)
            self.end_headers()
            return
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            payload = json.loads(body)
        except Exception:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid JSON')
            return

        transformed = transform(payload)

        thehive_url = os.environ.get('THEHIVE_URL')
        thehive_key = os.environ.get('THEHIVE_API_KEY')
        if not thehive_url or not thehive_key:
            logging.error('THEHIVE_URL or THEHIVE_API_KEY not set')
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Missing THEHIVE_URL or THEHIVE_API_KEY')
            return

        headers = {
            'Authorization': f'Bearer {thehive_key}',
            'Content-Type': 'application/json'
        }
        try:
            resp = requests.post(thehive_url.rstrip('/') + '/api/alert', headers=headers, json=transformed, timeout=30)
            logging.info('Forwarded to TheHive: %s %s', resp.status_code, resp.text[:200])
        except Exception as e:
            logging.exception('Failed to forward to TheHive')
            self.send_response(502)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
            return

        self.send_response(resp.status_code)
        for k, v in resp.headers.items():
            # avoid duplicate headers
            try:
                self.send_header(k, v)
            except Exception:
                pass
        self.end_headers()
        if resp.content:
            self.wfile.write(resp.content)


def run_server(host, port):
    server = HTTPServer((host, port), IngestHandler)
    logging.info('Starting ingest proxy on %s:%s', host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info('Shutting down')
        server.server_close()


def main():
    parser = argparse.ArgumentParser(description='Ingest proxy for Wazuh -> TheHive with safe transform')
    parser.add_argument('--host', default='127.0.0.1')
    parser.add_argument('--port', type=int, default=8080)
    args = parser.parse_args()
    run_server(args.host, args.port)


if __name__ == '__main__':
    main()
