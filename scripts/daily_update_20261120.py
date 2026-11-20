#!/usr/bin/env python3
"""Build the Beijing 2026-11-20 dual-store snapshots from official sources."""

# The 11-19 updater already contains the current direct-source, exact-baseline,
# product-audit and local-asset logic.  Import it, advance only the dated
# configuration, and let its builders use the 11-19 snapshot as the prior.
import daily_update_20261119 as prior
from daily_update_20260820 import data_uri


updater = prior.updater
prior.DATE = "2026-11-20"
prior.STAMP = "20261120"
prior.PREV = "20261119"
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = prior.DATE
updater.STAMP = prior.STAMP
updater.PREVIOUS_STAMP = prior.PREV
updater.GOOGLE_DATES = (prior.PREV,) + updater.GOOGLE_DATES
updater.IOS_DATES = (prior.PREV,) + updater.IOS_DATES


def refresh_reviewed_icon():
    """Persist the current official Coop TD icon flagged by visual audit."""
    game = next(x for x in updater.load("data/ios-games-20261120.json") if str(x["appId"]) == "6503702666")
    filename = "ios-icons-refresh-20261120.json"
    updater.save("assets/" + filename, {f"{int(game['assetRank']):02d}_icon": data_uri(game["rankIconUrl"], (256, 256))})
    manifest = updater.load("assets/ios-manifest.json")
    if filename not in manifest["files"]:
        manifest["files"].append(filename)
    updater.save("assets/ios-manifest.json", manifest)


def finalize_daily_audits():
    """Advance audit wording and attach today's first-party entrant evidence."""
    source = {
        "label": "SUNBORN 10月28日维护与限时招募公告",
        "url": "https://gf2exilium.sunborngame.com/NewsInfo?id=452&typeId=3",
        "type": "primary",
    }
    for games_path, trends_path, id_key, product_id in (
        ("data/games-20261120.json", "data/trends-20261120.json", "packageName", "com.Sunborn.SnqxExilium.Glo"),
        ("data/ios-games-20261120.json", "data/ios-trends-20261120.json", "appId", "6502505286"),
    ):
        games, trends = updater.load(games_path), updater.load(trends_path)
        for trend in trends.values():
            for audit_key in ("sourceAudit", "lifecycleAudit"):
                audit = trend[audit_key]
                audit["reviewedAt"] = prior.DATE
                audit["changeReason"] = str(audit.get("changeReason", "")).replace("11月19日", "11月20日")
        game = next(x for x in games if str(x[id_key]) == product_id)
        trend = trends[str(game["rank"])]
        event_note = "官方10月28日更新加入Faelynn、Welrod及限时活动；Surprise Access Permission从11月19日起可用于多类限时招募。该节点与双端回榜同窗，但不据单日榜位判断因果。"
        trend["sections"]["turningPoints"] = event_note
        trend["summary"] = (
            "趋势：2024年全球上线后以《少女前线》IP、三维掩体战棋和高规格人形互动承接二次元策略用户；"
            f"关键转折：较11月19日前一有效快照进入/回榜#{game['rank']}。{event_note}；"
            "主力素材：3D战术人形、掩体与高低差、技能演出、枪械改装、宿舍互动和限定角色。"
        )
        trend["sourceAudit"].setdefault("sources", []).append(source)
        trend["lifecycleAudit"].setdefault("sources", []).append(source)
        updater.save(trends_path, trends)
    ios_games = updater.load("data/ios-games-20261120.json")
    ios_trends = updater.load("data/ios-trends-20261120.json")
    raid = next(x for x in ios_games if str(x["appId"]) == "1371565796")
    raid_trend = ios_trends[str(raid["rank"])]
    raid_trend["summary"] = raid_trend["summary"].replace("不能直接解释今日单日上升", "不能直接解释今日单日位移")
    raid_trend["sections"]["turningPoints"] = raid_trend["sections"]["turningPoints"].replace("不能直接解释今日单日上升", "不能直接解释今日单日位移")
    updater.save("data/ios-trends-20261120.json", ios_trends)
if __name__ == "__main__":
    updater.main()
    prior.ensure_ios_assets()
    finalize_daily_audits()
    refresh_reviewed_icon()
