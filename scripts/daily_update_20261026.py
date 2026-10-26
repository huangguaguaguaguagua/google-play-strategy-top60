#!/usr/bin/env python3
"""Build the Beijing 2026-10-26 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
import unicodedata
from zoneinfo import ZoneInfo

import daily_update_20261023 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend


updater = prior.updater
base_enforce_required_product_language = prior.enforce_required_product_language
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-26"
updater.STAMP = "20261026"
updater.PREVIOUS_STAMP = "20261023"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-28"
updater.GOOGLE_DATES = ("20261023",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261023",) + updater.IOS_DATES


def enforce_required_product_language(game_name, analysis):
    """Keep the mandatory product narratives explicit and idempotent."""
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
        "data/games-20261023.json",
        "data/enrichment-20261023.json",
        "data/trends-20261023.json",
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

    enrichment = deepcopy(updater.load("data/enrichment-20261023.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261026.json", games)
    updater.save("data/enrichment-20261026.json", enrichment)
    updater.save("data/trends-20261026.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-26.json", {
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


def _age_of_spirits_ios(row, meta):
    """Create the first iOS profile from Apple and Leyi official sources."""
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
    screenshot = screenshots[0] if screenshots else icon
    release = (meta.get("releaseDate") or "")[:10]
    if release != "2026-09-15":
        raise RuntimeError(f"Age of Spirits iOS release date requires review: {release!r}")
    store_url = f"https://apps.apple.com/us/app/id{row['appId']}"
    game = {
        "rank": row["rank"],
        "appId": row["appId"],
        "packageName": row["appId"],
        "gameName": row["gameName"],
        "developer": row["developer"],
        "totalInstalls": "",
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "storeUrl": store_url,
        "iconUrl": icon,
        "rankIconUrl": icon,
        "screenshotUrl": screenshot,
        "shortDescription": (meta.get("description") or "").replace("\n", " ")[:220],
        "description": meta.get("description", ""),
        "releaseDate": release,
        "releaseDateIso": release,
        "updatedDate": (meta.get("currentVersionReleaseDate") or "")[:10],
        "genre": "SLG / 4X / 部落经营",
        "keywords": "原始部落；篝火；萨满；城建；回合制远征；世界地图；联盟；资源争夺",
        "note": "Apple Lookup显示iOS美国区于2026-09-15上架；90天状态只使用本商店日期。",
        "assetRank": 103,
        "store": "ios",
    }
    company = {
        "en": "LEXIANGCO.,LIMITED / LeyiGames / Shenzhen Leyi Network Co., Ltd.",
        "cn": "LEXIANGCO.,LIMITED（iOS法律主体）/ LeyiGames（发行品牌）/ 深圳乐易网络（产品体系）",
        "confidence": "已确认",
        "basis": "Apple美国区Lookup列LEXIANGCO.,LIMITED为seller，开发者网站、隐私政策邮箱与版权均指向LeyiGames；Leyi官方隐私声明列深圳办公地址并说明其开发及发行移动游戏。未据此延伸推断更上层集团。",
        "source": "https://www.leyinetwork.com/privacy/",
    }
    analysis = trend(
        "趋势：2026年9月以原始部落篝火、萨满和联盟4X在iOS进入首发验证；关键转折：10月19日1.1.1版本仍处近期窗口，本期首次进入项目保存的iOS榜#58，同时Google升至#57，只记为双端榜尾信号；主力素材：篝火扩建部落、巨兽压迫、萨满编队、回合制远征和联盟世界地图争夺。",
        "Apple美国区于2026年9月15日上架。产品以‘从一团火建立部落’呈现权力成长：先唤醒野人并分配采集、狩猎和制作岗位，再通过祭坛、采石场、伐木场和兵营扩张聚落，最终进入英雄远征、资源地争夺和联盟会战；上线时间短，仍处首发验证。",
        "本次首次进入项目保存的iOS美国策略畅销TOP60，位列第58名；按Apple Lookup上架日2026-09-15计算，属于近90天新品。Google Play同日第57名，两端均接近榜尾，尚不支持判断稳定承接。",
        "可确认节点为9月首发多语言、11级士兵和萨满部署/伤势系统，以及10月19日1.1.1版本更新；这些只作为首发期产品节点，不直接归因于本次入榜。",
        "Apple当前商店图依次展示篝火聚落、巨兽压迫、部落角色、城建资源和世界地图；获量层突出暗黑原始部落与生存压力，后续由居民分工、英雄远征和联盟4X承接。素材判断仅来自Apple商品页，可信度为中。",
        "未来1—2个有效快照观察双端能否同时留榜并脱离后十名；若iOS再次退出，只记录为首发验证期榜尾轮换，不推演后续走势。",
        store_url,
        [
            {"label": "LeyiGames官方产品页", "url": "https://www.leyinetwork.com/en/games/", "type": "primary"},
            {"label": "LeyiGames官方隐私与主体页", "url": "https://www.leyinetwork.com/privacy/", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-26",
        status="已复核",
        confidence="中",
        basis="上架日、版本、玩法、图标和商店图来自Apple美国区Lookup/商品页；发行链由Apple seller、Leyi开发者网站、版权、官方邮箱及官方隐私声明交叉核验。当前素材只有单一商店证据，不标高可信度。",
        changeReason="首次进入项目保存的iOS榜，按iOS自身releaseDate建立独立档案；版本节点仅作时间背景，不写成本次入榜的确定原因。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-26",
        status="已复核",
        confidence="中",
        scope="从2026年9月iOS上架与首发系统节点梳理到10月19日版本和本次首次进入项目TOP60。",
        evidenceNote="官方资料支持产品结构、商店主体与版本时间；缺少公开收入或投放数据，本次只按近90天新品的双端榜尾信号处理。",
    )
    return game, company, analysis, icon, screenshot


def build_ios_today(rows, source_url, source_updated):
    current = updater.records(
        "data/ios-games-20261023.json",
        "data/ios-enrichment-20261023.json",
        "data/ios-trends-20261023.json",
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
        elif app_id == "6805006706":
            game, company, analysis, icon, screenshot = _age_of_spirits_ios(row, metadata[app_id])
            bundle["103_icon"] = data_uri(icon, (256, 256))
            bundle["103_store"] = data_uri(screenshot, (720, 720))
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

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261023.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261026.json", games)
    updater.save("data/ios-enrichment-20261026.json", enrichment)
    updater.save("data/ios-trends-20261026.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if bundle:
        updater.save("assets/ios-assets-30.json", bundle)
        if "ios-assets-30.json" not in manifest["files"]:
            manifest["files"].append("ios-assets-30.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-26.json", {
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
    first_time = {"6805006706"}
    for games_path, trends_path, store_label, release_basis, key in (
        ("data/games-20261026.json", "data/trends-20261026.json", "Google Play", "Google Play美国区商品页released日期", "packageName"),
        ("data/ios-games-20261026.json", "data/ios-trends-20261026.json", "iOS", "Apple Lookup releaseDate", "appId"),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        for game in games:
            change = game["dailyChange"]
            if change == "NEW":
                movement = "项目历史首次收录" if str(game[key]) in first_time else "2026-10-23前一有效快照未入榜，回榜"
            elif change == "=":
                movement = "较2026-10-23前一有效快照持平"
            elif change.startswith("+"):
                movement = f"较2026-10-23前一有效快照上升{change[1:]}位"
            else:
                movement = f"较2026-10-23前一有效快照下降{change[1:]}位"

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
    """Update compact summaries for entrants, first-time products and major movers."""
    google = {
        "com.plarium.vikings": "趋势：2015年以北欧战争、城镇资源与联盟4X形成成熟长线盘；关键转折：本期回到Google #{rank}，iOS未入榜，仍是榜尾回补，未发现与今天同步的重大官方节点；主力素材：维京首领、城镇扩建、兵种集结、世界地图与联盟战争。",
        "com.global.antgame": "趋势：2022年以蚁巢剖面与昆虫生态承接联盟4X；关键转折：本期回到Google #{rank}，iOS未入榜，仅按后十名回补记录；主力素材：地下蚁巢、蚁后孵化、兵蚁编队、天敌压迫与联盟领地。",
        "com.ProjectMoon.LimbusCompany": "趋势：2023年以Project Moon世界观、回合制技能链和角色抽取形成核心用户盘；关键转折：本期回到Google #{rank}，iOS未入榜，未找到同步重大节点，只记为榜尾回补；主力素材：暗黑都市、人格抽取、技能拼点、章节Boss与剧情演出。",
        "com.gtarcade.ioe.global": "趋势：2021年以卡通文明、英灵和龙养成承接联盟4X；关键转折：本期Google上升8位至#{rank}、iOS未入榜，最近可确认的v2.9.9节点较早，不能解释全部升幅；主力素材：跨文明英灵、巨龙、卡通城建、元素编队与联盟攻城。",
        "com.nvsgames.snap": "趋势：2022年以Marvel IP、三路区域和短局卡牌博弈建立成熟盘；关键转折：本期Google上升6位至#{rank}、iOS未入榜，未发现与今天同步的重大节点；主力素材：Marvel角色、区域翻转、卡牌连锁、赛季通行证与高稀有变体。",
        "com.camelgames.aoz": "趋势：2018年以末日城建、兵种与联盟战争形成长线4X循环；关键转折：本期Google上升5位至#{rank}，iOS未入榜，单日回升尚不能确认结构转折；主力素材：丧尸压力、城市扩张、兵种编队、英雄与联盟大地图。",
        "com.justgame.jails": "趋势：2025年以监狱建设、犯人管理和轻量经营承接策略用户；关键转折：本期Google持平于#{rank}、iOS上升3位至#43，两端节奏不同，近期版本只作时间背景；主力素材：监狱扩建、人员调度、资源循环、冲突事件与经营升级。",
        "com.more.lastshelter.gp": "趋势：2026年以地下庇护所剖面、营救幸存者与僵尸压力承接房间建设、英雄编队和联盟战争，目前仍处上线早期验证；关键转折：本期Google下跌2位至#{rank}、iOS同产品掉榜，单个快照只记为双端留榜压力；主力素材：地下庇护所剖面、救援抉择、僵尸追击、房间扩建与英雄小队。",
        "com.farlightgames.samo.gp": "趋势：2023年以奇幻自由行军与联盟围猎巨兽切入，成熟期由战宠和赛季竞合支撑；关键转折：本期Google下跌9位至#{rank}，iOS未入榜，未发现与今天同步的重大节点；主力素材：巨兽围猎、战宠捕捉、自由行军、英雄技能与联盟Boss。",
        "com.YoStarEN.Arknights": "趋势：2020年以二次元干员收集、格子塔防与章节叙事建立长线核心盘；关键转折：Episode 17仍处开放窗口，本期Google下跌6位至#{rank}、iOS位于#42，版本不等于榜位必然抬升；主力素材：限定干员、格子部署、主线剧情、技能时机与高难关卡。",
    }
    ios = {
        "1035712810": "趋势：2017年借Game of Thrones IP、城堡建设与联盟4X建立长线盘；关键转折：九周年2026_10更新仍在窗口，本期回到iOS #{rank}、Google掉榜，跨端分化只记为待验证信号；主力素材：剧集角色、巨龙、城堡扩建、研究树与联盟战争。",
        "6479020757": "趋势：2025年以DC角色收集、地下基地经营和联盟PvP切入；关键转折：本期回到iOS #{rank}，Google未入榜，暂按中后段回补处理；主力素材：Batman等DC英雄、Dark Multiverse、基地房间、阵容克制与联盟战。",
        "1427744264": "趋势：2018年以星舰建造、星系探索与联盟4X形成长线盘；关键转折：Alliance Tournaments于10月22日调整，本期回到iOS #{rank}，Google#21，时间相邻但仍需连续留位验证；主力素材：经典舰船、星际基地、船员组合、星系探索与联盟竞赛。",
        "1480616990": "趋势：2021年以英雄联盟IP、双摇杆MOBA与短局竞技形成核心用户盘；关键转折：本期回到iOS #{rank}，Google下跌至#53，跨端不同步，不写成版本确定拉动；主力素材：英雄技能连招、五人团战、皮肤、排位与赛季活动。",
        "1241932094": "趋势：2017年以末日采集、基地建造和僵尸生存形成长线盘；关键转折：本期回到iOS #{rank}，Google仍在#5，iPhone端只记为榜尾回补；主力素材：僵尸压迫、资源采集、基地扩建、载具与限时地下城。",
        "6805006706": "趋势：2026年9月以原始部落篝火、萨满和联盟4X在iOS进入首发验证；关键转折：10月19日1.1.1仍处近期窗口，本期首次进入项目iOS榜#{rank}、Google#57，只记为双端榜尾信号；主力素材：篝火扩建部落、巨兽压迫、萨满编队、回合制远征和联盟世界地图。",
        "672150402": "趋势：2014年以海岛基地、登陆作战和异步攻防形成Supercell长线盘；关键转折：本期回到iOS #{rank}，Google未入榜，仍属后十名轮换；主力素材：海岛基地、登陆艇编队、火炮清障、英雄技能与特遣队行动。",
        "6740232087": "趋势：2025年以竖屏射击、基地扩张与联盟对抗承接轻量策略用户；关键转折：本期回到iOS #{rank}，Google#47，双端都在后段，尚无连续上行证据；主力素材：外星入侵、竖屏射击、英雄合成、基地防御与联盟地图。",
        "6741568655": "趋势：2025年以Mobile Legends美区独立版本、英雄收集和五人MOBA承接核心竞技盘；关键转折：本期iOS上升18位至#{rank}，Google未入榜，单日跃升只记为待验证信号；主力素材：英雄连招、五人团战、排位、皮肤与电竞赛事。",
        "1330123889": "趋势：2018年以百人战术竞技、赛季通行证和IP联动形成全球长线盘；关键转折：本期iOS上升18位至#{rank}，Google未入策略榜，未找到与今天同步的单一节点；主力素材：跳伞搜集、载具、团队枪战、限定地图与联动外观。",
        "6751086804": "趋势：2026年以龙族角色收集、战术编队与奇幻叙事进入首发验证；关键转折：本期iOS下跌21位至#{rank}，Google未入榜，前期跃升未连续保持；主力素材：龙族角色、技能演出、编队克制、Boss战与章节剧情。",
        "1642607669": "趋势：2026年以House of the Dragon IP、养龙与联盟4X进入首发运营；关键转折：10月15日Kalspire内容后，本期iOS下跌12位至#{rank}、Google升至#33，跨端反向需继续验证；主力素材：坦格利安角色、巨龙孵化、空战、城堡扩建与联盟争夺。",
        "1487451427": "趋势：2021年以卡通文明、英灵和龙养成承接联盟4X；关键转折：本期iOS下跌2位至#{rank}、Google反向上升8位至#28，9月v2.9.9节点已较早，不能解释本期跨端分化；主力素材：跨文明英灵、巨龙、卡通城建、元素编队与联盟攻城。",
        "1354260888": "趋势：2018年以文明选择、自由行军和联盟大地图建立长线4X盘，后期素材转向战力逆袭情景剧，近期更多展示城建资源与真实会战；关键转折：本期iOS上升4位至#{rank}、Google位于#26，单期上升不等于收入增长；主力素材：文明选择、自由行军、战力逆袭情景剧、城建资源与真实联盟会战。",
        "1464872022": "趋势：2020年全球上线后以职业克制、部署顺序与技能时机构成长线塔防核心；关键转折：Episode 17仍在开放窗口，本期iOS持平于#{rank}、Google下跌6位至#14，两端节奏不同；主力素材：新主线世界观、限定干员、多职业编队、格子部署与技能爆发。",
    }
    for games_path, trends_path, key, updates in (
        ("data/games-20261026.json", "data/trends-20261026.json", "packageName", google),
        ("data/ios-games-20261026.json", "data/ios-trends-20261026.json", "appId", ios),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        by_id = {str(game[key]): game for game in games}
        for product_id, summary in updates.items():
            game = by_id[product_id]
            trends[str(game["rank"])]["summary"] = summary.format(rank=game["rank"])
        updater.save(trends_path, trends)


def normalize_summary_rank_references():
    """Align every compact summary's current and cross-store ranks to today's two lists."""
    aliases = {
        "last war survival game": "last war survival",
        "evony the king s return": "evony",
        "rise of kingdoms lost crusade": "rise of kingdoms",
        "age of origins tower defense": "age of origins",
        "forge master idle rpg": "forge master",
        "marvel snap hero strategy ccg": "marvel snap",
        "marvel snap hero card game": "marvel snap",
        "top force commander": "top force",
        "kingdom guard tower defense td": "kingdom guard tower defense",
        "rise of castles ice and fire": "rise of castles",
        "rise of castles fire and war": "rise of castles",
    }

    def product_key(name):
        plain = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower()
        normalized = re.sub(r"[^a-z0-9]+", " ", plain).strip()
        return aliases.get(normalized, normalized)

    google_games = updater.load("data/games-20261026.json")
    ios_games = updater.load("data/ios-games-20261026.json")
    by_store = {
        "Google": {product_key(game["gameName"]): game for game in google_games},
        "iOS": {product_key(game["gameName"]): game for game in ios_games},
    }
    first_time = {("iOS", "6805006706")}

    def current_phrase(store_label, game, id_key):
        change = game["dailyChange"]
        if change == "NEW":
            if (store_label, str(game[id_key])) in first_time:
                return f"本期首次进入项目{store_label}榜#{game['rank']}"
            return f"本期回到{store_label} #{game['rank']}"
        if change == "=":
            return f"本期{store_label}持平于#{game['rank']}"
        direction = "上升" if change.startswith("+") else "下跌"
        return f"本期{store_label}{direction}{change[1:]}位至#{game['rank']}"

    for games_path, trends_path, store_label, counterpart_label, id_key in (
        ("data/games-20261026.json", "data/trends-20261026.json", "Google", "iOS", "packageName"),
        ("data/ios-games-20261026.json", "data/ios-trends-20261026.json", "iOS", "Google", "appId"),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        own_pattern = re.compile(
            rf"本期(?:首次进入项目{store_label}榜#\d+|回到{store_label}\s*#\d+|"
            rf"{store_label}(?:再)?(?:上升|下跌)\d+位至#\d+|{store_label}持平于#\d+|{store_label}位于#\d+)"
        )
        counterpart_pattern = re.compile(
            rf"{counterpart_label}(?:(?:上升|下跌)\d+位至|(?:升|跌)至|回榜|位于|仍高居|仍在|榜)?\s*#\d+"
        )
        counterpart_absent_pattern = re.compile(rf"{counterpart_label}未入(?:策略)?榜")
        for game in games:
            summary = trends[str(game["rank"])]["summary"]
            summary = own_pattern.sub(current_phrase(store_label, game, id_key), summary)
            counterpart = by_store[counterpart_label].get(product_key(game["gameName"]))
            replacement = (
                f"{counterpart_label}位于#{counterpart['rank']}" if counterpart else f"{counterpart_label}未入榜"
            )
            summary = counterpart_pattern.sub(replacement, summary)
            summary = counterpart_absent_pattern.sub(replacement, summary)
            trends[str(game["rank"])]["summary"] = summary
        updater.save(trends_path, trends)


if __name__ == "__main__":
    updater.main()
    refresh_rank_paths()
    refresh_visible_summaries()
    normalize_summary_rank_references()
