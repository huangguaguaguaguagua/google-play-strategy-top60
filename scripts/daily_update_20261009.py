#!/usr/bin/env python3
"""Build the Beijing 2026-10-09 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import daily_update_20261008 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, trend
from daily_update_20260821 import play_metadata


updater = prior.updater
enforce_required_product_language = prior.enforce_required_product_language
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-09"
updater.STAMP = "20261009"
updater.PREVIOUS_STAMP = "20261008"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-11"
updater.GOOGLE_DATES = ("20261008",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261008",) + updater.IOS_DATES


def _auto_drill_google(row):
    """Build Auto Drill from official US store pages and Lava Labs sources."""
    metadata = play_metadata(row["packageName"])
    release = metadata.get("released") or ""
    if release != "2026-06-24":
        raise RuntimeError(f"Auto Drill Google released date requires review: {release!r}")
    game = {
        "rank": row["rank"],
        "packageName": row["packageName"],
        "gameName": row["gameName"],
        "developer": row.get("developer") or metadata.get("developer", "LAVA LABS OYUN YAZILIM VE PAZARLAMA ANONIM SIRKETI"),
        "genre": "放置策略 / 自动战斗 / Roguelite",
        "keywords": "自动钻探；行星方块；飞船；手动摇杆；自动战斗；连锁爆炸；十种武器；技能融合；装备升级；无限区域",
        "totalInstalls": metadata.get("downloads", ""),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"],
        "store": "googlePlay",
        "storeUrl": metadata["url"],
        "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"],
        "shortDescription": metadata.get("description", ""),
        "description": (
            "驾驶自动钻探飞船逐块击穿行星，或用摇杆手动控制；通过连锁爆炸、十种武器、"
            "技能融合与装备升级推进无限区域。"
        ),
        "releaseDate": release,
        "releaseDateIso": release,
        "updatedDate": metadata.get("updated", ""),
        "note": "Google美国区商品页序列化released为2026-06-24；90天状态只使用本商店日期。",
        "assetRank": 83,
    }
    company = {
        "en": "Lava Labs / LAVA LABS OYUN YAZILIM VE PAZARLAMA A.S.",
        "cn": "Lava Labs（土耳其法律主体；未发现已确认的更上层集团）",
        "confidence": "已确认",
        "basis": "Google Play美国区与Apple官方商品页列出同一LAVA LABS法律主体；Lava Labs官网确认品牌与工作室对应，公开资料未披露更上层集团。",
        "source": "https://lava.gs/",
    }
    analysis = trend(
        "趋势：2026年6月以自动钻探飞船、手动摇杆和逐块击穿行星上线，把即时破坏反馈承接到十种武器、技能融合、装备升级与无限区域，本次首次进入项目Google #60；关键转折：10月2日版本仅披露错误修复和性能改善，未发现可确认的重大玩法转折，仍处首发验证；主力素材：飞船切入方块行星、连锁爆炸、武器弹幕、技能三选一/融合、装备升级与区域推进。",
        "Google美国区于2026年6月24日上架。首层可以自动驾驶，也可用摇杆操控飞船切入行星方块，以破坏、掉落与连锁爆炸建立短循环；中层由十种武器、技能融合和装备升级承接，长期目标是持续推进无限区域。产品尚处上线后不足四个月的首发验证，但上架日早于本期90天窗口。",
        "本次首次进入项目自2026年8月19日起保存的Google Play美国策略畅销TOP60，位列第60名；上架早于2026年7月11日窗口，且缺少精确90天同口径基准，内部状态为pending、页面按常规在榜展示。",
        "10月2日商品页更新只说明错误修复和性能改善，没有公开大型活动、系统重构或商业化变化；从首发到当前未发现可确认的重大转折，本次末位入榜只记为待验证信号。",
        "Google当前商店图以飞船钻入方块行星、连锁爆炸、不同武器弹幕、技能选取和装备升级为主；素材结论主要来自单一商店，可信度为中。",
        "观察未来1—2个有效快照能否连续留榜并脱离#60；没有连续榜位或公开运营节点前，不把首次入榜推断为长期增长。",
        metadata["url"],
        [
            {"label": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6747007384", "type": "primary"},
            {"label": "Lava Labs官网", "url": "https://lava.gs/", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-09",
        status="已复核",
        confidence="中",
        basis="上架日、核心玩法、图标和商店图来自Google Play美国区商品页；Apple官方页交叉法律主体与玩法；公司链由Lava Labs官网核验。当前素材主要来自单一商店，不标高可信度。",
        changeReason="首次进入项目Google榜，按Google US released建立独立档案；未将修复版本与末位入榜写成确定因果。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-09",
        status="已复核",
        confidence="中",
        scope="从2026年6月Google上架梳理到10月2日修复版本与本次首次进入项目TOP60。",
        evidenceNote="商品页支持首发玩法与当前素材；未发现可确认的重大转折或公开收入、投放数据，按仍处首发验证处理。",
    )
    return game, company, analysis, metadata


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20261008.json",
        "data/enrichment-20261008.json",
        "data/trends-20261008.json",
        "packageName",
    )
    historical = updater.merged_records(updater.history_specs("", updater.GOOGLE_DATES), "packageName")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    games, companies, analyses, bundle = [], {}, {}, {}

    for row in rows:
        package, rank = row["packageName"], row["rank"]
        if package in current:
            game, company, analysis = map(deepcopy, current[package])
        elif package in historical:
            game, company, analysis = map(deepcopy, historical[package])
        elif package == "com.lavalabs.autodrill":
            game, company, analysis, metadata = _auto_drill_google(row)
            bundle["83_icon"] = data_uri(metadata["icon"], (256, 256))
            bundle["83_store"] = data_uri(metadata["screenshot"], (720, 720))
        else:
            raise RuntimeError(f"Unexpected Google entrant: {row}")

        change = delta_label(old_rank.get(package), rank)
        comp = comparison(None, rank, updater.GOOGLE_DATE, updater.GOOGLE_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row.get("developer", game.get("developer", "")),
            store="googlePlay",
            storeUrl=row["storeUrl"],
            iconUrl=row["iconUrl"],
            rankIconUrl=row["iconUrl"],
            screenshotUrl=row["screenshotUrl"],
            totalInstalls=str(row.get("downloads") or game.get("totalInstalls") or "").replace("+", " +"),
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = updater.refresh_daily_rank_path(
            updater.clean_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/enrichment-20261008.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261009.json", games)
    updater.save("data/enrichment-20261009.json", enrichment)
    updater.save("data/trends-20261009.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    if bundle:
        updater.save("assets/assets-20.json", bundle)
        if "assets-20.json" not in manifest["files"]:
            manifest["files"].append("assets-20.json")
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-09.json", {
        "store": "google-play",
        "country": "US",
        "category": "Games > Strategy > Top Grossing",
        "date": updater.GOOGLE_DATE,
        "dataDate": updater.GOOGLE_DATE,
        "sourceCapturedAt": source["capturedAt"],
        "sourceUrl": source["sourceUrl"],
        "sourceEndpoint": source["sourceEndpoint"],
        "sourceMethod": source["sourceMethod"],
        "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。",
        "crossCheck": audit,
        "rankings": [
            {"rank": game["rank"], "packageName": game["packageName"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]}
            for game in games
        ],
    })
    return games, audit


def build_ios_today(rows, source_url, source_updated):
    current = updater.records(
        "data/ios-games-20261008.json",
        "data/ios-enrichment-20261008.json",
        "data/ios-trends-20261008.json",
        "appId",
    )
    historical = updater.merged_records(updater.history_specs("ios-", updater.IOS_DATES), "appId")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    games, companies, analyses = [], {}, {}

    for row in rows:
        app_id, rank = row["appId"], row["rank"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        elif app_id in historical:
            game, company, analysis = map(deepcopy, historical[app_id])
        else:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")

        change = delta_label(old_rank.get(app_id), rank)
        comp = comparison(None, rank, updater.IOS_DATE, updater.IOS_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row["developer"],
            store="ios",
            storeUrl=f"https://apps.apple.com/us/app/id{app_id}",
            totalInstalls="",
            recentInstalls30d="",
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = updater.refresh_daily_rank_path(
            updater.clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261008.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261009.json", games)
    updater.save("data/ios-enrichment-20261009.json", enrichment)
    updater.save("data/ios-trends-20261009.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-09.json", {
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


updater.build_google = build_google_today
updater.build_ios = build_ios_today


if __name__ == "__main__":
    updater.main()
