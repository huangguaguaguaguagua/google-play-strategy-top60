#!/usr/bin/env python3
"""Build the Beijing 2026-10-28 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
import unicodedata
from zoneinfo import ZoneInfo

import daily_update_20261027 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend
from daily_update_20260821 import play_metadata


updater = prior.updater
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-28"
updater.STAMP = "20261028"
updater.PREVIOUS_STAMP = "20261027"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-30"
updater.GOOGLE_DATES = ("20261027",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261027",) + updater.IOS_DATES


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


def last_human_google_profile(row):
    """Create the first project record from Google and Iterflor sources."""
    metadata = play_metadata(row["packageName"])
    release = metadata.get("released") or ""
    if release != "2026-08-19":
        raise RuntimeError(f"Last Human Google released date requires review: {release!r}")
    game = {
        "rank": row["rank"],
        "packageName": row["packageName"],
        "gameName": row["gameName"],
        "developer": row.get("developer") or metadata.get("developer", "Iterflor Pte Ltd"),
        "totalInstalls": metadata.get("downloads", ""),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"],
        "store": "googlePlay",
        "storeUrl": metadata["url"],
        "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"],
        "shortDescription": metadata.get("description", ""),
        "description": (
            "以僵尸射击波次作为即时入口，战斗后回到庇护所升级建筑、储备资源并加固城墙；"
            "中后期通过英雄编队、废土探索、联盟协作与领地资源争夺承接长期策略循环。"
        ),
        "releaseDate": release,
        "releaseDateIso": release,
        "updatedDate": metadata.get("updated", ""),
        "assetRank": 84,
        "genre": "SLG / 城建生存 / 僵尸射击",
        "keywords": "丧尸；竖屏射击；尸潮；庇护所；英雄编队；废土探索；联盟；资源争夺",
        "note": "Google美国区商品页序列化released为2026-08-19；90天状态只使用本商店日期。",
    }
    company = {
        "en": "ITERFLOR PTE. LTD.",
        "cn": "ITERFLOR PTE. LTD.（新加坡研发与发行主体；更上层集团未确认）",
        "confidence": "已确认",
        "basis": "Google Play开发者信息、Last Human专属隐私政策与服务条款均列ITERFLOR PTE. LTD.为运营主体；新加坡公开企业记录可核验同名法律主体。未发现足以确认更上层集团的官方证据，因此不继续外推。",
        "source": "https://iterflor.com/lh/terms/en/privacy.html",
    }
    analysis = trend(
        "趋势：2026年8月以竖屏僵尸射击、尸潮压迫和‘最后指挥官’叙事上线，再由庇护所城建、英雄编队与联盟废土争夺承接；关键转折：本期首次进入项目Google榜#59，按本店8月19日released归类为近90天新品，仍处首发验证；主力素材：近身尸潮、移动射击、废墟求生、庇护所扩建、英雄队伍与联盟领地。",
        "Google美国区于2026年8月19日上架。获量层先用角色移动射击、弹药压力、巨量尸潮和变异Boss提供即时生存反馈；商店说明随后把用户带入建筑升级、资源储备、城墙加固、英雄招募、废土探索与联盟协作，保持从个人存活到势力扩张的成长链。",
        "本期首次进入项目保存的Google Play美国策略畅销TOP60，位列第59名；Google本店released日期落在2026年7月29日至10月27日的90天窗口内，因此独立归类为近三个月新上榜。iOS策略TOP60本期未收录。",
        "可确认节点为8月19日Google上架与10月19日商品页更新；公开版本说明没有披露足以解释本次入榜的重大系统变化，因此不把更新时间写成确定拉升原因。",
        "Google当前商品图与描述重点展示近距离射击、尸潮和Boss压迫，并以废墟庇护所、英雄成长、探索和联盟争夺承接。素材判断只有Google单一商店证据，可信度为中。",
        "未来1—2个有效快照观察能否连续留榜并脱离后十名；若快速退出，只记录为首发验证期榜尾信号，不推演长期走势。",
        metadata["url"],
        [
            {"label": "ITERFLOR / Last Human官方隐私政策", "url": "https://iterflor.com/lh/terms/en/privacy.html", "type": "company-audit"},
            {"label": "ITERFLOR官网", "url": "https://iterflor.com/", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-28",
        status="已复核",
        confidence="中",
        basis="上架日、版本日期、玩法、图标和商店图来自Google美国区商品页；法律主体由Google开发者信息、产品专属隐私政策及服务条款交叉核验。当前素材只有单一商店证据，不标高可信度。",
        changeReason="首次进入项目Google榜，按Google US released建立独立档案；未借用第三方榜位或未确认的集团归属。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-28",
        status="已复核",
        confidence="中",
        scope="从2026年8月Google上架梳理到10月19日商品页更新与本次首次进入项目TOP60。",
        evidenceNote="官方资料支持玩法结构和主体；缺少公开收入及投放数据，本次仅按近90天新品的榜尾信号处理。",
    )
    return game, company, analysis, metadata


def west_game_ios_profile(row, meta):
    """Create West Game's first project record from Apple and Leyi sources."""
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
    screenshot = screenshots[0] if screenshots else icon
    release = (meta.get("releaseDate") or "")[:10]
    if release != "2019-04-15":
        raise RuntimeError(f"West Game iOS release date requires review: {release!r}")
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
        "genre": "SLG / 4X / 西部城镇经营",
        "keywords": "美国西部；城镇建设；警长；牛仔与亡命徒；帮派；联盟集结；铁路战场",
        "note": "Apple Lookup显示iOS美国区于2019-04-15上架；90天状态只使用本商店日期。",
        "assetRank": 104,
        "store": "ios",
    }
    company = {
        "en": "LEXIANGCO.,LIMITED / LeyiGames / Shenzhen Leyi Network Co., Ltd.",
        "cn": "LEXIANGCO.,LIMITED（iOS法律主体）/ LeyiGames（发行品牌）/ 深圳乐易网络（产品体系）",
        "confidence": "已确认",
        "basis": "Apple美国区Lookup列LEXIANGCO.,LIMITED为seller；Leyi官方产品页直接列出West Game，官方隐私声明说明Shenzhen Leyi Network Co., Ltd.及其关联方以LeyiGames开发和发行移动游戏。未据此延伸推断更上层集团。",
        "source": "https://www.leyinetwork.com/en/products/",
    }
    analysis = trend(
        "趋势：2019年以美国西部城镇、警长与帮派冲突切入，再由兵种扩张、联盟集结和世界地图战争形成长线SLG循环；关键转折：本期首次进入项目保存的iOS榜#57，但产品上架已久且缺少精确90天基准，只按榜尾回补观察；主力素材：荒漠城镇、警长与牛仔、亡命徒、枪战、帮派集结和铁路战场。",
        "Apple美国区于2019年4月15日上架。产品从南北战争后的西部边疆叙事起步，先让玩家建设并定制城镇、任命警长、招募牛仔和亡命徒，再通过兵种训练、科技、世界玩家对抗和联盟集结承接长期SLG循环；现阶段属于成熟长线运营。",
        "本次首次进入项目保存的iOS美国策略畅销TOP60，位列第57名；产品上架早于90天窗口，且项目缺少2026-07-30的精确同口径完整基准，因此内部保留pending、页面按常规在榜展示。Google Play同日策略TOP60未收录。",
        "可确认节点包括2019年首发和2026年9月28日7.4.0版本；该版本加入联盟科技无限捐赠、训练容量道具、集结提醒、Railway Rampage和Cargo Escort。版本时间与本期回榜相邻，但没有证据证明其单独造成名次变化。",
        "Apple当前商品页以西部荒漠、城镇扩建、警长、牛仔/亡命徒、枪械与帮派战争建立题材识别，再以联盟集结、世界地图和铁路事件承接成熟期玩法。素材判断只有Apple与Leyi官方产品页证据，可信度为中。",
        "未来1—2个有效快照观察能否连续留榜并离开后十名；若再次退出，只记录为成熟产品的榜尾轮换，不把单日回榜外推为长期增长。",
        store_url,
        [
            {"label": "Leyi官方West Game产品页", "url": "https://www.leyinetwork.com/en/products/", "type": "primary"},
            {"label": "LeyiGames官方隐私与主体页", "url": "https://www.leyinetwork.com/en/privacy/", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-28",
        status="已复核",
        confidence="中",
        basis="上架日、版本、玩法、图标和商店图来自Apple美国区Lookup/商品页；发行链由Apple seller、Leyi官方West Game产品页和官方隐私声明交叉核验。当前素材只有Apple与厂商产品页证据，不标高可信度。",
        changeReason="首次进入项目保存的iOS榜，按iOS自身releaseDate建立独立档案；版本节点仅作相邻背景，不写成本次回榜的确定原因。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-28",
        status="已复核",
        confidence="中",
        scope="从2019年iOS上架和西部题材城建入口梳理到2026年9月7.4.0联盟与铁路玩法节点及本次首次项目收录。",
        evidenceNote="官方资料支持产品结构、版本时间与发行链；缺少公开收入和投放数据，本次只按成熟产品榜尾回补处理。",
    )
    return game, company, analysis, icon, screenshot


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20261027.json",
        "data/enrichment-20261027.json",
        "data/trends-20261027.json",
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
        elif package == "com.avenue.zombie.gp":
            game, company, analysis, metadata = last_human_google_profile(row)
            bundle["84_icon"] = data_uri(metadata["icon"], (256, 256))
            bundle["84_store"] = data_uri(metadata["screenshot"], (720, 720))
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
        analysis = prior.prior.enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/enrichment-20261027.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261028.json", games)
    updater.save("data/enrichment-20261028.json", enrichment)
    updater.save("data/trends-20261028.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    if bundle:
        updater.save("assets/assets-21.json", bundle)
        if "assets-21.json" not in manifest["files"]:
            manifest["files"].append("assets-21.json")
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-28.json", {
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
        "data/ios-games-20261027.json",
        "data/ios-enrichment-20261027.json",
        "data/ios-trends-20261027.json",
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
        elif app_id == "1453356737":
            game, company, analysis, icon, screenshot = west_game_ios_profile(row, metadata[app_id])
            bundle["104_icon"] = data_uri(icon, (256, 256))
            bundle["104_store"] = data_uri(screenshot, (720, 720))
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
        analysis = prior.prior.enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261027.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261028.json", games)
    updater.save("data/ios-enrichment-20261028.json", enrichment)
    updater.save("data/ios-trends-20261028.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if bundle:
        updater.save("assets/ios-assets-31.json", bundle)
        if "ios-assets-31.json" not in manifest["files"]:
            manifest["files"].append("ios-assets-31.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-28.json", {
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
    first_time = {("Google Play", "com.avenue.zombie.gp"), ("iOS", "1453356737")}
    for games_path, trends_path, store_label, release_basis, id_key in (
        ("data/games-20261028.json", "data/trends-20261028.json", "Google Play", "Google Play美国区商品页released日期", "packageName"),
        ("data/ios-games-20261028.json", "data/ios-trends-20261028.json", "iOS", "Apple Lookup releaseDate", "appId"),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        for game in games:
            change = game["dailyChange"]
            if change == "NEW":
                movement = (
                    "项目历史首次收录"
                    if (store_label, str(game[id_key])) in first_time
                    else "2026-10-27前一有效快照未入榜，回榜"
                )
            elif change == "=":
                movement = "较2026-10-27前一有效快照持平"
            elif change.startswith("+"):
                movement = f"较2026-10-27前一有效快照上升{change[1:]}位"
            else:
                movement = f"较2026-10-27前一有效快照下降{change[1:]}位"
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
    google = {
        "com.more.dayzsurvival.gp": "趋势：2017年以末日采集、基地建设和联盟战争形成长线生存盘；关键转折：本期回到Google #{rank}，iOS同产品#59，双端均在后段，只记为回补信号；主力素材：丧尸压迫、荒野采集、基地扩建、兵种编队与联盟大地图。",
        "com.kingsgroup.dcdly": "趋势：2025年以DC角色收集、地下基地经营和联盟PvP切入；关键转折：本期回到Google #{rank}，iOS#44，两端同时留榜但均处中后段，尚无连续上行证据；主力素材：Batman等DC英雄、Dark Multiverse、基地房间、阵容克制与联盟战。",
        "com.wb.goog.got.conquest": "趋势：2017年借Game of Thrones IP、城堡建设与联盟4X建立长线盘；关键转折：九周年2026_10更新仍在窗口，本期回到Google #{rank}、iOS升至#22，时间相邻但仍需连续快照确认；主力素材：剧集角色、巨龙、城堡扩建、研究树与联盟战争。",
        "com.more.lastfortress.gp": "趋势：2022年以地下庇护所剖面、幸存者分工和联盟4X形成成熟盘；关键转折：本期回到Google #{rank}，iOS未入榜，仍是后十名回补，未发现同步重大节点；主力素材：地下房间扩建、幸存者岗位、丧尸围城、装甲车与联盟战争。",
        "com.avenue.zombie.gp": "趋势：2026年8月以竖屏僵尸射击、尸潮压迫和‘最后指挥官’叙事上线，再由庇护所城建、英雄编队与联盟废土争夺承接；关键转折：本期首次进入项目Google榜#{rank}，按本店8月19日released归类为近90天新品，仍处首发验证；主力素材：近身尸潮、移动射击、废墟求生、庇护所扩建、英雄队伍与联盟领地。",
        "com.im30.ROE.gp": "趋势：2018年以中世纪城堡、兵种训练、驯龙与联盟4X形成长线盘；关键转折：本期Google上升17位至#{rank}，iOS未入榜，未找到能解释全部升幅的同步官方节点，先按单期信号记录；主力素材：废墟重建、巨龙、英雄、兵种集结与联盟攻城。",
        "com.gtarcade.ioe.global": "趋势：2021年以卡通文明、英灵和龙养成承接联盟4X；关键转折：本期Google再升10位至#{rank}、iOS跌至#31，连续两次Android上行仍伴随跨端分化；主力素材：跨文明英灵、巨龙、卡通城建、元素编队与联盟攻城。",
        "com.sivona.stormshot.e": "趋势：2022年以弹道射击谜题吸量，后由海岛城建、英雄与联盟4X承接；关键转折：本期Google上升9位至#{rank}，iOS未入榜，未发现同步重大官方节点；主力素材：弹道解谜、海盗宝藏、海岛扩建、英雄编队与联盟战争。",
        "com.lilithgame.roc.gp": "趋势：2018年以文明选择与自由行军建立长线4X盘，后期素材转向战力逆袭情景剧，近期更多展示城建资源和真实会战；关键转折：本期Google上升7位至#{rank}、iOS#33，单期升幅不等于收入增长；主力素材：文明选择、自由行军、战力逆袭情景剧、城建资源与真实联盟会战。",
        "com.justgame.jails": "趋势：2025年以监狱建设、犯人管理和轻量经营承接策略用户；关键转折：本期Google下跌11位至#{rank}、iOS升至#39，跨端反向说明需继续观察；主力素材：监狱扩建、人员调度、资源循环、冲突事件与经营升级。",
        "com.a3.topgirl.gplay": "趋势：2025年以角色收集、城市经营和帮派竞争承接轻量策略用户；关键转折：本期Google下跌8位至#{rank}，iOS未入榜，当前只记为单期回落；主力素材：角色养成、城市产业、豪车住宅、帮派冲突与经营升级。",
        "com.funfizz.palmon.gp": "趋势：2025年以奇幻生物收集、营地经营和联盟4X切入；关键转折：本期Google下跌6位至#{rank}，iOS未入榜，未发现同步重大节点；主力素材：Palmon收集、农场与工坊、探索战斗、城镇扩张和联盟地图。",
        "com.topwar.gp": "趋势：2019年以合成升级、英雄与联盟战争形成成熟4X盘；关键转折：本期Google下跌6位至#{rank}、iOS#41，两端均在中后段，单日回落不足以判断长线转弱；主力素材：单位合成、英雄、基地扩建、跨服战与IP联动。",
        "com.farlightgames.samo.gp": "趋势：2023年以奇幻自由行军与联盟围猎巨兽切入，成熟期由战宠和赛季竞合支撑；关键转折：本期Google再跌6位至#{rank}并落到末位，iOS未入榜，留榜风险需下一快照确认；主力素材：巨兽围猎、战宠捕捉、自由行军、英雄技能与联盟Boss。",
    }
    ios = {
        "6740189002": "趋势：2025年以科幻堡垒、塔防关卡与英雄养成切入；关键转折：本期回到iOS #{rank}，Google未入榜，当前只按后段回补处理；主力素材：科幻堡垒、炮塔布阵、英雄技能、波次防守与基地升级。",
        "1570095804": "趋势：2021年以塔防关卡、英雄合成和联盟攻城形成长线混合盘；关键转折：本期回到iOS #{rank}，Google未入榜，仍需验证能否连续留榜；主力素材：塔防路径、英雄合成、基地扩建、巨兽与联盟地图。",
        "6476261995": "趋势：2024年借Age of Empires IP、文明发展与联盟4X承接成熟策略用户；关键转折：本期回到iOS #{rank}而Google掉榜，跨端反向只记为平台节奏分化；主力素材：文明选择、历史英雄、城镇时代升级、兵种编队与联盟会战。",
        "672150402": "趋势：2014年以海岛基地、登陆作战和异步攻防形成Supercell长线盘；关键转折：本期iOS上升22位至#{rank}，Google未入榜，10月Blitz仍是近期背景但不能单独解释全部升幅；主力素材：海岛基地、登陆艇编队、火炮清障、英雄技能与特遣队行动。",
        "1599937506": "趋势：2022年以Warhammer 40K IP、六角格战术与角色养成建立核心盘；关键转折：本期iOS上升22位至#{rank}，Google#43，10月生存活动时间相邻但仍需连续留位验证；主力素材：阵营角色、六角格部署、技能连携、Boss与限时生存活动。",
        "6744812012": "趋势：2025年以末日求生、角色收集和轻量经营切入；关键转折：本期iOS上升19位至#{rank}，Google未入榜，单期跃升不直接归因为某一活动；主力素材：末日角色、避难所经营、合成升级、战斗编队与联盟竞争。",
        "1035712810": "趋势：2017年借Game of Thrones IP、城堡建设与联盟4X建立长线盘；关键转折：九周年2026_10更新仍在窗口，本期iOS上升13位至#{rank}、Google回榜#57，两端改善但仍需连续验证；主力素材：剧集角色、巨龙、城堡扩建、研究树与联盟战争。",
        "625257520": "趋势：2014年以Warcraft角色、卡组构筑和短局对战形成长线卡牌盘；关键转折：Reign of the Black Empire已上线，本期iOS下跌17位至#{rank}，需继续区分资料片峰值与中期承接；主力素材：Old Gods、卡牌揭示、职业套牌、战棋与资料片内容。",
        "6755585789": "趋势：2025年以Overgeared IP、背包合成与角色养成切入；关键转折：本期iOS下跌9位至#{rank}、Google#36，跨端差距扩大，未发现同步重大节点；主力素材：Grid角色、背包合成、装备升级、技能爆发与关卡Boss。",
        "6741568655": "趋势：2025年以Mobile Legends美区独立版本、英雄收集和五人MOBA承接核心竞技盘；关键转折：本期iOS回落7位至#{rank}，Google未入榜，上期跃升未完全保持；主力素材：英雄连招、五人团战、排位、皮肤与电竞赛事。",
        "1071976327": "趋势：2016年以城堡扩建、英雄和联盟战争建立长线4X盘；关键转折：Heroic Saga仍在近期窗口，本期iOS再跌7位至#{rank}、Google升至#26，跨端反向不能写成版本确定拉动；主力素材：英雄、城堡扩建、Battle Spirit、联盟集结与跨服战。",
        "1342290011": "趋势：2018年以末日采集、基地建设和联盟战争形成长线生存盘；关键转折：本期iOS下跌7位至#{rank}、Google同名产品回榜#48，跨端路径不同；主力素材：丧尸压迫、荒野采集、基地扩建、兵种编队与联盟大地图。",
    }
    google = {
        "com.run.tower.defense": "趋势：2024年先行测投、2025年全球上线后，塔防/类Thronefall移动塔防/昼建夜守的获量层承接城镇经营与联盟4X，形成快速头部增长；关键转折：本期Google上升1位至#{rank}并与iOS同居榜首，但单日换位不写成长期优势扩大；主力素材：骑马领主走位、昼建夜守、低多边形城镇、英雄和联盟战争。",
        "com.gof.global": "趋势：2023年以极寒熔炉和幸存者分工建立差异化，再把硬核末日叙事扩展为捕鱼、采矿与救援事件，长期维持头部；关键转折：本期Google回落1位至#{rank}、iOS仍处前列，属于榜首小幅换位而非结构性退潮；主力素材：极寒求生、熔炉扩建、幸存者岗位与轻量资源反馈。",
        "com.doradogames.conflictnations.worldwar3": "趋势：2017年网页端上线、2020年扩展到Android后，以持续数天至数周的实时行军、外交和现代战争服务硬核大战略用户；关键转折：本期回到Google #{rank}、iOS位于#41，两端都在后段，先按榜尾回补观察；主力素材：全球领土地图、坦克/航母/战机、实时战线、联盟外交与核武。",
        "com.wb.goog.got.conquest": "趋势：2017年借Game of Thrones IP、城堡建设与联盟4X建立长线盘；关键转折：九周年2026_10更新仍在窗口，本期Google上升16位至#{rank}、iOS反向回落至#27，平台节奏分化仍需连续快照确认；主力素材：剧集角色、巨龙、城堡扩建、研究树与联盟战争。",
        "com.justgame.jails": "趋势：2025年以监狱建设、犯人管理和轻量经营承接策略用户；关键转折：本期Google上升5位至#{rank}、iOS也上升至#31，双端同向但单日同步不足以证明共同活动驱动；主力素材：监狱扩建、人员调度、资源循环、冲突事件与经营升级。",
        "com.im30.ROE.gp": "趋势：2018年以中世纪城堡、兵种训练、驯龙与联盟4X形成长线盘；关键转折：本期Google上升4位至#{rank}，未找到能解释全部升幅的同步官方节点，只记为单期回升；主力素材：废墟重建、巨龙、英雄、兵种集结与联盟攻城。",
        "com.snowprintstudios.tacticus": "趋势：2022年以Warhammer 40K正版阵营和短局六角战术切入，成熟期由新派系、限定角色和活动轮换支撑；关键转折：本期Google上升3位至#{rank}、iOS却下跌10位至#42，跨端反向不支持把变化归因于单一内容节点；主力素材：战锤单位、六角格部署、派系克制、Boss与限定角色。",
        "com.kingsgroup.dcdly": "趋势：2025年以DC角色收集、地下基地经营和联盟PvP切入；关键转折：本期Google上升3位至#{rank}、iOS位于#48，两端仍在中后段，尚无连续上行证据；主力素材：Batman等DC英雄、Dark Multiverse、基地房间、阵容克制与联盟战。",
        "com.mrtgd2us.google": "趋势：2025年用武装鸭子和昼建夜守形成轻松但高识别的末日塔防，再以武器等级和随机技能构筑延长短局变化；关键转折：本期Google下跌4位至#{rank}，没有同步重大官方节点，只记为中后段回落；主力素材：鸭子小队、昼建夜守、尸潮、武器等级与Roguelike组合。",
        "com.more.dayzsurvival.gp": "趋势：2017年以末日采集、基地建设和联盟战争形成长线生存盘；关键转折：本期Google下跌4位至#{rank}，iOS的Last Shelter: War Z为不同商店条目，不能据名称直接串榜；主力素材：丧尸压迫、荒野采集、基地扩建、兵种编队与联盟大地图。",
        "com.spark.sp.gp": "趋势：2026年7月用电影化毒枭崛起、秘密工厂和危险运输切入，仍处上线早期；关键转折：本期Google下跌3位至#{rank}，近90天新品身份不变，单期回落不外推成熟期趋势；主力素材：街头逆袭、秘密实验室、运输风险、洗钱门店和黑帮地盘。",
        "com.yottagames.gameofmafia": "趋势：2020年以黑帮首领、地盘战争和豪华生活建立稳定付费盘，成熟期通过逆袭情景剧、联动和联盟活动激活回流；关键转折：本期Google下跌3位至#{rank}，没有可确认的同步重大转折；主力素材：等级逆袭、黑帮冲突、豪车豪宅、女性角色与IP联动。",
        "com.lavalabs.autodrill": "趋势：2026年6月以自动钻探飞船、手动摇杆和逐块击穿行星上线，把即时破坏反馈承接到武器与装备成长；关键转折：本期Google下跌3位至#{rank}，10月修复版本不足以解释本次变化；主力素材：方块行星、连锁爆炸、武器弹幕、技能融合与区域推进。",
        "com.yottagames.mafiawar": "趋势：2017年上线后以Level 1 Crook到Boss的夸张逆袭短剧建立品牌记忆，成熟期再接豪车、伴侣、地盘与联盟赛季；关键转折：本期Google下跌3位至#{rank}，仅按榜尾压力信号处理；主力素材：等级逆袭、黑帮权力、豪车美女、剧情选择与城市地盘。",
    }
    ios = {
        "6767834940": "趋势：2026年以滑动扩军和轻量王国经营切入，短闯关后由封地、税收、领主与狮鹫养成承接；关键转折：本期iOS上升1位至#{rank}，仍处首轮商业化验证，不能由单日名次推演稳定性；主力素材：人群穿门、救回领民、册封骑士、狮鹫与王国扩张。",
        "1642607669": "趋势：2026年以House of the Dragon IP、养龙与联盟4X进入首发运营；关键转折：10月15日Kalspire内容后，本期iOS上升3位至#{rank}，但Google端节奏不同，版本仅作时间背景；主力素材：坦格利安角色、巨龙孵化、空战、城堡扩建与联盟争夺。",
        "1354260888": "趋势：2018年以文明选择、自由行军和联盟大地图建立长线4X盘，后期素材转向战力逆袭情景剧，近期更多展示城建资源与真实会战；关键转折：本期iOS上升7位至#{rank}，单期跃升不等于收入增长；主力素材：文明选择、自由行军、战力逆袭情景剧、城建资源与真实联盟会战。",
        "6738469826": "趋势：2025年以监狱建设、犯人管理和轻量经营承接策略用户；关键转折：本期iOS上升9位至#{rank}、Google也升至#28，双端同向只记为待验证信号；主力素材：监狱扩建、人员调度、资源循环、冲突事件与经营升级。",
        "1611722542": "趋势：2022年以中世纪塔防、英雄收集与领地经营形成轻量策略循环；关键转折：本期iOS上升5位至#{rank}，仍位于后十名，需验证是否能连续脱离榜尾；主力素材：中世纪城墙、英雄布阵、密集敌潮、防御塔升级与领地扩张。",
        "6776076449": "趋势：2026年8月以三分钟实时PvP、植物合并升级和轻量塔防切入，仍处首发验证；关键转折：10月15日2.0.2870加入Pirate Captain、新植物与Ace Plan，本期回到iOS #{rank}，时间相邻但不作确定归因；主力素材：双路实时对抗、三分钟倒计时、植物合并、海盗船长与Auto Chess模式。",
        "1575590830": "趋势：2021年从极简单塔守波起步，靠永久研究、卡牌和锦标赛社区形成长期积累；关键转折：v29加入全局预设、Mythic联赛并重做Vault与Harmony Tree，本期回到iOS #{rank}，仍需连续留位验证；主力素材：单塔清屏、指数成长、Boss波次、构筑预设与锦标赛。",
        "6447612873": "趋势：2022年以潜艇舰队、基地经营与海战SLG建立核心盘；关键转折：1.175.0于10月21日加入精英招募角色与回归福利，本期回到iOS #{rank}，更新与回榜相邻但因果未确认；主力素材：潜艇编队、海上基地、舰长招募、航线争夺与联盟海战。",
        "6760406772": "趋势：2026年6月上架后，以末日地下庇护所剖面、营救幸存者和僵尸压力承接房间建设、英雄编队与联盟战争；关键转折：本期回到iOS #{rank}，仍属上线早期的中后段信号；主力素材：地下庇护所剖面、救援抉择、僵尸追击、房间扩建与英雄小队。",
        "1465860096": "趋势：2019年以二战战场、女性军官和实时军团战争建立军事4X用户盘，长期由国家阵营和联盟竞争维持；关键转折：本期回到iOS #{rank}且位于后十名，未发现与今天同步的重大转折；主力素材：二战机械、军官收集、坦克、国家阵营、军团集结与实时大地图。",
        "6755173751": "趋势：2026年以三分钟合成塔防进入首发验证，用随机召唤和二合一进化兼顾即时爽感与构筑；关键转折：本期回到iOS #{rank}，PvP和英雄流派仍在验证付费承接；主力素材：连续合成、稀有进化、怪潮压线和三分钟翻盘。",
        "1453356737": "趋势：2019年以美国西部城镇、警长与帮派冲突切入，再由兵种扩张、联盟集结和世界地图战争形成长线SLG循环；关键转折：本期首次进入项目保存的iOS榜#{rank}，产品上架已久且缺少精确90天基准，只按榜尾回补观察；主力素材：荒漠城镇、警长与牛仔、亡命徒、枪战、帮派集结和铁路战场。",
        "1035712810": "趋势：2017年借Game of Thrones IP、城堡建设与联盟4X建立长线盘；关键转折：九周年2026_10更新仍在窗口，本期iOS下跌5位至#{rank}、Google反向升至#41，跨端分化需要继续验证；主力素材：剧集角色、巨龙、城堡扩建、研究树与联盟战争。",
        "6446389130": "趋势：2023年以三消加SLG的成熟框架切入，用冰封城堡、巨龙和奇幻英雄与同类题材拉开入口；关键转折：本期iOS下跌4位至#{rank}，未发现同步重大节点；主力素材：冰雪奇幻、三消、巨龙、英雄阵容与城堡扩张。",
        "1599937506": "趋势：2022年以Warhammer 40K IP、六角格战术与角色养成建立核心盘；关键转折：本期iOS下跌11位至#{rank}、Google反向升至#40，10月活动不足以解释跨端反向；主力素材：阵营角色、六角格部署、技能连携、Boss与限时生存活动。",
        "672150402": "趋势：2014年以海岛基地、登陆作战和异步攻防形成Supercell长线盘；关键转折：本期iOS下跌14位至#{rank}，10月Blitz仍是近期背景但不能抵消本期回落；主力素材：海岛基地、登陆艇编队、火炮清障、英雄技能与特遣队行动。",
        "852912420": "趋势：2014年以符文构筑、属性克制和回合制魔灵收集形成全球长线盘；关键转折：9.3.6加入Cosmic Worm，本期iOS下跌9位至#{rank}，版本与变化相邻但不作确定归因；主力素材：稀有召唤、符文搭配、魔灵养成、跨服竞技与赛事对局。",
    }
    for games_path, trends_path, key, updates in (
        ("data/games-20261028.json", "data/trends-20261028.json", "packageName", google),
        ("data/ios-games-20261028.json", "data/ios-trends-20261028.json", "appId", ios),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        by_id = {str(game[key]): game for game in games}
        for product_id, summary in updates.items():
            game = by_id[product_id]
            trends[str(game["rank"])]["summary"] = summary.format(rank=game["rank"])
        updater.save(trends_path, trends)


def normalize_summary_rank_references():
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

    google_games = updater.load("data/games-20261028.json")
    ios_games = updater.load("data/ios-games-20261028.json")
    by_store = {
        "Google": {product_key(game["gameName"]): game for game in google_games},
        "iOS": {product_key(game["gameName"]): game for game in ios_games},
    }
    first_time = {("Google", "com.avenue.zombie.gp"), ("iOS", "1453356737")}

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
        ("data/games-20261028.json", "data/trends-20261028.json", "Google", "iOS", "packageName"),
        ("data/ios-games-20261028.json", "data/ios-trends-20261028.json", "iOS", "Google", "appId"),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        own_pattern = re.compile(
            rf"本期(?:首次进入项目{store_label}榜#\d+|回到{store_label}\s*#\d+|"
            rf"{store_label}(?:再)?(?:上升|下跌|回落)\d+位至#\d+|{store_label}持平于#\d+|{store_label}位于#\d+)"
        )
        counterpart_pattern = re.compile(
            rf"{counterpart_label}(?:(?:同产品|当前|同期)?(?:上升|下跌)\d+位至|(?:同产品|当前|同期)?(?:升|跌)至|"
            rf"(?:同产品|当前|同期)?(?:回榜|位于|仍高居|仍在|榜)?\s*)#\d+"
        )
        counterpart_absent_pattern = re.compile(rf"{counterpart_label}(?:策略榜)?未入榜")
        for game in games:
            summary = trends[str(game["rank"])]["summary"]
            summary = own_pattern.sub(current_phrase(store_label, game, id_key), summary)
            counterpart = by_store[counterpart_label].get(product_key(game["gameName"]))
            replacement = f"{counterpart_label}位于#{counterpart['rank']}" if counterpart else f"{counterpart_label}未入榜"
            summary = counterpart_pattern.sub(replacement, summary)
            summary = counterpart_absent_pattern.sub(replacement, summary)
            trends[str(game["rank"])]["summary"] = summary
        updater.save(trends_path, trends)


if __name__ == "__main__":
    updater.main()
    refresh_rank_paths()
    refresh_visible_summaries()
    normalize_summary_rank_references()

