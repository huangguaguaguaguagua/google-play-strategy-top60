#!/usr/bin/env python3
"""Offline integrity checks for the reviewed 2026-11-27 dual-store release."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def asset_map(manifest_path):
    values = {}
    manifest = load(manifest_path)
    for filename in manifest["files"]:
        values.update(load("assets/" + filename))
    return manifest, values


brief = load("data/market-brief-20261127.json")
assert brief["date"] == "2026-11-27"
assert len(brief["marketNews"]) == 10
assert [item["rank"] for item in brief["marketNews"]] == list(range(1, 11))
assert all(str(item["url"]).startswith("https://") for item in brief["marketNews"])
assert sum(item["type"] == "判断" for item in brief["closing"]) == 3
assert sum(item["type"] == "关注" for item in brief["closing"]) == 3

for store, prefix, key, manifest_path, expected, anchors in (
    ("googlePlay", "", "packageName", "assets/manifest.json", {"new": 1, "pending": 59, "surge": 0}, ("Kingshot", "Clash Royale", "Last Shelter: Survival")),
    ("ios", "ios-", "appId", "assets/ios-manifest.json", {"new": 2, "pending": 58, "surge": 0}, ("Kingshot", "Game of Thrones: Conquest ™", "Lords Mobile: Kingdom Wars")),
):
    games = load(f"data/{prefix}games-20261127.json")
    enrichment = load(f"data/{prefix}enrichment-20261127.json")
    trends = load(f"data/{prefix}trends-20261127.json")
    history = load(f"data/history/{'google-play' if store == 'googlePlay' else 'ios'}/2026-11-27.json")
    manifest, assets = asset_map(manifest_path)
    assert len(games) == len(history["rankings"]) == 60
    assert len({str(game[key]) for game in games}) == 60
    assert [game["rank"] for game in games] == list(range(1, 61))
    assert tuple(games[index - 1]["gameName"] for index in (1, 25, 60)) == anchors
    assert enrichment["comparisonPolicy"]["baselineDate"] == "2026-08-29"
    assert enrichment["comparisonPolicy"]["baselineAvailable"] is False
    counts = {status: sum(game["comparison90d"]["status"] == status for game in games) for status in ("new", "pending", "surge")}
    assert counts == expected, (store, counts)
    assert all(game["comparison90d"]["baselineDate"] == "2026-08-29" for game in games)
    assert all(game["comparison90d"]["status"] != "normal" for game in games)
    assert all(str(game["comparison90d"].get("evidence", "")).strip() for game in games)
    assert manifest["date"] == "2026-11-27"
    assert all(str(assets.get(f"{int(game['assetRank']):02d}_icon", "")).startswith("data:image/") for game in games)
    assert all(str(assets.get(f"{int(game['assetRank']):02d}_store", "")).startswith("data:image/") for game in games)
    for game in games:
        trend = trends[str(game["rank"])]
        summary = trend["summary"]
        assert "趋势：" in summary and "关键转折：" in summary and "主力素材：" in summary
        assert trend["sourceAudit"]["reviewedAt"] == "2026-11-27"
        assert trend["lifecycleAudit"]["reviewedAt"] == "2026-11-27"
        assert trend["sourceAudit"].get("sources")
    audit = load(f"data/icon-audit-{'google' if store == 'googlePlay' else 'ios'}-2026-11-27.json")
    assert audit["rowCount"] == audit["matched"] == 60
    assert audit["review"] == audit["networkErrors"] == audit["missingLocal"] == 0
    products = brief["rankingDynamics"][store]["products"]
    prior = load(f"data/{prefix}games-20261126.json")
    current_ids, prior_ids = {str(x[key]) for x in games}, {str(x[key]) for x in prior}
    card_entries = {x["productId"] for x in products if x["changeType"] == "entry"}
    card_exits = {x["productId"] for x in products if x["changeType"] == "exit"}
    assert card_entries == current_ids - prior_ids
    assert card_exits == prior_ids - current_ids
    print(store, "rows=60", counts, "cards", len(products), "anchors", anchors)

assert brief["status"]["googlePlay"]["baselineAvailable"] is False
assert brief["status"]["ios"]["baselineAvailable"] is False
bundles = [brief["iconBundle"], *brief["iconOverrideBundles"]]
icons = {}
for bundle in bundles:
    icons.update(load(bundle))
cards = brief["rankingDynamics"]["googlePlay"]["products"] + brief["rankingDynamics"]["ios"]["products"]
assert len(cards) == 26
assert all(str(icons.get(item["iconKey"], "")).startswith("data:image/") for item in cards)

reports = load("reports/manifest.json")
dates = [item["date"] for item in reports["reports"]]
assert dates == sorted(dates, reverse=True) and len(dates) == len(set(dates)) and dates[0] == "2026-11-27"
assert (ROOT / brief["downloads"]["markdown"]).exists()
assert brief["globalStrategyRevenue"] == load("data/sensortower-global-strategy-revenue-latest.json")
assert brief["globalStrategyRevenue"]["period"] == "2026-10"

app = (ROOT / "app-20260819d.js").read_text(encoding="utf-8")
index = (ROOT / "index.html").read_text(encoding="utf-8")
assert 'CACHE_VERSION = "20261127"' in app and 'market-brief-20261127.json' in app
assert 'data/games-20261127.json' in app and 'data/ios-games-20261127.json' in app
assert 'styles-20260819d.css?v=20261127' in index and 'app-20260819d.js?v=20261127' in index
assert "类Thronefall移动塔防" in json.dumps(load("data/trends-20261127.json"), ensure_ascii=False)
assert "自由行军" in json.dumps(load("data/trends-20261127.json"), ensure_ascii=False)
assert "竖屏射击" in json.dumps(load("data/trends-20261127.json"), ensure_ascii=False)
print("market brief", len(cards), "cards", len(brief["marketNews"]), "news", len(bundles), "icon bundles; reports and Sensor consistent")
