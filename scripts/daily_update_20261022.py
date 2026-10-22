#!/usr/bin/env python3
"""Build the Beijing 2026-10-22 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
from zoneinfo import ZoneInfo

import daily_update_20261021 as prior
from daily_update_20260820 import comparison, delta_label


updater = prior.updater
base_enforce_required_product_language = prior.enforce_required_product_language
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-22"
updater.STAMP = "20261022"
updater.PREVIOUS_STAMP = "20261021"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-24"
updater.GOOGLE_DATES = ("20261021",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261021",) + updater.IOS_DATES


def enforce_required_product_language(game_name, analysis):
    """Keep mandatory narratives explicit while making daily rewrites idempotent."""
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
        "data/games-20261021.json",
        "data/enrichment-20261021.json",
        "data/trends-20261021.json",
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

    enrichment = deepcopy(updater.load("data/enrichment-20261021.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261022.json", games)
    updater.save("data/enrichment-20261022.json", enrichment)
    updater.save("data/trends-20261022.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-22.json", {
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
        "data/ios-games-20261021.json",
        "data/ios-enrichment-20261021.json",
        "data/ios-trends-20261021.json",
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

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261021.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261022.json", games)
    updater.save("data/ios-enrichment-20261022.json", enrichment)
    updater.save("data/ios-trends-20261022.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-22.json", {
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


def refresh_rank_paths():
    """Replace every visible rank paragraph with the current adjacent-snapshot result."""
    for games_path, trends_path, store_label, release_basis in (
        ("data/games-20261022.json", "data/trends-20261022.json", "Google Play", "Google Play美国区商品页released日期"),
        ("data/ios-games-20261022.json", "data/ios-trends-20261022.json", "iOS", "Apple Lookup releaseDate"),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        for game in games:
            change = game["dailyChange"]
            if change == "NEW":
                movement = "2026-10-21前一有效快照未入榜，回榜"
            elif change == "=":
                movement = "较2026-10-21前一有效快照持平"
            elif change.startswith("+"):
                movement = f"较2026-10-21前一有效快照上升{change[1:]}位"
            else:
                movement = f"较2026-10-21前一有效快照下降{change[1:]}位"

            status = game["comparison90d"]
            if status["status"] == "new":
                status_text = (
                    f"按{release_basis}{game['releaseDateIso']}计算，位于"
                    f"{status['baselineDate']}至{status['currentDate']}的90天窗口内，归类为近三个月新上榜。"
                )
            elif status["status"] == "surge":
                status_text = (
                    f"精确90天基准名次为#{status['baselineRank']}，至当前提升{status['delta']}位，"
                    "归类为近三个月飙升。"
                )
            else:
                status_text = (
                    f"上架早于90天窗口；因缺少{status['baselineDate']}同口径完整TOP60基准，"
                    "不判断近三个月飙升，页面按常规在榜展示。"
                )
            trends[str(game["rank"])]["sections"]["rankPath"] = (
                f"本次位于{store_label}美国策略畅销榜第{game['rank']}名（{movement}）。{status_text}"
            )
        updater.save(trends_path, trends)


def refresh_visible_summaries():
    """Refresh products whose current move makes the inherited summary snapshot-sensitive."""
    google = {
        "com.wireless.defenseland": "趋势：2023年以英雄放置、塔防路线与装备成长切入，成熟期依靠英雄收集、挑战关和活动维持；关键转折：本期回到Google #{rank}，iOS未入榜，前一快照刚从#60退出，连续压线换位只记为待验证信号；主力素材：英雄编队、塔防路线、技能爆发、装备养成与Boss关卡。",
        "com.YoStarEN.Arknights": "趋势：2020年以二次元干员收集、格子塔防与章节叙事建立长线核心盘；关键转折：Episode 17仍在开放窗口且Extreme Mode于10月21日开启，本期Google下跌6位至#{rank}、iOS位于#36，版本存在不等于榜位必然上升；主力素材：限定干员、格子部署、主线剧情、技能时机与高难关卡。",
        "com.more.lastshelter.gp": "趋势：2026年6月上架后，用末日地下庇护所切面、营救幸存者和僵尸压力承接房间建设、英雄编队与联盟战争，目前仍处首发验证；关键转折：本期Google下跌3位至#{rank}，尚未确认同一产品的iOS TOP60对应项；主力素材：地下庇护所剖面、救援抉择、僵尸追击、房间扩建与英雄小队。",
        "com.farlightgames.samo.gp": "趋势：2023年以奇幻自由行军与联盟围猎Behemoth切入，成熟期由战宠、新巨兽和赛季竞合支撑；关键转折：本期Google下跌3位至#{rank}，iOS未入榜，没有证据显示出现新的结构转折；主力素材：巨兽围猎、战宠捕捉、自由行军、英雄技能与联盟Boss。",
        "com.justgame.jails": "趋势：2025年以监狱建设、犯人管理和轻量经营承接策略用户；关键转折：本期Google下跌3位至#{rank}、iOS持平于#43，10月19日新英雄与护甲版本未形成同步抬升；主力素材：监狱扩建、人员调度、资源循环、冲突事件与经营升级。",
        "com.wb.goog.got.conquest": "趋势：2017年借Game of Thrones IP、城堡建设与联盟4X建立长线盘；关键转折：九周年月度内容仍在，本期Google下跌3位至#{rank}、iOS从#52掉榜，不能把周年活动直接写成榜位拉升；主力素材：剧集角色、巨龙、城堡扩建、联盟战争与九周年奖励。",
        "com.im30.ROE.gp": "趋势：2018年上线后，以中世纪城堡重建、英雄和联盟跨服战形成长线循环；关键转折：本期Google上升3位至#{rank}、iOS上升1位至#54，未找到与今日同步的重大官方节点；主力素材：城堡扩建、农耕采集、英雄兵种、世界地图与联盟战争。",
        "com.sivona.stormshot.e": "趋势：2022年以射击解谜获量层承接海盗城建、英雄与联盟4X；关键转折：本期Google上升3位至#{rank}，iOS未入榜，单日中后段改善不足以确认长期转折；主力素材：弹射射击、藏宝图、海盗英雄、城堡扩建与联盟海战。",
        "com.scopely.startrek": "趋势：2018年以正版Star Trek舰船、角色与联盟银河沙盒建立核心盘，成熟期靠剧集角色和连续活动回流；关键转折：Division 12于10月15日加入Rose Harper与Haven Exchange，本期Google持平于#{rank}，iOS未入榜；主力素材：经典角色、舰船对决、剧情章节、联盟战争与活动通行证。",
        "com.fiveminlab.overgeared.hero.backpack.merge": "趋势：2026年以像素背包装备合并、肉鸽短局和自动战斗进入榜单；关键转折：Raven联动与万圣节皮肤仍在，本期Google上升2位至#{rank}、iOS下跌2位至#50，两端方向相反，时间相邻但不作确定归因；主力素材：像素英雄、背包摆位、装备合成、联动角色与万圣节皮肤。",
        "com.funplus.kingofavalon": "趋势：2016年以亚瑟王题材、龙养成与联盟4X形成长线盘；关键转折：本期Google下跌1位至#{rank}，iOS未入榜，未找到与今天同步的重大官方节点；主力素材：巨龙养成、城堡扩建、联盟会战、英雄编队与赛季地图。",
        "com.lavalabs.autodrill": "趋势：2026年6月以自动钻探飞船、手动摇杆和逐块击穿行星上线，把即时破坏反馈承接到武器与装备成长；关键转折：10月2日版本仅披露修复和性能改善，本期Google下跌1位至#{rank}，未发现可确认的重大玩法转折；主力素材：方块行星、连锁爆炸、武器弹幕、技能融合与区域推进。",
        "aliens.zombies.invasion": "趋势：2024年以卡通外星人、丧尸潮和单机塔防上架，当前由路径控制、塔位布局与防御塔升级承接；关键转折：本期Google上升1位至#{rank}，iOS未入榜，未发现可确认的重大转折/长期稳定运营；主力素材：密集丧尸波次、不同射程塔位、升级分支与基地防线。",
        "com.riotgames.league.wildrift": "趋势：2021年以英雄联盟IP和移动端5v5切入，成熟期由新英雄、赛季、皮肤和电竞节点支撑；关键转折：7.3b仍在版本窗口，本期Google下跌2位至#{rank}，iOS未入榜，更新存在不等于畅销改善；主力素材：5v5团战、英雄技能、高光操作、版本平衡与赛事皮肤。",
        "com.hnhs.endlesssea.gp": "趋势：2026年5月以海洋淹没后的灯塔庇护所、舰队探索和鲨鱼压力上线，随后加入联盟、海上要塞及世界首领；关键转折：2.5.5仅披露稳定性优化，本期Google下跌1位至#{rank}，未发现可确认的重大结构转折；主力素材：孤岛灯塔、鲨鱼压力、漂浮庇护所、舰队与联盟海域争夺。",
        "leyi.ageofspirits": "趋势：2026年9月以原始部落篝火、萨满和联盟4X进入首发验证；关键转折：本期Google持平于#{rank}，首发版本加入多语言、11级兵种与萨满伤势机制，尚无更长期转折可确认；主力素材：篝火扩建部落、萨满编队、巨兽威胁和联盟世界地图争夺。",
    }
    ios = {
        "1181774280": "趋势：2017年以Fire Emblem角色收集、回合制棋盘战和章节剧情形成长线盘；关键转折：本期回到iOS #{rank}，10.10.0加入七名英雄武器精炼与限时Combat Manuals，但仍处榜尾，先按待验证回榜处理；主力素材：历代英雄、召唤、格子战术、武器克制与新章节。",
        "1241932094": "趋势：2017年以俯视角丧尸生存、基地建设和资源搜集形成长线核心盘；关键转折：本期回到iOS #{rank}，Google位于#5，跨端差距仍大，最近版本只有登录与进度恢复简化；主力素材：丧尸压迫、庇护所扩建、资源搜集、载具和多人据点。",
        "1231085864": "趋势：2018年以Jurassic World IP、地图探索、DNA收集和实时PvP建立长线盘；关键转折：本期回到iOS #{rank}，3.23.55仅预告新恐龙并修复问题，缺少证据把回榜归因为该版本；主力素材：AR地图恐龙、DNA采集、混种培育、实时竞技场与IP角色。",
        "852912420": "趋势：2014年以符文构筑、属性克制和回合制魔灵收集形成全球长线盘；关键转折：9.3.6加入Cosmic Worm，本期iOS上升15位至#{rank}，版本与变化相邻但不作确定归因；主力素材：稀有召唤、符文搭配、魔灵养成、跨服竞技与赛事对局。",
        "1071976327": "趋势：2016年以城建、英雄与联盟4X形成长线核心盘；关键转折：2.208 Heroic Saga于10月21日上线，本期iOS上升12位至#{rank}、Google升2位至#34，两端同向但仍需后续快照验证；主力素材：英雄Battle Spirit、Saga任务、城堡扩建、兵种编队与联盟会战。",
        "6746636289": "趋势：2025年以锻造合成、装备成长和放置战斗建立轻量循环；关键转折：本期iOS上升9位至#{rank}，10月8日版本仅加入成就、聊天翻译和稳定性修复，未发现与今日同步的重大转折；主力素材：锻造台、装备合成、数值成长、自动战斗与离线收益。",
        "6447612873": "趋势：2022年以潜艇舰队、基地经营与海战SLG建立核心盘；关键转折：1.175.0于10月21日加入两名精英招募角色与回归指挥官福利，本期iOS反而下跌8位至#{rank}、Google位于#58，不能以有更新推断增长；主力素材：潜艇编队、海上基地、舰长招募、航线争夺与联盟海战。",
        "6476261995": "趋势：2024年以帝国时代IP、文明发展与大地图联盟战切入；关键转折：本期iOS下跌8位至#{rank}、Google位于#41，10月8日版本仅披露修复，未发现可确认的重大转折；主力素材：历史文明、城建科技、名将编队、即时行军与联盟攻城。",
        "1354260888": "趋势：2018年以文明选择、自由行军和联盟大地图建立长线4X盘，后期素材转向战力逆袭情景剧，近期更多展示城建资源与真实会战；关键转折：本期iOS下跌6位至#{rank}，Google位于#7，单日回落不等于收入下滑；主力素材：文明选择、自由行军、战力逆袭情景剧、城建资源与真实联盟会战。",
        "921022358": "趋势：2015年以Star Wars角色收集、回合编队与公会战形成长线运营；关键转折：本期iOS持平于#{rank}，Google未入榜，未发现与今天同步的重大内容节点；主力素材：经典角色、舰队与小队编成、银河战争、团队副本及限时活动。",
        "625257520": "趋势：2014年以Warcraft卡牌对战切入，标准轮换、扩展包与酒馆战棋维持多模式长线；关键转折：Reign of the Black Empire已于10月20日上线，本期iOS下跌2位至#{rank}，仍需区分首发峰值和持续承接；主力素材：Old Gods、Assemble关键词、职业构筑、竞技场选牌与酒馆战棋。",
        "1464872022": "趋势：2020年全球上线后以职业克制、部署顺序与技能时机构成长线塔防核心；关键转折：Episode 17仍在开放窗口，本期iOS下跌3位至#{rank}、Google下跌6位至#14，版本节点与榜位只作时间对照；主力素材：新主线世界观、限定干员、多职业编队、格子部署与技能爆发。",
        "850057092": "趋势：2014年靠极简横版出兵和荒诞猫咪美术形成长尾，持续用新形态、关卡和联动回流；关键转折：本期iOS下跌1位至#{rank}，未找到与今天同步的重大官方节点；主力素材：怪猫进化、巨大敌人、低成本反差与联动角色。",
        "6738469826": "趋势：2025年以监狱建设、犯人管理和轻量经营承接策略用户；关键转折：本期iOS持平于#{rank}、Google下跌3位至#25，跨端差距仍大；主力素材：监狱扩建、人员调度、资源循环、冲突事件与经营升级。",
        "6755585789": "趋势：2026年以像素背包装备合并、肉鸽短局和自动战斗进入榜单；关键转折：Raven联动与万圣节皮肤仍在，本期iOS下跌2位至#{rank}、Google上升2位至#33，两端方向相反；主力素材：像素英雄、背包摆位、装备合成、联动角色与万圣节皮肤。",
        "1411917616": "趋势：2018年上线后，以中世纪城堡重建、国家战争和联盟跨服形成长线4X循环；关键转折：本期iOS上升1位至#{rank}、Google上升3位至#40，双端同向但幅度有限，未发现新的结构转折；主力素材：受损城镇重建、农耕采集、英雄兵种、世界地图和联盟战争。",
    }
    for games_path, trends_path, key, updates in (
        ("data/games-20261022.json", "data/trends-20261022.json", "packageName", google),
        ("data/ios-games-20261022.json", "data/ios-trends-20261022.json", "appId", ios),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        by_id = {str(game[key]): game for game in games}
        for product_id, summary in updates.items():
            game = by_id[product_id]
            trends[str(game["rank"])]["summary"] = summary.format(rank=game["rank"])
        updater.save(trends_path, trends)


if __name__ == "__main__":
    updater.main()
    refresh_rank_paths()
    refresh_visible_summaries()
