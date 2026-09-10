#!/usr/bin/env python3
"""Build the Beijing 2026-09-10 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_ios, save, trend
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-09-10"
GOOGLE_DATE = "2026-09-10"
GOOGLE_BASELINE = "2026-06-12"
IOS_DATE = "2026-09-10"
IOS_BASELINE = "2026-06-12"

GOOGLE_HISTORY = [
    (f"data/games-{date}.json", f"data/enrichment-{date}.json", f"data/trends-{date}.json")
    for date in (
        "20260909", "20260908", "20260907", "20260904", "20260903", "20260902",
        "20260901", "20260831", "20260828", "20260827", "20260826", "20260825",
        "20260824", "20260821", "20260820", "20260819d",
    )
]
IOS_HISTORY = [
    (f"data/ios-games-{date}.json", f"data/ios-enrichment-{date}.json", f"data/ios-trends-{date}.json")
    for date in (
        "20260909", "20260908", "20260907", "20260904", "20260903", "20260902",
        "20260901", "20260831", "20260828", "20260827", "20260826", "20260825",
        "20260824", "20260821", "20260820", "20260819",
    )
]


def clean_analysis(analysis):
    """Normalize a carried-forward audit to this capture date."""
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


def ios_game_from_metadata(row, metadata, asset_rank, genre, keywords):
    description = metadata.get("description", "")
    release = str(metadata.get("releaseDate", ""))[:10]
    icon = metadata.get("artworkUrl512") or metadata.get("artworkUrl100")
    screenshot = (metadata.get("screenshotUrls") or metadata.get("ipadScreenshotUrls") or [icon])[0]
    return {
        "rank": row["rank"],
        "appId": row["appId"],
        "packageName": row["appId"],
        "gameName": row["gameName"],
        "developer": metadata.get("sellerName") or row["developer"],
        "totalInstalls": "",
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "storeUrl": f"https://apps.apple.com/us/app/id{row['appId']}",
        "iconUrl": icon,
        "screenshotUrl": screenshot,
        "shortDescription": description.replace("\n", " ")[:180],
        "description": description,
        "releaseDate": release,
        "releaseDateIso": release,
        "updatedDate": str(metadata.get("currentVersionReleaseDate", ""))[:10],
        "genre": genre,
        "keywords": keywords,
        "note": "",
        "assetRank": asset_rank,
        "store": "ios",
    }


def pokemon_champions_profile(row, metadata, asset_rank):
    game = ios_game_from_metadata(
        row,
        metadata,
        asset_rank,
        "回合制战术 / 队伍构筑 / PvP",
        "宝可梦；单打与双打；属性克制；特性与招式；队伍构筑；排位赛；跨平台；Pokémon HOME",
    )
    company = {
        "en": "The Pokémon Company / The Pokémon Works",
        "cn": "宝可梦公司（移动端发行）/ The Pokémon Works（研发体系）",
        "confidence": "已确认",
        "basis": "Apple美国区店铺主体为The Pokemon Company；官方产品站与商店页确认跨平台宝可梦对战产品，开发署名由官方产品资料与游戏Credits交叉核对为The Pokémon Works。",
        "source": "https://champions.pokemon.com/en-us/",
    }
    analysis = trend(
        "趋势：2026年6月移动版上线，以宝可梦IP、跨平台排位和轻量队伍构筑承接竞技用户，目前仍处移动端首发验证；关键转折：4月Switch版扩展到6月iOS/Android，随后接入世界锦标赛与Regulation Set M-C，9月9日1.2.0仅确认问题修复；主力素材：经典宝可梦同场、单打/双打阵容、属性克制、Mega Evolution、排位段位和跨平台对战。",
        "Switch版于2026年4月推出，移动版于6月17日上线；产品把系列传统回合制对战独立成可随时进入的竞技入口，通过排位、休闲与私人对战、队伍招募及Pokémon HOME连接承接IP老用户和新手。移动端上线不足90天，仍处首发验证，当前主要由IP规模、赛事体系与核心对战用户支撑。",
        "本次首次进入iOS美国策略畅销榜第19名；Apple上架日期为2026年6月17日，位于本期90天窗口内，因此标记为近三个月新上榜。Google Play同产品未进入当前美国策略TOP60，暂不把iOS单端高位外推为双端收入趋势。",
        "可确认的产品阶段变化是由4月Switch首发扩展至6月移动端跨平台运营，并逐步承接官方竞技规则与赛事。Apple显示1.2.0于9月9日更新，但说明仅为修复问题；与本次进榜时间重合不等于已确认的收入原因。",
        "官方页面与商店图集中展示喷火龙、皮卡丘等高认知角色同场，单打/双打选阵、属性与招式博弈、Mega Evolution、排位赛、跨平台匹配及Pokémon HOME队伍导入；当前证据以官方商店和产品站为主，素材判断可信度为中。",
        "观察未来2—3个工作日能否守住前30，并核对Regulation Set M-C、排位赛季与Battle Pass节奏；如快速回落，只记录为版本/赛事窗口的单端付费峰值，不推演长期趋势。",
        game["storeUrl"],
        [
            {"label": "Pokémon Champions官方产品站", "url": "https://champions.pokemon.com/en-us/", "type": "primary"},
            {"label": "官方Regulation Set M-C说明", "url": "https://www.pokemon.com/us/news/get-ready-for-regulation-set-m-c-in-pokemon-champions", "type": "lifecycle-analysis"},
            {"label": "Google Play同产品商品页", "url": "https://play.google.com/store/apps/details?id=jp.pokemon.pokemonchampions&hl=en_US&gl=US", "type": "lifecycle-analysis"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="上架日期、当前版本、玩法与素材来自Apple美国区商品页；官方产品站和Google Play页面用于交叉确认跨平台定位。",
        changeReason="首次进入项目iOS榜，独立建立Apple上架日期、本地素材、公司与生命周期档案；未把9月9日修复更新写成确定进榜原因。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2026年4月Switch首发、6月移动端上线梳理至当前跨平台竞技运营。",
        evidenceNote="首发、玩法和规则节点有官方依据；公开材料未披露本次榜位变化的付费来源。",
    )
    return game, company, analysis


def f1_clash_profile(row, metadata, asset_rank):
    game = ios_game_from_metadata(
        row,
        metadata,
        asset_rank,
        "赛车经营 / 实时战术 / PvP",
        "Formula 1；车队经理；1v1；轮胎策略；进站时机；天气；车手与赛车升级；Grand Prix；Madring",
    )
    company = {
        "en": "Hutch Games Ltd / Modern Times Group (MTG)",
        "cn": "Hutch Games（研发与发行）/ Modern Times Group（母公司）",
        "confidence": "已确认",
        "basis": "Apple美国区店铺与F1 Clash官方产品页均列Hutch Games Ltd；Hutch官方公司历程确认其于2020年被Modern Times Group收购。",
        "source": "https://www.hutch.io/our-story/",
    }
    analysis = trend(
        "趋势：2019年以F1官方授权、车队经理和实时进站决策上线，成熟期由真实赛历、Grand Prix活动、车手/赛车收集及PvP联盟维持；关键转折：2021年从F1 Manager更名F1 Clash，逐步加入Pit Pass、Clubs与赛季轮换，9月1日Update 60新增Madring；主力素材：真实车手与赛车、天气/轮胎选择、进站超车、1v1胜负和赛道事件。",
        "产品2019年以F1 Manager上线，把赛车操作压缩为车队经理的两车编排、轮胎、加速和进站决策；长期围绕官方赛历的Grand Prix、周赛、联盟、Pit Pass及车手/赛车资产收集运营。成熟期主要由F1授权、现实比赛节点和核心策略/赛车用户支撑。",
        "本次首次进入项目iOS美国策略畅销榜第56名；Apple上架日期为2019年5月9日，早于90天窗口，因此属于成熟产品日榜进入，不是近三个月新上榜。Google Play当前美国策略TOP60没有对应排名。",
        "2021年官方基于受众研究把F1 Manager更名为F1 Clash，随后持续增加赛季分数、Clubs、Pit Pass和赛道更新。Update 60于9月1日加入Madring及未来活动内容；9月9日60.01版本只确认修复与优化，不能直接认定为今日进榜原因。",
        "官方商店图与产品页突出Max Verstappen等真实车手、两车同时管理、天气与轮胎磨损、进站窗口、最后一弯反超、车辆调校、1v1及Grand Prix活动；当前素材证据来自Apple与Hutch官方资料，可信度为中。",
        "观察未来2—3个工作日能否脱离#56榜尾，并结合Madring计时赛、现实F1赛历和Grand Prix活动检查回榜持续性；如下一快照退出，按赛事节点短峰处理。",
        game["storeUrl"],
        [
            {"label": "Hutch F1 Clash官方产品页", "url": "https://www.hutch.io/our-games/f1-clash/", "type": "primary"},
            {"label": "F1 Clash官方更新记录", "url": "https://www.hutch.io/our-games/f1-clash/patch-notes/", "type": "lifecycle-analysis"},
            {"label": "Hutch官方公司历程", "url": "https://www.hutch.io/our-story/", "type": "company-research"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="上架日期、当前版本与商店图来自Apple美国区商品页；玩法、更新与收购关系由Hutch官方页面交叉确认。",
        changeReason="首次进入项目iOS榜，补建独立商店素材、公司归属与生命周期；未把Update 60或修复版本写成确定进榜原因。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2019年F1 Manager上线、2021年更名梳理到2026年Madring与赛历运营。",
        evidenceNote="更名、功能与更新节点均有Hutch官方记录；此次榜位原因仍缺少公开收入证据。",
    )
    return game, company, analysis


def build_google(rows, source_info):
    current = records("data/games-20260909.json", "data/enrichment-20260909.json", "data/trends-20260909.json", "packageName")
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
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)

    enrichment = deepcopy(load("data/enrichment-20260909.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260910.json", games)
    save("data/enrichment-20260910.json", enrichment)
    save("data/trends-20260910.json", trends)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    save("assets/manifest.json", manifest)
    cross_check = audit_google(rows)
    save(
        "data/history/google-play/2026-09-10.json",
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
    current = records("data/ios-games-20260909.json", "data/ios-enrichment-20260909.json", "data/ios-trends-20260909.json", "appId")
    historical = merged_records(IOS_HISTORY, "appId")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    new_ids = [row["appId"] for row in rows if row["appId"] in {"6741503079", "1434561536"}]
    metadata_by_id = lookup(new_ids) if new_ids else {}
    games, companies, trends, bundle = [], {}, {}, {}
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id in historical:
            game, company, analysis = map(deepcopy, current.get(app_id, historical[app_id]))
        elif app_id == "6741503079":
            metadata = metadata_by_id[app_id]
            if str(metadata.get("releaseDate", ""))[:10] != "2026-06-17":
                raise RuntimeError(f"Pokémon Champions iOS release date missing or changed: {metadata.get('releaseDate')}")
            game, company, analysis = pokemon_champions_profile(row, metadata, 90)
            bundle["90_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle["90_store"] = data_uri(game["screenshotUrl"], (720, 720))
        elif app_id == "1434561536":
            metadata = metadata_by_id[app_id]
            if str(metadata.get("releaseDate", ""))[:10] != "2019-05-09":
                raise RuntimeError(f"F1 Clash iOS release date missing or changed: {metadata.get('releaseDate')}")
            game, company, analysis = f1_clash_profile(row, metadata, 91)
            bundle["91_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle["91_store"] = data_uri(game["screenshotUrl"], (720, 720))
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

    enrichment = deepcopy(load("data/ios-enrichment-20260909.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260910.json", games)
    save("data/ios-enrichment-20260910.json", enrichment)
    save("data/ios-trends-20260910.json", trends)
    if bundle:
        save("assets/ios-assets-18.json", bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if bundle and "ios-assets-18.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-18.json")
    save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save(
        "data/history/ios/2026-09-10.json",
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
