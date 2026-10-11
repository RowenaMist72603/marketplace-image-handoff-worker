import asyncio
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .infrai_client import InfraiClient


@dataclass
class SellerAsset:
    filename: str
    file: str
    state: str = "PENDING"
    image_id: str | None = None


@dataclass
class Order:
    order_id: str
    seller_id: str
    buyer_id: str
    assets: list[SellerAsset]
    state: str = "RECEIVED"
    buyer_update: dict[str, Any] | None = None


async def process_order(order: Order, client: InfraiClient) -> Order:
    async def handle(asset: SellerAsset) -> None:
        uploaded = await asyncio.to_thread(client.upload, asset.file, asset.filename, f"{order.order_id}:upload:{asset.filename}")
        image_id = uploaded.get("id") or uploaded.get("image")
        cropped = await asyncio.to_thread(client.smart_crop, image_id, "1:1", f"{order.order_id}:crop:{asset.filename}")
        asset.image_id = cropped.get("id") or cropped.get("image")
        asset.state = "READY"

    try:
        await asyncio.gather(*(handle(asset) for asset in order.assets))
    except Exception:
        order.state = "REJECTED"
        raise
    order.state = "HANDED_OFF"
    order.buyer_update = {"order_id": order.order_id, "buyer_id": order.buyer_id, "status": "media_ready", "images": [a.image_id for a in order.assets]}
    return order


def load_order(path: Path) -> Order:
    raw = json.loads(path.read_text())
    return Order(raw["order_id"], raw["seller_id"], raw["buyer_id"], [SellerAsset(**item) for item in raw["assets"]])


def main() -> None:
    order = load_order(Path(__file__).parent.parent / "fixtures" / "order.json")
    result = asyncio.run(process_order(order, InfraiClient()))
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()

