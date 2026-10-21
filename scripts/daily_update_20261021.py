#!/usr/bin/env python3
"""Build the Beijing 2026-10-21 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
from zoneinfo import ZoneInfo

import daily_update_20261020 as prior
from daily_update_20260820 import comparison, delta_label


updater = prior.updater
base_enforce_required_product_language = prior.enforce_required_product_language
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-21"
updater.STAMP = "20261021"
updater.PREVIOUS_STAMP = "20261020"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-23"
updater.GOOGLE_DATES = ("20261020",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261020",) + updater.IOS_DATES


def enforce_required_product_language(game_name, analysis):
    """Keep the three mandatory product narratives explicit and idempotent."""
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
        "data/games-20261020.json",
        "data/enrichment-20261020.json",
        "data/trends-20261020.json",
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

    enrichment = deepcopy(updater.load("data/enrichment-20261020.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261021.json", games)
    updater.save("data/enrichment-20261021.json", enrichment)
    updater.save("data/trends-20261021.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-21.json", {
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
        "data/ios-games-20261020.json",
        "data/ios-enrichment-20261020.json",
        "data/ios-trends-20261020.json",
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

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261020.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261021.json", games)
    updater.save("data/ios-enrichment-20261021.json", enrichment)
    updater.save("data/ios-trends-20261021.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-21.json", {
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


def mark_returns():
    """Make returning products explicit without claiming a cause for the move."""
    specs = (
        ("googlePlay", "com.ProjectMoon.LimbusCompany"),
        ("ios", "6755173751"),
        ("ios", "1035712810"),
        ("ios", "966810173"),
        ("ios", "672150402"),
        ("ios", "6746465127"),
        ("ios", "1342290011"),
        ("ios", "1465860096"),
        ("ios", "1071976327"),
    )
    for store, product_id in specs:
        if store == "googlePlay":
            games_path, trends_path, key, label = (
                "data/games-20261021.json", "data/trends-20261021.json", "packageName", "Google Play"
            )
        else:
            games_path, trends_path, key, label = (
                "data/ios-games-20261021.json", "data/ios-trends-20261021.json", "appId", "iOS"
            )
        games = updater.load(games_path)
        game = next(item for item in games if str(item[key]) == product_id)
        trends = updater.load(trends_path)
        analysis = trends[str(game["rank"])]
        release = game.get("releaseDateIso", "")
        status = game["comparison90d"]["status"]
        suffix = (
            f"按{label}商品页上架日期{release}计算，属于近三个月新上榜。"
            if status == "new"
            else "上架早于90天窗口；因缺少2026-07-23精确同口径基准，不判断近三个月飙升。"
        )
        analysis["sections"]["rankPath"] = (
            f"本次回到{label}美国策略畅销榜第{game['rank']}名（前一有效快照未入榜，回榜）。"
            f"{suffix}单日回榜只作为待验证信号，不据此断言长期趋势。"
        )
        analysis["sourceAudit"]["reviewedAt"] = updater.CAPTURE
        analysis["sourceAudit"]["changeReason"] = (
            "2026-10-21按对应商店官方榜单复核回榜与当前排名；沿用已核验产品、公司与素材证据。"
        )
        analysis["lifecycleAudit"]["reviewedAt"] = updater.CAPTURE
        analysis["lifecycleAudit"]["evidenceNote"] = (
            "回榜来自相邻有效快照对比；运营节点只作时间背景，不写成榜位变化的确定原因。"
        )
        updater.save(trends_path, trends)


def refresh_visible_summaries():
    """Update compact summaries for today's largest or analytically useful moves."""
    google = {
        "com.ProjectMoon.LimbusCompany": "趋势：2023年以都市怪谈、回合制罪人编队与章节叙事建立核心用户盘；关键转折：本期回到Google #{rank}，iOS未入榜，仍属榜尾轮换，未发现可确认的重大转折；主力素材：罪人角色、连续剧情、回合技能链、异常体战斗与暗色世界观。",
        "com.funplus.kingofavalon": "趋势：2016年以亚瑟王题材、龙养成与联盟4X形成长线盘；关键转折：本期Google上升4位至#{rank}，iOS位于#39，未找到与今天同步的重大官方节点；主力素材：巨龙养成、城堡扩建、联盟会战、英雄编队与赛季地图。",
        "com.more.lastshelter.gp": "趋势：2026年6月上架后，用末日地下庇护所切面、营救幸存者和僵尸压力承接房间建设、英雄编队与联盟战争，目前仍处首发验证；关键转折：8月26日版本补入联盟玩法与Doomsday Transport，本期Google上升1位至#{rank}，没有证据把单日变化归因于该旧版本；主力素材：地下庇护所剖面、救援抉择、僵尸追击、房间扩建、英雄小队和废土探索。",
        "com.fiveminlab.overgeared.hero.backpack.merge": "趋势：2026年以像素背包装备合并、肉鸽短局和自动战斗进入榜单；关键转折：Raven联动与万圣节皮肤仍在，本期Google上升1位至#{rank}、iOS下跌7位至#48，两端方向相反，时间相邻但不作确定归因；主力素材：像素英雄、背包摆位、装备合成、联动角色与万圣节皮肤。",
        "com.lavalabs.autodrill": "趋势：2026年6月以自动钻探飞船、手动摇杆和逐块击穿行星上线，把即时破坏反馈承接到武器、技能融合、装备升级与无限区域；关键转折：10月2日版本仅披露错误修复和性能改善，本期Google持平于#{rank}，未发现可确认的重大玩法转折；主力素材：飞船切入方块行星、连锁爆炸、武器弹幕、技能三选一/融合、装备升级与区域推进。",
        "com.farlightgames.samo.gp": "趋势：2023年以奇幻自由行军与联盟围猎Behemoth切入，成熟期由战宠、新巨兽和赛季竞合支撑；关键转折：第二赛季引入War Pets并压缩赛季间歇，本期Google持平于#{rank}，没有证据显示出现新的结构转折；主力素材：巨兽围猎、战宠捕捉、奇幻自由行军、英雄技能与联盟Boss。",
        "com.riotgames.league.wildrift": "趋势：2021年以英雄联盟IP和移动端5v5切入，成熟期由新英雄、赛季、皮肤和电竞节点支撑；关键转折：7.3b调整英雄、装备、符文与野区，本期Google持平于#{rank}，iOS从上期#58掉榜，更新存在不等于畅销改善；主力素材：5v5团战、英雄技能、高光操作、版本平衡与赛事皮肤。",
        "aliens.zombies.invasion": "趋势：2024年以卡通外星人、丧尸潮和单机塔防上架，当前由路径控制、塔位布局与防御塔升级承接；关键转折：本期Google下跌2位至#{rank}，iOS从上期#51掉榜，未发现可确认的重大转折/长期稳定运营；主力素材：密集丧尸波次、不同射程塔位、升级分支与基地防线。",
        "com.scopely.startrek": "趋势：2018年以正版Star Trek舰船、角色与联盟银河沙盒建立核心盘，成熟期靠剧集角色和连续活动回流；关键转折：Division 12于10月15日加入Rose Harper、Haven Exchange与限时里程碑，本期Google升1位至#{rank}，iOS仍未入榜；主力素材：经典角色、舰船对决、剧情章节、联盟战争与活动通行证。",
        "com.hnhs.endlesssea.gp": "趋势：2026年5月以海洋淹没后的灯塔庇护所、舰队探索和鲨鱼压力上线，随后加入联盟、海上要塞及世界首领；关键转折：当前2.5.5版本仅披露服务器性能与稳定性优化，本期Google升1位至#{rank}，未发现可确认的重大结构转折；主力素材：孤岛灯塔、篝火与鲨鱼包围的生存压力，承接漂浮庇护所扩建、舰队、海怪/海盗和联盟海域争夺。",
        "leyi.ageofspirits": "趋势：2026年9月以原始部落篝火、萨满和联盟4X进入首发验证，本期Google上升2位至#{rank}；关键转折：首发版本同步新增七种语言、11级兵种与萨满伤势机制，尚无更长期转折可确认；主力素材：从单一篝火扩建部落、萨满编队、巨兽威胁和联盟世界地图争夺。",
    }
    ios = {
        "921022358": "趋势：2015年以Star Wars角色收集、回合编队与公会战形成长线运营；关键转折：本期iOS上升24位至#{rank}，Google未入榜，单日跃升先按待验证信号处理；主力素材：经典角色、舰队与小队编成、银河战争、团队副本及限时活动。",
        "625257520": "趋势：2014年以Warcraft卡牌对战切入，标准轮换、扩展包与酒馆战棋维持多模式长线；关键转折：37.0预载Reign of the Black Empire，本期iOS上升38位至#{rank}，版本窗口与名次相邻但不作确定归因；主力素材：Old Gods、Assemble关键词、职业构筑、竞技场选牌与酒馆战棋。",
        "850057092": "趋势：2014年靠极简横版出兵和荒诞猫咪美术形成长尾，持续用新形态、关卡和联动回流；关键转折：本期iOS上升12位至#{rank}，未找到与今天同步的重大官方节点；主力素材：怪猫进化、巨大敌人、低成本反差与联动角色。",
        "6447612873": "趋势：2022年以潜艇舰队、基地经营与海战SLG建立核心盘；关键转折：本期iOS上升11位至#{rank}，Google位于#59，单日改善仍需连续快照验证；主力素材：潜艇编队、海上基地、航线争夺、舰长养成与联盟海战。",
        "6476261995": "趋势：2024年以帝国时代IP、文明发展与大地图联盟战切入；关键转折：本期iOS下跌8位至#{rank}，Google位于#39，未发现可确认的重大转折；主力素材：历史文明、城建科技、名将编队、即时行军与联盟攻城。",
        "6755585789": "趋势：2026年以像素背包装备合并、肉鸽短局和自动战斗进入榜单；关键转折：Raven联动与万圣节皮肤仍在，本期iOS下跌7位至#{rank}、Google位于#35，时间相邻但不作确定归因；主力素材：像素英雄、背包摆位、装备合成、联动角色与万圣节皮肤。",
        "6738469826": "趋势：2025年以监狱建设、犯人管理和轻量经营承接策略用户；关键转折：本期iOS下跌8位至#{rank}，Google位于#22，跨端差距扩大，未发现可确认的重大转折；主力素材：监狱扩建、人员调度、资源循环、冲突事件与经营升级。",
        "852912420": "趋势：2014年以符文构筑、属性克制和回合制魔灵收集形成全球长线盘；关键转折：SWC2026赛事内容仍在，本期iOS下跌6位至#{rank}，赛事节点与单日变化只作时间对照；主力素材：赛事对局、Pick & Ban、稀有召唤、符文搭配、魔灵养成与跨服竞技。",
        "1411917616": "趋势：2018年上线后，以中世纪城堡重建、国家战争和联盟跨服形成长线4X循环，目前由老服联盟、英雄养成与持续活动支撑；关键转折：9月7日版本仅确认优化和修复，本期iOS下跌6位至#{rank}，不能据此解释单日变化；主力素材：受损城镇重建、农耕采集、城堡扩张、英雄与兵种克制、世界地图和联盟战争。",
    }
    for games_path, trends_path, key, updates in (
        ("data/games-20261021.json", "data/trends-20261021.json", "packageName", google),
        ("data/ios-games-20261021.json", "data/ios-trends-20261021.json", "appId", ios),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        by_id = {str(game[key]): game for game in games}
        for product_id, summary in updates.items():
            game = by_id[product_id]
            trends[str(game["rank"])]["summary"] = summary.format(rank=game["rank"])
        updater.save(trends_path, trends)


def refresh_rank_paths():
    """Keep the visible rank-path paragraph limited to the current two snapshots."""
    for games_path, trends_path, store_label, release_basis in (
        (
            "data/games-20261021.json",
            "data/trends-20261021.json",
            "Google Play",
            "Google Play美国区商品页released日期",
        ),
        (
            "data/ios-games-20261021.json",
            "data/ios-trends-20261021.json",
            "iOS",
            "Apple Lookup releaseDate",
        ),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        for game in games:
            change = game["dailyChange"]
            if change == "NEW":
                movement = "2026-10-20前一有效快照未入榜，回榜"
            elif change == "=":
                movement = "较2026-10-20前一有效快照持平"
            elif change.startswith("+"):
                movement = f"较2026-10-20前一有效快照上升{change[1:]}位"
            else:
                movement = f"较2026-10-20前一有效快照下降{change[1:]}位"

            comparison = game["comparison90d"]
            if comparison["status"] == "new":
                status_text = (
                    f"按{release_basis}{game['releaseDateIso']}计算，位于"
                    f"{comparison['baselineDate']}至{comparison['currentDate']}的90天窗口内，"
                    "归类为近三个月新上榜。"
                )
            elif comparison["status"] == "surge":
                status_text = (
                    f"精确90天基准名次为#{comparison['baselineRank']}，"
                    f"至当前提升{comparison['delta']}位，归类为近三个月飙升。"
                )
            else:
                status_text = (
                    f"上架早于90天窗口；因缺少{comparison['baselineDate']}同口径完整TOP60基准，"
                    "不判断近三个月飙升，页面按常规在榜展示。"
                )

            trends[str(game["rank"])]["sections"]["rankPath"] = (
                f"本次位于{store_label}美国策略畅销榜第{game['rank']}名"
                f"（{movement}）。{status_text}"
            )
        updater.save(trends_path, trends)


def refresh_snapshot_sensitive_sections():
    """Remove prior-snapshot wording that no longer describes the current chart."""
    google = {
        "com.more.lastshelter.gp": {
            "turningPoints": "Google Play商品页显示8月26日更新增加联盟玩法与Doomsday Transport；该版本早于本期快照近两个月，不能用于解释10月21日的1位上升，未发现与今日同步的重大结构节点。",
            "watch": "观察未来2—3个工作日能否保持Google前40，以及iOS是否重新进入同口径TOP60；若很快回落，只记录为首发阶段波动，不预判长期走势。",
        },
        "com.lavalabs.autodrill": {
            "turningPoints": "10月2日商品页更新只说明错误修复和性能改善，没有公开大型活动、系统重构或商业化变化；本期Google持平于#42，从首发至今未发现可确认的重大转折。",
        },
        "com.farlightgames.samo.gp": {
            "watch": "未来1—2个有效快照观察Google中后段位置能否维持，并留意iOS是否重新进入TOP60；没有双端连续数据前不升级为长期趋势。",
        },
        "com.riotgames.league.wildrift": {
            "watch": "下一有效快照观察Google #48能否维持，以及iOS在从上期#58掉榜后是否回补；没有连续快照前只记录为7.3b窗口内的平台分化。",
        },
        "aliens.zombies.invasion": {
            "watch": "观察Google #49能否连续留榜，以及iOS从上期#51掉榜后是否回补；Boss活动结束前不把单日平台分化推断为长期趋势。",
        },
        "com.hnhs.endlesssea.gp": {
            "turningPoints": "当前2.5.5版本只披露服务器性能和稳定性优化，没有公开足以解释10月21日1位上升的新增系统或重大活动；产品已由首发庇护所生存延伸至联盟与世界首领，但未发现可确认的重大转折。",
            "watch": "观察未来1—2个有效快照能否离开Google后十名，并核对联盟与世界首领内容是否伴随连续留榜；没有连续数据前不把当前#52写成版本驱动或长期增长。",
        },
        "com.ProjectMoon.LimbusCompany": {
            "watch": "观察下一有效快照能否守住Google TOP60，以及iOS是否重新进入同口径榜单；若很快回落，则把本次记录为榜尾回补，而非长期趋势。",
        },
    }
    ios = {
        "852912420": {
            "watch": "未来1—2个有效快照观察iOS #53能否止跌并继续留在TOP60，再区分赛事曝光、版本活动与一次性波动。",
        },
        "1411917616": {
            "turningPoints": "可确认的长期变化是同一产品从Rise of Empires命名逐步切换至Rise of Castles，并持续强化城堡经营、英雄和联盟战争。Apple显示26.805.1版于9月7日更新，但公开说明只有性能优化和问题修复；本期下跌6位至#55，未发现可确认的近期重大转折。",
            "watch": "未来1—2个有效快照观察能否守住iOS TOP60；若继续下滑，只记录为成熟产品的榜尾波动，不把旧版本更新时间与本期变化写成确定因果。",
        },
    }
    for games_path, trends_path, key, updates in (
        ("data/games-20261021.json", "data/trends-20261021.json", "packageName", google),
        ("data/ios-games-20261021.json", "data/ios-trends-20261021.json", "appId", ios),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        by_id = {str(game[key]): game for game in games}
        for product_id, section_updates in updates.items():
            game = by_id[product_id]
            trends[str(game["rank"])]["sections"].update(section_updates)
        updater.save(trends_path, trends)


if __name__ == "__main__":
    updater.main()
    mark_returns()
    refresh_visible_summaries()
    refresh_rank_paths()
    refresh_snapshot_sensitive_sections()
