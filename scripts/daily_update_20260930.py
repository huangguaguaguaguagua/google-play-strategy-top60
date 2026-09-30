#!/usr/bin/env python3
"""Build the Beijing 2026-09-30 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import daily_update_20260929 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend


updater = prior.updater
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-09-30"
updater.STAMP = "20260930"
updater.PREVIOUS_STAMP = "20260929"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-02"
updater.GOOGLE_DATES = ("20260929",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20260929",) + updater.IOS_DATES


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20260929.json",
        "data/enrichment-20260929.json",
        "data/trends-20260929.json",
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

    enrichment = deepcopy(updater.load("data/enrichment-20260929.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20260930.json", games)
    updater.save("data/enrichment-20260930.json", enrichment)
    updater.save("data/trends-20260930.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-09-30.json", {
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


def _plants_on_fire_ios(row, meta):
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
    screenshot = screenshots[0] if screenshots else icon
    release = (meta.get("releaseDate") or "")[:10]
    if release != "2026-08-26":
        raise RuntimeError(f"Plants on Fire iOS release date requires review: {release!r}")
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
        "genre": "合并塔防 / 三分钟PvP / 卡组策略",
        "keywords": "植物；合并升级；3分钟PvP；塔防；卡组组合；自动棋；合作Boss；赛季",
        "note": "Apple Lookup显示iOS美国区于2026-08-26上架；90天状态只使用本商店日期。",
        "assetRank": 98,
        "store": "ios",
    }
    company = {
        "en": "Shanghai Shenmeng Technology Co., Ltd. / Shimmer Dream / Nuverse",
        "cn": "上海神萌科技（Shimmer Dream；Nuverse/字节跳动游戏发行体系）",
        "confidence": "已确认",
        "basis": "Apple美国区列上海神萌科技为seller，商品版权为Shimmer Dream；产品官网同时署名Shimmer Dream与Nuverse，Nuverse为字节跳动游戏业务品牌。",
        "source": "https://www.plantsonfire.com/",
    }
    analysis = trend(
        "趋势：8月26日iOS美国区上线，以三分钟合并植物、卡组组合和PvP塔防切入，本次随海盗赛季首次进入项目iOS #39；关键转折：9月29日2.0版本带回Pirate Captain、加入Chuckleberry与Thornmelon及四种变体，仍处首发验证；主力素材：萌系植物合并、双路对抗、快速升星、阵容克制、海盗船长与赛季新单位。",
        "iOS美国区于2026年8月26日上架，首发入口是单局约三分钟的PvP塔防：抽取并合并植物、调整站位与卡组协同，同时用自动棋、合作Boss、PvE和Club Point Race承接更长周期。上线不足两个月，仍处首发验证。",
        "本次首次进入项目保存的iOS美国策略畅销TOP60，位列第39名；Apple Lookup releaseDate落在90天窗口内，因此归类为近三个月新上榜。Google同口径本期未进入TOP60。",
        "可确认节点是8月26日iOS上架，以及9月29日Rebel of the Seas赛季与2.0.2810版本：Pirate Captain回归，新增Chuckleberry、Thornmelon、四种变体及Ace Plan活动。除此之外未发现可确认的重大生命周期转折。",
        "Apple商店图以左右对抗战场、植物合并升星、卡组选择和轻量角色为主；当前版本再加入海盗船长、新植物与赛季奖励。判断仅基于Apple商品页和产品官网，可信度为中。",
        "观察未来1—2个有效快照能否留在iOS前45，以及2.0赛季结束后是否仍在榜；没有连续数据前不把首次#39写成长期增长。",
        game["storeUrl"],
        [
            {"label": "Plants on Fire产品官网", "url": "https://www.plantsonfire.com/", "type": "primary"},
            {"label": "Nuverse品牌官网", "url": "https://www.nvsgames.com/", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-09-30",
        status="已复核",
        confidence="中",
        basis="上架日、版本说明、玩法与当前素材来自Apple美国区商品页；产品官网用于核对Shimmer Dream与Nuverse署名。",
        changeReason="首次进入项目iOS榜，按Apple Lookup建立独立商店档案，未借用Google日期或安装量。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-09-30",
        status="已复核",
        confidence="中",
        scope="从2026年8月iOS上架梳理到9月29日海盗赛季与首次进入项目TOP60。",
        evidenceNote="版本节点与首次入榜时间相邻，但没有公开收入或投放数据证明因果；仍处首发验证。",
    )
    return game, company, analysis, icon, screenshot


def build_ios_today(rows, source_url, source_updated):
    current = updater.records(
        "data/ios-games-20260929.json",
        "data/ios-enrichment-20260929.json",
        "data/ios-trends-20260929.json",
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
        elif app_id == "6776076449":
            game, company, analysis, icon, screenshot = _plants_on_fire_ios(row, metadata[app_id])
            bundle["98_icon"] = data_uri(icon, (256, 256))
            bundle["98_store"] = data_uri(screenshot, (720, 720))
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

    enrichment = deepcopy(updater.load("data/ios-enrichment-20260929.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20260930.json", games)
    updater.save("data/ios-enrichment-20260930.json", enrichment)
    updater.save("data/ios-trends-20260930.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if bundle:
        updater.save("assets/ios-assets-26.json", bundle)
        if "ios-assets-26.json" not in manifest["files"]:
            manifest["files"].append("ios-assets-26.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-09-30.json", {
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
