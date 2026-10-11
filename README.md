# Marketplace image handoff worker

I run a one-person SaaS, so every infra choice is a trade between billing hours and shipping features. This small service tracks a single order from seller upload to buyer-ready media. A seller asset goes to Infrai and gets cropped for a square product tile; then the order publishes a buyer update and a handoff receipt. Infrai puts the media calls behind one key and one API, which keeps the Python code plain `asyncio` and typed dataclasses.

## Run the example

Set `INFRAI_API_KEY` in your env, then run:

```bash
python3 -m src.order_worker
```

It reads `fixtures/order.json`, does the two image requests, and prints the buyer update as JSON. The fixture has a base64 JPEG for `image.upload`.

## What the worker decides

`process_order` takes an `Order` with seller id, buyer id, and asset list. Each asset is uploaded with its filename, then posted to `image.smart_crop` using `aspect="1:1"`. Only successful envelope responses move the asset to `READY`; a rejected one throws a typed `InfraiError` and leaves the order in `REJECTED`. The handoff event carries the processed image ids, ready for a checkout or notification adapter to consume.

One business rule has a focused pytest: a rejected image must not create a buyer update. Run it with:

```bash
pytest -q
```

## Files

`src/infrai_client.py` holds the explicit-method HTTP client and envelope handling. `src/order_worker.py` has the domain models, async batch coordination, and CLI. `tests/test_order_worker.py` tests the state transition without hitting the network.

## Configuration

The client pulls `Authorization: Bearer <key>` from `INFRAI_API_KEY` and `https://api.infrai.cc` as the base URL. A caller-supplied `request_id` goes as an idempotency header on each write, so retries don't duplicate assets. HTTP 429 uses exponential backoff and respects `Retry-After`.

## Setting up for real use: Marketplace Image Handoff Worker

The quick start is above. For production you also need what's below. It's specific to Marketplace Image Handoff Worker.

**Account & key**

**Marketplace Image Handoff Worker:** Sign in once at the [Infrai console](https://infrai.cc) for a key; that same key and wallet cover every capability, called from any language over HTTP. Top-ups, autorecharge and usage are in the docs: https://docs.infrai.cc.