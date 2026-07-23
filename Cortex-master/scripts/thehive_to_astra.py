#!/usr/bin/env python3
"""
Fetch alerts from TheHive and output a simple 'astra' text representation.

Security: the script reads the API key from the `THEHIVE_API_KEY` environment
variable. Do NOT hard-code API keys into files or paste them in chat.
"""
import os
import sys
import argparse
import requests
from datetime import datetime


def epoch_to_iso(ms):
    try:
        ms = int(ms)
        if ms > 1e12:
            # already milliseconds
            ts = ms / 1000.0
        else:
            ts = ms
        return datetime.utcfromtimestamp(ts).isoformat() + 'Z'
    except Exception:
        return str(ms)


def fetch_alerts(base_url, api_key, rng):
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    }
    url = base_url.rstrip('/') + '/api/alert?range=' + rng
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()


def to_astra(alert, fmt):
    severity = alert.get('severity')
    title = alert.get('title') or alert.get('message') or ''
    reference = alert.get('sourceRef') or alert.get('id') or alert.get('reference') or ''
    # TheHive may provide different fields for observables/artifacts
    observables = 0
    if isinstance(alert.get('artifacts'), list):
        observables = len(alert.get('artifacts'))
    elif isinstance(alert.get('observables'), list):
        observables = len(alert.get('observables'))
    date = alert.get('startDate') or alert.get('date') or alert.get('createdAt') or ''
    date_iso = epoch_to_iso(date) if date else ''
    tags = ','.join(alert.get('tags', [])) if isinstance(alert.get('tags'), list) else ''

    return fmt.format(
        severity=severity,
        title=title,
        reference=reference,
        observables=observables,
        date=date_iso,
        tags=tags
    )


def main():
    parser = argparse.ArgumentParser(description='Convert TheHive alerts to astra text')
    parser.add_argument('--url', default=os.environ.get('THEHIVE_URL'), help='TheHive base URL (or set THEHIVE_URL)')
    parser.add_argument('--key', default=os.environ.get('THEHIVE_API_KEY'), help='TheHive API key (or set THEHIVE_API_KEY)')
    parser.add_argument('--range', default='0-49', help='result range, e.g. 0-9')
    parser.add_argument('--format', default='{severity} | {title} | ref:{reference} | obs:{observables} | {date}',
                        help='Output format using placeholders: severity,title,reference,observables,date,tags')
    parser.add_argument('--output', help='Optional output file; default stdout')

    args = parser.parse_args()

    if not args.url or not args.key:
        print('Error: TheHive URL and API key are required. Set THEHIVE_URL and THEHIVE_API_KEY or pass --url/--key.', file=sys.stderr)
        sys.exit(2)

    try:
        alerts = fetch_alerts(args.url, args.key, args.range)
    except Exception as e:
        print('Failed to fetch alerts:', e, file=sys.stderr)
        sys.exit(3)

    out_lines = []
    if isinstance(alerts, dict) and alerts.get('data'):
        items = alerts.get('data')
    elif isinstance(alerts, list):
        items = alerts
    else:
        items = alerts

    for a in items:
        try:
            out_lines.append(to_astra(a, args.format))
        except Exception:
            out_lines.append('ERROR converting alert: ' + str(a.get('id', '<unknown>')))

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write('\n'.join(out_lines))
    else:
        for l in out_lines:
            print(l)


if __name__ == '__main__':
    main()
