#!/usr/bin/env python3
"""Offline integrity checks for the reviewed 2026-11-24 dual-store release."""

import base64
from collections import Counter
from datetime import date, datetime, timedelta
from io import BytesIO
import json
from pathlib import Path
import re
import unicodedata
from zoneinfo import ZoneInfo

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DAY, STAMP, PREV = "2026-11-24", "20261124", "20261123"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def image_ok(value):
    assert isinstance(value, str) and value.startswith("data:image/"), "non-local image"
    image = Image.open(BytesIO(base64.b64decode(value.split(",", 1)[1])))
    image.verify()


def product_key(name):
    value = unicodedata.normalize("NFKD", name).lower()
    value = "".join(c for c in value if not unicodedata.combining(c))
    value = re.sub(r"[^a-z0-9]+", " ", value).strip()
    return {
        "last war survival game": "last war survival",
        "evony the king s return": "evony",
        "rise of kingdoms lost crusade": "rise of kingdoms",
        "age of origins tower defense": "age of origins",
        "forge master idle rpg": "forge master",
        "marvel snap hero strategy ccg": "marvel snap",
        "marvel snap hero card game": "marvel snap",
        "top force commander": "top force",
        "kingdom guard tower defense td": "kingdom guard tower defense",
        "rise of castles ice and fire": "rise of castles",
        "rise of castles fire and war": "rise of castles",
    }.get(value, value)


stores = {
    "googlePlay": ("", "google-play", "packageName", "assets/manifest.json", "Google"),
    "ios": ("ios-", "ios", "appId", "assets/ios-manifest.json", "iOS"),
}
datasets = {store: load(f"data/{settings[0]}games-{STAMP}.json") for store, settings in stores.items()}
brief = load(f"data/market-brief-{STAMP}.json")
icon_bundles = [brief["iconBundle"]] + brief.get("iconOverrideBundles", [])
market_icons = {}
for bundle in icon_bundles:
    market_icons.update(load(bundle))

for store, (prefix, folder, id_key, manifest_path, own_label) in stores.items():
    games = datasets[store]
    trends = load(f"data/{prefix}trends-{STAMP}.json")
    prior = load(f"data/{prefix}games-{PREV}.json")
    history = load(f"data/history/{folder}/{DAY}.json")
    baseline = load(f"data/history/{folder}/2026-08-26.json")
    assert len(games) == 60 and len({str(g[id_key]) for g in games}) == 60
    assert [g["rank"] for g in games] == list(range(1, 61))
    assert len({g["assetRank"] for g in games}) == 60
    assets = {}
    for bundle in load(manifest_path)["files"]:
        assets.update(load("assets/" + bundle))
    other_store = "ios" if store == "googlePlay" else "googlePlay"
    other_label = "iOS" if store == "googlePlay" else "Google"
    counterpart = {product_key(g["gameName"]): g for g in datasets[other_store]}
    for game in games:
        key = str(game["rank"])
        for kind in ("icon", "store"):
            inline = game.get("iconData" if kind == "icon" else "storeImageData")
            image_ok(inline or assets[f"{game['assetRank']:02d}_{kind}"])
        comparison = game["comparison90d"]
        released = date.fromisoformat(game["releaseDateIso"][:10])
        in_window = date.fromisoformat(DAY) - timedelta(days=90) <= released <= date.fromisoformat(DAY)
        assert (comparison["status"] == "new") == in_window
        assert comparison["status"] != "pending"
        trend = trends[key]
        assert all(label in trend["summary"] for label in ("趋势：", "关键转折：", "主力素材："))
        assert set(trend["sections"]) == {"development", "rankPath", "turningPoints", "creative", "watch"}
        assert f"第{game['rank']}名" in trend["sections"]["rankPath"]
        for audit in ("sourceAudit", "lifecycleAudit"):
            assert trend[audit]["reviewedAt"] == DAY
        match = counterpart.get(product_key(game["gameName"]))
        for rank in re.findall(rf"{other_label}[^，；。]*?#(\d+)", trend["summary"]):
            assert match and int(rank) == match["rank"], (store, game["gameName"], rank)
    now_ids, old_ids = {str(g[id_key]) for g in games}, {str(g[id_key]) for g in prior}
    cards = brief["rankingDynamics"][store]["products"]
    assert {c["productId"] for c in cards if c["changeType"] == "entry"} == now_ids - old_ids
    assert {c["productId"] for c in cards if c["changeType"] == "exit"} == old_ids - now_ids
    assert len({c["productId"] for c in cards}) == len(cards)
    for card in cards:
        image_ok(market_icons[card["iconKey"]])
        row = next((g for g in games if str(g[id_key]) == card["productId"]), None)
        if row:
            assert f"#{row['rank']}" in card["changeLabel"]
    print(store, "60 unique rows; 120 local images;", Counter(g["comparison90d"]["status"] for g in games), f"{len(cards)} cards")

assert brief["date"] == DAY and 8 <= len(brief["marketNews"]) <= 12
assert Counter(x["type"] for x in brief["closing"]) == {"判断": 3, "关注": 3}
manifest = load("reports/manifest.json")["reports"]
assert manifest[0]["date"] == DAY and len({r["date"] for r in manifest}) == len(manifest)
revenue = load("data/sensortower-global-strategy-revenue-latest.json")
assert brief["globalStrategyRevenue"]["period"] == revenue["period"]
assert brief["globalStrategyRevenue"]["rankings"] == revenue["rankings"]
assert len(revenue["rankings"]) == revenue["strategyMatches"] == 2
assert revenue["period"] == "2026-10"
assert "2026-11-24T09:19:10+08:00" in (ROOT / f"reports/{DAY}.md").read_text()
print(f"{sum(len(brief['rankingDynamics'][s]['products']) for s in stores)} movement cards; {len(brief['marketNews'])} news; 3 judgments + 3 followups; reports and Sensor Tower subset consistent")
