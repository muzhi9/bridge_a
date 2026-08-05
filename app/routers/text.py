from fastapi import APIRouter, Depends, Request

from ..engines import EngineBundle
from ..schemas import TextRequest, TextResponse
from ..security import verify_api_key

router = APIRouter(prefix="/api/tool", tags=["text"], dependencies=[Depends(verify_api_key)])


def _get_engines(request: Request) -> EngineBundle:
    return request.app.state.engines


@router.post("/text", response_model=TextResponse, summary="文本工具箱")
def text_tool(payload: TextRequest, engines: EngineBundle = Depends(_get_engines)) -> TextResponse:
    result = engines.text.process(payload.text)
    return TextResponse(**result)
