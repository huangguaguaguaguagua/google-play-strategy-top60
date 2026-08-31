#!/usr/bin/env python3
"""Build the Beijing 2026-08-31 Google Play and Apple App Store snapshots."""
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_ios, save, trend
from daily_update_20260825 import add_primary_source, appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-08-31"
GOOGLE_DATE = "2026-08-31"
GOOGLE_BASELINE = "2026-06-02"
IOS_DATE = "2026-08-31"
IOS_BASELINE = "2026-06-02"


GOOGLE_HISTORY = [
    (f"data/games-{date}.json", f"data/enrichment-{date}.json", f"data/trends-{date}.json")
    for date in ("20260828", "20260827", "20260826", "20260825", "20260824", "20260821", "20260820", "20260819d")
]
IOS_HISTORY = [
    (f"data/ios-games-{date}.json", f"data/ios-enrichment-{date}.json", f"data/ios-trends-{date}.json")
    for date in ("20260828", "20260827", "20260826", "20260825", "20260824", "20260821", "20260820", "20260819")
]


def clean_analysis(analysis):
    """Carry the product narrative forward and stamp both audits for this run."""
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


def idle_heroes_profile(meta, asset_rank):
    store_url = "https://apps.apple.com/us/app/id1153461915"
    game = {
        "appId": "1153461915",
        "packageName": "1153461915",
        "store": "ios",
        "assetRank": asset_rank,
        "genre": "放置RPG / 卡牌养成 / 阵容策略",
        "keywords": "离线收益；英雄收集；六人阵容；阵营克制；装备锻造；公会战；竞技场；十周年",
    }
    company = {
        "en": "DHGames Limited / Chengdu Droidhang Network Technology Co., Ltd.",
        "cn": "成都卓杭网络科技股份有限公司（DHGames）",
        "confidence": "已确认",
        "basis": "Apple店铺发行主体为DHGames Limited；DHGames官方产品页列出Idle Heroes，中文官网页脚标明成都卓杭网络科技股份有限公司。",
        "source": "https://www.dhgames.com/cn/index.html",
    }
    analysis = trend(
        "趋势：2016年以离线收益、英雄收集和低操作阵容养成切入全球市场，长期由新英雄、养成层、公会战、竞技场与核心存量用户支撑；关键转折：DHGames官方记录其2018年进入83个国家畅销TOP10；2026年十周年活动以连续登录和回归奖励重新召回老用户，但本次iOS回榜尚无可确认的单一活动因果；主力素材：离线资源累积、英雄升星与阵营组合、技能连锁、公会Boss、竞技场排名、十周年福利和回归奖励。",
        "2016年上线后用离线训练降低重复操作，把付费与长期目标放在英雄抽取、升星、装备、阵营克制和六人阵容。随后加入公会战、Boss、竞技场及多层副本，产品从早期放置入口扩展为长期收集和社交竞争。",
        "本次从榜外进入iOS美国策略畅销榜第53名；上架已远超90天，Google Play当前未进入同口径TOP60。榜位靠近尾部，先记为待验证的iOS侧回榜信号。",
        "DHGames官方发展史记录产品2018年进入83个国家畅销TOP10并在37个国家登顶畅销榜，是从新品到全球长线的可核验转折。2026年十周年活动继续使用登录和回归机制，但未发现足以把本次回榜直接归因于单一版本的证据。",
        "当前商店图以高稀有度英雄、阵营队伍、技能演出和养成界面为主；公开活动补充十周年签到、回归奖励、公会与竞技场竞争。素材判断主要来自Apple商品页和官方资料，可信度为中。",
        "观察未来3个工作日能否守住TOP60，并核验iOS侧是否存在服务器活动、召回投放或新英雄节点；若快速掉榜，按成熟产品短期回补处理。",
        store_url,
        [
            {"label": "DHGames官方Idle Heroes页", "url": "https://ih.dhgames.com/", "type": "primary"},
            {"label": "DHGames官方公司发展史", "url": "https://www.dhgames.cn/en/about.html", "type": "lifecycle-analysis"},
            {"label": "Apple十周年活动页", "url": "https://apps.apple.com/us/app/id1153461915?eventid=6776969369", "type": "lifecycle-analysis"},
            {"label": "成都卓杭中文官网", "url": "https://www.dhgames.com/cn/index.html", "type": "company-research"},
        ],
    )
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshot = (meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or [icon])[0]
    game.update(
        iconUrl=icon,
        screenshotUrl=screenshot,
        rankIconUrl=icon,
        description=meta.get("description", ""),
        shortDescription=meta.get("description", "").replace("\n", " ")[:220],
        releaseDate=(meta.get("releaseDate") or "")[:10],
        releaseDateIso=(meta.get("releaseDate") or "")[:10],
        updatedDate=(meta.get("currentVersionReleaseDate") or "")[:10],
        totalInstalls="",
        recentInstalls30d="",
    )
    return game, company, analysis, icon, screenshot


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
    current = records("data/games-20260828.json", "data/enrichment-20260828.json", "data/trends-20260828.json", "packageName")
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
    enrichment = deepcopy(load("data/enrichment-20260828.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260831.json", games)
    save("data/enrichment-20260831.json", enrichment)
    save("data/trends-20260831.json", trends)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    save("assets/manifest.json", manifest)
    cross_check = audit_google(rows)
    save("data/history/google-play/2026-08-31.json", {
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
    })
    return games, cross_check


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260828.json", "data/ios-enrichment-20260828.json", "data/ios-trends-20260828.json", "appId")
    historical = merged_records(IOS_HISTORY, "appId")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in historical]
    metadata = lookup(entrant_ids) if entrant_ids else {}
    if set(metadata) != set(entrant_ids):
        raise RuntimeError(f"Apple Lookup did not return every new product: {entrant_ids}")
    games, companies, trends, bundle = [], {}, {}, {}
    next_asset = 85
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id in historical:
            game, company, analysis = map(deepcopy, current.get(app_id, historical[app_id]))
        elif app_id == "1153461915":
            game, company, analysis, icon, screenshot = idle_heroes_profile(metadata[app_id], next_asset)
            bundle[f"{next_asset}_icon"] = data_uri(icon, (256, 256))
            bundle[f"{next_asset}_store"] = data_uri(screenshot, (720, 720))
            next_asset += 1
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
        if app_id == "1153461915":
            analysis["sections"]["rankPath"] = (
                "本次从榜外进入iOS美国策略畅销榜第53名；上架已远超90天，Google Play当前未进入同口径TOP60。"
                "榜位靠近尾部，先记为待验证的iOS侧回榜信号。"
            )
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)
    enrichment = deepcopy(load("data/ios-enrichment-20260828.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260831.json", games)
    save("data/ios-enrichment-20260831.json", enrichment)
    save("data/ios-trends-20260831.json", trends)
    if bundle:
        save("assets/ios-assets-14.json", bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if bundle and "ios-assets-14.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-14.json")
    save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save("data/history/ios/2026-08-31.json", {
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
    })
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
