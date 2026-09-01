#!/usr/bin/env python3
"""Build the Beijing 2026-09-01 Google Play and Apple App Store snapshots."""
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_ios, save, trend
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-09-01"
GOOGLE_DATE = "2026-09-01"
GOOGLE_BASELINE = "2026-06-03"
IOS_DATE = "2026-09-01"
IOS_BASELINE = "2026-06-03"

GOOGLE_HISTORY = [
    (f"data/games-{date}.json", f"data/enrichment-{date}.json", f"data/trends-{date}.json")
    for date in ("20260831", "20260828", "20260827", "20260826", "20260825", "20260824", "20260821", "20260820", "20260819d")
]
IOS_HISTORY = [
    (f"data/ios-games-{date}.json", f"data/ios-enrichment-{date}.json", f"data/ios-trends-{date}.json")
    for date in ("20260831", "20260828", "20260827", "20260826", "20260825", "20260824", "20260821", "20260820", "20260819")
]


def clean_analysis(analysis):
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


def sd_gundam_profile(meta, asset_rank):
    store_url = "https://apps.apple.com/us/app/id6692615881"
    game = {
        "appId": "6692615881", "packageName": "6692615881", "store": "ios", "assetRank": asset_rank,
        "genre": "战棋SRPG / 高达IP / 机体与角色收集",
        "keywords": "GUNDAM；G Generation；回合制战棋；作品剧情重演；机体开发；驾驶员编队；1170机体；500日庆典",
    }
    company = {
        "en": "Bandai Namco Entertainment Inc.",
        "cn": "万代南梦宫娱乐",
        "confidence": "已确认",
        "basis": "Apple Lookup的sellerName与artistName均为Bandai Namco Entertainment Inc.；官方站和商品页均由万代南梦宫运营。",
        "source": "https://gget.ggame.jp/en/",
    }
    analysis = trend(
        "趋势：2025年4月全球上线后，以高达各作品剧情重演、回合制格子战与机体/驾驶员收集承接核心IP用户，长期由限定机体、作品主题关卡、开发养成和月卡支撑；关键转折：上线两周突破300万下载，2026年8月28日进入500日庆典，当前Full Armor Hyaku-Shiki Kai活动与iOS进榜时间重合，但仍只视为待验证活动信号；主力素材：高达机体阵容、战棋站位、必杀演出、作品名场面、机体开发树和庆典限定奖励。",
        "2025年4月全球同步上线，用G Generation系列的剧情关卡、格子战斗、机体开发和驾驶员编队建立IP入口。官方商品页目前列出104部作品、1170台以上机体，产品已从首发收集扩展到作品轮换、限定机体和订阅权益并行的长线运营。",
        "本次首次进入本项目iOS美国策略畅销榜第53名；Google Play商品存在，但未进入美国策略畅销TOP60。产品上架早于90天，属于成熟产品日榜进入，不是近三个月新上榜。",
        "官方在2025年5月确认全球下载突破300万；2026年8月28日开启500日纪念活动，Google Play同时展示Full Armor Hyaku-Shiki Kai限定节点。活动时间与本次进榜重合，但尚不能拆分庆典奖励、限定卡池和存量IP用户各自贡献。",
        "当前商店图集中展示跨作品机体编队、格子地图选择、战斗动画和剧情名场面；公开活动补充限定机体、纪念登录与抽取奖励。素材依据来自Apple、Google Play和官方站，可信度为中。",
        "观察未来3个工作日能否脱离#50—60，并核验500日庆典结束前是否形成持续榜位；若迅速掉榜，按限定机体与庆典带来的短期收入峰值处理。",
        store_url,
        [
            {"label": "SD Gundam G Generation ETERNAL官方站", "url": "https://gget.ggame.jp/en/", "type": "primary"},
            {"label": "Apple App Store美国区商品页", "url": store_url, "type": "primary"},
            {"label": "Gundam官方300万下载公告", "url": "https://en.gundam-official.com/news/i/news/games/02_14089", "type": "lifecycle-analysis"},
            {"label": "官方英文账号500日庆典", "url": "https://x.com/ggene_eternalEN", "type": "lifecycle-analysis"},
        ],
    )
    return finish_new_game(game, meta), company, analysis


def game_of_kings_profile(meta, asset_rank):
    store_url = "https://apps.apple.com/us/app/id1071673198"
    game = {
        "appId": "1071673198", "packageName": "1071673198", "store": "ios", "assetRank": asset_rank,
        "genre": "SLG / 城建战争 / 联盟PvP",
        "keywords": "中世纪奇幻；城堡；六资源；四兵种；联盟集结；跨服战争；怪物培养；英雄装备；实时翻译",
    }
    company = {
        "en": "KOOFEI LIMITED / Lightning Studios Limited",
        "cn": "KOOFEI LIMITED发行；疑似Lightning Studios产品体系",
        "confidence": "疑似",
        "basis": "Apple店铺发行主体为KOOFEI LIMITED；商品页版权及产品隐私政策指向Lightning Studios Limited，但未找到足以确认两者股权关系或最终集团的公开材料。",
        "source": "https://gameofkings-app.com/privacypolicy.html",
    }
    analysis = trend(
        "趋势：2017年上线后以中世纪奇幻城建、六资源经营、英雄与怪物养成、联盟集结和跨服王座战承接传统COK-like用户，目前主要依赖存量联盟和核心付费用户；关键转折：未发现可确认的重大转折，2026年公开版本记录仍以修复为主；主力素材：城堡升级、巨量兵团、联盟集结、跨服王座、奇幻怪物和英雄装备。",
        "2017年上线后围绕城堡、六类资源、科技、四兵种和世界地图PvP展开，再用怪物图鉴、英雄双技能树、联盟协作与34语种实时翻译强化跨服社交。现阶段属于九年长线产品，公开资料未显示玩法结构发生新的方向切换。",
        "本次进入iOS美国策略畅销榜第60名，Google Play未进入同口径TOP60；产品上架远早于90天，只能记为成熟产品压线回榜信号。",
        "未发现可确认的重大转折/长期稳定运营。Apple版本历史显示2026年7月21日最近一次更新仅写明错误修复，没有证据把本次进榜归因于新系统、IP或大版本。",
        "商店图以奇幻城堡、世界地图、英雄和兵团对抗为主，描述强调联盟、资源、科技、怪物和跨服竞争；缺少独立公开广告资料，因此素材判断仅标中等可信度。",
        "优先观察下一个工作日能否继续留榜，并核验是否存在未公开的服务器战争、联盟礼包或召回投放；若立即掉榜，按存量核心用户的短时付费脉冲处理。",
        store_url,
        [
            {"label": "Apple App Store美国区商品页", "url": store_url, "type": "primary"},
            {"label": "Game of Kings隐私政策", "url": "https://gameofkings-app.com/privacypolicy.html", "type": "company-research"},
        ],
    )
    return finish_new_game(game, meta), company, analysis


def finish_new_game(game, meta):
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshot = (meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or [icon])[0]
    game.update(
        iconUrl=icon, screenshotUrl=screenshot, rankIconUrl=icon,
        description=meta.get("description", ""), shortDescription=meta.get("description", "").replace("\n", " ")[:220],
        releaseDate=(meta.get("releaseDate") or "")[:10], releaseDateIso=(meta.get("releaseDate") or "")[:10],
        updatedDate=(meta.get("currentVersionReleaseDate") or "")[:10], totalInstalls="", recentInstalls30d="",
    )
    return game


def audit_google(rows):
    try:
        return appbrain_audit(rows)
    except Exception as exc:
        return {"sourceRole": "audit-only", "sourceUrl": "https://www.appbrain.com/stats/google-play-rankings/top_grossing/strategy/us", "status": "unavailable", "error": f"{type(exc).__name__}: {exc}", "note": "审计源失败不覆盖或阻断Google Play直连榜单。"}


def build_google(rows, source_info):
    current = records("data/games-20260831.json", "data/enrichment-20260831.json", "data/trends-20260831.json", "packageName")
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
        game.update(rank=rank, gameName=row["gameName"], developer=row.get("developer", ""), store="googlePlay", storeUrl=row["storeUrl"], iconUrl=row["iconUrl"], screenshotUrl=row["screenshotUrl"], totalInstalls=str(row.get("downloads") or "").replace("+", " +"), dailyChange=change, comparison90d=comp)
        analysis = refresh_daily_rank_path(clean_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", ""))
        companies[str(rank)] = company; trends[str(rank)] = analysis; games.append(game)
    enrichment = deepcopy(load("data/enrichment-20260831.json")); enrichment["productCompaniesByRank"] = companies
    save("data/games-20260901.json", games); save("data/enrichment-20260901.json", enrichment); save("data/trends-20260901.json", trends)
    manifest = load("assets/manifest.json"); manifest["date"] = GOOGLE_DATE; save("assets/manifest.json", manifest)
    cross_check = audit_google(rows)
    save("data/history/google-play/2026-09-01.json", {"store": "google-play", "country": "US", "category": "Games > Strategy > Top Grossing", "date": CAPTURE, "dataDate": GOOGLE_DATE, "sourceCapturedAt": source_info["capturedAt"], "sourceUrl": source_info["sourceUrl"], "sourceEndpoint": source_info["sourceEndpoint"], "sourceMethod": source_info["sourceMethod"], "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。", "crossCheck": cross_check, "rankings": [{"rank": game["rank"], "packageName": game["packageName"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]} for game in games]})
    return games, cross_check


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260831.json", "data/ios-enrichment-20260831.json", "data/ios-trends-20260831.json", "appId")
    historical = merged_records(IOS_HISTORY, "appId")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in current]
    metadata = lookup(entrant_ids) if entrant_ids else {}
    if set(metadata) != set(entrant_ids):
        raise RuntimeError(f"Apple Lookup did not return every entrant: {entrant_ids}")
    games, companies, trends, bundle = [], {}, {}, {}
    next_asset = 86
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id in current or app_id in historical:
            game, company, analysis = map(deepcopy, current.get(app_id, historical[app_id]))
        elif app_id == "6692615881":
            game, company, analysis = sd_gundam_profile(metadata[app_id], next_asset)
            bundle[f"{next_asset}_icon"] = data_uri(game["iconUrl"], (256, 256)); bundle[f"{next_asset}_store"] = data_uri(game["screenshotUrl"], (720, 720)); next_asset += 1
        elif app_id == "1071673198":
            game, company, analysis = game_of_kings_profile(metadata[app_id], next_asset)
            bundle[f"{next_asset}_icon"] = data_uri(game["iconUrl"], (256, 256)); bundle[f"{next_asset}_store"] = data_uri(game["screenshotUrl"], (720, 720)); next_asset += 1
        else:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")
        change = delta_label(old_rank.get(app_id), rank)
        comp = comparison(None, rank, IOS_DATE, IOS_BASELINE, True, game.get("releaseDateIso"))
        game.update(rank=rank, gameName=row["gameName"], developer=row["developer"], store="ios", storeUrl=f"https://apps.apple.com/us/app/id{app_id}", dailyChange=change, comparison90d=comp)
        analysis = refresh_daily_rank_path(clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", ""))
        companies[str(rank)] = company; trends[str(rank)] = analysis; games.append(game)
    enrichment = deepcopy(load("data/ios-enrichment-20260831.json")); enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260901.json", games); save("data/ios-enrichment-20260901.json", enrichment); save("data/ios-trends-20260901.json", trends)
    if bundle: save("assets/ios-assets-15.json", bundle)
    manifest = load("assets/ios-manifest.json"); manifest["date"] = IOS_DATE
    if bundle and "ios-assets-15.json" not in manifest["files"]: manifest["files"].append("ios-assets-15.json")
    save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save("data/history/ios/2026-09-01.json", {"store": "ios", "country": "US", "device": "iPhone", "category": "Games > Strategy > Top Grossing", "date": source_date, "dataDate": source_date, "sourceUpdated": source_updated, "sourceUrl": source_url, "rankings": [{"rank": game["rank"], "appId": game["appId"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]} for game in games]})
    return games, source_date


def main():
    google_source = fetch_top_grossing_strategy(); ios_url, ios_updated, ios_rows = parse_ios()
    ios_source_date = datetime.fromisoformat(ios_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    if google_source["dataDate"] != GOOGLE_DATE: raise RuntimeError(f"Google capture date is {google_source['dataDate']}, expected {GOOGLE_DATE}")
    if ios_source_date != IOS_DATE: raise RuntimeError(f"Apple source is still dated {ios_source_date}; keep the previous valid iOS snapshot")
    google, audit = build_google(google_source["rows"], google_source); ios, _ = build_ios(ios_rows, ios_url, ios_updated)
    print("Google", google_source["capturedAt"], [(g["rank"], g["gameName"]) for g in google if g["rank"] in (1, 25, 60)])
    print("AppBrain audit", audit)
    print("iOS", ios_updated, [(g["rank"], g["gameName"]) for g in ios if g["rank"] in (1, 25, 60)])


if __name__ == "__main__":
    main()
