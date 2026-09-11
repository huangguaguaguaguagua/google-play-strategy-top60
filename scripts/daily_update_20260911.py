#!/usr/bin/env python3
"""Build the Beijing 2026-09-11 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_ios, save, trend
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from daily_update_20260910 import ios_game_from_metadata
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-09-11"
GOOGLE_DATE = "2026-09-11"
GOOGLE_BASELINE = "2026-06-13"
IOS_DATE = "2026-09-11"
IOS_BASELINE = "2026-06-13"

GOOGLE_HISTORY = [
    (f"data/games-{date}.json", f"data/enrichment-{date}.json", f"data/trends-{date}.json")
    for date in (
        "20260910", "20260909", "20260908", "20260907", "20260904", "20260903",
        "20260902", "20260901", "20260831", "20260828", "20260827", "20260826",
        "20260825", "20260824", "20260821", "20260820", "20260819d",
    )
]
IOS_HISTORY = [
    (f"data/ios-games-{date}.json", f"data/ios-enrichment-{date}.json", f"data/ios-trends-{date}.json")
    for date in (
        "20260910", "20260909", "20260908", "20260907", "20260904", "20260903",
        "20260902", "20260901", "20260831", "20260828", "20260827", "20260826",
        "20260825", "20260824", "20260821", "20260820", "20260819",
    )
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


def coop_td_profile(row, metadata, asset_rank):
    game = ios_game_from_metadata(
        row,
        metadata,
        asset_rank,
        "合作塔防 / 生存防守 / 轻度策略",
        "双人合作；塔防；战略布阵；城墙防守；怪物；卡组搭配；赛季通行证；传奇皮肤",
    )
    company = {
        "en": "SuperMagic Inc.",
        "cn": "SuperMagic（韩国研发与发行主体）",
        "confidence": "已确认",
        "basis": "Apple美国区店铺主体为Supermagic Inc.；SuperMagic官网将Coop TD列入自研及发行产品，并显示公司版权与首尔办公地址。未发现足够证据证明其归属于更大集团。",
        "source": "https://www.supermagic.io/",
    }
    analysis = trend(
        "趋势：2024年以双人协作塔防、短局布阵和卡组组合上线，成熟阶段通过新军团、赛季通行证与外观内容维持；关键转折：1.6.8加入Demon Legion城墙防守、Golden Draw Board及三款传奇皮肤，但未发现可确认的商业化重大转折；主力素材：双人同屏守线、可爱怪物潮、单位合成与布阵、城墙攻防、传奇皮肤和协作胜利。",
        "产品于2024年10月上线，用双人合作而不是单人守塔作为第一识别点：双方配置单位、选择站位并共同抵挡怪物波次。上线后围绕卡组成长、关卡、赛季与外观扩展，当前属于已进入常态内容运营的轻度塔防产品。",
        "本次首次进入本项目iOS美国策略畅销榜第55名；Apple上架日期为2024年10月28日，早于90天窗口，因此属于成熟产品日榜进入，不标记为近三个月新品。Google Play同口径策略TOP60当前没有对应排名。",
        "未发现可确认的重大产品或发行转折。Apple 1.6.8版本于8月24日加入Demon Legion“Defend the Wall”、Golden Draw Board、传奇皮肤与Season Pass内容；这些节点与本次进榜相隔两周以上，不能直接认定为榜位原因。",
        "Apple商店图和描述突出双人同时守线、怪物波次、战略放置和合作胜利；1.6.8进一步用恶魔军团、城墙防守、抽奖盘、传奇皮肤和通行证展示活动层。当前素材证据以官方商店与产品官网为主，可信度为中。",
        "观察下一个2—3个工作日能否从#55脱离榜尾，并核对Demon Legion与Season Pass是否持续更新；若快速退出，只记录为成熟产品的单日付费脉冲。",
        game["storeUrl"],
        [
            {"label": "SuperMagic官方网站", "url": "https://www.supermagic.io/", "type": "company-research"},
            {"label": "Google Play同产品商品页", "url": "https://play.google.com/store/apps/details?id=com.percent.aos.cooptd&hl=en_US&gl=US", "type": "lifecycle-analysis"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="上架日期、版本说明、玩法与素材来自Apple美国区商品页；公司主体由SuperMagic官网交叉确认。",
        changeReason="首次进入项目iOS榜，独立建立商店素材、发行归属与生命周期档案；未把8月版本内容写成确定进榜原因。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2024年10月上架梳理到2026年8月Demon Legion、皮肤与赛季通行证更新。",
        evidenceNote="玩法、版本和公司信息有官方来源；公开材料未披露本次榜位变化对应的收入或投放原因。",
    )
    return game, company, analysis


def build_google(rows, source_info):
    current = records("data/games-20260910.json", "data/enrichment-20260910.json", "data/trends-20260910.json", "packageName")
    historical = merged_records(GOOGLE_HISTORY, "packageName")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    games, companies, trends = [], {}, {}
    for row in rows:
        rank, package = row["rank"], row["packageName"]
        if package not in historical:
            raise RuntimeError(f"Unexpected Google entrant: {row}")
        game, company, analysis = map(deepcopy, current.get(package, historical[package]))
        change = delta_label(old_rank.get(package), rank)
        comp = comparison(None, rank, GOOGLE_DATE, GOOGLE_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row.get("developer", ""),
            store="googlePlay",
            storeUrl=row["storeUrl"],
            iconUrl=row["iconUrl"],
            screenshotUrl=row["screenshotUrl"],
            totalInstalls=str(row.get("downloads") or "").replace("+", " +"),
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(
            clean_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        if package == "com.readygo.dark.gp":
            analysis["summary"] = analysis["summary"].replace("黑暗丧尸压力", "暗黑压力")
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)

    enrichment = deepcopy(load("data/enrichment-20260910.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=GOOGLE_BASELINE,
        currentDate=GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/games-20260911.json", games)
    save("data/enrichment-20260911.json", enrichment)
    save("data/trends-20260911.json", trends)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    save("assets/manifest.json", manifest)
    cross_check = audit_google(rows)
    save(
        "data/history/google-play/2026-09-11.json",
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
                {"rank": game["rank"], "packageName": game["packageName"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]}
                for game in games
            ],
        },
    )
    return games, cross_check


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260910.json", "data/ios-enrichment-20260910.json", "data/ios-trends-20260910.json", "appId")
    historical = merged_records(IOS_HISTORY, "appId")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    unknown_ids = [row["appId"] for row in rows if row["appId"] not in historical]
    metadata_by_id = lookup(unknown_ids) if unknown_ids else {}
    if set(metadata_by_id) != set(unknown_ids):
        raise RuntimeError(f"Apple Lookup did not return every new product: {unknown_ids}")
    games, companies, trends, bundle = [], {}, {}, {}
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id in historical:
            game, company, analysis = map(deepcopy, current.get(app_id, historical[app_id]))
        elif app_id == "6503702666":
            metadata = metadata_by_id[app_id]
            if str(metadata.get("releaseDate", ""))[:10] != "2024-10-28":
                raise RuntimeError(f"Coop TD iOS release date missing or changed: {metadata.get('releaseDate')}")
            game, company, analysis = coop_td_profile(row, metadata, 92)
            bundle["92_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle["92_store"] = data_uri(game["screenshotUrl"], (720, 720))
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

    enrichment = deepcopy(load("data/ios-enrichment-20260910.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=IOS_BASELINE,
        currentDate=IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/ios-games-20260911.json", games)
    save("data/ios-enrichment-20260911.json", enrichment)
    save("data/ios-trends-20260911.json", trends)
    if bundle:
        save("assets/ios-assets-19.json", bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if bundle and "ios-assets-19.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-19.json")
    save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save(
        "data/history/ios/2026-09-11.json",
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
                {"rank": game["rank"], "appId": game["appId"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]}
                for game in games
            ],
        },
    )
    return games, source_date


def main():
    google_source = fetch_top_grossing_strategy()
    ios_url, ios_updated, ios_rows = parse_ios()
    ios_source_date = datetime.fromisoformat(ios_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    if google_source["dataDate"] != GOOGLE_DATE:
        raise RuntimeError(f"Google capture date is {google_source['dataDate']}, expected {GOOGLE_DATE}")
    if ios_source_date != IOS_DATE:
        raise RuntimeError(f"Apple source is still dated {ios_source_date}; keep the previous valid iOS snapshot")
    google, audit = build_google(google_source["rows"], google_source)
    ios, _ = build_ios(ios_rows, ios_url, ios_updated)
    print("Google", google_source["capturedAt"], [(g["rank"], g["gameName"]) for g in google if g["rank"] in (1, 25, 60)])
    print("AppBrain audit", audit)
    print("iOS", ios_updated, [(g["rank"], g["gameName"]) for g in ios if g["rank"] in (1, 25, 60)])


if __name__ == "__main__":
    main()
