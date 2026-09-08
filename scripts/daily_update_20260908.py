#!/usr/bin/env python3
"""Build the Beijing 2026-09-08 Google Play and Apple App Store snapshots."""
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, parse_ios, save, trend
from daily_update_20260821 import play_metadata
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-09-08"
GOOGLE_DATE = "2026-09-08"
GOOGLE_BASELINE = "2026-06-10"
IOS_DATE = "2026-09-08"
IOS_BASELINE = "2026-06-10"

GOOGLE_HISTORY = [
    (f"data/games-{date}.json", f"data/enrichment-{date}.json", f"data/trends-{date}.json")
    for date in (
        "20260907", "20260904", "20260903", "20260902", "20260901", "20260831", "20260828",
        "20260827", "20260826", "20260825", "20260824", "20260821", "20260820", "20260819d",
    )
]
IOS_HISTORY = [
    (f"data/ios-games-{date}.json", f"data/ios-enrichment-{date}.json", f"data/ios-trends-{date}.json")
    for date in (
        "20260907", "20260904", "20260903", "20260902", "20260901", "20260831", "20260828",
        "20260827", "20260826", "20260825", "20260824", "20260821", "20260820", "20260819",
    )
]


def clean_analysis(analysis):
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


def supremacy_profile(row, metadata, asset_rank):
    """Build a Google-specific record from the US Play page and official product/company sources."""
    release = metadata.get("released", "")
    game = {
        "rank": row["rank"],
        "packageName": row["packageName"],
        "gameName": row["gameName"],
        "developer": metadata.get("developer") or row.get("developer", ""),
        "genre": "大战略 / 实时4X / 现代战争",
        "keywords": "第三次世界大战；真实世界地图；海陆空军；实时行军；100人对局；联盟外交；核武器",
        "totalInstalls": str(metadata.get("downloads") or "").replace("+", " +"),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata.get("icon") or row["iconUrl"],
        "storeUrl": metadata["url"],
        "iconUrl": metadata.get("icon") or row["iconUrl"],
        "screenshotUrl": metadata.get("screenshot") or row["screenshotUrl"],
        "shortDescription": metadata.get("description", ""),
        "description": metadata.get("description", ""),
        "releaseDate": release,
        "releaseDateIso": release,
        "updatedDate": metadata.get("updated", ""),
        "note": "",
        "assetRank": asset_rank,
        "store": "googlePlay",
    }
    company = {
        "en": "Dorado Games / Stillfront Supremacy Ltd / Stillfront Group",
        "cn": "Dorado Games（研发）/ Stillfront Supremacy（发行）/ Stillfront Group",
        "confidence": "已确认",
        "basis": "Google Play美国区商品页列发行主体Stillfront Supremacy Ltd；Dorado Games官方产品页收录Supremacy: World War 3；Stillfront官方确认2014年收购Dorado Games。",
        "source": "https://www.stillfront.com/en/stillfront-group-to-acquire-doradogames/",
    }
    analysis = trend(
        "趋势：2017年浏览器版上线、2020年Android版推出后，以持续数天至数周的现代战争、实时行军和联盟外交服务硬核大战略用户，目前由长期对局、联盟社群与赛季内容支撑；关键转折：从网页端扩展到移动端，并持续简化移动操作与新手入口，未发现可确认的近期重大转折；主力素材：全球领土地图、坦克/航母/战机、实时战线、联盟外交、核导弹与百人长期对局。",
        "产品2017年先以浏览器端Conflict of Nations上线，2020年Android版进入移动端。首局以选择国家、城市经济、科研树和实时海陆空部署建立入口，之后通过长达数天至数周的百人对局、联盟外交与赛季单位维持深度；当前主要依赖长期战局、联盟社群和核心策略用户。",
        "本次进入Google Play美国策略畅销榜第60名；iOS同名产品当前位于第37名。Android上架日期为2020年9月3日，早于90天窗口，因此这是成熟产品日榜回归，不是近三个月新上榜。",
        "可确认的结构变化是从浏览器大战略扩展到Android/iOS，并围绕移动端性能、界面和新手流程持续优化。Google Play显示最近更新为2026年8月25日，但公开版本信息不足以把本次进榜归因于具体活动；未发现可确认的近期重大转折。",
        "Google Play当前商店图突出全球领土推进、现代坦克、潜艇/航母、战机、雷达与导弹覆盖，配合‘真实玩家持续战争’和联盟外交；与iOS商店图口径一致，素材证据可信度为中。",
        "观察未来2—3个工作日Android能否脱离#60榜尾，并对照iOS #37附近是否保持；若Android立即掉榜，按成熟长局产品的短期付费回补处理。",
        metadata["url"],
        [
            {"label": "Dorado Games官方产品页", "url": "https://doradogames.com/games/", "type": "primary"},
            {"label": "Conflict of Nations官方站", "url": "https://www.conflictnations.com/", "type": "primary"},
            {"label": "Stillfront收购Dorado Games公告", "url": "https://www.stillfront.com/en/stillfront-group-to-acquire-doradogames/", "type": "company-research"},
            {"label": "Stillfront确认产品2017年浏览器上线", "url": "https://www.stillfront.com/en/stillfront-conflict-of-nations-launched-on-steam/", "type": "lifecycle-analysis"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="Android上架日期、核心玩法、更新日期与当前素材来自Google Play美国区商品页；产品线和公司关系由Dorado Games及Stillfront官方资料交叉确认。",
        changeReason="首次进入项目Google榜，独立建立Android上架日期、本地素材、公司归属与生命周期档案；未借用iOS上架日期或榜位历史。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2017年浏览器首发、2020年Android上线梳理到当前移动端长线运营。",
        evidenceNote="平台扩展与核心循环有官方依据；近期具体活动缺少公开证据，因此不将本次进榜写成版本或活动因果。",
    )
    return game, company, analysis


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
    current = records("data/games-20260907.json", "data/enrichment-20260907.json", "data/trends-20260907.json", "packageName")
    historical = merged_records(GOOGLE_HISTORY, "packageName")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    games, companies, trends, bundle = [], {}, {}, {}
    for row in rows:
        rank, package = row["rank"], row["packageName"]
        if package in historical:
            game, company, analysis = map(deepcopy, current.get(package, historical[package]))
        elif package == "com.doradogames.conflictnations.worldwar3":
            metadata = play_metadata(package)
            if metadata.get("released") != "2020-09-03":
                raise RuntimeError(f"Supremacy Android release date missing or changed: {metadata.get('released')}")
            game, company, analysis = supremacy_profile(row, metadata, 73)
            bundle["73_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle["73_store"] = data_uri(game["screenshotUrl"], (720, 720))
        else:
            raise RuntimeError(f"Unexpected Google entrant: {row}")
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
    enrichment = deepcopy(load("data/enrichment-20260907.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260908.json", games)
    save("data/enrichment-20260908.json", enrichment)
    save("data/trends-20260908.json", trends)
    if bundle:
        save("assets/assets-12.json", bundle)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    if bundle and "assets-12.json" not in manifest["files"]:
        manifest["files"].append("assets-12.json")
    save("assets/manifest.json", manifest)
    cross_check = audit_google(rows)
    save(
        "data/history/google-play/2026-09-08.json",
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
                {"rank": game["rank"], "packageName": game["packageName"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]}
                for game in games
            ],
        },
    )
    return games, cross_check


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260907.json", "data/ios-enrichment-20260907.json", "data/ios-trends-20260907.json", "appId")
    historical = merged_records(IOS_HISTORY, "appId")
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
    enrichment = deepcopy(load("data/ios-enrichment-20260907.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260908.json", games)
    save("data/ios-enrichment-20260908.json", enrichment)
    save("data/ios-trends-20260908.json", trends)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save(
        "data/history/ios/2026-09-08.json",
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
                {"rank": game["rank"], "appId": game["appId"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]}
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
