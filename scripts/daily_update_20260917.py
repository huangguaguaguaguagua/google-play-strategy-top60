#!/usr/bin/env python3
"""Build the Beijing 2026-09-17 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, parse_ios, save, trend
from daily_update_20260821 import play_metadata
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-09-17"
GOOGLE_DATE = "2026-09-17"
GOOGLE_BASELINE = "2026-06-19"
IOS_DATE = "2026-09-17"
IOS_BASELINE = "2026-06-19"

GOOGLE_DATES = (
    "20260916", "20260915", "20260914", "20260911", "20260910", "20260909", "20260908",
    "20260907", "20260904", "20260903", "20260902", "20260901", "20260831", "20260828",
    "20260827", "20260826", "20260825", "20260824", "20260821", "20260820", "20260819d",
)
IOS_DATES = (
    "20260916", "20260915", "20260914", "20260911", "20260910", "20260909", "20260908",
    "20260907", "20260904", "20260903", "20260902", "20260901", "20260831", "20260828",
    "20260827", "20260826", "20260825", "20260824", "20260821", "20260820", "20260819",
)


def history_specs(prefix, dates):
    return [
        (
            f"data/{prefix}games-{date}.json",
            f"data/{prefix}enrichment-{date}.json",
            f"data/{prefix}trends-{date}.json",
        )
        for date in dates
    ]


def clean_analysis(analysis):
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


def audit_google(rows):
    try:
        return appbrain_audit(rows)
    except Exception as exc:
        return {
            "sourceRole": "audit-only",
            "sourceUrl": "https://www.appbrain.com/stats/google-play-rankings/top_grossing/strategy/us",
            "status": "unavailable",
            "error": f"{type(exc).__name__}: {exc}",
            "note": "审计源失败不覆盖或阻断Google Play直连榜单。",
        }


def aliens_profile(row, metadata):
    package = row["packageName"]
    store_url = metadata["url"]
    release = metadata.get("released") or "2024-11-15"
    if release != "2024-11-15":
        raise RuntimeError(f"Unexpected Aliens vs Zombies release date: {release}")
    game = {
        "rank": row["rank"],
        "packageName": package,
        "gameName": row["gameName"],
        "developer": metadata.get("developer") or row.get("developer", "GAMEGEARS LTD"),
        "totalInstalls": metadata.get("downloads", ""),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"],
        "store": "googlePlay",
        "storeUrl": store_url,
        "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"],
        "shortDescription": metadata.get("description", ""),
        "description": "Alien invasion tower defense：布置与升级防御塔、控制敌人路径、平衡资源，并抵御丧尸潮。",
        "releaseDate": release,
        "updatedDate": metadata.get("updated", ""),
        "genre": "塔防 / 丧尸 / 单机策略",
        "keywords": "外星入侵；丧尸；塔防；路径控制；防御塔升级；资源管理；离线",
        "note": "",
        "releaseDateIso": release,
        "assetRank": 76,
        "comparison90d": comparison(None, row["rank"], GOOGLE_DATE, GOOGLE_BASELINE, True, release),
    }
    company = {
        "en": "GAMEGEARS LTD",
        "cn": "GAMEGEARS LTD（塞浦路斯发行与研发主体；未发现更大集团归属披露）",
        "confidence": "已确认",
        "basis": "Google Play店铺发行名为GAMEGEARS LTD；官方隐私政策列明同名法律主体及塞浦路斯注册地址。未找到可确认的更上层集团披露。",
        "source": "https://www.gamegears.online/privacy-policy",
    }
    analysis = trend(
        "趋势：2024年以卡通外星人、丧尸潮和单机塔防上架，当前由路径控制、塔位布局与防御塔升级承接；关键转折：未发现可确认的重大转折/长期稳定运营，本次首次进入项目记录的Google TOP60；主力素材：密集丧尸波次、不同射程塔位、升级分支与基地防线。",
        "2024年11月上架，商品页从一开始即把外星入侵包装与经典塔防结合：玩家布置并升级防御塔、控制敌军行进路线、分配有限资源并抵御连续丧尸潮；离线单机是其区别于联盟4X产品的持续入口。",
        "上架日期早于本期90天窗口；本次首次出现在项目保存的Google Play美国策略畅销TOP60，位列第60名。因缺少2026-06-19同口径基准，内部保持pending并按常规展示。",
        "官方商品页显示2026年8月31日更新，并在当前商店活动中突出Boss挑战与Fire Crossbow Tower解锁；除这一活动节点外，未发现可确认的玩法重构或商业化重大转折。",
        "卡通外星人对抗丧尸、分路推进的尸潮、塔位覆盖范围、火力升级选择、资源不足压力、Boss攻城与Fire Crossbow Tower奖励。素材判断仅基于Google商品页和当前商店图，可信度为中。",
        "观察首次#60是否只是Boss活动附近的榜尾脉冲，以及活动结束后能否连续留榜；没有连续快照前不推断长期趋势。",
        store_url,
        [{"label": "GAMEGEARS官方隐私政策", "url": "https://www.gamegears.online/privacy-policy", "type": "primary"}],
    )
    return game, company, clean_analysis(analysis)


def age_of_spirits_profile(row, metadata):
    package = row["packageName"]
    store_url = metadata["url"]
    release = metadata.get("released") or "2026-09-16"
    if release != "2026-09-16":
        raise RuntimeError(f"Unexpected Age of Spirits release date: {release}")
    game = {
        "rank": row["rank"],
        "packageName": package,
        "gameName": row["gameName"],
        "developer": metadata.get("developer") or row.get("developer", "LeyiGames"),
        "totalInstalls": metadata.get("downloads", ""),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"],
        "store": "googlePlay",
        "storeUrl": store_url,
        "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"],
        "shortDescription": metadata.get("description", ""),
        "description": "以篝火建立部落，建设祭坛、采石场与伐木场，培养萨满和军队，并在世界地图争夺资源、圣地与联盟领土。",
        "releaseDate": release,
        "updatedDate": metadata.get("updated", ""),
        "genre": "SLG / 4X / 部落经营",
        "keywords": "原始部落；篝火；萨满；城建；世界地图；联盟；4X；资源争夺",
        "note": "",
        "releaseDateIso": release,
        "assetRank": 75,
        "comparison90d": comparison(None, row["rank"], GOOGLE_DATE, GOOGLE_BASELINE, True, release),
    }
    company = {
        "en": "LeyiGames / Shenzhen Leyi Network Co., Ltd. / APPLOVIN CYPRUS LIMITED",
        "cn": "LeyiGames（店铺品牌）/ 深圳乐易网络（产品体系）/ APPLOVIN CYPRUS LIMITED（Google Play法律主体）",
        "confidence": "已确认",
        "basis": "Google Play列明LeyiGames为店铺品牌、APPLOVIN CYPRUS LIMITED为开发者法律主体；Leyi官网以Shenzhen Leyi Network Co., Ltd.介绍其模拟策略游戏业务。未据此延伸推断当前更上层集团归属。",
        "source": "https://www.leyinetwork.com/",
    }
    analysis = trend(
        "趋势：美国区9月16日上架即以原始部落篝火、萨满和联盟4X进入首发验证，本次首次进入Google TOP60；关键转折：首发版本同步新增七种语言、11级兵种与萨满伤势机制，尚无更长期转折可判断；主力素材：从单一篝火扩建部落、萨满编队、巨兽威胁和联盟世界地图争夺。",
        "Google Play美国区released日期为2026年9月16日。首发入口以‘从一团火建立部落’呈现城建成长，再把祭坛、采石场、伐木场与兵种训练承接到萨满编队、世界地图资源争夺、圣地Boss和联盟战争；上线时间短，仍处首发验证。",
        "美国区上架次日首次进入项目保存的Google Play策略畅销TOP60，当前第59名；按同商店released日期落在90天窗口内，归类为近三个月新上榜。没有连续快照前不把首日排名写成稳定趋势。",
        "9月16日版本同时加入德、法、葡、西、日、韩与繁中七种语言，开放11级士兵，并重做萨满部署、伤势与升级；这是可确认的首发范围扩张和战斗系统节点，但尚不能判断其收入影响。",
        "篝火到聚落的建设前后对比、巨型野兽压迫、萨满与部族战士编队、祭坛和资源建筑升级、世界地图行军、圣地争夺与联盟集结。素材判断仅基于当前Google商品页与商店图，可信度为中。",
        "观察9月18—21日能否脱离榜尾并连续留榜，以及多语言与萨满改版后的首发买量是否在Google美国区形成可重复排名；不推演未来表现。",
        store_url,
        [{"label": "Leyi官方公司页", "url": "https://www.leyinetwork.com/", "type": "primary"}],
    )
    return game, company, clean_analysis(analysis)


def build_google(rows, source_info):
    current = records(
        "data/games-20260916.json", "data/enrichment-20260916.json", "data/trends-20260916.json", "packageName"
    )
    historical = merged_records(history_specs("", GOOGLE_DATES), "packageName")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    games, companies, trends, asset_bundle = [], {}, {}, {}
    for row in rows:
        rank, package = row["rank"], row["packageName"]
        if package in current:
            game, company, analysis = map(deepcopy, current[package])
        elif package in historical:
            game, company, analysis = map(deepcopy, historical[package])
        elif package == "leyi.ageofspirits":
            metadata = play_metadata(package)
            game, company, analysis = age_of_spirits_profile(row, metadata)
            asset_bundle["75_icon"] = data_uri(metadata["icon"], (256, 256))
            asset_bundle["75_store"] = data_uri(metadata["screenshot"], (720, 720))
        elif package == "aliens.zombies.invasion":
            metadata = play_metadata(package)
            game, company, analysis = aliens_profile(row, metadata)
            asset_bundle["76_icon"] = data_uri(metadata["icon"], (256, 256))
            asset_bundle["76_store"] = data_uri(metadata["screenshot"], (720, 720))
        else:
            raise RuntimeError(f"Unexpected Google entrant: {row}")
        change = delta_label(old_rank.get(package), rank)
        comp = comparison(None, rank, GOOGLE_DATE, GOOGLE_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row.get("developer", game.get("developer", "")),
            store="googlePlay",
            storeUrl=row["storeUrl"],
            iconUrl=row["iconUrl"],
            screenshotUrl=row["screenshotUrl"],
            totalInstalls=str(row.get("downloads") or game.get("totalInstalls") or "").replace("+", " +"),
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(
            clean_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)

    enrichment = deepcopy(load("data/enrichment-20260916.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=GOOGLE_BASELINE,
        currentDate=GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/games-20260917.json", games)
    save("data/enrichment-20260917.json", enrichment)
    save("data/trends-20260917.json", trends)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    if asset_bundle:
        save("assets/assets-14.json", asset_bundle)
        if "assets-14.json" not in manifest["files"]:
            manifest["files"].append("assets-14.json")
    save("assets/manifest.json", manifest)

    cross_check = audit_google(rows)
    save(
        "data/history/google-play/2026-09-17.json",
        {
            "store": "google-play",
            "country": "US",
            "category": "Games > Strategy > Top Grossing",
            "date": CAPTURE,
            "dataDate": GOOGLE_DATE,
            "sourceCapturedAt": source_info["capturedAt"],
            "sourceUrl": source_info["sourceUrl"],
            "sourceEndpoint": source_info["sourceEndpoint"],
            "sourceMethod": source_info["sourceMethod"],
            "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。",
            "crossCheck": cross_check,
            "rankings": [
                {
                    "rank": game["rank"],
                    "packageName": game["packageName"],
                    "gameName": game["gameName"],
                    "sourceUrl": game["storeUrl"],
                }
                for game in games
            ],
        },
    )
    return games, cross_check


def build_ios(rows, source_url, source_updated):
    current = records(
        "data/ios-games-20260916.json",
        "data/ios-enrichment-20260916.json",
        "data/ios-trends-20260916.json",
        "appId",
    )
    historical = merged_records(history_specs("ios-", IOS_DATES), "appId")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    games, companies, trends = [], {}, {}
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        elif app_id in historical:
            game, company, analysis = map(deepcopy, historical[app_id])
        else:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")
        change = delta_label(old_rank.get(app_id), rank)
        comp = comparison(None, rank, IOS_DATE, IOS_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row["developer"],
            store="ios",
            storeUrl=f"https://apps.apple.com/us/app/id{app_id}",
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(
            clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)

    enrichment = deepcopy(load("data/ios-enrichment-20260916.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=IOS_BASELINE,
        currentDate=IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/ios-games-20260917.json", games)
    save("data/ios-enrichment-20260917.json", enrichment)
    save("data/ios-trends-20260917.json", trends)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    save("assets/ios-manifest.json", manifest)

    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(
        ZoneInfo("Asia/Shanghai")
    ).date().isoformat()
    save(
        "data/history/ios/2026-09-17.json",
        {
            "store": "ios",
            "country": "US",
            "device": "iPhone",
            "category": "Games > Strategy > Top Grossing",
            "date": source_date,
            "dataDate": source_date,
            "sourceUpdated": source_updated,
            "sourceUrl": source_url,
            "rankings": [
                {
                    "rank": game["rank"],
                    "appId": game["appId"],
                    "gameName": game["gameName"],
                    "sourceUrl": game["storeUrl"],
                }
                for game in games
            ],
        },
    )
    return games, source_date


def main():
    google_source = fetch_top_grossing_strategy()
    ios_url, ios_updated, ios_rows = parse_ios()
    ios_source_date = datetime.fromisoformat(ios_updated.replace("Z", "+00:00")).astimezone(
        ZoneInfo("Asia/Shanghai")
    ).date().isoformat()
    if google_source["dataDate"] != GOOGLE_DATE:
        raise RuntimeError(f"Google capture date is {google_source['dataDate']}, expected {GOOGLE_DATE}")
    if ios_source_date != IOS_DATE:
        raise RuntimeError(f"Apple source is still dated {ios_source_date}; keep the previous valid iOS snapshot")
    if len(google_source["rows"]) != 60 or len({row["packageName"] for row in google_source["rows"]}) != 60:
        raise RuntimeError("Google direct source is not a complete unique TOP60")
    if len(ios_rows) != 60 or len({row["appId"] for row in ios_rows}) != 60:
        raise RuntimeError("Apple RSS is not a complete unique TOP60")
    google, audit = build_google(google_source["rows"], google_source)
    ios, _ = build_ios(ios_rows, ios_url, ios_updated)
    print("Google", google_source["capturedAt"], [(g["rank"], g["gameName"]) for g in google if g["rank"] in (1, 25, 60)])
    print("AppBrain audit", audit)
    print("iOS", ios_updated, [(g["rank"], g["gameName"]) for g in ios if g["rank"] in (1, 25, 60)])


if __name__ == "__main__":
    main()
