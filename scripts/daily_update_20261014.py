#!/usr/bin/env python3
"""Build the Beijing 2026-10-14 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import daily_update_20261013 as prior
from daily_update_20260820 import comparison, delta_label


updater = prior.updater
enforce_required_product_language = prior.enforce_required_product_language
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-14"
updater.STAMP = "20261014"
updater.PREVIOUS_STAMP = "20261013"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-16"
updater.GOOGLE_DATES = ("20261013",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261013",) + updater.IOS_DATES


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20261013.json",
        "data/enrichment-20261013.json",
        "data/trends-20261013.json",
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
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/enrichment-20261013.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261014.json", games)
    updater.save("data/enrichment-20261014.json", enrichment)
    updater.save("data/trends-20261014.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-14.json", {
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
        "data/ios-games-20261013.json",
        "data/ios-enrichment-20261013.json",
        "data/ios-trends-20261013.json",
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

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261013.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261014.json", games)
    updater.save("data/ios-enrichment-20261014.json", enrichment)
    updater.save("data/ios-trends-20261014.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-14.json", {
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


def apply_verified_event_updates():
    """Refresh the few lifecycle notes changed by newly verified official releases."""

    def update(store, games_path, trends_path, game_name, summary, sections, source):
        games = updater.load(games_path)
        game = next(item for item in games if item["gameName"] == game_name)
        trends = updater.load(trends_path)
        analysis = trends[str(game["rank"])]
        analysis["summary"] = summary
        analysis["sections"].update(sections)
        for audit_name in ("sourceAudit", "lifecycleAudit"):
            audit = analysis[audit_name]
            audit["reviewedAt"] = updater.CAPTURE
            audit["status"] = "已复核"
            if audit.get("confidence") == "高":
                audit["confidence"] = "中"
            sources = audit.setdefault("sources", [])
            if not any(item.get("url") == source["url"] for item in sources):
                sources.append(source)
        analysis["sourceAudit"]["changeReason"] = (
            f"{updater.CAPTURE}按官方版本资料更新产品节点与当前{store}榜位；时间相邻只作背景，不写成确定因果。"
        )
        analysis["lifecycleAudit"]["evidenceNote"] = (
            "当前版本节点来自官方资料；榜位变化来自对应商店相邻有效快照，二者只作时间对照。"
        )
        updater.save(trends_path, trends)

    update(
        "iOS",
        "data/ios-games-20261014.json",
        "data/ios-trends-20261014.json",
        "Hearthstone",
        "趋势：2014年以Warcraft卡牌对战切入，标准轮换、扩展包与酒馆战棋维持多模式长线运营；关键转折：2026年37.0开启Reign of the Black Empire预发布、新竞技场赛季与Journal，iOS单日升至#31但仍待连续验证；主力素材：Old Gods、Assemble关键词、职业构筑、竞技场选牌、酒馆战棋与奖励轨。",
        {
            "rankPath": "本次位于iOS美国策略畅销榜第31名（较前一有效快照上升22位）。37.0于10月13日上线并开启新竞技场赛季，时间与跃升高度重合；只有一个快照，暂按待验证活动峰值记录。",
            "turningPoints": "标准轮换建立稳定卡池节奏，酒馆战棋拓展八人自走棋用户；2026年37.0进一步把Reign of the Black Empire预发布、Assemble关键词、新竞技场卡池、Journal与奖励内容并行，正式资料片排期10月20日。",
            "creative": "Warcraft与Old Gods高认知角色、Assemble自定义随从、职业套牌连锁、竞技场12胜、传奇卡开包、八人酒馆战棋和活动奖励轨。",
            "watch": "观察10月20日资料片正式发布前后能否连续保持iOS前35，并区分预发布峰值、竞技场新赛季和正式扩展包消费。",
        },
        {"label": "Hearthstone 37.0官方补丁说明", "url": "https://hearthstone.blizzard.com/en-us/news/24301454", "type": "lifecycle-analysis"},
    )
    update(
        "iOS",
        "data/ios-games-20261014.json",
        "data/ios-trends-20261014.json",
        "The Tower - Idle Tower Defense",
        "趋势：2021年从极简单塔守波起步，靠永久研究、卡牌和锦标赛社区逐步爬升；关键转折：v29加入全局预设、Mythic联赛、重做Vault与Harmony Tree后，本期iOS +25至#34；主力素材：单塔清屏、指数成长、Boss波次、构筑预设、锦标赛与长期研究。",
        {
            "rankPath": "本次位于iOS美国策略畅销榜第34名（较前一有效快照上升25位），为本端最大上涨。v29于10月6日上线，时间相邻但相隔约一周，仍需下一快照排除一次性峰值。",
            "turningPoints": "实验室研究建立超长期时间线，卡牌与终极武器提升构筑上限，锦标赛增加比较目标；v29再加入Global Presets、Preset Lab、Mythic联赛、重做Vault与Harmony Tree，使成熟期重点从单纯推波扩到多套配置与赛事循环。",
            "creative": "极简几何弹幕、攻击速度暴涨、屏幕清场、Boss压塔、研究前后收益、预设切换、Mythic联赛段位与Vault长期升级。",
            "watch": "未来1—2个有效快照观察能否维持iOS前40；若迅速回到榜尾，则把本次视为v29窗口内的短时峰值。",
        },
        {"label": "Apple App Store美国区v29版本说明", "url": "https://apps.apple.com/us/app/id1575590830", "type": "primary"},
    )

    for store, games_path, trends_path, game_name, rank_text in (
        ("Google Play", "data/games-20261014.json", "data/trends-20261014.json", "Overgeared Hero: Merge RPG", "Google上升5位至#34"),
        ("iOS", "data/ios-games-20261014.json", "data/ios-trends-20261014.json", "Overgeared Hero: Merge RPG", "iOS下跌6位至#54"),
    ):
        update(
            store,
            games_path,
            trends_path,
            game_name,
            f"趋势：2026年以像素背包装备合并、肉鸽短局和自动战斗进入榜单；关键转折：10月13日加入Raven联动皮肤、万圣节传奇皮肤与装备工坊，{rank_text}且双端方向相反；主力素材：像素英雄、背包摆位、装备合成、联动角色、万圣节皮肤与自动战斗。",
            {
                "turningPoints": "首发把背包摆位、同类装备合成和自动战斗连成短循环；10月13日新增Raven联动皮肤、三款万圣节传奇皮肤，以及装备分解和材料兑换的Gear Workshop。该节点已发生，但双端相反方向不支持统一归因。",
                "creative": "像素英雄、背包装备摆放、同类道具合成、肉鸽关卡、Raven联动角色、万圣节传奇皮肤、装备工坊与自动战斗。",
                "watch": "观察未来1—2个有效快照中Google能否守住前40、iOS能否脱离后七名；只有双端或单端连续改善，才判断联动形成承接。",
            },
            {"label": "Apple App Store美国区1.41.0版本说明", "url": "https://apps.apple.com/us/app/id6755585789", "type": "lifecycle-analysis"},
        )


if __name__ == "__main__":
    updater.main()
    apply_verified_event_updates()
