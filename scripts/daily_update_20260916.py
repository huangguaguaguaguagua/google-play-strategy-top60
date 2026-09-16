#!/usr/bin/env python3
"""Build the Beijing 2026-09-16 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, delta_label, load, parse_ios, save
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-09-16"
GOOGLE_DATE = "2026-09-16"
GOOGLE_BASELINE = "2026-06-18"
IOS_DATE = "2026-09-16"
IOS_BASELINE = "2026-06-18"

GOOGLE_DATES = (
    "20260915", "20260914", "20260911", "20260910", "20260909", "20260908", "20260907",
    "20260904", "20260903", "20260902", "20260901", "20260831", "20260828", "20260827",
    "20260826", "20260825", "20260824", "20260821", "20260820", "20260819d",
)
IOS_DATES = (
    "20260915", "20260914", "20260911", "20260910", "20260909", "20260908", "20260907",
    "20260904", "20260903", "20260902", "20260901", "20260831", "20260828", "20260827",
    "20260826", "20260825", "20260824", "20260821", "20260820", "20260819",
)


def history_specs(prefix, dates):
    return [
        (
            f"data/{prefix}games-{date}.json",
            f"data/{prefix}enrichment-{date}.json",
            f"data/{prefix}trends-{date}.json",
        )
        for date in dates
    ]


def clean_analysis(analysis):
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


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
    current = records(
        "data/games-20260915.json", "data/enrichment-20260915.json", "data/trends-20260915.json", "packageName"
    )
    historical = merged_records(history_specs("", GOOGLE_DATES), "packageName")
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
        if package == "com.readygo.dark.gp":
            analysis["summary"] = analysis["summary"].replace("黑暗丧尸压力", "暗黑压力")
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)

    enrichment = deepcopy(load("data/enrichment-20260915.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=GOOGLE_BASELINE,
        currentDate=GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/games-20260916.json", games)
    save("data/enrichment-20260916.json", enrichment)
    save("data/trends-20260916.json", trends)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    save("assets/manifest.json", manifest)

    cross_check = audit_google(rows)
    save(
        "data/history/google-play/2026-09-16.json",
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
    current = records(
        "data/ios-games-20260915.json",
        "data/ios-enrichment-20260915.json",
        "data/ios-trends-20260915.json",
        "appId",
    )
    historical = merged_records(history_specs("ios-", IOS_DATES), "appId")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    games, companies, trends = [], {}, {}
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id not in historical:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")
        game, company, analysis = map(deepcopy, current.get(app_id, historical[app_id]))
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

    enrichment = deepcopy(load("data/ios-enrichment-20260915.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=IOS_BASELINE,
        currentDate=IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/ios-games-20260916.json", games)
    save("data/ios-enrichment-20260916.json", enrichment)
    save("data/ios-trends-20260916.json", trends)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    save("assets/ios-manifest.json", manifest)

    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(
        ZoneInfo("Asia/Shanghai")
    ).date().isoformat()
    save(
        "data/history/ios/2026-09-16.json",
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
    ios_source_date = datetime.fromisoformat(ios_updated.replace("Z", "+00:00")).astimezone(
        ZoneInfo("Asia/Shanghai")
    ).date().isoformat()
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
