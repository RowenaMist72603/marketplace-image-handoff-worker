import asyncio

import pytest

from src.infrai_client import InfraiError
from src.order_worker import Order, SellerAsset, process_order


class RejectingClient:
    def upload(self, file, filename, request_id):
        raise InfraiError("INVALID_ARGUMENT", {"message": "asset rejected"}, 400)

    def smart_crop(self, image, aspect, request_id):
        raise AssertionError("crop must not run after rejection")


def test_rejected_asset_cannot_publish_buyer_update():
    order = Order("ord-test", "seller", "buyer", [SellerAsset("bad.jpg", "source")])
    with pytest.raises(InfraiError):
        asyncio.run(process_order(order, RejectingClient()))
    assert order.state == "REJECTED"
    assert order.buyer_update is None

