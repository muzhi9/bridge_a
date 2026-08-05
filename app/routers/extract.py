import requests
from fastapi import APIRouter, Depends, HTTPException, Request

from ..engines import EngineBundle
from ..schemas import ExtractRequest, ExtractResponse
from ..security import verify_api_key

router = APIRouter(prefix="/api/tool", tags=["extract"], dependencies=[Depends(verify_api_key)])


def _get_engines(request: Request) -> EngineBundle:
    return request.app.state.engines


@router.post("/extract", response_model=ExtractResponse, summary="网页正文提取")
def extract_article(
    payload: ExtractRequest, engines: EngineBundle = Depends(_get_engines)
) -> ExtractResponse:
    try:
        result = engines.extract.extract(str(payload.url))
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"抓取网页失败: {exc}")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ExtractResponse(**result)
