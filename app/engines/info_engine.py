import csv
import re
import struct
from datetime import datetime
from pathlib import Path

_ID_CARD_PATTERN = re.compile(r"^\d{17}[\dXx]$")
_PHONE_PATTERN = re.compile(r"^1\d{10}$")
_WEIGHTS = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
_CHECK_CODES = "10X98765432"

_CARD_TYPES = {
    1: "中国移动",
    2: "中国联通",
    3: "中国电信",
    4: "中国电信虚拟运营商",
    5: "中国联通虚拟运营商",
    6: "中国移动虚拟运营商",
    7: "中国广电",
    8: "中国广电虚拟运营商",
}


class IdCardParser:
    def __init__(self, data_dir: Path) -> None:
        self._region_names: dict[str, str] = {}
        for filename in ("provinces.csv", "cities.csv", "areas.csv"):
            self._load_csv(data_dir / filename)
        if not self._region_names:
            raise FileNotFoundError("未找到行政区划数据（provinces/cities/areas.csv）")

    def _load_csv(self, path: Path) -> None:
        if not path.exists():
            return
        with open(path, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                code = (row.get("code") or "").strip()
                name = (row.get("name") or "").strip()
                if code and name:
                    self._region_names[code] = name

    def parse(self, id_card: str) -> dict:
        id_card = id_card.strip().upper()
        if not _ID_CARD_PATTERN.fullmatch(id_card):
            raise ValueError("身份证号码格式不正确")
        checksum = sum(int(id_card[i]) * _WEIGHTS[i] for i in range(17)) % 11
        if _CHECK_CODES[checksum] != id_card[17]:
            raise ValueError("身份证校验位不正确")
        year, month, day = (int(id_card[6:10]), int(id_card[10:12]), int(id_card[12:14]))
        try:
            birth_date = datetime(year, month, day)
        except ValueError:
            raise ValueError("出生日期无效")
        code = id_card[:6]
        return {
            "province": self._region_names.get(code[:2]),
            "city": self._region_names.get(code[:4]),
            "area": self._region_names.get(code),
            "birth_date": birth_date.strftime("%Y-%m-%d"),
            "gender": "男" if int(id_card[16]) % 2 == 1 else "女",
        }


class PhoneParser:
    def __init__(self, dat_path: Path) -> None:
        if not dat_path.exists():
            raise FileNotFoundError("未找到 phone.dat 文件")
        with open(dat_path, "rb") as f:
            self._data = f.read()
        self._first_offset = struct.unpack_from("<i", self._data, 4)[0]
        self._count = (len(self._data) - self._first_offset) // 9

    def find(self, phone: str) -> dict:
        phone = phone.strip()
        if not _PHONE_PATTERN.fullmatch(phone):
            raise ValueError("手机号码格式不正确")
        target = int(phone[:7])
        left, right = 0, self._count
        while left <= right:
            mid = (left + right) // 2
            index_offset = self._first_offset + mid * 9
            if index_offset + 9 > len(self._data):
                break
            current = struct.unpack_from("<I", self._data, index_offset)[0]
            if current < target:
                left = mid + 1
            elif current > target:
                right = mid - 1
            else:
                return self._parse_record(index_offset, target)
        raise ValueError("未找到该号码的归属地信息")

    def _parse_record(self, index_offset: int, phone_prefix: int) -> dict:
        record_offset = struct.unpack_from("<I", self._data, index_offset + 4)[0]
        card_type = self._data[index_offset + 8]
        end = self._data.index(b"\x00", record_offset)
        fields = self._data[record_offset:end].decode("utf-8").split("|")
        if len(fields) < 4:
            raise ValueError("归属地数据损坏")
        return {
            "phone_prefix": phone_prefix,
            "province": fields[0],
            "city": fields[1],
            "zip_code": fields[2],
            "area_code": fields[3],
            "carrier": _CARD_TYPES.get(card_type, "未知运营商"),
        }
