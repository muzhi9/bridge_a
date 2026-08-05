"""下载离线数据文件到 data 目录。

用法:
    python scripts/download_data.py [--data-dir app/data]
"""

import argparse
import urllib.error
import urllib.request
from pathlib import Path

REGION_BASE = "https://raw.githubusercontent.com/modood/Administrative-divisions-of-China/master/dist"
PHONE_DAT_URL = "https://raw.githubusercontent.com/xluohome/phonedata/master/phone.dat"

FILES = {
    "provinces.csv": f"{REGION_BASE}/provinces.csv",
    "cities.csv": f"{REGION_BASE}/cities.csv",
    "areas.csv": f"{REGION_BASE}/areas.csv",
    "phone.dat": PHONE_DAT_URL,
}


def download(url: str, dest: Path, retries: int = 3) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(1, retries + 1):
        try:
            print(f"下载 {url} -> {dest}")
            with urllib.request.urlopen(url, timeout=120) as resp, open(dest, "wb") as out:
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            print(f"完成: {dest} ({dest.stat().st_size} 字节)")
            return
        except (urllib.error.URLError, OSError) as exc:
            print(f"第 {attempt} 次尝试失败: {exc}")
            if attempt == retries:
                raise
    raise RuntimeError("下载失败")


def main() -> None:
    parser = argparse.ArgumentParser(description="下载离线数据文件")
    parser.add_argument(
        "--data-dir",
        default=str(Path(__file__).resolve().parent.parent / "app" / "data"),
        help="数据输出目录",
    )
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    for name, url in FILES.items():
        download(url, data_dir / name)


if __name__ == "__main__":
    main()
