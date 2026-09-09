#!/usr/bin/env python3
"""Build the Beijing 2026-09-09 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_ios, save, trend
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-09-09"
GOOGLE_DATE = "2026-09-09"
GOOGLE_BASELINE = "2026-06-11"
IOS_DATE = "2026-09-09"
IOS_BASELINE = "2026-06-11"

GOOGLE_HISTORY = [
    (f"data/games-{date}.json", f"data/enrichment-{date}.json", f"data/trends-{date}.json")
    for date in (
        "20260908", "20260907", "20260904", "20260903", "20260902", "20260901",
        "20260831", "20260828", "20260827", "20260826", "20260825", "20260824",
        "20260821", "20260820", "20260819d",
    )
]
IOS_HISTORY = [
    (f"data/ios-games-{date}.json", f"data/ios-enrichment-{date}.json", f"data/ios-trends-{date}.json")
    for date in (
        "20260908", "20260907", "20260904", "20260903", "20260902", "20260901",
        "20260831", "20260828", "20260827", "20260826", "20260825", "20260824",
        "20260821", "20260820", "20260819",
    )
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


def rise_of_castles_profile(row, metadata, asset_rank):
    """Build the iOS record from Apple metadata and IM30-owned sources."""
    description = metadata.get("description", "")
    release = str(metadata.get("releaseDate", ""))[:10]
    updated = str(metadata.get("currentVersionReleaseDate", ""))[:10]
    icon = metadata.get("artworkUrl512") or metadata.get("artworkUrl100")
    screenshot = (metadata.get("screenshotUrls") or metadata.get("ipadScreenshotUrls") or [icon])[0]
    game = {
        "rank": row["rank"],
        "appId": row["appId"],
        "packageName": row["appId"],
        "gameName": row["gameName"],
        "developer": metadata.get("sellerName") or row["developer"],
        "totalInstalls": "",
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "storeUrl": f"https://apps.apple.com/us/app/id{row['appId']}",
        "iconUrl": icon,
        "screenshotUrl": screenshot,
        "shortDescription": description[:180],
        "description": description,
        "releaseDate": release,
        "releaseDateIso": release,
        "updatedDate": updated,
        "genre": "SLG / 实时4X / 城建战争",
        "keywords": "中世纪；城堡重建；国家战争；实时行军；英雄招募；兵种克制；联盟跨服",
        "note": "",
        "assetRank": asset_rank,
        "store": "ios",
    }
    company = {
        "en": "LONG TECH NETWORK LIMITED / IM30",
        "cn": "Long Tech Network Limited（海外发行）/ 北京龙创悦动（IM30）",
        "confidence": "已确认",
        "basis": "Apple美国区商品页列出LONG TECH NETWORK LIMITED，并将开发者网站及隐私政策指向IM30；IM30官方About页面说明其北京团队及Long Tech Network Limited产品体系。",
        "source": "https://www.im30.net/about.html",
    }
    analysis = trend(
        "趋势：2018年上线后，以中世纪城堡重建、国家战争和联盟跨服形成长线4X循环，目前由老服联盟、英雄养成与持续活动支撑；关键转折：产品从Rise of Empires品牌逐步转为Rise of Castles，当前版本刚于9月7日更新，但更新说明仅确认优化和修复，不能据此解释本次回榜；主力素材：受损城镇重建、农耕采集、城堡扩张、英雄与兵种克制、世界地图和联盟战争。",
        "2018年iOS上线后，产品从受损小镇重建切入，连接自由城建、科技研究、英雄招募、步骑弓兵种克制和实时国家战争；成熟期主要由联盟跨服、长期城堡养成和核心SLG用户支撑。当前商店仍强调‘One World, One Server’和国家对抗，而非轻度副玩法获量。",
        "本次回到iOS美国策略畅销榜第59名；Google Play同产品当前未进入TOP60。iOS上架日期为2018年10月20日，早于90天窗口，因此属于成熟产品日榜回归，不是近三个月新上榜。",
        "可确认的长期变化是同一产品从Rise of Empires命名逐步切换至Rise of Castles，并持续强化城堡经营、英雄和联盟战争。Apple显示26.805.1版于2026年9月7日更新，但公开说明只有性能优化和问题修复；本次回榜原因仍待验证，未发现可确认的近期重大转折。",
        "Apple当前商店图突出从受损城镇起步、农耕与资源采集、城堡设施扩张、英雄/军团成长和世界版图战争；主力是成熟SLG的城建—养成—联盟战争链路，单一商店证据下素材判断可信度为中。",
        "观察未来2—3个工作日能否脱离#59榜尾，并核对9月7日版本后的活动日历；若迅速掉榜，只记录为成熟产品短期回榜，不把版本时间重合写成确定因果。",
        game["storeUrl"],
        [
            {"label": "Apple美国区商品页与当前商店图", "url": game["storeUrl"], "type": "primary"},
            {"label": "IM30官方About页面", "url": "https://www.im30.net/about.html", "type": "company-research"},
            {"label": "IM30官方隐私政策", "url": "https://www.im30.net/privacy.html", "type": "company-research"},
            {"label": "Google Play同产品商品页", "url": "https://play.google.com/store/apps/details?id=com.im30.ROE.gp&hl=en_US&gl=US", "type": "lifecycle-analysis"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="上架日期、当前版本、玩法描述与素材来自Apple美国区商品页；同产品Google Play页面及IM30官方站用于交叉确认产品体系。",
        changeReason="首次进入项目iOS榜，独立建立Apple上架日期、本地素材、公司归属和生命周期档案；未借用Google上架日期。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2018年iOS上线、品牌命名迁移梳理到当前成熟联盟运营阶段。",
        evidenceNote="玩法、发行关系和当前版本有官方依据；公开版本说明未披露活动内容，因此不把本次回榜归因于更新。",
    )
    return game, company, analysis


def build_google(rows, source_info):
    current = records("data/games-20260908.json", "data/enrichment-20260908.json", "data/trends-20260908.json", "packageName")
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

    enrichment = deepcopy(load("data/enrichment-20260908.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260909.json", games)
    save("data/enrichment-20260909.json", enrichment)
    save("data/trends-20260909.json", trends)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    save("assets/manifest.json", manifest)
    cross_check = audit_google(rows)
    save(
        "data/history/google-play/2026-09-09.json",
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
    current = records("data/ios-games-20260908.json", "data/ios-enrichment-20260908.json", "data/ios-trends-20260908.json", "appId")
    historical = merged_records(IOS_HISTORY, "appId")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    games, companies, trends, bundle = [], {}, {}, {}
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id in historical:
            game, company, analysis = map(deepcopy, current.get(app_id, historical[app_id]))
        elif app_id == "1411917616":
            metadata = lookup([app_id])[app_id]
            if str(metadata.get("releaseDate", ""))[:10] != "2018-10-20":
                raise RuntimeError(f"Rise of Castles iOS release date missing or changed: {metadata.get('releaseDate')}")
            game, company, analysis = rise_of_castles_profile(row, metadata, 89)
            bundle["89_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle["89_store"] = data_uri(game["screenshotUrl"], (720, 720))
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

    enrichment = deepcopy(load("data/ios-enrichment-20260908.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260909.json", games)
    save("data/ios-enrichment-20260909.json", enrichment)
    save("data/ios-trends-20260909.json", trends)
    if bundle:
        save("assets/ios-assets-17.json", bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if bundle and "ios-assets-17.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-17.json")
    save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save(
        "data/history/ios/2026-09-09.json",
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
