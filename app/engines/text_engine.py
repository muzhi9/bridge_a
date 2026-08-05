import re

import jieba
from opencc import OpenCC
from pypinyin import Style, lazy_pinyin

_converter_s2t = OpenCC("s2t")


class TextEngine:
    def __init__(self) -> None:
        pass

    @staticmethod
    def to_pinyin(text: str) -> list[str]:
        return lazy_pinyin(text, style=Style.TONE)

    @staticmethod
    def segment(text: str) -> list[str]:
        return jieba.lcut(text)

    @staticmethod
    def to_traditional(text: str) -> str:
        return _converter_s2t.convert(text)

    @staticmethod
    def count_chars(text: str) -> int:
        return len(re.sub(r"\s+", "", text))

    def process(self, text: str) -> dict:
        return {
            "pinyin": self.to_pinyin(text),
            "segments": self.segment(text),
            "traditional": self.to_traditional(text),
            "char_count": self.count_chars(text),
        }
