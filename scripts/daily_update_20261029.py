#!/usr/bin/env python3
"""Build the Beijing 2026-10-29 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
import unicodedata
from zoneinfo import ZoneInfo

import daily_update_20261028 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend


updater = prior.updater
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-29"
updater.STAMP = "20261029"
updater.PREVIOUS_STAMP = "20261028"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-31"
updater.GOOGLE_DATES = ("20261028",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261028",) + updater.IOS_DATES


def avatar_ios_profile(row, meta):
    """Create Avatar: Realms Collide from Apple and first-party publisher records."""
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
    screenshot = screenshots[0] if screenshots else icon
    release = (meta.get("releaseDate") or "")[:10]
    if release != "2025-03-18":
        raise RuntimeError(f"Avatar iOS release date requires review: {release!r}")
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
        "genre": "4X / IP策略 / 城建联盟战争",
        "keywords": "Avatar；Aang；Korra；元素弯曲；城市扩张；英雄编队；同伴；联盟战争；跨服战",
        "note": "Apple Lookup显示iOS美国区于2025-03-18上架；90天状态只使用本商店日期。",
        "assetRank": 105,
        "store": "ios",
    }
    company = {
        "en": "Tilting Point LLC / AN Games Co., Ltd.",
        "cn": "Tilting Point LLC（发行）/ AN Games Co., Ltd.（研发与运营）",
        "confidence": "已确认",
        "basis": "Apple美国区Lookup列Tilting Point LLC为seller；Tilting Point官方工作室页明确其为Avatar: Realms Collide发行商，并列AN Games为研发方；产品官方运营政策进一步列AN Games Co., Ltd.为运营主体。未把IP授权方误写为发行或研发主体。",
        "source": "https://www.tiltingpoint.com/studios",
    }
    analysis = trend(
        "趋势：2025年借Avatar IP、Aang/Korra等角色与元素弯曲切入，再由城市扩张、英雄编队、同伴养成和联盟4X承接；关键转折：本期首次进入项目iOS榜#60，10月SvS预赛仍在活动窗口，但榜尾入榜只记为待验证信号；主力素材：Aang与Korra、元素战斗、四国城市、同伴、世界地图与联盟会战。",
        "2025年3月全球上线。早期用Avatar: The Last Airbender与The Legend of Korra角色、原作配音和元素战斗降低4X理解门槛；进入长期运营后，以城市研究、资源扩张、英雄装备、同伴成长、联盟冲突和跨服竞争承接核心策略用户。",
        "本期首次进入项目保存的iOS美国策略畅销TOP60，位列第60名；产品上架早于90天窗口，项目缺少2026-07-31同口径完整基准，因此内部保留pending、页面按常规在榜展示。Google Play同日策略TOP60未收录。",
        "可确认节点包括2025年全球首发、联盟大规模对抗MGM，以及2026年10月3日至30日的SvS预赛Glowworm's Ruse；Apple Lookup记录10月28日版本更新。活动与本次入榜时间相邻，但没有证据证明其单独造成榜位变化。",
        "Apple当前商品图以Aang、Korra、Zuko等IP角色、元素技能、四国场景和英雄编队建立识别，再以城建、伙伴、联盟与世界地图承接4X深度。素材依据为Apple商品页及发行商官方资料，可信度为中。",
        "未来1—2个有效快照观察能否连续留榜并脱离第60名；同时在10月30日SvS预赛结束后核验是否回落，单日入榜不外推为长期增长。",
        store_url,
        [
            {"label": "Tilting Point官方产品页", "url": "https://www.tiltingpoint.com/games/avatar", "type": "primary"},
            {"label": "Tilting Point官方工作室与发行链", "url": "https://www.tiltingpoint.com/studios", "type": "company-audit"},
            {"label": "Avatar官方运营政策", "url": "https://avatarrc.zendesk.com/hc/en-us/articles/8911297780495-Game-Operation-Policy", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-29",
        status="已复核",
        confidence="中",
        basis="上架日、版本日期、玩法、图标和商店图来自Apple美国区Lookup/商品页；发行、研发与运营链由Tilting Point官方工作室页和产品官方运营政策交叉核验。素材只有Apple与发行方资料，不标高可信度。",
        changeReason="首次进入项目保存的iOS榜，按iOS自身releaseDate建立独立档案；10月SvS节点仅作相邻背景，不写成本次入榜的确定原因。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-29",
        status="已复核",
        confidence="中",
        scope="从2025年3月iOS上线与IP获量入口梳理到联盟跨服玩法、2026年10月SvS预赛和本次首次项目收录。",
        evidenceNote="官方资料支持产品结构、活动时间与发行链；缺少公开收入和投放数据，本次只按榜尾待验证信号处理。",
    )
    return game, company, analysis, icon, screenshot


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20261028.json",
        "data/enrichment-20261028.json",
        "data/trends-20261028.json",
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
            prior.prepare_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = prior.prior.prior.enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis
    enrichment = deepcopy(updater.load("data/enrichment-20261028.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261029.json", games)
    updater.save("data/enrichment-20261029.json", enrichment)
    updater.save("data/trends-20261029.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-29.json", {
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
        "data/ios-games-20261028.json",
        "data/ios-enrichment-20261028.json",
        "data/ios-trends-20261028.json",
        "appId",
    )
    historical = updater.merged_records(updater.history_specs("ios-", updater.IOS_DATES), "appId")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in current and row["appId"] not in historical]
    metadata = lookup(entrant_ids) if entrant_ids else {}
    if set(metadata) != set(entrant_ids):
        raise RuntimeError(f"Apple Lookup did not return every new product: {entrant_ids}")
    games, companies, analyses, bundle = [], {}, {}, {}
    for row in rows:
        app_id, rank = row["appId"], row["rank"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        elif app_id in historical:
            game, company, analysis = map(deepcopy, historical[app_id])
        elif app_id == "6479603752":
            game, company, analysis, icon, screenshot = avatar_ios_profile(row, metadata[app_id])
            bundle["105_icon"] = data_uri(icon, (256, 256))
            bundle["105_store"] = data_uri(screenshot, (720, 720))
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
            prior.prepare_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = prior.prior.prior.enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis
    enrichment = deepcopy(updater.load("data/ios-enrichment-20261028.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261029.json", games)
    updater.save("data/ios-enrichment-20261029.json", enrichment)
    updater.save("data/ios-trends-20261029.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if bundle:
        updater.save("assets/ios-assets-32.json", bundle)
        if "ios-assets-32.json" not in manifest["files"]:
            manifest["files"].append("ios-assets-32.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-29.json", {
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
    first_time = {("iOS", "6479603752")}
    for games_path, trends_path, store_label, release_basis, id_key in (
        ("data/games-20261029.json", "data/trends-20261029.json", "Google Play", "Google Play美国区商品页released日期", "packageName"),
        ("data/ios-games-20261029.json", "data/ios-trends-20261029.json", "iOS", "Apple Lookup releaseDate", "appId"),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        for game in games:
            change = game["dailyChange"]
            if change == "NEW":
                movement = "项目历史首次收录" if (store_label, str(game[id_key])) in first_time else "2026-10-28前一有效快照未入榜，回榜"
            elif change == "=":
                movement = "较2026-10-28前一有效快照持平"
            elif change.startswith("+"):
                movement = f"较2026-10-28前一有效快照上升{change[1:]}位"
            else:
                movement = f"较2026-10-28前一有效快照下降{change[1:]}位"
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

    google_games = updater.load("data/games-20261029.json")
    ios_games = updater.load("data/ios-games-20261029.json")
    by_store = {
        "Google": {product_key(game["gameName"]): game for game in google_games},
        "iOS": {product_key(game["gameName"]): game for game in ios_games},
    }
    first_time = {("iOS", "6479603752")}

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
        ("data/games-20261029.json", "data/trends-20261029.json", "Google", "iOS", "packageName"),
        ("data/ios-games-20261029.json", "data/ios-trends-20261029.json", "iOS", "Google", "appId"),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        own_pattern = re.compile(
            rf"本期(?:首次进入项目{store_label}榜#\d+|回到{store_label}\s*#\d+|"
            rf"{store_label}(?:再)?(?:上升|下跌|回落|升|跌)\d+位至#\d+|{store_label}持平于#\d+|{store_label}位于#\d+)"
        )
        counterpart_pattern = re.compile(
            rf"{counterpart_label}(?:(?:同产品|当前|同期|反向)?(?:上升|下跌)\d+位至|(?:同产品|当前|同期|反向)?(?:升|跌)至|"
            rf"(?:同产品|当前|同期|反向)?(?:回榜|位于|仍高居|仍在|榜)?\s*)#\d+"
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


def refresh_semantic_summaries():
    """Repair product-specific clauses whose old directional wording is no longer true."""
    updates = {
        "data/trends-20261029.json": {
            "com.run.tower.defense": "趋势：2024年先行测投、2025年全球上线后，塔防/类Thronefall移动塔防/昼建夜守的获量层承接城镇经营与联盟4X，形成快速头部增长；关键转折：本期Google下跌1位至#2，iOS下跌2位至#3，双端均从前一快照榜首回落但仍处头部；主力素材：骑马领主走位、昼建夜守、低多边形城镇、英雄与联盟战争。",
            "com.lilithgame.roc.gp": "趋势：2018年以文明选择与自由行军建立长线4X盘，后期素材转向战力逆袭情景剧，近期更多展示城建资源和真实会战；关键转折：本期Google持平于#19，iOS下跌1位至#27，平台名次小幅分化不等于收入变化；主力素材：文明选择、自由行军、战力逆袭情景剧、城建资源与真实联盟会战。",
            "com.gtarcade.ioe.global": "趋势：2021年以卡通文明、英灵和龙养成承接联盟4X；关键转折：本期Google下跌1位至#18，iOS上升1位至#30，双端反向幅度均小，未发现可确认的重大转折；主力素材：跨文明英灵、巨龙、卡通城建、元素编队与联盟攻城。",
            "com.wb.goog.got.conquest": "趋势：2017年借Game of Thrones IP、城堡建设与联盟4X建立长线盘；关键转折：九周年2026_10更新仍在窗口，本期Google上升1位至#40、iOS下跌8位至#35，跨端分化不能写成版本确定拉动；主力素材：剧集角色、巨龙、城堡扩建、研究树与联盟战争。",
            "com.snowprintstudios.tacticus": "趋势：2022年以Warhammer 40K正版阵营和短局六角战术切入，成熟期由新派系、限定角色和活动轮换支撑；关键转折：本期Google下跌1位至#41、iOS下跌5位至#48，双端同向回落但幅度不同，10月活动不足以解释全部变化；主力素材：战锤单位、六角格部署、派系克制、Boss与限定角色。",
        },
        "data/ios-trends-20261029.json": {
            "6739554056": "趋势：2024年先行测投、2025年全球上线后，塔防/类Thronefall移动塔防/昼建夜守的获量层承接城镇经营与联盟4X，形成快速头部增长；关键转折：本期iOS下跌2位至#3，Google下跌1位至#2，双端均从前一快照榜首回落但仍处头部；主力素材：骑马领主走位、昼建夜守、低多边形城镇、英雄与联盟战争。",
            "1354260888": "趋势：2018年以文明选择、自由行军和联盟大地图建立长线4X盘，后期素材转向战力逆袭情景剧，近期更多展示城建资源与真实会战；关键转折：本期iOS下跌1位至#27，Google持平于#19，单日分化不等于收入变化；主力素材：文明选择、自由行军、战力逆袭情景剧、城建资源与真实联盟会战。",
            "6738469826": "趋势：2025年以监狱建设、犯人管理和轻量经营承接策略用户；关键转折：本期iOS下跌8位至#38，Google上升1位至#27，前一日双端同向改善未延续，继续按待验证信号处理；主力素材：监狱扩建、人员调度、资源循环、冲突事件与经营升级。",
            "1342290011": "趋势：2018年以末日采集、基地建设和联盟战争形成长线生存盘；关键转折：本期回到iOS #46，Google同名产品位于#51，双端均在中后段但两条商店记录仍独立计算；主力素材：丧尸压迫、荒野采集、基地扩建、兵种编队与联盟大地图。",
        },
    }
    for trends_path, summaries in updates.items():
        ios = trends_path.startswith("data/ios-")
        games_path = "data/ios-games-20261029.json" if ios else "data/games-20261029.json"
        key = "appId" if ios else "packageName"
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        by_id = {str(game[key]): game for game in games}
        for product_id, summary in summaries.items():
            trends[str(by_id[product_id]["rank"])]["summary"] = summary
        updater.save(trends_path, trends)


if __name__ == "__main__":
    updater.main()
    refresh_rank_paths()
    normalize_summary_rank_references()
    refresh_semantic_summaries()
