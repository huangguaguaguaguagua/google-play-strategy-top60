#!/usr/bin/env python3
"""Build the Beijing 2026-11-23 dual-store snapshots from official sources."""

import daily_update_20261120 as prior
from daily_update_20260820 import data_uri


updater = prior.updater
prior.prior.DATE = "2026-11-23"
prior.prior.STAMP = "20261123"
prior.prior.PREV = "20261120"
prior.prior.BASELINE = "2026-08-25"
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-11-23"
updater.STAMP = "20261123"
updater.PREVIOUS_STAMP = "20261120"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-08-25"
updater.GOOGLE_DATES = ("20261120",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261120",) + updater.IOS_DATES


def finalize_audits():
    for path in ("data/trends-20261123.json", "data/ios-trends-20261123.json"):
        values = updater.load(path)
        for trend in values.values():
            for key in ("sourceAudit", "lifecycleAudit"):
                audit = trend.get(key, {})
                audit["reviewedAt"] = "2026-11-23"
                reason = str(audit.get("changeReason", ""))
                audit["changeReason"] = reason.replace("11月20日", "11月23日")
        updater.save(path, values)
    ios = updater.load("data/ios-trends-20261123.json")
    games = updater.load("data/ios-games-20261123.json")
    fleet = next(game for game in games if str(game["appId"]) == "1427744264")
    trend = ios[str(fleet["rank"])]
    completion = "是近期可核验的社区与内容节点，但不能直接解释本次回榜。"
    trend["sections"]["turningPoints"] = trend["sections"]["turningPoints"].replace("是；", completion)
    trend["summary"] = trend["summary"].replace("是；主力素材：", completion + "；主力素材：")
    updater.save("data/ios-trends-20261123.json", ios)


def refresh_changed_ios_icons():
    targets = {"6744812012", "6476261995", "6482291732"}
    games = updater.load("data/ios-games-20261123.json")
    additions = {
        f"{int(game['assetRank']):02d}_icon": data_uri(game["rankIconUrl"], (256, 256))
        for game in games if str(game["appId"]) in targets
    }
    filename = "ios-icons-refresh-20261123.json"
    updater.save("assets/" + filename, additions)
    manifest = updater.load("assets/ios-manifest.json")
    if filename not in manifest["files"]:
        manifest["files"].append(filename)
    updater.save("assets/ios-manifest.json", manifest)


if __name__ == "__main__":
    updater.main()
    prior.prior.ensure_ios_assets()
    finalize_audits()
    refresh_changed_ios_icons()
