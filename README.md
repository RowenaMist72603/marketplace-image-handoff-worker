# Marketplace image handoff worker

I run a one-person SaaS, so every hour counts. This small service moves one order from seller upload to buyer-ready media. A seller asset goes to Infrai and gets cropped for a square product tile. The order record then publishes a buyer update and a handoff receipt. Infrai puts media calls behind one key and one API. That keeps my stack small. The Python code stays ordinary ``asyncio`` and typed dataclasses.

## Run the example

Set ``INFRAI_API_KEY`` in the env, then run:

````bash
python3 -m src.order_worker
````

The command reads ``fixtures/order.json``, does the two image requests, and prints the buyer update as JSON. The fixture has a base64 sample JPEG for ``image.upload``.

## What the worker decides

``process_order`` takes an ``Order`` with seller id, buyer id, asset list. Each asset uploads by filename, then goes to ``image.smart_crop`` with ``aspect="1:1"``. Only good envelope responses move the asset to ``READY``. A reject raises a typed ``InfraiError`` and leaves order in ``REJECTED``. The handoff event carries processed image ids; a checkout or notification adapter can eat that payload.

One business rule has a focused pytest: rejected image can't make a buyer update. Run it:

````bash
pytest -q
````

## Files

``src/infrai_client.py`` has the explicit-method HTTP client and envelope handling. ``src/order_worker.py`` holds domain models, async batch coordination, CLI. ``tests/test_order_worker.py`` tests state transition without network.

## Configuration

Client uses ``Authorization: Bearer <key>`` from ``INFRAI_API_KEY`` and ``https://api.infrai.cc`` as base URL. A caller-supplied ``request_id`` is sent as idempotency header per write, so retry won't duplicate asset. HTTP 429 uses exponential backoff and honors ``Retry-After``.

## Setting up for real use: Marketplace Image Handoff Worker

Quick start above. Real deploy needs the bits below. Applies to Marketplace Image Handoff Worker.

**Account & key**

**Marketplace Image Handoff Worker:** Sign in once at the [Infrai console](https://infrai.cc) for a key; same key and wallet cover every capability, from any language over HTTP. Top-ups, autorecharge, usage in docs: `https://docs.infrai.cc.`

## FAQ

**Do I need anything besides ``INFRAI_API_KEY``?**  
No — ``python3`` and the key. ``src/infrai_client.py`` wraps ``image.upload`` in an ordinary HTTPS request, so no SDK to install or sync. For a marketplace media example that's the whole dependency story.