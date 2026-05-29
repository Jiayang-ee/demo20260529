"""本地 JSON 文件存储"""
import json
from pathlib import Path
from datetime import date, datetime
from app.core.config import DATA_DIR
from app.models.schemas import FundNavRecord


def _get_file_path(fund_code: str) -> Path:
    path = Path(DATA_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path / f"{fund_code}.json"


def load_nav_records(fund_code: str) -> list[FundNavRecord]:
    """从本地 JSON 加载基金净值记录"""
    file_path = _get_file_path(fund_code)
    if not file_path.exists():
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = []
    for item in data:
        record_date = datetime.strptime(item["date"], "%Y-%m-%d").date()
        records.append(FundNavRecord(
            date=record_date,
            unit_nav=item["unit_nav"],
            accumulated_nav=item.get("accumulated_nav"),
            fetched_at=item["fetched_at"],
            source=item["source"],
        ))

    records.sort(key=lambda x: x.date)
    return records


def save_nav_records(fund_code: str, records: list[FundNavRecord], append: bool = True) -> None:
    """保存基金净值记录到本地 JSON 文件"""
    file_path = _get_file_path(fund_code)

    existing_dates: set[date] = set()
    if append and file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
        for item in existing_data:
            existing_dates.add(datetime.strptime(item["date"], "%Y-%m-%d").date())

    all_records: list[dict] = []
    if append and file_path.exists():
        all_records = []
        with open(file_path, "r", encoding="utf-8") as f:
            all_records = json.load(f)

    for record in records:
        if record.date not in existing_dates:
            all_records.append({
                "date": record.date.isoformat(),
                "unit_nav": record.unit_nav,
                "accumulated_nav": record.accumulated_nav,
                "fetched_at": record.fetched_at,
                "source": record.source,
            })

    all_records.sort(key=lambda x: x["date"])
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(all_records, f, ensure_ascii=False, indent=2)


def get_nav_date_range(fund_code: str) -> tuple[date | None, date | None]:
    """获取本地缓存数据的日期范围"""
    records = load_nav_records(fund_code)
    if not records:
        return None, None
    return records[0].date, records[-1].date


def is_fund_cached(fund_code: str) -> bool:
    """检查基金数据是否已缓存"""
    return _get_file_path(fund_code).exists()