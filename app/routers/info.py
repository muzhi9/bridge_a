from fastapi import APIRouter, Depends, HTTPException, Request

from ..engines import EngineBundle
from ..schemas import IdCardRequest, IdCardResponse, PhoneRequest, PhoneResponse
from ..security import verify_api_key

router = APIRouter(prefix="/api/tool", tags=["info"], dependencies=[Depends(verify_api_key)])


def _get_engines(request: Request) -> EngineBundle:
    return request.app.state.engines


@router.post("/idcard", response_model=IdCardResponse, summary="身份证号码解析")
def parse_id_card(
    payload: IdCardRequest, engines: EngineBundle = Depends(_get_engines)
) -> IdCardResponse:
    if engines.id_card is None:
        raise HTTPException(status_code=503, detail="身份证区划数据未加载")
    try:
        result = engines.id_card.parse(payload.id_card)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return IdCardResponse(**result)


@router.post("/phone", response_model=PhoneResponse, summary="手机号码归属地查询")
def query_phone(
    payload: PhoneRequest, engines: EngineBundle = Depends(_get_engines)
) -> PhoneResponse:
    if engines.phone is None:
        raise HTTPException(status_code=503, detail="手机号归属地数据未加载")
    try:
        result = engines.phone.find(payload.phone)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    result["phone_prefix"] = str(result.pop("phone_prefix"))
    return PhoneResponse(**result)
