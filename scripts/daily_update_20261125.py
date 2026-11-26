#!/usr/bin/env python3
"""Build the Beijing 2026-11-25 dual-store snapshots from official sources."""

import daily_update_20261124 as prior
from daily_update_20260820 import data_uri


updater = prior.updater
editorial = prior.editorial
editorial.DATE = "2026-11-25"
editorial.STAMP = "20261125"
editorial.PREV = "20261124"
editorial.BASELINE = "2026-08-27"
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-11-25"
updater.STAMP = "20261125"
updater.PREVIOUS_STAMP = "20261124"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-08-27"
updater.GOOGLE_DATES = ("20261124",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261124",) + updater.IOS_DATES


def finalize_audits():
    for path in ("data/trends-20261125.json", "data/ios-trends-20261125.json"):
        values = updater.load(path)
        for trend in values.values():
            for key in ("sourceAudit", "lifecycleAudit"):
                audit = trend.get(key, {})
                audit["reviewedAt"] = "2026-11-25"
                reason = str(audit.get("changeReason", ""))
                for old in ("11月24日", "11月23日", "11月20日"):
                    reason = reason.replace(old, "11月25日")
                audit["changeReason"] = reason
        updater.save(path, values)


def ensure_assets(games_path, manifest_path, filename):
    manifest = updater.load(manifest_path)
    assets = {}
    for bundle in manifest["files"]:
        assets.update(updater.load("assets/" + bundle))
    additions = {}
    for game in updater.load(games_path):
        for suffix, url, size in (("icon", game.get("rankIconUrl") or game.get("iconUrl"), (256, 256)), ("store", game.get("screenshotUrl"), (720, 960))):
            key = f"{int(game['assetRank']):02d}_{suffix}"
            if key not in assets:
                additions[key] = data_uri(url, size)
    if additions:
        updater.save("assets/" + filename, additions)
        manifest["files"].append(filename)
    manifest["date"] = "2026-11-25"
    updater.save(manifest_path, manifest)


def refresh_ios_icon():
    game = next(item for item in updater.load("data/ios-games-20261125.json") if str(item["appId"]) == "850057092")
    filename = "ios-icons-refresh-20261125.json"
    updater.save("assets/" + filename, {f"{int(game['assetRank']):02d}_icon": data_uri(game["rankIconUrl"], (256, 256))})
    manifest = updater.load("assets/ios-manifest.json")
    if filename not in manifest["files"]:
        manifest["files"].append(filename)
    updater.save("assets/ios-manifest.json", manifest)


if __name__ == "__main__":
    updater.main()
    ensure_assets("data/games-20261125.json", "assets/manifest.json", "google-assets-refresh-20261125.json")
    ensure_assets("data/ios-games-20261125.json", "assets/ios-manifest.json", "ios-assets-refresh-20261125.json")
    refresh_ios_icon()
    finalize_audits()
