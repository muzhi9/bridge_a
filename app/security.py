from fastapi import Header, HTTPException

from .config import API_KEY


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="无效或缺失的 API Key")
