from pydantic import BaseModel, Field, HttpUrl


class TextRequest(BaseModel):
    text: str = Field(min_length=1, max_length=100_000)


class TextResponse(BaseModel):
    pinyin: list[str]
    segments: list[str]
    traditional: str
    char_count: int


class ExtractRequest(BaseModel):
    url: HttpUrl


class ExtractResponse(BaseModel):
    url: str
    title: str
    text: str


class IdCardRequest(BaseModel):
    id_card: str = Field(min_length=15, max_length=18)


class IdCardResponse(BaseModel):
    province: str | None
    city: str | None
    area: str | None
    birth_date: str
    gender: str


class PhoneRequest(BaseModel):
    phone: str = Field(pattern=r"^1\d{10}$")


class PhoneResponse(BaseModel):
    phone_prefix: str
    province: str
    city: str
    carrier: str
    area_code: str
    zip_code: str
