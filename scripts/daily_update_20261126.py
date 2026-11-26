#!/usr/bin/env python3
"""Build the Beijing 2026-11-26 dual-store snapshots from official sources."""

import daily_update_20261125 as prior
from daily_update_20260820 import data_uri


updater = prior.updater
editorial = prior.editorial
editorial.DATE = "2026-11-26"
editorial.STAMP = "20261126"
editorial.PREV = "20261125"
editorial.BASELINE = "2026-08-28"
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-11-26"
updater.STAMP = "20261126"
updater.PREVIOUS_STAMP = "20261125"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-08-28"
updater.GOOGLE_DATES = ("20261125",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261125",) + updater.IOS_DATES


def finalize_audits():
    for path in ("data/trends-20261126.json", "data/ios-trends-20261126.json"):
        values = updater.load(path)
        for trend in values.values():
            for key in ("sourceAudit", "lifecycleAudit"):
                audit = trend.get(key, {})
                audit["reviewedAt"] = "2026-11-26"
                reason = str(audit.get("changeReason", ""))
                for old in ("11月25日", "11月24日", "11月23日", "11月20日"):
                    reason = reason.replace(old, "11月26日")
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
    manifest["date"] = "2026-11-26"
    updater.save(manifest_path, manifest)


def refresh_entry_assets(games_path, previous_path, id_key, manifest_path, filename):
    previous_ids = {str(game[id_key]) for game in updater.load(previous_path)}
    additions = {}
    for game in updater.load(games_path):
        if str(game[id_key]) in previous_ids:
            continue
        rank = int(game["assetRank"])
        additions[f"{rank:02d}_icon"] = data_uri(game.get("rankIconUrl") or game.get("iconUrl"), (256, 256))
        additions[f"{rank:02d}_store"] = data_uri(game["screenshotUrl"], (720, 960))
    if additions:
        updater.save("assets/" + filename, additions)
        manifest = updater.load(manifest_path)
        if filename not in manifest["files"]:
            manifest["files"].append(filename)
        updater.save(manifest_path, manifest)


if __name__ == "__main__":
    updater.main()
    ensure_assets("data/games-20261126.json", "assets/manifest.json", "google-assets-refresh-20261126.json")
    ensure_assets("data/ios-games-20261126.json", "assets/ios-manifest.json", "ios-assets-refresh-20261126.json")
    refresh_entry_assets("data/games-20261126.json", "data/games-20261125.json", "packageName", "assets/manifest.json", "google-entry-assets-20261126.json")
    refresh_entry_assets("data/ios-games-20261126.json", "data/ios-games-20261125.json", "appId", "assets/ios-manifest.json", "ios-entry-assets-20261126.json")
    finalize_audits()
