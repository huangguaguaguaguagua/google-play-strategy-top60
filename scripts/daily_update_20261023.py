#!/usr/bin/env python3
"""Build the Beijing 2026-10-23 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
from zoneinfo import ZoneInfo

import daily_update_20261022 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend


updater = prior.updater
base_enforce_required_product_language = prior.enforce_required_product_language
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-23"
updater.STAMP = "20261023"
updater.PREVIOUS_STAMP = "20261022"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-25"
updater.GOOGLE_DATES = ("20261022",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261022",) + updater.IOS_DATES


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
        "data/games-20261022.json",
        "data/enrichment-20261022.json",
        "data/trends-20261022.json",
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

    enrichment = deepcopy(updater.load("data/enrichment-20261022.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261023.json", games)
    updater.save("data/enrichment-20261023.json", enrichment)
    updater.save("data/trends-20261023.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-23.json", {
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


def _infinite_borders_ios(row, meta):
    """Create the first project profile from Apple and NetEase official sources."""
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
    screenshot = screenshots[1] if len(screenshots) > 1 else (screenshots[0] if screenshots else icon)
    release = (meta.get("releaseDate") or "")[:10]
    if release != "2023-08-01":
        raise RuntimeError(f"Infinite Borders iOS release date requires review: {release!r}")
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
        "genre": "SLG / 三国 / 沙盘4X",
        "keywords": "三国；沙盘；地缘争夺；300武将；战法搭配；城建资源；联盟；陆海会战；赛季",
        "note": "Apple Lookup显示iOS美国区于2023-08-01上架；90天状态只使用本商店日期。",
        "assetRank": 102,
        "store": "ios",
    }
    company = {
        "en": "NetEase Games / Hong Kong NetEase Interactive Entertainment Limited / NetEase, Inc.",
        "cn": "网易游戏／网易（美国区seller为香港网易互动娱乐有限公司）",
        "confidence": "已确认",
        "basis": "Apple美国区Lookup列Hong Kong NetEase Interactive Entertainment Limited为seller、NetEase Games为发行名；网易游戏官方发布确认Infinite Borders由NetEase Games全球发行，官网版权归NetEase, Inc.。",
        "source": "https://www.neteasegames.com/news/20231201/37000_1123343.html",
    }
    analysis = trend(
        "趋势：2023年先在iOS美国区上架并于12月全球发行，以三国武将、2.25百万格沙盘和无VIP优势的联盟地缘战建立长线盘；关键转折：2026年周年活动与10月21日例行更新仍在窗口，本期首次进入项目保存的iOS榜#60，只记为待验证信号；主力素材：三国名将、超大规模陆海会战、沙盘行军、城池经营、季节场景与联盟争地。",
        "Apple美国区于2023年8月1日上架，网易在同年12月1日宣布全球发行。首层以刘备、曹操、吕布等三国认知与武将收集降低门槛，中层由战法组合、城建资源和政策经营承接，长期循环落在2.25百万格沙盘、联盟外交与领土争夺。",
        "本次首次进入项目自2026年8月19日起保存的iOS美国策略畅销TOP60，位列第60名；产品上架远早于2026年7月25日窗口，且缺少精确90天同口径基准，内部状态为pending、页面按常规在榜展示。Google Play策略TOP60本期未收录。",
        "可确认节点为2023年12月全球发行、2026年10月周年庆两阶段活动及10月21日例行更新；这些节点与本次末位入榜时间相邻，但没有证据证明单一活动直接造成榜位变化。",
        "Apple当前商店图同时展示Q版季节庭院、马超等三国武将、沙盘界面以及超大规模陆海会战；当前主要由成熟赛季、联盟地缘盘与周年内容支撑。素材判断来自Apple商品页，可信度为中。",
        "观察未来1—2个有效快照能否连续留榜并脱离#60，再结合周年活动结束后的名次判断是短期回补还是稳定承接；没有连续证据前不推演长期走势。",
        game["storeUrl"],
        [
            {"label": "Infinite Borders官方网站", "url": "https://www.infinitebordersgame.com/", "type": "primary"},
            {"label": "NetEase Games全球发行公告", "url": "https://www.neteasegames.com/news/20231201/37000_1123343.html", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-23",
        status="已复核",
        confidence="中",
        basis="上架日、版本、玩法、图标和商店图来自Apple美国区Lookup/商品页；全球发行、沙盘规模与发行主体由NetEase Games和产品官网交叉核验。当前素材主要来自单一商店，不标高可信度。",
        changeReason="首次进入项目保存的iOS榜，建立独立商店档案；周年和例行更新仅作时间背景，不写成末位入榜的确定原因。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-23",
        status="已复核",
        confidence="中",
        scope="从2023年iOS上架和全球发行梳理到2026年周年活动、10月21日例行更新与本次首次进入项目TOP60。",
        evidenceNote="官方资料支持产品结构、发行链和近期活动；缺少公开收入或投放数据，本次只按成熟产品榜尾待验证信号处理。",
    )
    return game, company, analysis, icon, screenshot


def build_ios_today(rows, source_url, source_updated):
    current = updater.records(
        "data/ios-games-20261022.json",
        "data/ios-enrichment-20261022.json",
        "data/ios-trends-20261022.json",
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
        elif app_id == "1080541643":
            game, company, analysis, icon, screenshot = _infinite_borders_ios(row, metadata[app_id])
            bundle["102_icon"] = data_uri(icon, (256, 256))
            bundle["102_store"] = data_uri(screenshot, (720, 720))
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

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261022.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261023.json", games)
    updater.save("data/ios-enrichment-20261023.json", enrichment)
    updater.save("data/ios-trends-20261023.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if bundle:
        updater.save("assets/ios-assets-29.json", bundle)
        if "ios-assets-29.json" not in manifest["files"]:
            manifest["files"].append("ios-assets-29.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-23.json", {
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
    first_time = {"1080541643"}
    for games_path, trends_path, store_label, release_basis, key in (
        ("data/games-20261023.json", "data/trends-20261023.json", "Google Play", "Google Play美国区商品页released日期", "packageName"),
        ("data/ios-games-20261023.json", "data/ios-trends-20261023.json", "iOS", "Apple Lookup releaseDate", "appId"),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        for game in games:
            change = game["dailyChange"]
            if change == "NEW":
                movement = (
                    "项目历史首次收录"
                    if str(game[key]) in first_time
                    else "2026-10-22前一有效快照未入榜，回榜"
                )
            elif change == "=":
                movement = "较2026-10-22前一有效快照持平"
            elif change.startswith("+"):
                movement = f"较2026-10-22前一有效快照上升{change[1:]}位"
            else:
                movement = f"较2026-10-22前一有效快照下降{change[1:]}位"

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
    """Update compact summaries for today's entrants and major movers."""
    google = {
        "com.seaofconquest.global": "趋势：2023年以海盗探索、船队养成与联盟海战承接4X长线盘；关键转折：本期回到Google #{rank}，iOS未入榜，仍是末位回补，未发现与今天同步的重大转折；主力素材：海盗船队、寻宝探索、甲板战斗、港口扩建与联盟海域争夺。",
        "com.YoStarEN.Arknights": "趋势：2020年以二次元干员收集、格子塔防与章节叙事建立长线核心盘；关键转折：Episode 17 Extreme Mode仍在窗口，本期Google上升6位至#{rank}、iOS下跌6位至#42，双端反向，版本不等于榜位必然抬升；主力素材：限定干员、格子部署、主线剧情、技能时机与高难关卡。",
        "com.wb.goog.hotd.socialstrategy": "趋势：2026年以House of the Dragon IP、养龙与联盟4X进入首发运营；关键转折：10月15日Kalspire角色内容后，本期Google下跌6位至#{rank}、iOS上升13位至#11，双端反向，活动只作时间背景；主力素材：坦格利安角色、巨龙孵化、空战、城堡扩建与联盟争夺。",
        "com.camelgames.aoz": "趋势：2018年以末日城建、兵种与联盟战争形成长线4X循环；关键转折：本期Google下跌5位至#{rank}，iOS未入榜，未发现与今天同步的重大官方节点；主力素材：丧尸压力、城市扩张、兵种编队、英雄与联盟大地图。",
        "com.farlightgames.samo.gp": "趋势：2023年以奇幻自由行军与联盟围猎Behemoth切入，成熟期由战宠、新巨兽和赛季竞合支撑；关键转折：本期Google上升4位至#{rank}，iOS未入榜，单日回升尚不足以确认结构转折；主力素材：巨兽围猎、战宠捕捉、自由行军、英雄技能与联盟Boss。",
        "com.justgame.jails": "趋势：2025年以监狱建设、犯人管理和轻量经营承接策略用户；关键转折：本期Google上升3位至#{rank}、iOS下跌3位至#46，两端反向，近期版本只作时间背景；主力素材：监狱扩建、人员调度、资源循环、冲突事件与经营升级。",
        "com.funplus.kingofavalon": "趋势：2016年以亚瑟王题材、巨龙养成和联盟4X形成长线核心盘；关键转折：本期Google上升3位至#{rank}，iOS未入榜，未发现与今天同步的重大官方节点；主力素材：巨龙、圆桌英雄、城堡扩建、兵种编队与联盟会战。",
        "com.more.lastshelter.gp": "趋势：2026年以地下庇护所剖面、营救幸存者与僵尸压力承接房间建设、英雄编队和联盟战争，目前仍处首发验证；关键转折：本期Google上升3位至#{rank}、iOS回榜#50，双端同时进入中后段但未发现新的重大节点；主力素材：地下庇护所剖面、救援抉择、僵尸追击、房间扩建与英雄小队。",
        "com.wb.goog.got.conquest": "趋势：2017年借Game of Thrones IP、城堡建设与联盟4X建立长线盘；关键转折：九周年月度内容仍在，本期Google上升3位至#{rank}、iOS未入榜，单端改善不写成活动直接拉升；主力素材：剧集角色、巨龙、城堡扩建、联盟战争与九周年奖励。",
        "com.sivona.stormshot.e": "趋势：2022年以射击解谜获量层承接海盗城建、英雄与联盟4X；关键转折：本期Google下跌3位至#{rank}，iOS未入榜，未发现与今天同步的重大节点；主力素材：弹射射击、藏宝图、海盗英雄、城堡扩建与联盟海战。",
        "leyi.ageofspirits": "趋势：2026年9月以原始部落篝火、萨满和联盟4X进入首发验证；关键转折：本期Google下跌3位至#{rank}，仍属近90天新品，尚无更长期转折可确认；主力素材：篝火扩建部落、萨满编队、巨兽威胁和联盟世界地图争夺。",
    }
    ios = {
        "6503702666": "趋势：2024年以多人合作塔防、英雄组合与即时布防切入；关键转折：本期回到iOS #{rank}，Google未入榜，暂按中段回补而非长期趋势处理；主力素材：多人同屏防线、英雄技能、路线阻挡、塔位升级与Boss波次。",
        "6760406772": "趋势：2026年6月上架后，用末日地下庇护所切面、营救幸存者和僵尸压力承接房间建设、英雄编队与联盟战争，目前仍处首发验证；关键转折：本期回到iOS #{rank}，Google同产品当前#33，双端同时进入中后段但未发现新的重大节点；主力素材：地下庇护所剖面、救援抉择、僵尸追击、房间扩建与英雄小队。",
        "1611722542": "趋势：2022年以中世纪塔防、英雄收集与领地经营形成轻量策略循环；关键转折：本期回到iOS #{rank}，Google未入榜，仍需连续快照验证；主力素材：中世纪城墙、英雄布阵、密集敌潮、防御塔升级与领地扩张。",
        "1080541643": "趋势：2023年先在iOS美国区上架并于12月全球发行，以三国武将、2.25百万格沙盘和联盟地缘战建立长线盘；关键转折：周年活动与10月21日例行更新仍在窗口，本期首次进入项目保存的iOS榜#{rank}，只记为待验证信号；主力素材：三国名将、超大规模陆海会战、沙盘行军、城池经营、季节场景与联盟争地。",
        "1487451427": "趋势：2021年以卡通文明、英灵和龙养成承接联盟4X；关键转折：本期iOS上升20位至#{rank}，9月v2.9.9的Horus、联盟章程与成长优化仍是最近可确认节点，不能据此解释全部升幅；主力素材：跨文明英灵、巨龙、卡通城建、元素编队与联盟攻城。",
        "1642607669": "趋势：2026年以House of the Dragon IP、养龙与联盟4X进入首发运营；关键转折：10月15日Kalspire角色内容后，本期iOS上升13位至#{rank}，Google位于#11，时间相邻但仍需后续留位验证；主力素材：坦格利安角色、巨龙孵化、空战、城堡扩建与联盟争夺。",
        "6751086804": "趋势：2026年以龙族角色收集、战术编队与奇幻叙事进入首发验证；关键转折：本期iOS上升12位至#{rank}，未找到与今天同步的重大官方节点，单日跃升只作待验证信号；主力素材：龙族角色、技能演出、编队克制、Boss战与章节剧情。",
        "625257520": "趋势：2014年以Warcraft卡牌对战切入，标准轮换、扩展包与酒馆战棋维持多模式长线；关键转折：Reign of the Black Empire已于10月20日上线，本期iOS下跌11位至#{rank}，需要区分首发峰值回落与稳定承接；主力素材：Old Gods、Assemble关键词、职业构筑、竞技场选牌与酒馆战棋。",
        "6450953550": "趋势：2024年以救援解谜、英雄养成与城镇联盟承接轻量4X；关键转折：本期iOS下跌10位至#{rank}，Google位于#44，已逼近榜尾，未发现与今天同步的重大节点；主力素材：救援情景、英雄编队、城镇扩建、世界Boss与联盟战争。",
        "1071976327": "趋势：2016年以城建、英雄与联盟4X形成长线核心盘；关键转折：2.208 Heroic Saga于10月21日上线，本期iOS再上升9位至#{rank}、Google位于#35，仍需连续快照验证版本承接；主力素材：英雄Battle Spirit、Saga任务、城堡扩建、兵种编队与联盟会战。",
        "1181774280": "趋势：2017年以Fire Emblem角色收集、回合制棋盘战和章节剧情形成长线盘；关键转折：本期iOS上升7位至#{rank}，10.10.0武器精炼仍在窗口，但仍属后十名波动；主力素材：历代英雄、召唤、格子战术、武器克制与新章节。",
        "1464872022": "趋势：2020年全球上线后以职业克制、部署顺序与技能时机构成长线塔防核心；关键转折：Episode 17仍在开放窗口，本期iOS下跌6位至#{rank}、Google上升6位至#8，双端反向；主力素材：新主线世界观、限定干员、多职业编队、格子部署与技能爆发。",
        "1071744151": "趋势：2016年以奇幻城建、兽人题材和联盟战争形成长线4X循环；关键转折：本期iOS下跌6位至#{rank}，Google未入榜，未发现与今天同步的重大官方节点；主力素材：奇幻城堡、兽人兵团、英雄养成、世界地图与联盟攻城。",
        "6746465127": "趋势：2026年以竖屏割草射击、英雄成长和防线生存进入首发验证；关键转折：本期iOS上升6位至#{rank}，Google未入榜，尚无可确认的重大转折；主力素材：密集敌潮、走位射击、技能合成、Boss波次与局内成长。",
    }
    for games_path, trends_path, key, updates in (
        ("data/games-20261023.json", "data/trends-20261023.json", "packageName", google),
        ("data/ios-games-20261023.json", "data/ios-trends-20261023.json", "appId", ios),
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
