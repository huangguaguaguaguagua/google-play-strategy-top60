#!/usr/bin/env python3
"""Build the Beijing 2026-10-15 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
from zoneinfo import ZoneInfo

import daily_update_20261014 as prior
from daily_update_20260820 import comparison, delta_label


updater = prior.updater
base_enforce_required_product_language = prior.enforce_required_product_language
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-15"
updater.STAMP = "20261015"
updater.PREVIOUS_STAMP = "20261014"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-17"
updater.GOOGLE_DATES = ("20261014",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261014",) + updater.IOS_DATES


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
        "data/games-20261014.json",
        "data/enrichment-20261014.json",
        "data/trends-20261014.json",
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

    enrichment = deepcopy(updater.load("data/enrichment-20261014.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261015.json", games)
    updater.save("data/enrichment-20261015.json", enrichment)
    updater.save("data/trends-20261015.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-15.json", {
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
        "data/ios-games-20261014.json",
        "data/ios-enrichment-20261014.json",
        "data/ios-trends-20261014.json",
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

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261014.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261015.json", games)
    updater.save("data/ios-enrichment-20261015.json", enrichment)
    updater.save("data/ios-trends-20261015.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-15.json", {
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
    """Refresh lifecycle notes where current official material changes the record."""

    def update(games_path, trends_path, game_name, summary, sections, source):
        games = updater.load(games_path)
        game = next(item for item in games if item["gameName"] == game_name)
        trends = updater.load(trends_path)
        analysis = trends[str(game["rank"])]
        replacements = {"{rank}": str(game["rank"]), "{change}": game["dailyChange"]}
        for token, value in replacements.items():
            summary = summary.replace(token, value)
        resolved_sections = {}
        for key, value in sections.items():
            for token, replacement in replacements.items():
                value = value.replace(token, replacement)
            resolved_sections[key] = value
        analysis["summary"] = summary
        analysis["sections"].update(resolved_sections)
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
            "2026-10-15按官方版本或活动资料更新节点，并与对应商店相邻快照对照；不把时间相邻写成确定因果。"
        )
        analysis["lifecycleAudit"]["evidenceNote"] = (
            "产品节点来自官方资料；榜位来自对应商店相邻有效快照，二者仅作时间对照。"
        )
        updater.save(trends_path, trends)

    arknights_source = {
        "label": "Arknights Episode 17官方公告",
        "url": "https://www.arknights.global/news/4814",
        "type": "primary",
    }
    for store, games_path, trends_path in (
        ("Google Play", "data/games-20261015.json", "data/trends-20261015.json"),
        ("iOS", "data/ios-games-20261015.json", "data/ios-trends-20261015.json"),
    ):
        update(
            games_path,
            trends_path,
            "Arknights",
            f"趋势：2020年全球上线后以职业克制、部署顺序与技能时机构成长线塔防核心；关键转折：主线Episode 17 Critical Phase Transition于10月14日开放，本期{store}回榜#{{rank}}且双端同时进入TOP60；主力素材：新主线世界观、限定干员、多职业编队、格子部署、敌人路线与技能爆发。",
            {
                "rankPath": f"本次位于{store}美国策略畅销榜第{{rank}}名，此前一份有效快照未进TOP60。Episode 17于10月14日08:00（UTC-7）开放，时间高度重合，但只有一个榜单截面，先记为活动窗口待验证信号。",
                "turningPoints": "上线初期以职业、射程、部署费用和敌人路线形成差异化塔防；长期由干员收集、章节活动、危机合约与基地系统扩展。2026年10月主线Episode 17 Critical Phase Transition及配套限时内容成为当前可核验节点。",
                "creative": "Episode 17叙事与角色视觉、限定干员展示、多职业编队、格子部署顺序、敌人路线拆解、技能爆发和罗德岛世界观。",
                "watch": "观察未来1—2个有效快照能否分别守住Google前20与iOS前10；若快速退出，则把本次视为主线更新窗口内的短峰。",
            },
            arknights_source,
        )

    update(
        "data/ios-games-20261015.json",
        "data/ios-trends-20261015.json",
        "Summoners War",
        "趋势：2014年以符文构筑、属性克制和回合制魔灵收集形成全球长线盘；关键转折：SWC2026美洲杯结果与亚太杯排期于10月14日集中发布，本期iOS回榜#{rank}；主力素材：赛事对局、Pick & Ban、稀有召唤、符文搭配、魔灵养成与跨服竞技。",
        {
            "rankPath": "本次回到iOS美国策略畅销榜第{rank}名，前一有效快照未进TOP60。SWC2026美洲杯结果与亚太杯赛程在源更新日前后发布，但赛事曝光是否转化为消费仍需连续快照验证。",
            "turningPoints": "早期以魔灵收集、属性克制和23类符文建立高深度养成；实时竞技、Pick & Ban、跨服公会战与SWC赛事逐步强化成熟期竞技身份。当前可核验节点是SWC2026区域杯与世界总决赛席位竞争。",
            "creative": "SWC赛事舞台与选手、Pick & Ban、稀有魔灵召唤、符文套装前后对比、属性克制、实时竞技和公会战。",
            "watch": "未来1—2个有效快照观察能否保持iOS前30，并区分赛事曝光、版本活动与一次性回榜。",
        },
        {
            "label": "Summoners War官方SWC2026公告",
            "url": "https://summonerswar.com/en/skyarena/news",
            "type": "primary",
        },
    )

    update(
        "data/ios-games-20261015.json",
        "data/ios-trends-20261015.json",
        "SimCity BuildIt",
        "趋势：2014年以触屏城市建设、生产链与服务覆盖切入，成熟期由市长竞赛、俱乐部战争和主题赛季维持；关键转折：Haunted Metropolis赛季10月14日开启，本期iOS回榜#{rank}；主力素材：哥特城市、Rift Tower、永久夜景、主题道路、天际线设计与市长通行证。",
        {
            "rankPath": "本次回到iOS美国策略畅销榜第{rank}名，仍靠近榜尾。Haunted Metropolis于10月14日06:00 UTC开启，时间相邻但单日回榜不足以证明赛季形成持续承接。",
            "turningPoints": "早期以道路、住宅、生产与城市服务构成经典建城循环；市长竞赛、俱乐部战争、设计挑战和赛季通行证把单人扩城变为周期竞争与主题收藏。当前赛季加入13级Rift Tower及全城永久夜景效果。",
            "creative": "哥特天际线、Rift Tower升级前后、02:00永久夜景、红雾与闪电、Haunted Street、主题地标和市长竞赛进度。",
            "watch": "未来1—2个有效快照观察能否脱离后八名；若立即掉榜，仍按万圣节赛季首日回补处理。",
        },
        {
            "label": "EA Haunted Metropolis官方公告",
            "url": "https://www.ea.com/games/simcity/simcity-buildit/news/welcome-to-haunted-metropolis-streets-of-fright",
            "type": "primary",
        },
    )

    update(
        "data/ios-games-20261015.json",
        "data/ios-trends-20261015.json",
        "War Machines：Battle Tank Games",
        "趋势：2016年上线后以短局实时坦克对战、载具升级与全球排行榜长期运营；关键转折：本期iOS回榜#{rank}且9月29日版本仅披露修复与性能优化，未发现可确认的重大转折；主力素材：第三人称坦克瞄准、城市与荒漠战场、装甲火力升级、小队协同和世界排行。",
        {
            "rankPath": "本次回到iOS美国策略畅销榜第{rank}名，恰处掉榜线。当前公开版本仅写修复与性能优化，未发现可确认的活动或系统转折。",
            "watch": "下一有效快照观察是否继续留榜；若再次退出，则维持为成熟产品的榜尾短时回补。",
        },
        {
            "label": "War Machines官方产品页",
            "url": "https://wildlifestudios.com/games/war-machines/",
            "type": "primary",
        },
    )

    update(
        "data/ios-games-20261015.json",
        "data/ios-trends-20261015.json",
        "Hearthstone",
        "趋势：2014年以Warcraft卡牌对战切入，标准轮换、扩展包与酒馆战棋维持多模式长线运营；关键转折：37.0开启Reign of the Black Empire预发布、新竞技场赛季与Journal，本期iOS继续改善至#{rank}；主力素材：Old Gods、Assemble关键词、职业构筑、竞技场选牌、酒馆战棋与奖励轨。",
        {
            "rankPath": "本次位于iOS美国策略畅销榜第{rank}名（相邻快照变化{change}），继上一快照明显上涨后继续改善。37.0于10月13日上线并开启新竞技场赛季，时间高度重合，但仍不把榜位变化换算成收入或写成确定因果。",
            "watch": "观察10月20日资料片正式发布前后能否连续保持iOS前25，并区分预发布、新竞技场赛季与正式扩展包窗口。",
        },
        {
            "label": "Hearthstone 37.0官方补丁说明",
            "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
            "type": "primary",
        },
    )

    update(
        "data/ios-games-20261015.json",
        "data/ios-trends-20261015.json",
        "The Tower - Idle Tower Defense",
        "趋势：2021年从极简单塔守波起步，靠永久研究、卡牌和锦标赛社区逐步爬升；关键转折：v29加入全局预设、Mythic联赛、重做Vault与Harmony Tree后，昨日跃升、本期回落至#{rank}；主力素材：单塔清屏、指数成长、Boss波次、构筑预设、锦标赛与长期研究。",
        {
            "rankPath": "本次位于iOS美国策略畅销榜第{rank}名（相邻快照变化{change}），部分回吐上一快照+25的跃升。v29是可核验背景，但一升一降更符合短时峰值待确认，而非持续趋势。",
            "watch": "未来1—2个有效快照观察能否重新进入前40；若继续向榜尾回落，则把10月14日跃升视为v29窗口内的短峰。",
        },
        {
            "label": "Apple App Store美国区v29版本说明",
            "url": "https://apps.apple.com/us/app/id1575590830",
            "type": "primary",
        },
    )

    update(
        "data/games-20261015.json",
        "data/trends-20261015.json",
        "Auto Drill: Galaxy",
        "趋势：2026年6月以自动钻探飞船、手动摇杆和逐块击穿行星上线，把即时破坏反馈承接到武器、技能融合、装备升级与无限区域；关键转折：10月2日版本仅披露错误修复和性能改善，本期Google改善至#{rank}，未发现可确认的重大玩法转折；主力素材：飞船切入方块行星、连锁爆炸、武器弹幕、技能三选一/融合、装备升级与区域推进。",
        {
            "rankPath": "本次位于Google Play美国策略畅销榜第{rank}名（相邻快照变化{change}）。产品已越过最初上架窗口，但缺少7月17日精确榜单基准，内部保持pending、页面按常规展示。",
            "watch": "观察未来1—2个有效快照能否继续脱离榜尾，并核对后续版本是否出现可确认的内容节点。",
        },
        {
            "label": "Google Play美国区商品页",
            "url": "https://play.google.com/store/apps/details?id=com.lavalabs.autodrill&hl=en_US&gl=US",
            "type": "primary",
        },
    )

    update(
        "data/ios-games-20261015.json",
        "data/ios-trends-20261015.json",
        "The Battle Cats",
        "趋势：2014年靠极简横版出兵和荒诞猫咪美术形成长尾，十余年通过新形态、关卡和高频联动反复回流；关键转折：从单纯推线扩展出稀有猫养成与高难挑战，本期iOS回落至#{rank}；主力素材：怪猫进化、巨大敌人、低成本反差和联动角色。",
        {
            "rankPath": "本次位于iOS美国策略畅销榜第{rank}名（相邻快照变化{change}），已进入后四名掉榜风险区。未发现与今天同日的可确认重大节点。",
            "watch": "下一有效快照观察能否留榜；若回升再核对联动或扭蛋节点，若掉榜则只记录为成熟长尾产品的单日回落。",
        },
        {
            "label": "Apple App Store美国区商品页",
            "url": "https://apps.apple.com/us/app/id850057092",
            "type": "primary",
        },
    )


if __name__ == "__main__":
    updater.main()
    apply_verified_event_updates()
