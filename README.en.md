# H4 AccessPilot — Acessibilidade digital verificável

**Criador / Creator / Creador: Chris Cruz — [@H4ckD4d](https://github.com/H4ckD4d)**

Open project with a working starter API, demo and multilingual SEO.

## Why / Por quê / Por qué
Find accessibility barriers before your users do. Analyze authorized HTML, organize findings and prioritize manual checks guided by WCAG.

## Start / Iniciar / Empezar

```bash
python3 -m pip install -e './apps/api[test]'
python3 -m pytest apps/api/tests -q
python3 scripts/build_site.py --preview
python3 scripts/check_seo.py site/dist
```

API (`H4_TENANTS` with SHA-256 demo credentials) must be configured before use. Run `python3 scripts/bootstrap_keys.py` locally; never commit output.

## Documentation
- [Architecture](docs/ARCHITECTURE.md) · [SEO](docs/SEO.md) · [Roadmap](docs/ROADMAP.md)
- [Storytelling](docs/STORYTELLING.en.md) · [Contributing](docs/CONTRIBUTING.en.md)

## Limitations
Technical starter, not a production or certified service. No paying customers, rankings, partnerships or service-level guarantees are claimed.

MIT license. **Chris Cruz — @h4ckd4d.**
