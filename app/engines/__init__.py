from pathlib import Path

from ..config import DATA_DIR
from .extract_engine import ExtractEngine
from .info_engine import IdCardParser, PhoneParser
from .text_engine import TextEngine


class EngineBundle:
    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = data_dir
        self.text = TextEngine()
        self.extract = ExtractEngine()
        self.id_card = None
        self.phone = None
        self.data_errors: list[str] = []
        try:
            self.id_card = IdCardParser(data_dir)
        except FileNotFoundError as exc:
            self.data_errors.append(str(exc))
        try:
            self.phone = PhoneParser(data_dir / "phone.dat")
        except FileNotFoundError as exc:
            self.data_errors.append(str(exc))

    @property
    def ready(self) -> bool:
        return not self.data_errors
