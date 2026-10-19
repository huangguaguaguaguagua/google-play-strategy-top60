#!/usr/bin/env python3
"""Build the Beijing 2026-10-19 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
from zoneinfo import ZoneInfo

import daily_update_20261016 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend


updater = prior.updater
base_enforce_required_product_language = prior.enforce_required_product_language
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-19"
updater.STAMP = "20261019"
updater.PREVIOUS_STAMP = "20261016"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-21"
updater.GOOGLE_DATES = ("20261016",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261016",) + updater.IOS_DATES


def enforce_required_product_language(game_name, analysis):
    """Keep required narratives explicit while making daily rewrites idempotent."""
    analysis = base_enforce_required_product_language(game_name, analysis)
    if game_name != "Kingshot":
        return analysis

    def rewrite(value):
        if isinstance(value, dict):
            return {key: rewrite(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rewrite(item) for item in value]
        if isinstance(value, str):
            return re.sub(r"(?:城镇经营、)+居民分工", "城镇经营、居民分工", value)
        return value

    return rewrite(analysis)


def prepare_analysis(analysis):
    """Remove expired 90-day labels before rebuilding the current rank path."""
    analysis = updater.clean_analysis(analysis)
    path = analysis["sections"].get("rankPath", "")
    path = re.sub(
        r"(?:按(?:Google Play|iOS)商品页上架日期[^。；]*?属于近三个月新上榜[。；]?)+",
        "",
        path,
    )
    path = re.sub(r"按上架日期口径属于近三个月新上榜[。；]?", "", path)
    path = re.sub(r"[，；]{2,}", "；", path).strip("，；。 ")
    analysis["sections"]["rankPath"] = path
    return analysis


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20261016.json",
        "data/enrichment-20261016.json",
        "data/trends-20261016.json",
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
            prepare_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/enrichment-20261016.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261019.json", games)
    updater.save("data/enrichment-20261019.json", enrichment)
    updater.save("data/trends-20261019.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-19.json", {
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


def _plants_on_fire(meta):
    app_id = "6776076449"
    store_url = f"https://apps.apple.com/us/app/id{app_id}"
    screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshot = screenshots[0] if screenshots else icon
    description = meta.get("description", "")
    game = {
        "rank": 59,
        "appId": app_id,
        "packageName": app_id,
        "gameName": meta.get("trackName", "Plants on Fire"),
        "developer": meta.get("sellerName", "Shanghai Shenmeng Technology Co., Ltd."),
        "totalInstalls": "",
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "storeUrl": store_url,
        "iconUrl": icon,
        "rankIconUrl": icon,
        "screenshotUrl": screenshot,
        "shortDescription": description.replace("\n", " ")[:220],
        "description": description,
        "releaseDate": (meta.get("releaseDate") or "")[:10],
        "releaseDateIso": (meta.get("releaseDate") or "")[:10],
        "updatedDate": (meta.get("currentVersionReleaseDate") or "")[:10],
        "note": "",
        "assetRank": 102,
        "store": "ios",
        "genre": "合并塔防 / 实时PvP / Auto Chess",
        "keywords": "植物；三分钟对战；合并升级；实时PvP；塔防；Auto Chess；合作；Boss",
    }
    company = {
        "en": "Shanghai Shenmeng Technology Co., Ltd. / Shimmer Dream (Nuverse relationship unconfirmed)",
        "cn": "上海深盟科技（Shimmer Dream；官方站同时列有Nuverse Pte. Ltd.权利标识，具体合作与最终集团归属待确认）",
        "confidence": "疑似",
        "basis": "Apple Lookup与美国区商品页确认店铺法律主体为Shanghai Shenmeng Technology Co., Ltd.，商品页版权名为Shimmer Dream；产品官网同时列出上海深盟与Nuverse Pte. Ltd.权利标识，但未披露双方股权或具体发行关系，因此不把产品直接并入某一最终集团。",
        "source": "https://www.plantsonfire.com/",
    }
    analysis = trend(
        "趋势：2026年8月以三分钟实时PvP、植物合并升级和轻量塔防切入，当前仍处首发验证；关键转折：10月15日版本加入新植物与活动后首次进入iOS美国策略畅销TOP60，尚不能确认长期承接；主力素材：双路实时对抗、同类植物合并、三分钟倒计时、植物组合、Boss与Auto Chess模式。",
        "2026年8月26日在美国iOS上架，以左右对局的三分钟实时PvP为核心：玩家合并植物、即时调整阵容并压制对手，同时用合作、Boss、PvE和Auto Chess拓展短局入口。上线不足两个月，仍处首发验证，尚无成熟期可供比较。",
        "本次首次进入iOS美国策略畅销榜第59名；按Apple Lookup releaseDate位于2026-07-21至2026-10-19的90天窗口内，归类为近三个月新上榜。Google Play同口径本期未进入TOP60。",
        "可确认节点是8月26日美国iOS上架及10月15日版本更新；新植物、变体和活动与首次进榜时间相邻，但没有证据证明它们单独造成榜位变化，未发现可确认的长期运营转折。",
        "商店图以分屏PvP、三分钟倒计时、合并升星、植物队伍与技能组合为主；官网和描述补充Auto Chess、合作、Boss与PvE。当前只有商店/官网一侧素材证据，可信度不标高。",
        "未来1—2个有效快照观察能否脱离榜尾并连续留榜；若快速退出，只记录为首发验证期的一次榜尾信号，不推演后续走势。",
        store_url,
        [{"label": "Plants on Fire官方站", "url": "https://www.plantsonfire.com/", "type": "primary"}],
    )
    return game, company, analysis


def build_ios_today(rows, source_url, source_updated):
    current = updater.records(
        "data/ios-games-20261016.json",
        "data/ios-enrichment-20261016.json",
        "data/ios-trends-20261016.json",
        "appId",
    )
    historical = updater.merged_records(updater.history_specs("ios-", updater.IOS_DATES), "appId")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in current]
    metadata = lookup(entrant_ids)
    games, companies, analyses, bundle = [], {}, {}, {}

    for row in rows:
        app_id, rank = row["appId"], row["rank"]
        is_new_profile = app_id not in current and app_id not in historical
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        elif app_id in historical:
            game, company, analysis = map(deepcopy, historical[app_id])
        elif app_id == "6776076449":
            game, company, analysis = _plants_on_fire(metadata[app_id])
        else:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")

        meta = metadata.get(app_id)
        if meta and app_id == "6776076449":
            icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
            screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
            game.update(
                iconUrl=icon,
                rankIconUrl=icon,
                screenshotUrl=screenshots[0] if screenshots else icon,
                description=meta.get("description", game.get("description", "")),
                shortDescription=meta.get("description", "").replace("\n", " ")[:220],
                releaseDate=(meta.get("releaseDate") or "")[:10],
                releaseDateIso=(meta.get("releaseDate") or "")[:10],
                updatedDate=(meta.get("currentVersionReleaseDate") or "")[:10],
            )
            if is_new_profile:
                game["assetRank"] = 102
                bundle["102_icon"] = data_uri(game["iconUrl"], (256, 256))
                bundle["102_store"] = data_uri(game["screenshotUrl"], (720, 720))

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
            prepare_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261016.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261019.json", games)
    updater.save("data/ios-enrichment-20261019.json", enrichment)
    updater.save("data/ios-trends-20261019.json", analyses)
    if bundle:
        updater.save("assets/ios-assets-29.json", bundle)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if bundle and "ios-assets-29.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-29.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-19.json", {
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


def refresh_plants_on_fire():
    """Update the returning product with the current verified version and rank."""
    games = updater.load("data/ios-games-20261019.json")
    game = next(item for item in games if item["appId"] == "6776076449")
    trends = updater.load("data/ios-trends-20261019.json")
    analysis = trends[str(game["rank"])]
    analysis["summary"] = (
        "趋势：2026年8月以三分钟实时PvP、植物合并升级和轻量塔防切入，9月至10月曾多次进入项目榜单，本期回到iOS #59；"
        "关键转折：10月15日2.0.2870加入Pirate Captain、新植物、四种变体与Ace Plan活动，仍处首发验证；"
        "主力素材：双路实时对抗、三分钟倒计时、同类植物合并、卡组组合、海盗船长、Boss与Auto Chess模式。"
    )
    analysis["sections"] = {
        "development": "2026年8月26日在美国iOS上架，以左右对局的三分钟实时PvP为核心：玩家合并植物、即时调整阵容并压制对手，同时用合作、Boss、PvE和Auto Chess拓展短局入口。上线不足两个月，仍处首发验证。",
        "rankPath": "本次位于iOS美国策略畅销榜第59名（前一有效快照未入榜，回榜）。按Apple商品页上架日期2026-08-26计算，属于近三个月新上榜；Google Play同口径本期未进入TOP60。",
        "turningPoints": "可确认节点是8月26日美国iOS上架及10月15日2.0.2870：Pirate Captain回归，加入Chuckleberry、Thornmelon、四种变体与Ace Plan活动。版本与本次回榜时间相邻，但没有证据证明单一内容造成榜位变化，未发现可确认的长期运营转折。",
        "creative": "商店图以分屏PvP、三分钟倒计时、合并升星、植物队伍与技能组合为主；官网和描述补充Auto Chess、合作、Boss与PvE。当前只有商店与产品官网一侧素材证据，可信度不标高。",
        "watch": "未来1—2个有效快照观察能否脱离榜尾并连续留榜；若快速退出，只记录为首发验证期的一次榜尾回补，不推演后续走势。",
    }
    sources = [
        {"label": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id6776076449", "type": "primary"},
        {"label": "Plants on Fire官方站", "url": "https://www.plantsonfire.com/", "type": "primary"},
    ]
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-19",
        status="已复核",
        confidence="中",
        basis="上架日、2.0.2870版本说明、玩法与当前素材来自Apple美国区商品页；产品官网用于核对Shimmer Dream与Nuverse署名。",
        changeReason="回榜后按Apple Lookup与官网复核；保持独立商店日期，不把版本与榜位时间相邻写成确定因果。",
        sources=sources,
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-19",
        status="已复核",
        confidence="中",
        scope="从2026年8月iOS上架梳理到10月15日2.0.2870及本期榜尾回归。",
        evidenceNote="版本节点与回榜时间相邻，但没有公开收入或投放数据证明因果；仍处首发验证。",
        sources=sources,
    )
    updater.save("data/ios-trends-20261019.json", trends)


if __name__ == "__main__":
    updater.main()
    refresh_plants_on_fire()
