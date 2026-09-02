#!/usr/bin/env python3
"""Build store-separated revenue-momentum proxies from valid TOP60 snapshots.

The output deliberately measures chart momentum, not estimated revenue. Missing
products in an otherwise valid TOP60 snapshot are assigned rank 61 so entries,
exits and re-entries remain comparable without inventing weekend observations.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]
STORE_SETTINGS = {
    "google-play": {
        "label": "Google Play · Android",
        "history": "data/history/google-play",
        "idField": "packageName",
    },
    "ios": {
        "label": "App Store · iPhone/iOS",
        "history": "data/history/ios",
        "idField": "appId",
    },
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def product_key(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "").lower()
    normalized = normalized.replace("™", "").replace("®", "")
    normalized = re.sub(r"[^a-z0-9]+", " ", normalized).strip()
    aliases = {
        "last war survival game": "last war survival",
        "evony the king s return": "evony",
        "rise of kingdoms lost crusade": "rise of kingdoms",
        "age of origins tower defense": "age of origins",
        "marvel snap hero strategy ccg": "marvel snap",
        "marvel snap hero card game": "marvel snap",
        "top force commander": "top force",
        "kingdom guard tower defense td": "kingdom guard tower defense",
        "dark war survival": "dark war survival",
    }
    return aliases.get(normalized, normalized)


def valid_snapshot(path: Path, store: str, target: date):
    try:
        value = load(path)
        snapshot_date = date.fromisoformat(str(value.get("dataDate") or value.get("date")))
        rankings = value.get("rankings") or []
        id_field = STORE_SETTINGS[store]["idField"]
        ids = [str(item.get(id_field) or "").strip() for item in rankings]
        ranks = [item.get("rank") for item in rankings]
        if snapshot_date > target or len(rankings) != 60:
            return None
        if any(not item_id for item_id in ids) or len(set(ids)) != 60:
            return None
        if sorted(ranks) != list(range(1, 61)):
            return None
        return {
            "date": snapshot_date,
            "dateText": snapshot_date.isoformat(),
            "path": path.relative_to(ROOT).as_posix(),
            "value": value,
            "byId": {str(item[id_field]): item for item in rankings},
        }
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return None


def confidence(sample_count: int) -> str:
    if sample_count >= 15:
        return "高"
    if sample_count >= 10:
        return "中"
    if sample_count >= 5:
        return "低"
    return "积累中"


def classify(recent: list[int], previous: list[int], momentum: float | None):
    if len(recent) < 5:
        return "accumulating", "观察积累中"
    if len(previous) < 5:
        return "new-reentry", "新进/回榜观察"
    if all(rank == 61 for rank in previous) and any(rank <= 60 for rank in recent):
        return "new-reentry", "新进/回榜"
    assert momentum is not None
    if momentum >= 8:
        return "strong-up", "强势上升"
    if momentum >= 3:
        return "up", "上升"
    if momentum <= -8:
        return "strong-down", "明显回落"
    if momentum <= -3:
        return "down", "回落"
    return "stable", "稳定"


def rounded(value: float | None):
    return None if value is None else round(value, 1)


def build_store(store: str, target: date):
    settings = STORE_SETTINGS[store]
    history_dir = ROOT / settings["history"]
    start = target - timedelta(days=29)
    snapshots = []
    for path in sorted(history_dir.glob("*.json")):
        snapshot = valid_snapshot(path, store, target)
        if snapshot and snapshot["date"] >= start:
            snapshots.append(snapshot)
    # A run may capture the same underlying source date again (for example when
    # a provider has not rolled over yet). Count that as one observation and
    # keep the latest stored copy for the date.
    snapshots = list({snapshot["dateText"]: snapshot for snapshot in snapshots}.values())
    snapshots.sort(key=lambda item: item["date"])
    if not snapshots:
        raise RuntimeError(f"{store}: no valid TOP60 snapshot on or before {target}")

    current = snapshots[-1]
    recent_snapshots = snapshots[-5:]
    previous_snapshots = snapshots[-10:-5]
    games = []
    for current_item in current["value"]["rankings"]:
        item_id = str(current_item[settings["idField"]])
        ranks = [snapshot["byId"].get(item_id, {}).get("rank", 61) for snapshot in snapshots]
        recent = ranks[-5:]
        previous = ranks[-10:-5]
        recent_avg = mean(recent) if recent else None
        previous_avg = mean(previous) if len(previous) == 5 else None
        momentum = previous_avg - recent_avg if previous_avg is not None and recent_avg is not None else None
        status, label = classify(recent, previous, momentum)
        in_chart = sum(rank <= 60 for rank in ranks)
        games.append({
            "productId": item_id,
            "gameName": current_item["gameName"],
            "productKey": product_key(current_item["gameName"]),
            "currentRank": current_item["rank"],
            "recent5AverageRank": rounded(recent_avg),
            "previous5AverageRank": rounded(previous_avg),
            "momentum5d": rounded(momentum),
            "averageRank30d": rounded(mean(ranks)),
            "top60Rate30d": round(in_chart / len(snapshots) * 100, 1),
            "validSnapshotCount30d": len(snapshots),
            "inChartSnapshotCount30d": in_chart,
            "status": status,
            "label": label,
            "confidence": confidence(len(snapshots)),
            "crossStoreResonance": False,
        })

    games.sort(key=lambda item: item["currentRank"])
    return {
        "date": target.isoformat(),
        "sourceDate": current["dateText"],
        "store": store,
        "storeLabel": settings["label"],
        "scope": "US / Games > Strategy / Top Grossing / TOP60",
        "metricType": "榜位动能代理指标（非收入估算）",
        "validSnapshotDates30d": [snapshot["dateText"] for snapshot in snapshots],
        "recentWindowDates": [snapshot["dateText"] for snapshot in recent_snapshots],
        "previousWindowDates": [snapshot["dateText"] for snapshot in previous_snapshots],
        "methodology": {
            "formula": "前5个有效快照平均名次 - 最近5个有效快照平均名次；正值代表榜位改善。",
            "missingRule": "仅在商店当日TOP60快照完整有效时计算；产品缺席该有效快照按第61名计，周末和缺失快照不补值。",
            "thresholds": "≥+8强势上升；+3至+7.9上升；-2.9至+2.9稳定；-3至-7.9回落；≤-8明显回落。",
            "confidence": "30日有效快照≥15为高、10—14为中、5—9为低、少于5为积累中。",
        },
        "games": games,
    }


def movers(store_data: dict, direction: str):
    eligible = [item for item in store_data["games"] if item["momentum5d"] is not None]
    reverse = direction == "up"
    eligible.sort(key=lambda item: (item["momentum5d"], -item["currentRank"]), reverse=reverse)
    if direction == "up":
        eligible = [item for item in eligible if item["momentum5d"] > 0]
    else:
        eligible = [item for item in eligible if item["momentum5d"] < 0]
    return [{
        "productId": item["productId"],
        "gameName": item["gameName"],
        "currentRank": item["currentRank"],
        "momentum5d": item["momentum5d"],
        "label": item["label"],
    } for item in eligible[:5]]


def add_resonance(google: dict, ios: dict):
    ios_by_key = {item["productKey"]: item for item in ios["games"]}
    for google_item in google["games"]:
        ios_item = ios_by_key.get(google_item["productKey"])
        if not ios_item:
            continue
        if (google_item["momentum5d"] or 0) >= 3 and (ios_item["momentum5d"] or 0) >= 3:
            google_item["crossStoreResonance"] = True
            ios_item["crossStoreResonance"] = True


def build_module(target: date):
    google = build_store("google-play", target)
    ios = build_store("ios", target)
    add_resonance(google, ios)
    observations_path = ROOT / "data/revenue-observations.json"
    observations = load(observations_path).get("observations", []) if observations_path.exists() else []
    generated_at = load(ROOT / "data/history/google-play" / f"{google['sourceDate']}.json").get(
        "sourceCapturedAt", f"{target.isoformat()}T00:00:00+08:00"
    )
    module = {
        "date": target.isoformat(),
        "timezone": "Asia/Shanghai",
        "generatedAt": generated_at,
        "title": "收入观察与畅销动能",
        "disclaimer": "收入观察仅引用公开披露或第三方公开估算；全榜动能只反映同商店畅销排名变化，不等同于收入金额或同比。",
        "observationCadence": "工作日保留最新有效观察；每周一复核最多8款，且每月8日后的首个工作日深度复核上月最多20款。",
        "momentumCadence": "每个工作日随双榜更新重算，Google Play与iOS严格分开。",
        "observations": observations,
        "stores": {
            "googlePlay": {
                "label": google["storeLabel"],
                "path": f"data/revenue-momentum/google-play/{target.isoformat()}.json",
                "validSnapshotCount30d": len(google["validSnapshotDates30d"]),
                "confidence": confidence(len(google["validSnapshotDates30d"])),
                "topRisers": movers(google, "up"),
                "topFallers": movers(google, "down"),
            },
            "ios": {
                "label": ios["storeLabel"],
                "path": f"data/revenue-momentum/ios/{target.isoformat()}.json",
                "validSnapshotCount30d": len(ios["validSnapshotDates30d"]),
                "confidence": confidence(len(ios["validSnapshotDates30d"])),
                "topRisers": movers(ios, "up"),
                "topFallers": movers(ios, "down"),
            },
        },
        "methodology": google["methodology"],
    }
    save(ROOT / module["stores"]["googlePlay"]["path"], google)
    save(ROOT / module["stores"]["ios"]["path"], ios)
    save(ROOT / "data/revenue-module-latest.json", module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="Beijing report date (YYYY-MM-DD); defaults to latest common history date")
    args = parser.parse_args()
    if args.date:
        target = date.fromisoformat(args.date)
    else:
        latest = []
        for settings in STORE_SETTINGS.values():
            dates = [date.fromisoformat(path.stem) for path in (ROOT / settings["history"]).glob("*.json")]
            latest.append(max(dates))
        target = min(latest)
    module = build_module(target)
    print(
        f"Wrote revenue module {module['date']}: "
        f"Google {module['stores']['googlePlay']['validSnapshotCount30d']} snapshots, "
        f"iOS {module['stores']['ios']['validSnapshotCount30d']} snapshots"
    )


if __name__ == "__main__":
    main()
