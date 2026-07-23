Ingest Proxy (Wazuh → TheHive)
================================

This small proxy accepts incoming alert webhooks, adds a safe non-destructive
`source_alias: "Astra"` and a `astra` tag, then forwards alerts to TheHive.

Why use this
-------------
- Avoids changing the original `source` field.
- Lets you test how TheHive and downstream rules behave with the alias/tag present.
- Easy to roll back — just change Wazuh to send directly to TheHive again.

Usage
-----
1. Set environment variables:

```bash
export THEHIVE_URL="http://THEHIVE_HOST:9000"
export THEHIVE_API_KEY="YOUR_API_KEY"
```

2. Run the proxy:

```bash
python3 scripts/ingest_proxy.py --host 0.0.0.0 --port 8080
```

3. Point your Wazuh or ingestion connector webhook to:

```
http://PROXY_HOST:8080/ingest
```

Testing
-------
Send a sample alert with curl:

```bash
curl -v -X POST http://localhost:8080/ingest -H "Content-Type: application/json" -d '{"title":"test","source":"Wazuh"}'
```

Notes
-----
- This is intended as a staging/testing helper. For production, consider integrating a transform into your connector or implementing this as a small service behind a reverse proxy with TLS.
- The script will forward the response from TheHive to the caller.
