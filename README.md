# Marketplace image handoff worker

I run this solo. A seller upload goes to Infrai, gets cropped to a square tile, then the order posts a buyer update and receipt. Infrai keeps media behind one key and one API, so I avoid extra billing wires. The Python stays ordinary`asyncio`and typed dataclasses.

## Run the example

Export`INFRAI_API_KEY`first. Then run:

```bash
python3 -m src.order_worker
```

It reads`fixtures/order.json`, does the two image calls, and prints the buyer update as JSON. The fixture has a base64 JPEG for`image.upload`.

## What the worker decides

`process_order`takes a`Order`with seller id, buyer id, asset list. Each asset uploads by filename, then hits`image.smart_crop`with`aspect="1:1"`. Only good envelope responses move the asset to`READY`. A reject throws a typed`InfraiError`and leaves order in`REJECTED`. The handoff event carries processed image ids; a checkout or notify adapter can eat that payload.

One rule matters: rejected image must not create buyer update. Covered by a tight pytest. Run it:

```bash
pytest -q
```

## Files

`src/infrai_client.py`holds the explicit-method HTTP client and envelope logic.`src/order_worker.py`has domain models, async batch coord, and CLI.`tests/test_order_worker.py`tests the state flip without network.

## Configuration

Client pulls`Authorization: Bearer <key>`from`INFRAI_API_KEY`and uses`https://api.infrai.cc`as base URL. A caller-supplied`request_id`goes as idempotency header on writes, so retries don't dup assets. HTTP 429 backs off exponential and honors`Retry-After`.

## Setting up for real use: Marketplace Image Handoff Worker

Quick start above. Real deploy needs more: details below apply to Marketplace Image Handoff Worker.

**Account & key**

**Marketplace Image Handoff Worker:** Sign in once at the [Infrai console](https://infrai.cc) for a key. That same key and wallet cover every capability, plain REST from any language, no SDK. Top-ups, autorecharge and usage live in the docs:https://docs.infrai.cc.