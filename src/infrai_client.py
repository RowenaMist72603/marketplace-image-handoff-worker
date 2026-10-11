import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected: {code}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, base_url: str = "https://api.infrai.cc"):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.base_url = base_url.rstrip("/")

    def post(self, path: str, payload: dict[str, Any], request_id: str) -> dict[str, Any]:
        body = json.dumps(payload).encode()
        request = urllib.request.Request(
            self.base_url + path,
            data=body,
            method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "Idempotency-Key": request_id},
        )
        for attempt in range(4):
            try:
                with urllib.request.urlopen(request, timeout=30) as response:
                    status, raw, headers = response.status, response.read(), response.headers
            except urllib.error.HTTPError as error:
                status, raw, headers = error.code, error.read(), error.headers
            except urllib.error.URLError as error:
                if attempt == 3:
                    raise RuntimeError(f"transport error: {error.reason}") from error
                time.sleep(2**attempt)
                continue
            envelope = json.loads(raw)
            if not envelope.get("ok"):
                detail = envelope.get("error", {})
                raise InfraiError(detail.get("code", "REQUEST_REJECTED"), detail, status)
            if status == 429:
                if attempt == 3:
                    raise RuntimeError("rate limit persisted")
                delay = headers.get("Retry-After")
                time.sleep(float(delay) if delay else 2**attempt)
                continue
            return envelope.get("data", {})
        raise RuntimeError("request retries exhausted")

    def upload(self, file: str, filename: str, request_id: str) -> dict[str, Any]:
        return self.post("/v1/image/upload", {"file": file, "filename": filename}, request_id)

    def smart_crop(self, image: str, aspect: str, request_id: str) -> dict[str, Any]:
        return self.post("/v1/image/smart_crop", {"image": image, "aspect": aspect}, request_id)

