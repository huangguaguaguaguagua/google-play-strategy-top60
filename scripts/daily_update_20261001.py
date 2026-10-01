#!/usr/bin/env python3
"""Build the Beijing 2026-10-01 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import daily_update_20260930 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend


updater = prior.updater
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-01"
updater.STAMP = "20261001"
updater.PREVIOUS_STAMP = "20260930"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-03"
updater.GOOGLE_DATES = ("20260930",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20260930",) + updater.IOS_DATES


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20260930.json",
        "data/enrichment-20260930.json",
        "data/trends-20260930.json",
        "packageName",
    )
    historical = updater.merged_records(updater.history_specs("", updater.GOOGLE_DATES), "packageName")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    games, companies, analyses = [], {}, {}

    for row in rows:
        package, rank = row["packageName"], row["rank"]
        if package in current:
            game, company, analysis = map(deepcopy, current[package])
        elif package in historical:
            game, company, analysis = map(deepcopy, historical[package])
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
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/enrichment-20260930.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261001.json", games)
    updater.save("data/enrichment-20261001.json", enrichment)
    updater.save("data/trends-20261001.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-01.json", {
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


def _war_machines_ios(row, meta):
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
    screenshot = screenshots[0] if screenshots else icon
    release = (meta.get("releaseDate") or "")[:10]
    if release != "2016-11-16":
        raise RuntimeError(f"War Machines iOS release date requires review: {release!r}")
    game = {
        "rank": row["rank"],
        "appId": row["appId"],
        "packageName": row["appId"],
        "gameName": row["gameName"],
        "developer": row["developer"],
        "totalInstalls": "",
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "storeUrl": f"https://apps.apple.com/us/app/id{row['appId']}",
        "iconUrl": icon,
        "rankIconUrl": icon,
        "screenshotUrl": screenshot,
        "shortDescription": (meta.get("description") or "").replace("\n", " ")[:220],
        "description": meta.get("description", ""),
        "releaseDate": release,
        "releaseDateIso": release,
        "updatedDate": (meta.get("currentVersionReleaseDate") or "")[:10],
        "genre": "坦克竞技 / 实时PvP / 载具养成",
        "keywords": "坦克；实时PvP；三分钟战斗；小队；升级部件；全球排行；第三人称射击；联盟",
        "note": "Apple Lookup显示iOS美国区于2016-11-16上架；90天状态只使用本商店日期。",
        "assetRank": 99,
        "store": "ios",
    }
    company = {
        "en": "Wildlife Studios, Inc. / Wildlife Studios",
        "cn": "Wildlife Studios（巴西移动游戏公司；美国区seller为Wildlife Studios, Inc.）",
        "confidence": "已确认",
        "basis": "Apple美国区Lookup列Wildlife Studios, Inc.为seller、Wildlife Studios为发行名；Wildlife官网与招聘页把War Machines列入自有游戏组合。",
        "source": "https://wildlifestudios.com/",
    }
    analysis = trend(
        "趋势：2016年上线后以短局实时坦克对战、载具升级与全球排行榜长期运营，本次首次进入项目保存的iOS榜#57；关键转折：9月29日8.74.2版本仅披露修复与性能优化，未发现可确认的重大转折；主力素材：第三人称坦克瞄准、城市与荒漠战场、装甲火力升级、小队协同和世界排行。",
        "iOS美国区于2016年11月上架，核心是短局第三人称坦克PvP：玩家驾驶并升级火炮、装甲与引擎，加入小队参与全球匹配和排行榜。产品已属长线成熟运营，本次回到分类榜不代表重新首发。",
        "本次首次进入项目自8月19日起保存的iOS美国策略畅销TOP60，位列第57名；产品上架远早于90天窗口且缺少2026年7月3日同口径基准，因此内部状态为pending、页面按常规在榜展示。Google策略TOP60本期未收录。",
        "可确认节点是2016年上架及2026年9月29日8.74.2版本；本次版本说明只有缺陷修复和性能优化，未发现可确认的重大内容或商业化转折。",
        "Apple商店图以坦克瞄准射击、城市与荒漠战场、战车编队和部件升级为主；当前主要依靠成熟PvP核心用户、小队与排行榜循环。素材判断仅基于Apple商品页，可信度为中。",
        "观察未来1—2个有效快照能否留在iOS TOP60，以及后续是否出现可核验的活动或内容更新；没有证据前不把本次#57归因于特定运营事件。",
        game["storeUrl"],
        [
            {"label": "Wildlife Studios官网", "url": "https://wildlifestudios.com/", "type": "company-audit"},
            {"label": "Wildlife Studios招聘页（游戏组合）", "url": "https://careers.wildlifestudios.com/", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-01",
        status="已复核",
        confidence="中",
        basis="上架日、版本说明、玩法与当前素材来自Apple美国区商品页；Wildlife官网和招聘页用于核对发行主体与自有产品组合。",
        changeReason="首次进入项目保存的iOS榜，按Apple Lookup建立独立商店档案，未借用Google日期或安装量。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-01",
        status="已复核",
        confidence="中",
        scope="从2016年iOS上架梳理到2026年9月29日维护版本与本次首次进入项目保存的TOP60。",
        evidenceNote="没有公开收入或投放数据，也未发现与本次入榜同日对应的重大内容节点；按成熟期榜尾待验证信号处理。",
    )
    return game, company, analysis, icon, screenshot


def build_ios_today(rows, source_url, source_updated):
    current = updater.records(
        "data/ios-games-20260930.json",
        "data/ios-enrichment-20260930.json",
        "data/ios-trends-20260930.json",
        "appId",
    )
    historical = updater.merged_records(updater.history_specs("ios-", updater.IOS_DATES), "appId")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in current and row["appId"] not in historical]
    metadata = lookup(entrant_ids)
    games, companies, analyses, bundle = [], {}, {}, {}

    for row in rows:
        app_id, rank = row["appId"], row["rank"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        elif app_id in historical:
            game, company, analysis = map(deepcopy, historical[app_id])
        elif app_id == "1058528141":
            game, company, analysis, icon, screenshot = _war_machines_ios(row, metadata[app_id])
            bundle["99_icon"] = data_uri(icon, (256, 256))
            bundle["99_store"] = data_uri(screenshot, (720, 720))
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
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/ios-enrichment-20260930.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261001.json", games)
    updater.save("data/ios-enrichment-20261001.json", enrichment)
    updater.save("data/ios-trends-20261001.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if bundle:
        updater.save("assets/ios-assets-27.json", bundle)
        if "ios-assets-27.json" not in manifest["files"]:
            manifest["files"].append("ios-assets-27.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-01.json", {
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
