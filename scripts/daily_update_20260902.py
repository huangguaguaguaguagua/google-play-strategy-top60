#!/usr/bin/env python3
"""Build the Beijing 2026-09-02 Google Play and Apple App Store snapshots."""
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, parse_ios, save, trend
from daily_update_20260821 import play_metadata
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-09-02"
GOOGLE_DATE = "2026-09-02"
GOOGLE_BASELINE = "2026-06-04"
IOS_DATE = "2026-09-02"
IOS_BASELINE = "2026-06-04"

GOOGLE_HISTORY = [
    (f"data/games-{date}.json", f"data/enrichment-{date}.json", f"data/trends-{date}.json")
    for date in (
        "20260901", "20260831", "20260828", "20260827", "20260826",
        "20260825", "20260824", "20260821", "20260820", "20260819d",
    )
]
IOS_HISTORY = [
    (f"data/ios-games-{date}.json", f"data/ios-enrichment-{date}.json", f"data/ios-trends-{date}.json")
    for date in (
        "20260901", "20260831", "20260828", "20260827", "20260826",
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


def last_shelter_war_z_profile(row, metadata, asset_rank):
    """Create a store-specific profile without asserting an unproven group owner."""
    store_url = metadata["url"]
    description = metadata.get("description", "").replace("â", "").replace("\u200b", "").strip()
    game = {
        "rank": row["rank"],
        "packageName": row["packageName"],
        "gameName": row["gameName"],
        "developer": row.get("developer") or metadata.get("developer", ""),
        "genre": "SLG / 地下庇护所经营 / 末日生存",
        "keywords": "丧尸末日；地下庇护所；房间建设；幸存者营救；隧道探索；英雄编队；联盟战争；废土",
        "totalInstalls": metadata.get("downloads", ""),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata.get("icon") or row["iconUrl"],
        "storeUrl": store_url,
        "iconUrl": metadata.get("icon") or row["iconUrl"],
        "screenshotUrl": metadata.get("screenshot") or row["screenshotUrl"],
        "shortDescription": description,
        "description": description,
        "releaseDate": metadata.get("released", ""),
        "releaseDateIso": metadata.get("released", ""),
        "updatedDate": metadata.get("updated", ""),
        "note": "",
        "assetRank": asset_rank,
        "store": "googlePlay",
    }
    company = {
        "en": "LAST ORIGIN STUDIO LIMITED / suspected LONG TECH NETWORK LIMITED (IM30) product lineage",
        "cn": "LAST ORIGIN STUDIO LIMITED发行；疑似龙创悦动（IM30）产品体系",
        "confidence": "疑似",
        "basis": "Google Play店铺、官方服务条款与隐私政策确认法律发行主体为LAST ORIGIN STUDIO LIMITED；Last Shelter品牌、com.more包名体系与既有产品存在关联线索，但未找到足以确认其与LONG TECH NETWORK LIMITED（IM30）股权关系或最终集团的公开材料，因此仅作疑似产品体系标注。",
        "source": "https://www.lastshelter.net/terms.html",
    }
    analysis = trend(
        "趋势：2026年6月上架后，用末日地下庇护所切面、营救幸存者和僵尸压力作为首发获量入口，再承接房间建设、隧道探索、英雄编队与联盟战争，目前仍处首发验证；关键转折：8月26日版本补入联盟玩法与Doomsday Transport，本次首次进入Google美国策略畅销TOP60，但尚不能确认由版本直接驱动；主力素材：地下庇护所剖面、救援抉择、僵尸追击、房间扩建、英雄小队和废土探索。",
        "2026年6月24日上架后，以地下庇护所剖面和营救幸存者建立末日压力入口，随后把玩家带入房间建设、研究与控制中心升级，再延伸到隧道/废土探索、英雄编队和联盟协作。产品上线时间较短，目前仍处首发验证。",
        "本次首次进入Google Play美国策略畅销榜第60名；按Google Play美国区商品页上架日期计算属于近三个月新上榜。iOS存在同名商品，但未进入美国iPhone策略畅销TOP60。",
        "Google Play商品页显示8月26日更新增加联盟玩法与Doomsday Transport；更新时间与本次进榜接近，但现有证据只能确认时间重合，不能把榜位直接归因于该版本。",
        "当前商店图重点展示地下庇护所剖面、僵尸追击与救援抉择，并补充房间扩建、英雄小队和废土探索。素材证据主要来自单一商店及官方商品页，可信度为中。",
        "观察未来2—3个工作日能否守住TOP60，以及iOS是否出现同步收入信号；若快速掉榜，优先按榜尾首发买量或版本短峰处理，不预判长期走势。",
        store_url,
        [
            {"label": "Last Shelter官方服务条款", "url": "https://www.lastshelter.net/terms.html", "type": "company-research"},
            {"label": "Last Shelter官方隐私政策", "url": "https://www.lastshelter.net/en/privacy.html", "type": "company-research"},
            {"label": "IM30官方既有Last Shelter产品页", "url": "https://www.im30.net/en/games/83/", "type": "company-inference"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="核心玩法与版本节点来自Google Play美国区商品页；素材结合当前商店图逐项核对，只有单一商店证据，不标高可信度。",
        changeReason="首次进入项目Google榜，按商品页上架日期建立生命周期和素材档案；版本与榜位仅写时间相关性。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2026年6月上架期梳理庇护所获量层、经营/探索承接与联盟版本节点。",
        evidenceNote="商品页可确认上架日期、玩法与8月26日版本说明；尚无足够长期榜位与跨商店证据。",
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
    current = records("data/games-20260901.json", "data/enrichment-20260901.json", "data/trends-20260901.json", "packageName")
    historical = merged_records(GOOGLE_HISTORY, "packageName")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    games, companies, trends, bundle = [], {}, {}, {}
    for row in rows:
        rank, package = row["rank"], row["packageName"]
        if package in current or package in historical:
            game, company, analysis = map(deepcopy, current.get(package, historical[package]))
        elif package == "com.more.lastshelter.gp":
            metadata = play_metadata(package)
            if metadata.get("released") != "2026-06-24":
                raise RuntimeError(f"Last Shelter: War Z release date missing or changed: {metadata.get('released')}")
            game, company, analysis = last_shelter_war_z_profile(row, metadata, 71)
            bundle["71_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle["71_store"] = data_uri(game["screenshotUrl"], (720, 720))
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
    enrichment = deepcopy(load("data/enrichment-20260901.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260902.json", games)
    save("data/enrichment-20260902.json", enrichment)
    save("data/trends-20260902.json", trends)
    if bundle:
        save("assets/assets-10.json", bundle)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    if bundle and "assets-10.json" not in manifest["files"]:
        manifest["files"].append("assets-10.json")
    save("assets/manifest.json", manifest)
    cross_check = audit_google(rows)
    save(
        "data/history/google-play/2026-09-02.json",
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
    current = records("data/ios-games-20260901.json", "data/ios-enrichment-20260901.json", "data/ios-trends-20260901.json", "appId")
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
    enrichment = deepcopy(load("data/ios-enrichment-20260901.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260902.json", games)
    save("data/ios-enrichment-20260902.json", enrichment)
    save("data/ios-trends-20260902.json", trends)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save(
        "data/history/ios/2026-09-02.json",
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
