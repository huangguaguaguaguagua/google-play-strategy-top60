#!/usr/bin/env python3
"""Build the Beijing 2026-09-28 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import daily_update_20260925 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend
from daily_update_20260821 import play_metadata


updater = prior.updater
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-09-28"
updater.STAMP = "20260928"
updater.PREVIOUS_STAMP = "20260925"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-06-30"
updater.GOOGLE_DATES = ("20260925",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20260925",) + updater.IOS_DATES


def _kingdom_rush_google(row):
    """Create a Google-specific profile without borrowing Apple's release date."""
    metadata = play_metadata(row["packageName"])
    if metadata["released"] != "2026-09-16":
        raise RuntimeError(f"Kingdom Rush 6 Google released date requires review: {metadata['released']!r}")
    game = {
        "rank": row["rank"],
        "packageName": row["packageName"],
        "gameName": row["gameName"],
        "developer": row.get("developer") or metadata["developer"],
        "totalInstalls": metadata["downloads"],
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"],
        "storeUrl": metadata["url"],
        "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"],
        "shortDescription": metadata["description"],
        "description": (
            "Kingdom Rush经典塔防系列前传：在Linirea早期组合弓箭、法师、兵营与火炮等15座塔，"
            "每局携带两名英雄和法术，跨18个战役关卡阻挡40余种敌人与6个Boss，并支持离线游玩。"
        ),
        "releaseDate": metadata["released"],
        "releaseDateIso": metadata["released"],
        "updatedDate": metadata["updated"],
        "assetRank": 80,
        "genre": "塔防 / 战术布阵 / 单机策略",
        "keywords": "Kingdom Rush；经典塔防；Linirea；前传；15座塔；双英雄；法术；离线",
        "note": "Google美国区商品页序列化released为2026-09-16；iOS Lookup为2026-09-24。90天状态严格使用本商店日期。",
        "store": "googlePlay",
    }
    company = {
        "en": "Ironhide Games / Ironhide Game Studio",
        "cn": "Ironhide Game Studio（乌拉圭独立研发发行）",
        "confidence": "已确认",
        "basis": "Google Play店铺主体为Ironhide Games；产品官网和商品页均明确由Ironhide Game Studio研发发行，未发现更上层集团归属披露。",
        "source": "https://www.kingdomrushgenesis.com/",
    }
    analysis = trend(
        "趋势：9月16日Google美国区上架后以Kingdom Rush经典塔防回归、Linirea前传与离线单机承接系列用户，本次首次进入Google #57；关键转折：首发即提供15座塔、双英雄、9种法术与18个手工关卡，仍处首发验证；主力素材：经典四类塔协同、分路怪潮、双英雄技能、Vez'nan前传与Boss破线。",
        "Google美国区于2026年9月16日上架，定位为系列前传：回到Linirea早期，以弓箭、法师、兵营、火炮等15座塔覆盖路线，再由每局两名英雄和9种法术处理高压波次。当前仍在上线初期，只确认首发内容与初始榜位，不推演长期表现。",
        "本次首次进入项目保存的Google Play美国策略畅销TOP60，位列第57名；Google商品页released日期落在90天窗口内，因此归类为近三个月新上榜。iOS已在9月25日进入同口径榜单，但两端上架日期分别保存。",
        "可确认节点是Google商品页9月16日上架、9月24日更新，并一次性开放18个战役关卡、40余种敌人、6个Boss、双英雄与离线模式；尚未发现上线后的系统重构或长期运营转折。",
        "Google商店图集中展示塔位覆盖、不同兵种协同、双英雄同场、法术清屏、密集波次与巨型Boss；系列角色和Vez'nan前传负责IP识别。素材判断基于Google商品页与产品官网，可信度为中。",
        "观察未来1—2个有效快照能否脱离Google后五名，并与iOS首发回落幅度对照；没有连续数据前不把首次#57写成稳定趋势。",
        metadata["url"],
        [{"label": "Kingdom Rush 6: Genesis官网", "url": "https://www.kingdomrushgenesis.com/", "type": "primary"}],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-09-28",
        confidence="中",
        basis="上架日期、玩法与素材来自Google美国区商品页；研发发行由产品官网交叉确认。",
        changeReason="首次进入项目Google榜，按Google US released建立独立商店档案，未借用Apple上架日期。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-09-28",
        status="已复核",
        confidence="中",
        scope="从2026年9月Google上架梳理到首次进入本项目TOP60。",
        evidenceNote="上线时间短，仍处首发验证；没有公开收入或买量数据证明榜位变化因果。",
    )
    return game, company, analysis, metadata


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20260925.json",
        "data/enrichment-20260925.json",
        "data/trends-20260925.json",
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
        elif package == "com.ironhidegames.android.kingdomrush6.genesis":
            game, company, analysis, metadata = _kingdom_rush_google(row)
            bundle["80_icon"] = data_uri(metadata["icon"], (256, 256))
            bundle["80_store"] = data_uri(metadata["screenshot"], (720, 720))
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

    enrichment = deepcopy(updater.load("data/enrichment-20260925.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20260928.json", games)
    updater.save("data/enrichment-20260928.json", enrichment)
    updater.save("data/trends-20260928.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    if bundle:
        updater.save("assets/assets-17.json", bundle)
        if "assets-17.json" not in manifest["files"]:
            manifest["files"].append("assets-17.json")
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-09-28.json", {
        "store": "google-play",
        "country": "US",
        "category": "Games > Strategy > Top Grossing",
        "date": "2026-09-28",
        "dataDate": "2026-09-28",
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


def _sea_of_conquest_ios(row, meta):
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
    screenshot = screenshots[0] if screenshots else icon
    release = (meta.get("releaseDate") or "")[:10]
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
        "genre": "海战SLG / 舰队经营 / RPG",
        "keywords": "海盗；舰队；船舱建设；英雄编队；海洋探索；港口；联盟海战",
        "note": "Apple Lookup显示iOS美国区于2024-01-03上架；90天状态只使用本商店日期。",
        "assetRank": 97,
        "store": "ios",
    }
    if release != "2024-01-03":
        raise RuntimeError(f"Sea of Conquest iOS release date requires review: {release!r}")
    company = {
        "en": "FunPlus International AG / FunPlus",
        "cn": "趣加游戏（FunPlus；FunPlus International AG发行）",
        "confidence": "已确认",
        "basis": "Apple Lookup列明FunPlus International AG为seller；FunPlus官方产品页将Sea of Conquest列入其自研发行产品体系。",
        "source": "https://funplus.com/games/sea-of-conquest/",
    }
    analysis = trend(
        "趋势：2024年以高品质海盗世界、船舱定制和舰队探索上线，成熟期通过英雄收集、港口争夺、联盟海战与跨界活动维持；关键转折：品牌化海洋冒险逐步叠加更直接的危机/选择素材，9月24日版本提醒当前联动即将结束，本次首次进入项目iOS #59；主力素材：海盗船长、舰船改造、船舱经营、海怪冲突与港口联盟战。",
        "iOS美国区于2024年1月3日上架，先用海盗船长、旗舰船舱、航海探索与高品质音画建立中重度入口，再把用户承接到英雄编队、舰船养成、港口争夺和联盟海战。当前已进入成熟长线运营，而非首发验证。",
        "本次首次进入本项目iOS美国策略畅销TOP60，位列第59名；Apple上架日期早于90天窗口，且缺少2026-06-30精确同口径基准，因此内部保持pending、页面按常规展示。Google同口径本期未进入TOP60。",
        "软启动期官方强调AAA海盗模拟、Dolby音画、旗舰船舱和大世界探索；全球发行后公开素材出现鲨鱼、动物危机和怪诞选择等更直接的短视频钩子，再回接舰船、英雄与港口战争。9月24日1.1.800版本仅确认当前联动临近结束，未披露收入或投放变化。",
        "Apple商店图以英雄阵容、船舱升级、旗舰定制、舰炮对战和航海探索为主；成熟期外部创意再叠加海怪、鲨鱼与危机选择。素材判断结合Apple商品页、FunPlus官方软启动资料与公开创意观察，可信度为中。",
        "观察联动结束后的下一个1—2个有效快照能否继续留榜；若迅速退出，只记录为活动末期的榜尾信号，同时继续区分iOS与Google表现。",
        game["storeUrl"],
        [
            {"label": "FunPlus Sea of Conquest产品页", "url": "https://funplus.com/games/sea-of-conquest/", "type": "primary"},
            {"label": "Sea of Conquest软启动定位", "url": "https://funplus.com/sea-of-conquest-the-ultimate-aaa-quality-pirate-mobile-strategy-game/", "type": "lifecycle-analysis"},
            {"label": "Sea of Conquest成熟期创意观察", "url": "https://mobilegamer.biz/ad-break-sea-of-conquests-grim-goat-hooves-shark-shooting-and-booty-tasting/", "type": "lifecycle-analysis"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-09-28",
        confidence="中",
        basis="上架日、版本说明、玩法和当前素材来自Apple美国区商品页；公司归属由FunPlus官方产品页确认。",
        changeReason="首次进入项目iOS榜，建立独立商店档案；未借用Google上架日期或安装量。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-09-28",
        status="已复核",
        confidence="中",
        scope="从2023年软启动、2024年iOS上架梳理到2026年9月联动末期版本。",
        evidenceNote="产品与素材迁移有公开来源；当前榜位与联动结束只记录时间相邻，不写成确定因果。",
    )
    return game, company, analysis, icon, screenshot


def build_ios_today(rows, source_url, source_updated):
    current = updater.records(
        "data/ios-games-20260925.json",
        "data/ios-enrichment-20260925.json",
        "data/ios-trends-20260925.json",
        "appId",
    )
    historical = updater.merged_records(updater.history_specs("ios-", updater.IOS_DATES), "appId")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    games, companies, analyses, bundle = [], {}, {}, {}
    for row in rows:
        app_id, rank = row["appId"], row["rank"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        elif app_id in historical:
            game, company, analysis = map(deepcopy, historical[app_id])
        elif app_id == "6463715971":
            meta = lookup([app_id])[app_id]
            game, company, analysis, icon, screenshot = _sea_of_conquest_ios(row, meta)
            bundle["97_icon"] = data_uri(icon, (256, 256))
            bundle["97_store"] = data_uri(screenshot, (720, 720))
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
        if app_id == "6759664029":
            analysis["sections"]["rankPath"] = (
                f"本次位于iOS美国策略畅销榜第{rank}名（较9月25日最终有效快照下降20位）。"
                "Apple Lookup上架日期为2026-09-24，落在90天窗口内，因此继续归类为近三个月新上榜；"
                "首个完整快照曾到#26，本期回到后15名，Google Play则首次进入TOP60。"
            )
            analysis["sections"]["watch"] = (
                "观察未来1—2个有效快照能否守住iOS前50并让Google脱离后五名；"
                "若双端继续下移，则更接近系列IP首发峰值后的正常回落。"
            )
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/ios-enrichment-20260925.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20260928.json", games)
    updater.save("data/ios-enrichment-20260928.json", enrichment)
    updater.save("data/ios-trends-20260928.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if bundle:
        updater.save("assets/ios-assets-25.json", bundle)
        if "ios-assets-25.json" not in manifest["files"]:
            manifest["files"].append("ios-assets-25.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-09-28.json", {
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
