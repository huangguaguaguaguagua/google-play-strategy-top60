#!/usr/bin/env python3
"""Build the Beijing 2026-09-03 Google Play and Apple App Store snapshots."""
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_ios, save, trend
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from daily_update_20260901 import finish_new_game
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-09-03"
GOOGLE_DATE = "2026-09-03"
GOOGLE_BASELINE = "2026-06-05"
IOS_DATE = "2026-09-03"
IOS_BASELINE = "2026-06-05"

GOOGLE_HISTORY = [
    (f"data/games-{date}.json", f"data/enrichment-{date}.json", f"data/trends-{date}.json")
    for date in (
        "20260902", "20260901", "20260831", "20260828", "20260827", "20260826",
        "20260825", "20260824", "20260821", "20260820", "20260819d",
    )
]
IOS_HISTORY = [
    (f"data/ios-games-{date}.json", f"data/ios-enrichment-{date}.json", f"data/ios-trends-{date}.json")
    for date in (
        "20260902", "20260901", "20260831", "20260828", "20260827", "20260826",
        "20260825", "20260824", "20260821", "20260820", "20260819",
    )
]


def clean_analysis(analysis):
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


def last_fortress_profile(meta, asset_rank):
    store_url = "https://apps.apple.com/us/app/id1540557475"
    game = {
        "appId": "1540557475",
        "packageName": "1540557475",
        "store": "ios",
        "assetRank": asset_rank,
        "genre": "SLG / 地下堡垒经营 / 末日生存",
        "keywords": "地下堡垒；房间建设；幸存者分工；丧尸；英雄编队；荒野采集；联盟协作",
    }
    company = {
        "en": "IM30 / Beijing Longchuang Yuetong / LIFE GAME PTE. LTD.",
        "cn": "北京龙创悦动（IM30；产品体系）/ LIFE GAME PTE. LTD.（海外发行）",
        "confidence": "已确认",
        "basis": "Apple店铺发行主体为LIFE GAME PTE. LTD.；IM30官方产品页将Last Fortress列为旗下产品，确认实际产品体系归属。",
        "source": "https://www.im30.net/en/games/84/",
    }
    analysis = trend(
        "趋势：2021年iOS上线后，以地下堡垒剖面、幸存者职业分工和丧尸压力建立经营入口，再承接英雄编队、荒野采集与联盟SLG，目前由存量联盟和核心用户支撑；关键转折：产品由单纯地下设施扩建逐步加入外部地图、英雄队伍与联盟竞争，近期版本公开说明仅为常规改进，未发现可确认的重大转折；主力素材：堡垒剖面、房间扩建、职业幸存者、丧尸围攻、荒野探索和联盟作战。",
        "2021年iOS上线后，先用地下空间从废墟逐层修复、发电与生产房间布局、厨师/医生/工程师等幸存者分工构成直观经营循环，再把玩家带入英雄小队、荒野资源点和联盟协作。当前已进入成熟长线阶段，主要依赖存量联盟与核心用户。",
        "本次回到iOS美国策略畅销榜第58名；Google Play同名产品当前位于美国策略畅销榜第53名，形成双端同步在榜。产品上架早于90天，属于成熟产品日榜回归，不是近三个月新上榜。",
        "可确认的长期结构变化是从地下堡垒内部经营扩展至外部荒野、英雄编队和联盟对抗。Apple 8月26日版本说明只写常规改进与修复，缺少证据把本次回榜归因于具体活动或版本。",
        "Apple当前商店图集中展示地下堡垒剖面、房间生产、幸存者分工、英雄队伍和荒野据点；这些素材由可视化经营入口承接中后期联盟SLG。素材证据来自Apple与Google Play商品页，可信度为中。",
        "观察未来2—3个工作日iOS能否脱离#58榜尾，同时比较Google #53附近是否保持；若iOS立即掉榜，则按成熟产品的单日付费回补处理。",
        store_url,
        [
            {"label": "IM30官方Last Fortress产品页", "url": "https://www.im30.net/en/games/84/", "type": "company-research"},
            {"label": "Last Fortress官方站", "url": "https://last-fortress.net/", "type": "primary"},
        ],
    )
    return finish_new_game(game, meta), company, analysis


def audit_google(rows):
    try:
        return appbrain_audit(rows)
    except Exception as exc:
        return {
            "sourceRole": "audit-only",
            "sourceUrl": "https://www.appbrain.com/stats/google-play-rankings/top_grossing/strategy/us",
            "status": "unavailable",
            "error": f"{type(exc).__name__}: {exc}",
            "note": "审计源失败不覆盖或阻断Google Play直连榜单。",
        }


def build_google(rows, source_info):
    current = records("data/games-20260902.json", "data/enrichment-20260902.json", "data/trends-20260902.json", "packageName")
    historical = merged_records(GOOGLE_HISTORY, "packageName")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    games, companies, trends = [], {}, {}
    for row in rows:
        rank, package = row["rank"], row["packageName"]
        if package not in historical:
            raise RuntimeError(f"Unexpected Google entrant: {row}")
        game, company, analysis = map(deepcopy, current.get(package, historical[package]))
        change = delta_label(old_rank.get(package), rank)
        comp = comparison(None, rank, GOOGLE_DATE, GOOGLE_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row.get("developer", ""),
            store="googlePlay",
            storeUrl=row["storeUrl"],
            iconUrl=row["iconUrl"],
            screenshotUrl=row["screenshotUrl"],
            totalInstalls=str(row.get("downloads") or "").replace("+", " +"),
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(
            clean_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)
    enrichment = deepcopy(load("data/enrichment-20260902.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260903.json", games)
    save("data/enrichment-20260903.json", enrichment)
    save("data/trends-20260903.json", trends)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    save("assets/manifest.json", manifest)
    cross_check = audit_google(rows)
    save(
        "data/history/google-play/2026-09-03.json",
        {
            "store": "google-play",
            "country": "US",
            "category": "Games > Strategy > Top Grossing",
            "date": CAPTURE,
            "dataDate": GOOGLE_DATE,
            "sourceCapturedAt": source_info["capturedAt"],
            "sourceUrl": source_info["sourceUrl"],
            "sourceEndpoint": source_info["sourceEndpoint"],
            "sourceMethod": source_info["sourceMethod"],
            "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。",
            "crossCheck": cross_check,
            "rankings": [
                {
                    "rank": game["rank"],
                    "packageName": game["packageName"],
                    "gameName": game["gameName"],
                    "sourceUrl": game["storeUrl"],
                }
                for game in games
            ],
        },
    )
    return games, cross_check


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260902.json", "data/ios-enrichment-20260902.json", "data/ios-trends-20260902.json", "appId")
    historical = merged_records(IOS_HISTORY, "appId")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in historical]
    metadata = lookup(entrant_ids) if entrant_ids else {}
    if set(metadata) != set(entrant_ids):
        raise RuntimeError(f"Apple Lookup did not return every entrant: {entrant_ids}")
    games, companies, trends, bundle = [], {}, {}, {}
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id in historical:
            game, company, analysis = map(deepcopy, current.get(app_id, historical[app_id]))
        elif app_id == "1540557475":
            game, company, analysis = last_fortress_profile(metadata[app_id], 88)
            bundle["88_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle["88_store"] = data_uri(game["screenshotUrl"], (720, 720))
        else:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")
        change = delta_label(old_rank.get(app_id), rank)
        comp = comparison(None, rank, IOS_DATE, IOS_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row["developer"],
            store="ios",
            storeUrl=f"https://apps.apple.com/us/app/id{app_id}",
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(
            clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)
    enrichment = deepcopy(load("data/ios-enrichment-20260902.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260903.json", games)
    save("data/ios-enrichment-20260903.json", enrichment)
    save("data/ios-trends-20260903.json", trends)
    if bundle:
        save("assets/ios-assets-16.json", bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if bundle and "ios-assets-16.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-16.json")
    save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save(
        "data/history/ios/2026-09-03.json",
        {
            "store": "ios",
            "country": "US",
            "device": "iPhone",
            "category": "Games > Strategy > Top Grossing",
            "date": source_date,
            "dataDate": source_date,
            "sourceUpdated": source_updated,
            "sourceUrl": source_url,
            "rankings": [
                {
                    "rank": game["rank"],
                    "appId": game["appId"],
                    "gameName": game["gameName"],
                    "sourceUrl": game["storeUrl"],
                }
                for game in games
            ],
        },
    )
    return games, source_date


def main():
    google_source = fetch_top_grossing_strategy()
    ios_url, ios_updated, ios_rows = parse_ios()
    ios_source_date = datetime.fromisoformat(ios_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    if google_source["dataDate"] != GOOGLE_DATE:
        raise RuntimeError(f"Google capture date is {google_source['dataDate']}, expected {GOOGLE_DATE}")
    if ios_source_date != IOS_DATE:
        raise RuntimeError(f"Apple source is still dated {ios_source_date}; keep the previous valid iOS snapshot")
    google, audit = build_google(google_source["rows"], google_source)
    ios, _ = build_ios(ios_rows, ios_url, ios_updated)
    print("Google", google_source["capturedAt"], [(g["rank"], g["gameName"]) for g in google if g["rank"] in (1, 25, 60)])
    print("AppBrain audit", audit)
    print("iOS", ios_updated, [(g["rank"], g["gameName"]) for g in ios if g["rank"] in (1, 25, 60)])


if __name__ == "__main__":
    main()
