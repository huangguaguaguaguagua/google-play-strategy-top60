#!/usr/bin/env python3
"""Build the Beijing 2026-10-16 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
from zoneinfo import ZoneInfo

import daily_update_20261015 as prior
from daily_update_20260820 import comparison, delta_label


updater = prior.updater
base_enforce_required_product_language = prior.enforce_required_product_language
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-16"
updater.STAMP = "20261016"
updater.PREVIOUS_STAMP = "20261015"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-18"
updater.GOOGLE_DATES = ("20261015",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261015",) + updater.IOS_DATES


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
        "data/games-20261015.json",
        "data/enrichment-20261015.json",
        "data/trends-20261015.json",
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

    enrichment = deepcopy(updater.load("data/enrichment-20261015.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261016.json", games)
    updater.save("data/enrichment-20261016.json", enrichment)
    updater.save("data/trends-20261016.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-16.json", {
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
        "data/ios-games-20261015.json",
        "data/ios-enrichment-20261015.json",
        "data/ios-trends-20261015.json",
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
            prepare_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261015.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261016.json", games)
    updater.save("data/ios-enrichment-20261016.json", enrichment)
    updater.save("data/ios-trends-20261016.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-16.json", {
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
    """Refresh returning products without turning one-day moves into causal claims."""

    def update(games_path, trends_path, game_name, summary, sections, source=None):
        games = updater.load(games_path)
        game = next(item for item in games if item["gameName"] == game_name)
        trends = updater.load(trends_path)
        analysis = trends[str(game["rank"])]
        replacements = {"{rank}": str(game["rank"]), "{change}": game["dailyChange"]}

        def resolve(value):
            for token, replacement in replacements.items():
                value = value.replace(token, replacement)
            return value

        analysis["summary"] = resolve(summary)
        analysis["sections"].update({key: resolve(value) for key, value in sections.items()})
        for audit_name in ("sourceAudit", "lifecycleAudit"):
            audit = analysis[audit_name]
            audit["reviewedAt"] = updater.CAPTURE
            audit["status"] = "已复核"
            if audit.get("confidence") == "高":
                audit["confidence"] = "中"
            if source:
                sources = audit.setdefault("sources", [])
                if not any(item.get("url") == source["url"] for item in sources):
                    sources.append(source)
        analysis["sourceAudit"]["changeReason"] = (
            "2026-10-16按官方产品或版本资料与双商店相邻有效快照复核；单日榜位仅作时间对照。"
        )
        analysis["lifecycleAudit"]["evidenceNote"] = (
            "玩法与运营节点来自官方资料；榜位来自对应商店官方榜单，不把时间相邻写成确定因果。"
        )
        updater.save(trends_path, trends)

    arknights = {
        "label": "Arknights Episode 17官方公告",
        "url": "https://www.arknights.global/news/4814",
        "type": "primary",
    }
    update(
        "data/games-20261016.json", "data/trends-20261016.json", "Arknights",
        "趋势：2020年全球上线后以职业克制、部署顺序与技能时机构成长线塔防核心；关键转折：Episode 17于10月14日开放，本期Google继续升至#{rank}、iOS仍守前10；主力素材：新主线世界观、限定干员、多职业编队、格子部署、敌人路线与技能爆发。",
        {
            "rankPath": "本次位于Google Play美国策略畅销榜第{rank}名（较前一榜单上升6位）；继昨日回榜后继续改善，说明Episode 17窗口至少延续到第二个快照，但仍不能把名次变化换算为收入增幅。",
            "watch": "未来1—2个有效快照观察Google能否保持前15、iOS能否继续守住前10；活动窗口结束后的留位更能判断长期承接。",
        }, arknights,
    )
    update(
        "data/ios-games-20261016.json", "data/ios-trends-20261016.json", "Arknights",
        "趋势：2020年全球上线后以职业克制、部署顺序与技能时机构成长线塔防核心；关键转折：Episode 17于10月14日开放，本期iOS小幅回落至#{rank}但仍守前10、Google继续上升；主力素材：新主线世界观、限定干员、多职业编队、格子部署、敌人路线与技能爆发。",
        {
            "rankPath": "本次位于iOS美国策略畅销榜第{rank}名（较前一榜单下降1位）；昨日回榜后仍留在前10，与Google继续上升共同构成第二个活动窗口快照。",
            "watch": "未来1—2个有效快照观察iOS能否继续守住前10、Google能否保持前15；活动窗口结束后的留位更能判断长期承接。",
        }, arknights,
    )

    wild_rift = {
        "label": "Wild Rift 7.3b官方补丁说明",
        "url": "https://wildrift.leagueoflegends.com/en-us/news/game-updates/wild-rift-patch-notes-7-3b/",
        "type": "primary",
    }
    for store, games_path, trends_path, rank_path in (
        ("Google Play", "data/games-20261016.json", "data/trends-20261016.json", "本次回到Google Play美国策略畅销榜第{rank}名，恰处最后一名；iOS也回到#50。7.3b于10月14日发布、部分兑换内容10月15日开放，时间相邻但榜尾回归仍需连续快照确认。"),
        ("iOS", "data/ios-games-20261016.json", "data/ios-trends-20261016.json", "本次回到iOS美国策略畅销榜第{rank}名，Google也回到#60。7.3b于10月14日发布、部分兑换内容10月15日开放，双端同期回归是待验证信号；该产品本质仍为MOBA分类边界。"),
    ):
        update(
            games_path, trends_path, "League of Legends: Wild Rift",
            f"趋势：2021年以英雄联盟IP和移动端5v5切入，成熟期由新英雄、赛季、皮肤和电竞节点支撑；关键转折：7.3b调整英雄、装备、符文与野区，并于10月15日开放限定兑换内容，本期{store}回榜#{{rank}}且双端同步进入；主力素材：5v5团战、英雄技能、高光操作、版本平衡与赛事皮肤。",
            {
                "rankPath": rank_path,
                "turningPoints": "首发以正统《英雄联盟》移动化降低教育成本；成熟期传播转向新英雄、赛季、皮肤与团战高光。当前7.3b对多名英雄、装备、符文和野区作平衡调整，并开放Legends Showdown Volibear限定兑换内容。",
                "creative": "5v5团战、技能连招、版本强弱变化、英雄与皮肤展示、赛事高光；本期官方资料证据来自补丁说明，未据此反推广告投放规模。",
                "watch": "下一有效快照观察两端能否同时留榜；Google位于#60，若立即退出则只记录为7.3b窗口内的短时回补。",
            }, wild_rift,
        )

    star_trek = {
        "label": "Star Trek Fleet Command Division 12官方补丁说明",
        "url": "https://startrekfleetcommand.com/news/division-12-patch-notes/",
        "type": "primary",
    }
    for store, games_path, trends_path, rank_path in (
        ("Google Play", "data/games-20261016.json", "data/trends-20261016.json", "本次位于Google Play美国策略畅销榜第{rank}名（较前一榜单下降2位）；同日iOS回榜#55，跨端强度不一致。"),
        ("iOS", "data/ios-games-20261016.json", "data/ios-trends-20261016.json", "本次回到iOS美国策略畅销榜第{rank}名；Google仍在#25。Division 12活动于10月15日启动，时间相邻但iOS仍靠近榜尾。"),
    ):
        update(
            games_path, trends_path, "Star Trek Fleet Command",
            f"趋势：2018年以正版Star Trek舰船、角色与联盟银河沙盒建立核心盘，成熟期靠剧集角色和连续活动回流；关键转折：Division 12于10月15日加入SNW Rose Harper、Haven Exchange与限时里程碑，本期{store}位于#{{rank}}；主力素材：经典角色、舰船对决、剧情章节、联盟战争与活动通行证。",
            {
                "rankPath": rank_path,
                "turningPoints": "首发以拥有、升级经典舰船和联盟银河沙盒承接IP用户；成熟期持续引入剧集角色、跨界合作与赛季系统。Division 12新增Epic Officer SNW Rose Harper、Haven Exchange及10月15日开启的限时活动，是本期可核验节点。",
                "creative": "Star Trek经典角色与舰船、太空战斗、联盟银河战、剧情章节、活动通行证和限时结构选择；官方补丁只证明内容上线，不证明单日榜位因果。",
                "watch": "未来1—2个有效快照观察iOS能否脱离后六名，同时比较Google能否守住前30，以区分活动回补与稳定跨端承接。",
            }, star_trek,
        )

    update(
        "data/ios-games-20261016.json", "data/ios-trends-20261016.json", "Limbus Company",
        "趋势：2023年以12名罪人、技能连锁和Clash硬币判定切入Project Moon核心用户，成熟期由章节、赛季、Identity与E.G.O更新支撑；关键转折：9月Season 8是最近可确认节点，本期iOS回到#{rank}而Google掉出TOP60，未发现同日重大转折；主力素材：反乌托邦都市、巴士小队、技能链、硬币判定、E.G.O爆发与异常体Boss。",
        {
            "rankPath": "本次回到iOS美国策略畅销榜第{rank}名，而Google从上期#45掉榜；跨端方向相反，不把回榜归因于9月Season 8或未经核验的单一活动。",
            "watch": "下一有效快照观察iOS能否留在前40，以及Google是否重新进入；若继续分化，则按平台端短时消费差异记录。",
        }, {"label": "Limbus Company官方产品站", "url": "https://limbuscompany.com/eng/", "type": "primary"},
    )

    update(
        "data/ios-games-20261016.json", "data/ios-trends-20261016.json", "Last Shelter: War Z",
        "趋势：2026年6月以地下庇护所建设、荒原探索与英雄防线切入，后续开放联盟集结和跨服对抗；关键转折：9月联盟决斗锦标赛仍是最近可确认节点，本期iOS回榜#{rank}、同名产品Google位于#35；主力素材：地下房间扩建、幸存者分工、丧尸防守、英雄编队与联盟战争。",
        {
            "rankPath": "本次回到iOS美国策略畅销榜第{rank}名；对应Google产品当前位于#35，形成双端在榜但名次差异明显。未发现与今天同步的可确认重大版本节点。",
            "watch": "未来1—2个有效快照观察iOS能否脱离后七名，并与Google中段位置对照；若立即掉榜，仍按iPhone端榜尾回补处理。",
        }, {"label": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id6760406772", "type": "primary"},
    )

    for store, games_path, trends_path, rank_path in (
        ("Google Play", "data/games-20261016.json", "data/trends-20261016.json", "本次回到Google Play美国策略畅销榜第{rank}名，iOS也回到#60；两端均在后段，未发现与今天同步的官方重大节点。"),
        ("iOS", "data/ios-games-20261016.json", "data/ios-trends-20261016.json", "本次回到iOS美国策略畅销榜第{rank}名，Google同步回到#53；双端共同进入但均贴近榜尾，先按待验证信号处理。"),
    ):
        update(
            games_path, trends_path, "Call of Dragons",
            f"趋势：2023年以奇幻自由行军与联盟围猎Behemoth切入，成熟期由战宠、新巨兽和赛季竞合支撑；关键转折：第二赛季引入War Pets并压缩赛季间歇，本期{store}回榜#{{rank}}且双端同步进入；主力素材：巨兽围猎、战宠捕捉、奇幻自由行军、英雄技能与联盟Boss。",
            {
                "rankPath": rank_path,
                "watch": "未来1—2个有效快照观察两端能否同时留榜；若任一端立即退出，则不把本次双端回归升级为长期趋势。",
            }, {"label": "Call of Dragons官方产品站", "url": "https://callofdragons.farlightgames.com/", "type": "primary"},
        )


if __name__ == "__main__":
    updater.main()
    apply_verified_event_updates()
