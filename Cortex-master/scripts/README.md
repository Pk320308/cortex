TheHive → Astra conversion script
=================================

This folder contains `thehive_to_astra.py`, a small helper to fetch alerts
from TheHive and emit a simple textual ("astra") representation.

Usage
-----

1. Export your TheHive URL and API key as environment variables (recommended):

```bash
export THEHIVE_URL="http://THEHIVE_HOST:9000"
export THEHIVE_API_KEY="YOUR_API_KEY"
```

2. Run the script:

```bash
python3 scripts/thehive_to_astra.py --range 0-9
```

Or pass `--url` and `--key` on the command line if you prefer.

Security
--------
- Do not commit API keys to the repository.
- Avoid pasting keys in chat. If you already did, rotate the key.

Customization
-------------
Use `--format` to change the output layout. Available placeholders: `{severity}`, `{title}`, `{reference}`, `{observables}`, `{date}`, `{tags}`.
