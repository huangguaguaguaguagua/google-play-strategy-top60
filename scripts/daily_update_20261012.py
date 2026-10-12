#!/usr/bin/env python3
"""Build the Beijing 2026-10-12 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import daily_update_20261009 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend


updater = prior.updater
base_enforce_required_product_language = prior.enforce_required_product_language
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-12"
updater.STAMP = "20261012"
updater.PREVIOUS_STAMP = "20261009"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-14"
updater.GOOGLE_DATES = ("20261009",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261009",) + updater.IOS_DATES


GDEV_COMPANY = {
    "en": "GAMEGEARS LTD / GDEV Inc.",
    "cn": "Game Gears（塞浦路斯发行与研发主体；GDEV游戏与娱乐集团旗下工作室）",
    "confidence": "已确认",
    "basis": "Apple美国区列Gamegears Limited、Google Play列GAMEGEARS LTD为店铺发行主体；Game Gears官方隐私政策指向母公司GDEV Inc.，GDEV官网及2026年官方公告将Game Gears列为集团工作室/子公司。",
    "source": "https://www.gdev.inc/overview/about-gdev",
}


def enforce_required_product_language(game_name, analysis):
    """Keep the requested Kingshot narrative explicit in both store views."""
    analysis = base_enforce_required_product_language(game_name, analysis)
    if game_name != "Kingshot":
        return analysis

    def rewrite(value):
        if isinstance(value, dict):
            return {key: rewrite(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rewrite(item) for item in value]
        if isinstance(value, str):
            return value.replace(
                "居民分工、英雄养成和联盟4X",
                "城镇经营、居民分工、英雄养成和联盟4X",
            )
        return value

    return rewrite(analysis)


def _correct_gamegears_company(company, analysis):
    """Apply the newly verified Game Gears -> GDEV ownership chain."""
    company = deepcopy(GDEV_COMPANY)
    analysis = deepcopy(analysis)
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        audit = analysis.get(audit_name, {})
        sources = audit.setdefault("sources", [])
        if not any(source.get("url") == GDEV_COMPANY["source"] for source in sources):
            sources.append({"label": "GDEV官方公司页", "url": GDEV_COMPANY["source"], "type": "company-audit"})
        audit["reviewedAt"] = "2026-10-12"
    analysis["sourceAudit"]["changeReason"] = (
        "按Game Gears隐私政策与GDEV官方公司页补全最终集团归属；榜位与产品生命周期判断仍独立使用对应商店证据。"
    )
    return company, analysis


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20261009.json",
        "data/enrichment-20261009.json",
        "data/trends-20261009.json",
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

        if package == "aliens.zombies.invasion":
            company, analysis = _correct_gamegears_company(company, analysis)

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

    enrichment = deepcopy(updater.load("data/enrichment-20261009.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261012.json", games)
    updater.save("data/enrichment-20261012.json", enrichment)
    updater.save("data/trends-20261012.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-12.json", {
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


def _ios_game(row, meta, asset_rank, genre, keywords):
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
    screenshot = screenshots[0] if screenshots else icon
    release = (meta.get("releaseDate") or "")[:10]
    return {
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
        "genre": genre,
        "keywords": keywords,
        "note": f"Apple Lookup显示iOS美国区于{release}上架；90天状态只使用本商店日期。",
        "assetRank": asset_rank,
        "store": "ios",
    }, icon, screenshot


def _bloons_ios(row, meta):
    game, icon, screenshot = _ios_game(
        row, meta, 100,
        "塔防 / 英雄养成 / 合作策略",
        "猴塔；气球；塔防；三路线升级；英雄；Paragon；合作；Boss；地图；长期活动",
    )
    if game["releaseDate"] != "2018-06-14":
        raise RuntimeError(f"Bloons TD 6 iOS release date requires review: {game['releaseDate']!r}")
    company = {
        "en": "Ninja Kiwi Limited / Modern Times Group MTG AB",
        "cn": "Ninja Kiwi（新西兰研发与发行；MTG全资游戏工作室）",
        "confidence": "已确认",
        "basis": "Apple美国区Lookup列Ninja Kiwi Limited为seller；MTG官方公告确认于2021年6月完成对Ninja Kiwi 100%股权收购，并明确Bloons TD 6属于该工作室。",
        "source": "https://www.mtg.com/pressroom/article/?a=mtg-completes-the-acquisition-of-ninja-kiwi--the-leading-tower-defense-gaming-studio-and-publisher-a&i=30D3BA8D6C650418",
    }
    analysis = trend(
        "趋势：2018年上线后以猴塔部署、三路线升级与英雄体系长期运营，本次首次进入项目iOS #54；关键转折：10月6日57.0加入Sniper Paragon S.P.I.D.E.R. Monkey与社区地图Ship Capture，但单日入榜原因仍待验证；主力素材：多猴塔覆盖、气球波次、英雄技能、Paragon进阶、Boss与合作关卡。",
        "iOS美国区于2018年6月上架。核心循环是布置猴塔抵挡气球波次，并在三条升级路线、英雄技能、Paragon与地图机制之间做资源选择；在线合作、Boss和手工活动承接成熟期玩家。",
        "本次首次进入项目自2026年8月19日起保存的iOS美国策略畅销TOP60，位列第54名；上架早于90天窗口，且缺少2026年7月14日精确同口径基准，内部状态为pending、页面按常规在榜展示。",
        "10月6日57.0版本加入Sniper Paragon S.P.I.D.E.R. Monkey、社区竞赛地图Ship Capture及平衡与体验调整；版本与本次入榜相邻，但没有公开证据证明榜位由该版本直接推动。",
        "Apple当前商店图持续展示多种猴塔、气球路线、英雄与升级树；57.0的新增看点集中在狙击Paragon、社区地图与Boss挑战。素材判断基于Apple商品页与官方版本说明，可信度为中。",
        "观察未来1—2个有效快照能否脱离后十名，并核对57.0后续活动窗口；没有连续留榜前不把本次#54写成长期回升。",
        game["storeUrl"],
        [{"label": "MTG完成收购Ninja Kiwi官方公告", "url": company["source"], "type": "company-audit"}],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-12", status="已复核", confidence="中",
        basis="上架日、玩法、版本说明、ICON与商店图来自Apple美国区商品页；最终集团归属由MTG官方收购公告核验。",
        changeReason="首次进入项目保存的iOS榜，按Apple Lookup建立独立商店档案，未借用Google日期或安装量。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-12", status="已复核", confidence="中",
        scope="从2018年iOS上架梳理到2026年10月6日57.0版本与本次首次进入项目TOP60。",
        evidenceNote="版本节点与本次入榜时间相邻，但没有公开收入或投放证据证明因果，按成熟产品榜尾信号处理。",
    )
    return game, company, analysis, icon, screenshot


def _aliens_ios(row, meta):
    game, icon, screenshot = _ios_game(
        row, meta, 101,
        "塔防 / 丧尸 / 轻度策略",
        "飞碟吞噬；丧尸；塔防；炮塔建造；资源掉落；装备2.0；Boss；万圣节活动",
    )
    if game["releaseDate"] != "2025-02-05":
        raise RuntimeError(f"Aliens vs Zombies iOS release date requires review: {game['releaseDate']!r}")
    company = deepcopy(GDEV_COMPANY)
    analysis = trend(
        "趋势：2025年iOS上线，以飞碟吞噬、资源掉落和炮塔防守连接动作入口与丧尸塔防，本次首次进入项目iOS #59；关键转折：10月6日1.22b重做装备系统，并预告10月19日Boss Hunt与10月26日Halloween Night，榜位承接仍待验证；主力素材：飞碟吞噬、炮塔建造升级、丧尸潮、装备合成与万圣节Boss。",
        "iOS美国区于2025年2月上架。玩家操控飞碟吞噬场景物体取得资源与经验，再建造和升级炮塔保护基地；动作操控负责首层反馈，丧尸波次、装备与基地防线承接轻度塔防循环。",
        "本次首次进入项目保存的iOS美国策略畅销TOP60，位列第59名；Google同产品也处榜尾。Apple上架日早于90天窗口，且缺少2026年7月14日精确同口径基准，内部状态为pending、页面按常规在榜展示。",
        "10月6日1.22b把装备改为配方制作、一键合成、槽位升级与最高Cosmic稀有度，并预告10月19日Boss Hunt和10月26日Halloween Night；活动尚未开始，不能用未来节点解释今天榜位。",
        "Apple商店图以飞碟吞噬物件、资源落下、炮塔覆盖与丧尸潮为主；当前版本新增装备工坊、合成稀有度和万圣节Boss。素材判断基于Apple商品页，可信度为中。",
        "先观察10月19日前能否连续留榜，再分别核对Boss Hunt与Halloween Night上线后的双端位置；活动前不把本次#59归因为万圣节内容。",
        game["storeUrl"],
        [
            {"label": "Game Gears官方隐私政策", "url": "https://www.gamegears.online/privacy-policy", "type": "company-audit"},
            {"label": "GDEV官方公司页", "url": company["source"], "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-12", status="已复核", confidence="中",
        basis="上架日、版本说明、玩法、ICON与商店图来自Apple美国区商品页；Game Gears与GDEV官方资料用于核对最终集团归属。",
        changeReason="首次进入项目iOS榜，按Apple Lookup建立独立档案；未混用Google上架日期，且未把尚未开始的活动写成榜位原因。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-12", status="已复核", confidence="中",
        scope="从2025年2月iOS上架梳理到2026年10月6日装备2.0与万圣节预告。",
        evidenceNote="可确认装备重做与活动排期，但活动尚未开始；本次末位入榜只记为待验证信号。",
    )
    return game, company, analysis, icon, screenshot


def build_ios_today(rows, source_url, source_updated):
    current = updater.records(
        "data/ios-games-20261009.json",
        "data/ios-enrichment-20261009.json",
        "data/ios-trends-20261009.json",
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
        elif app_id == "1118115766":
            game, company, analysis, icon, screenshot = _bloons_ios(row, metadata[app_id])
            bundle["100_icon"] = data_uri(icon, (256, 256))
            bundle["100_store"] = data_uri(screenshot, (720, 720))
        elif app_id == "6740232087":
            game, company, analysis, icon, screenshot = _aliens_ios(row, metadata[app_id])
            bundle["101_icon"] = data_uri(icon, (256, 256))
            bundle["101_store"] = data_uri(screenshot, (720, 720))
        else:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")

        if app_id == "6740232087":
            company, analysis = _correct_gamegears_company(company, analysis)

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

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261009.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261012.json", games)
    updater.save("data/ios-enrichment-20261012.json", enrichment)
    updater.save("data/ios-trends-20261012.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if bundle:
        updater.save("assets/ios-assets-28.json", bundle)
        if "ios-assets-28.json" not in manifest["files"]:
            manifest["files"].append("ios-assets-28.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-12.json", {
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
