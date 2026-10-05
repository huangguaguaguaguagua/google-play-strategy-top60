#!/usr/bin/env python3
"""Build the Beijing 2026-10-05 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import daily_update_20261002 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, trend
from daily_update_20260821 import play_metadata


updater = prior.updater
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-05"
updater.STAMP = "20261005"
updater.PREVIOUS_STAMP = "20261002"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-07"
updater.GOOGLE_DATES = ("20261002",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261002",) + updater.IOS_DATES


def _last_beacon_google(row):
    """Build Last Beacon from its US store page and official Yalla sources."""
    metadata = play_metadata(row["packageName"])
    release = metadata.get("released") or ""
    if release != "2026-05-11":
        raise RuntimeError(f"Last Beacon Google released date requires review: {release!r}")
    game = {
        "rank": row["rank"],
        "packageName": row["packageName"],
        "gameName": row["gameName"],
        "developer": row.get("developer") or metadata.get("developer", "YG Technology FZ-LLC"),
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
            "在海洋淹没后的末日世界扩建灯塔庇护所、组织舰队探索，抵御鲨鱼、海怪与海盗，"
            "再由联盟、海上要塞和世界首领承接长期策略竞争。"
        ),
        "releaseDate": release,
        "releaseDateIso": release,
        "updatedDate": metadata.get("updated", ""),
        "assetRank": 82,
        "genre": "SLG / 4X / 海洋生存城建",
        "keywords": "海洋末日；灯塔；庇护所；鲨鱼；舰队；海怪；海盗；联盟；海上要塞；4X",
        "note": "Google美国区商品页序列化released为2026-05-11；90天状态只使用本商店日期。",
    }
    company = {
        "en": "YG Technology FZ-LLC / Yalla Game / Yalla Group",
        "cn": "YG Technology FZ-LLC（Yalla Game发行体系／Yalla Group）",
        "confidence": "已确认",
        "basis": "Google Play开发者页以YG Technology FZ-LLC为法律主体，并明确以Yalla Game介绍游戏业务；Yalla Group官网将Yalla Game列为集团子公司。",
        "source": "https://play.google.com/store/apps/dev?id=7399304807843371837&hl=en_US&gl=US",
    }
    analysis = trend(
        "趋势：2026年5月以海洋淹没后的灯塔庇护所、舰队探索和鲨鱼压力上线，随后加入联盟、海上要塞及世界首领，本次首次进入项目Google #51；关键转折：当前2.5.5版本仅披露服务器性能与稳定性优化，未发现可确认的重大结构转折；主力素材：孤岛灯塔、篝火与鲨鱼包围的生存压力，承接漂浮庇护所扩建、舰队、海怪/海盗和联盟海域争夺。",
        "Google美国区于2026年5月上架，首层用被海水淹没的孤岛、灯塔、篝火和鲨鱼制造生存压力，再将用户带入漂浮庇护所扩建、资源管理、舰队探索以及联盟海域竞争。上线不足半年，但已早于本期90天窗口，不按近三个月新品展示。",
        "本次首次进入项目自2026年8月19日起保存的Google Play美国策略畅销TOP60，位列第51名；上架早于2026年7月7日窗口且缺少精确90天同口径基准，内部状态为pending、页面按常规在榜展示。",
        "当前2.5.5版本只披露服务器性能和稳定性优化，没有公开足以解释本次入榜的新增系统或重大活动；产品已由首发庇护所生存延伸至联盟与世界首领，但未发现可确认的重大转折。",
        "Google首张商店图以灯塔、篝火和环岛鲨鱼建立即时压力，后续商品页素材转向淹没废墟、漂浮基地扩建、舰队、海怪/海盗和联盟地图。素材判断由Google商品页并以Apple官方版本说明交叉，可信度为中。",
        "观察未来1—2个有效快照能否离开Google后十名，并核对联盟与世界首领内容是否伴随连续留榜；没有连续数据前不把首次#51写成版本驱动或长期增长。",
        metadata["url"],
        [
            {"label": "Last Beacon官网", "url": "https://www.lastbeacon.net", "type": "primary"},
            {"label": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6761043541", "type": "primary"},
            {"label": "Yalla Group官网", "url": "https://www.yalla.com", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-05",
        status="已复核",
        confidence="中",
        basis="上架日、玩法、图标和商店图来自Google美国区商品页；当前版本由Apple官方商品页交叉；公司链由Google开发者页与Yalla Group官网核验。",
        changeReason="首次进入项目Google榜，按Google US released建立独立档案，未借用Apple日期或第三方榜位。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-05",
        status="已复核",
        confidence="中",
        scope="从2026年5月Google上架梳理到2.5.5稳定性版本、多人内容扩展与本次首次进入项目TOP60。",
        evidenceNote="版本节点与本次入榜时间相邻但没有公开收入或投放数据证明因果；按首次入榜待验证信号处理。",
    )
    return game, company, analysis, metadata


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20261002.json",
        "data/enrichment-20261002.json",
        "data/trends-20261002.json",
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
        elif package == "com.hnhs.endlesssea.gp":
            game, company, analysis, metadata = _last_beacon_google(row)
            bundle["82_icon"] = data_uri(metadata["icon"], (256, 256))
            bundle["82_store"] = data_uri(metadata["screenshot"], (720, 720))
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
        analysis = prior.enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/enrichment-20261002.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261005.json", games)
    updater.save("data/enrichment-20261005.json", enrichment)
    updater.save("data/trends-20261005.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    if bundle:
        updater.save("assets/assets-19.json", bundle)
        if "assets-19.json" not in manifest["files"]:
            manifest["files"].append("assets-19.json")
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-05.json", {
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
        "data/ios-games-20261002.json",
        "data/ios-enrichment-20261002.json",
        "data/ios-trends-20261002.json",
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
            updater.clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = prior.enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261002.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261005.json", games)
    updater.save("data/ios-enrichment-20261005.json", enrichment)
    updater.save("data/ios-trends-20261005.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-05.json", {
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
