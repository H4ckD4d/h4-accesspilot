# AccessPilot — Local-only API examples

Configure `H4_TENANTS` with the SHA-256 hash of a new 24+ character API key (see `scripts/bootstrap_keys.py`). Export the *matching raw token* to `H4_API_KEY` locally and never commit or paste it into issues.

```bash
curl -X POST http://127.0.0.1:8000/v1/audits \
  -H "X-API-Key: $H4_API_KEY" -H 'Content-Type: application/json' \
  -d '{"label":"Local example","html_source":"<html><head></head><body><img src=sample.png></body></html>"}'
```

`GET /healthz`, `GET /readyz`, `GET /v1/me`, and `GET /v1/audit` are common routes. API routes use authorization and are explicitly `noindex`.

This example is synthetic and assumes the API runs privately on 127.0.0.1:8000.
