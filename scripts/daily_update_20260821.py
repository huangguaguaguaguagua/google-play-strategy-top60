#!/usr/bin/env python3
"""Build the 2026-08-21 capture from the two public US store charts."""
import json
import re
from copy import deepcopy

from lxml import html

from daily_update_20260820 import (
    ROOT, comparison, data_uri, delta_label, fetch, load, lookup,
    parse_google, parse_ios, save, trend,
)

CAPTURE_DATE = "2026-08-21"
GOOGLE_DATE = "2026-08-20"
GOOGLE_BASELINE = "2026-05-22"
IOS_DATE = "2026-08-21"
IOS_BASELINE = "2026-05-23"


def source_maps(games_path, enrichment_path, trends_path):
    games = load(games_path)
    enrichment = load(enrichment_path)["productCompaniesByRank"]
    trends = load(trends_path)
    return {
        str(game.get("appId") or game.get("packageName")): (
            game,
            enrichment[str(game["rank"])],
            trends[str(game["rank"])],
        )
        for game in games
    }


def refresh_audit_dates(analysis):
    for key in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(key):
            analysis[key]["reviewedAt"] = CAPTURE_DATE
    return analysis


def play_metadata(package):
    url = f"https://play.google.com/store/apps/details?id={package}&hl=en_US&gl=US"
    page = fetch(url)
    document = html.fromstring(page)
    text = " ".join(document.text_content().split())
    image = (document.xpath('//meta[@property="og:image"]/@content') or [""])[0]
    description = (document.xpath('//meta[@property="og:description"]/@content') or [""])[0]
    developer = " ".join((document.xpath('//*[contains(@class,"Vbfug")]//text()') or [""])).strip()
    downloads = [" ".join(x.text_content().split()) for x in document.xpath('//*[contains(@class,"ClM7O")]')]
    downloads = next((x for x in downloads if "+" in x), "")
    updated = re.search(r"Updated on\s*([A-Z][a-z]{2} \d{1,2}, 2026)", text)
    candidates = re.findall(r"https://play-lh\.googleusercontent\.com/[^\" ]+=w1052-h592", page.decode("utf-8"))
    screenshot = next((x for x in candidates if x.split("=")[0] != image.split("=")[0]), image)
    return {
        "url": url, "icon": image, "screenshot": screenshot,
        "description": description, "developer": developer,
        "downloads": downloads.replace("+", " +"),
        "updated": updated.group(1) if updated else "",
    }


def google_entrant(row, metadata, asset_rank, ios_records_by_name):
    package, name = row["packageName"], row["gameName"]
    prior = ios_records_by_name.get(name.lower())
    release_dates = {
        "com.global.antgame": "2021-06-24",
        "com.studion.mergearena": "2023-10-17",
    }
    if prior:
        prior_game, prior_company, prior_trend = prior
        genre, keywords = prior_game["genre"], prior_game["keywords"]
        release = prior_game.get("releaseDateIso") or prior_game.get("releaseDate") or ""
        company, analysis = deepcopy(prior_company), deepcopy(prior_trend)
    elif package == "com.global.antgame":
        genre = "SLG / 4X / 模拟经营"
        keywords = "蚂蚁；地下巢穴；昆虫写实；蚁种收集；联盟；4X领地"
        release = release_dates[package]
        company = {
            "en": "37GAMES / Sanqi Interactive Entertainment",
            "cn": "37GAMES（三七互娱海外发行品牌）/ 三七互娱",
            "confidence": "已确认",
            "basis": "Google Play店铺主体为37GAMES；37GAMES官方产品页收录Ant Legion，统一溯源至三七互娱产品体系。",
            "source": "https://www.37games.com/antslgofficial/index.html",
        }
        analysis = trend(
            "趋势：2021年以写实蚂蚁生态、巢穴扩建和蚁种收集切入，长期由联盟4X与跨服竞争支撑；关键转折：素材从自然纪录片式蚁群观察逐步叠加变异螳螂、强力蚁种和战力成长；主力素材：蚂蚁微距、地下巢穴、昆虫对决、蚁种孵化与联盟领地战。",
            "2021年上线时用写实昆虫微距、地下巢穴分层建设和蚁群繁育建立差异化，前期任务把自然观察承接到资源生产、特化蚁收集和队列养成；成熟期主要依靠联盟集结、世界地图领地争夺及持续蚁种扩充维持付费。",
            "本次进入Google Play美国策略畅销榜第58名，属于成熟产品的榜尾回归；因缺少2026-05-22同口径快照，90天状态保持pending并按常规样式展示。",
            "早期核心是‘真实蚂蚁世界’和巢穴经营，随后加入更多特化蚁、联盟战争与跨服竞争；当前版本叙事用神秘螳螂赋予力量和变异冒险强化英雄化表达，但未发现玩法主循环发生重大重构。",
            "真实蚂蚁微距、蚁后与卵室、纵向地下巢穴、蚂蚁围攻大型昆虫、稀有蚁种孵化、数值战力提升、联盟集结和世界地图领地。",
            "观察本次回榜是短期活动回流还是能稳定留在TOP60，以及英雄化变异素材能否比纯自然题材带来更稳定新增。",
            metadata["url"],
            [{"label": "Ant Legion官方产品页", "url": "https://www.37games.com/antslgofficial/index.html", "type": "primary"}],
        )
    elif package == "com.studion.mergearena":
        genre = "合成 / PvP / 卡牌策略"
        keywords = "实时PvP；单位合成；卡组；竞技场；英雄升级；天梯"
        release = release_dates[package]
        company = {
            "en": "TOP APP GAMES LTD / Utmost Games",
            "cn": "TOP APP GAMES（研发与发行主体）/ Utmost Games（投资/合作体系）",
            "confidence": "已确认",
            "basis": "Google Play与Apple店铺均列TOP APP GAMES LTD；公开公司稿将LUDUS归为Top App Games产品并关联Utmost Games，未发现可确认的更上层中国集团。",
            "source": "https://www.gamespress.com/LUDUS-Reaches-10-Million-Downloads-and-Introduces-Divisions-a-Major-Ne",
        }
        analysis = trend(
            "趋势：2023年以短局实时PvP、拖拽合成和卡组克制起量，2025年收入规模扩大，成熟期转向分段联赛、角色活动和持续卡组平衡；关键转折：月收入在2025年3月达到约200万美元，2026年累计下载突破千万并上线Divisions；主力素材：棋盘合成升级、单位数量压制、英雄大招、卡组反制与天梯晋级。",
            "2023年10月上线后，以对称小棋盘、同单位合成升星、随机出战和实时PvP把卡牌构筑压缩成短局决策；随着卡池与英雄扩展，运营重心从‘合一下就变强’的即时反馈转向天梯、锦标赛、部落与角色活动。",
            "本次进入Google Play美国策略畅销榜第59名。公开节点显示产品自上线后持续增长、2025年3月月收入达到约200万美元，2026年下载突破千万；当前仍处成熟运营阶段，而非首发验证。",
            "可确认的转折是2025年收入规模化及2026年新增Divisions分段系统，说明产品从单纯短局合成扩展为更明确的长期竞技进程；当前商店活动主推新角色Chainsaw，继续用角色节点拉动卡组回流。",
            "拖拽相同单位合成升星、五格/多格阵型、对手兵力快速对比、英雄技能清场、稀有卡抽取、角色Chainsaw和天梯段位晋升。",
            "观察新分段体系与角色活动是否能把榜尾回归转成稳定在榜，以及卡池膨胀后新玩家能否保持短局易懂的优势。",
            metadata["url"],
            [{"label": "LUDUS千万下载与Divisions公告", "url": "https://www.gamespress.com/LUDUS-Reaches-10-Million-Downloads-and-Introduces-Divisions-a-Major-Ne", "type": "company-research"}],
        )
    else:
        raise RuntimeError(f"Unexpected Google entrant {row}")
    game = {
        "rank": row["rank"], "packageName": package, "gameName": name,
        "developer": metadata["developer"] or row.get("developer", ""),
        "totalInstalls": metadata["downloads"], "recentInstalls30d": "",
        "dailyChange": "NEW", "rankIconUrl": metadata["icon"],
        "storeUrl": metadata["url"], "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"], "shortDescription": metadata["description"],
        "description": prior[0].get("description", metadata["description"]) if prior else metadata["description"],
        "releaseDate": release, "updatedDate": metadata["updated"],
        "genre": genre, "keywords": keywords, "note": "", "releaseDateIso": release,
        "assetRank": asset_rank,
        "comparison90d": comparison(None, row["rank"], GOOGLE_DATE, GOOGLE_BASELINE, True),
    }
    return game, company, refresh_audit_dates(analysis)


def build_google(rows, source_url):
    old = load("data/games-20260820.json")
    old_by_id = {game["packageName"]: game for game in old}
    old_enrichment = load("data/enrichment-20260820.json")
    old_trends = load("data/trends-20260820.json")
    ios_records = source_maps("data/ios-games-20260820.json", "data/ios-enrichment-20260820.json", "data/ios-trends-20260820.json")
    ios_by_name = {record[0]["gameName"].lower(): record for record in ios_records.values()}
    companies, trends, games, asset_bundle = {}, {}, [], {}
    entrant_assets = {
        "com.zroute.global": 61, "com.global.antgame": 62,
        "com.studion.mergearena": 63, "com.QuestLab.DraftWar": 64,
    }
    for row in rows:
        rank, package = row["rank"], row["packageName"]
        if package in old_by_id:
            previous = old_by_id[package]
            old_rank = previous["rank"]
            game = deepcopy(previous)
            game.update(
                rank=rank, gameName=row["gameName"], developer=row["developer"],
                dailyChange=delta_label(old_rank, rank),
                comparison90d=comparison(None, rank, GOOGLE_DATE, GOOGLE_BASELINE, True),
            )
            company = deepcopy(old_enrichment["productCompaniesByRank"][str(old_rank)])
            analysis = deepcopy(old_trends[str(old_rank)])
        else:
            metadata = play_metadata(package)
            asset_rank = entrant_assets[package]
            game, company, analysis = google_entrant(row, metadata, asset_rank, ios_by_name)
            asset_bundle[f"{asset_rank}_icon"] = data_uri(metadata["icon"], (256, 256))
            asset_bundle[f"{asset_rank}_store"] = data_uri(metadata["screenshot"], (720, 720))
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)
    enrichment = deepcopy(old_enrichment)
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260821.json", games)
    save("data/enrichment-20260821.json", enrichment)
    save("data/trends-20260821.json", trends)
    save("assets/assets-04.json", asset_bundle)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    if "assets-04.json" not in manifest["files"]:
        manifest["files"].append("assets-04.json")
    save("assets/manifest.json", manifest)
    save("data/history/google-play/2026-08-21.json", {
        "store": "google-play", "country": "US",
        "category": "Games > Strategy > Top Grossing", "date": CAPTURE_DATE,
        "dataDate": GOOGLE_DATE, "sourceLastUpdated": "August 20, 2026",
        "sourceUrl": source_url,
        "rankings": [{
            "rank": game["rank"], "packageName": game["packageName"],
            "gameName": game["gameName"], "sourceUrl": game["storeUrl"],
        } for game in games],
    })
    return games


def watcher_record(row, metadata, asset_rank):
    app_id = row["appId"]
    store = f"https://apps.apple.com/us/app/id{app_id}"
    shots = metadata.get("screenshotUrls") or metadata.get("ipadScreenshotUrls") or []
    icon = metadata.get("artworkUrl512") or metadata.get("artworkUrl100")
    screenshot = shots[0] if shots else icon
    game = {
        "rank": row["rank"], "appId": app_id, "packageName": app_id,
        "gameName": metadata.get("trackName", row["gameName"]),
        "developer": metadata.get("sellerName") or row["developer"],
        "genre": "塔防 / 卡牌RPG / 英雄养成",
        "keywords": "暗黑奇幻；英雄布阵；塔防站位；技能时机；巨型Boss；刺客信条联动",
        "totalInstalls": "", "recentInstalls30d": "", "dailyChange": "NEW",
        "storeUrl": store, "iconUrl": icon, "screenshotUrl": screenshot,
        "shortDescription": (metadata.get("description") or "").replace("\n", " ")[:220],
        "description": metadata.get("description", ""),
        "releaseDate": (metadata.get("releaseDate") or "")[:10],
        "releaseDateIso": (metadata.get("releaseDate") or "")[:10],
        "updatedDate": (metadata.get("currentVersionReleaseDate") or "")[:10],
        "note": "", "assetRank": asset_rank, "store": "ios",
        "comparison90d": comparison(None, row["rank"], IOS_DATE, IOS_BASELINE, True),
    }
    company = {
        "en": "Shanghai MOONTON Technology / Skystone Games (US publishing partner) / Savvy Games Group (acquisition agreed)",
        "cn": "上海沐瞳科技（研发/实际产品体系）/ Skystone Games（美国发行伙伴）/ Savvy Games Group（已协议收购；沙特PIF旗下）",
        "confidence": "已确认",
        "basis": "Skystone美国区隐私政策明确其代表上海沐瞳运营本产品；2026年公开交易信息显示字节跳动已同Savvy Games Group达成出售沐瞳的协议，未把协议收购写成已完成交割。",
        "source": "https://us.skystone.games/wor-pp",
    }
    analysis = trend(
        "趋势：产品全球版本2023年起以暗黑奇幻英雄、塔防式站位与Boss战获量；美国专属客户端2025年迁移后进入长线英雄/公会运营；关键转折：美国发行伙伴切换并迁移账号，当前以刺客信条联动、公会战和新团本拉动回流；主力素材：暗黑英雄近景、格子布阵、技能时机、巨型Boss伤害与IP联动。",
        "产品全球版本2023年以高精度暗黑奇幻角色、分路站位、手动技能时机和巨型Boss建立认知；美国区因发行伙伴调整，于2025年3月上线Skystone运营的专属客户端并承接既有账号，因此本次不能按普通新品理解。迁移完成后，核心运营转向170余名英雄与阵营收集、公会战赛季、Immortal Codex团本和联动活动。",
        "本次首次进入当前iOS日榜第47名。由于缺少2026-05-23同口径TOP60快照，90天状态保持pending并按常规样式展示；只记录今日相对昨日榜单的进榜事实。",
        "最明确的产品节点是2025年美国区发行伙伴与客户端迁移，既有用户被导入新包；成熟期内容从首发英雄展示扩展为公会战、团本Boss和限定联动。2026年7月版本加入公会战第15赛季及新团本，当前公开商店传播又叠加《刺客信条》联动。",
        "暗黑奇幻3D英雄近景、战场格子与分路站位、终极技能释放时机、巨型Boss伤害数字、英雄招募/阵营组合，以及《刺客信条》联动角色与场景。",
        "观察联动和公会战节点结束后能否守住TOP60，以及美国专属客户端的存量用户活跃能否继续支撑榜位。",
        store,
        [
            {"label": "Skystone Watcher of Realms隐私政策", "url": "https://us.skystone.games/wor-pp", "type": "primary"},
            {"label": "Watcher of Realms美国区官方站", "url": "https://us.skystone.games/", "type": "primary"},
            {"label": "Google Play美国区商品页", "url": "https://play.google.com/store/apps/details?id=com.td.uswatcherofrealms&hl=en_US", "type": "primary"},
            {"label": "Reuters沐瞳交易报道", "url": "https://www.reuters.com/world/asia-pacific/bytedance-sell-gaming-unit-moonton-saudi-pif-owned-firm-2026-03-20/", "type": "company-research"},
        ],
    )
    return game, company, refresh_audit_dates(analysis), icon, screenshot


def build_ios(rows, source_url, source_updated):
    old = load("data/ios-games-20260820.json")
    old_rank = {game["appId"]: game["rank"] for game in old}
    records = source_maps("data/ios-games-20260820.json", "data/ios-enrichment-20260820.json", "data/ios-trends-20260820.json")
    fallback = source_maps("data/ios-games-20260819.json", "data/ios-enrichment-20260819.json", "data/ios-trends-20260819.json")
    for app_id, value in fallback.items():
        records.setdefault(app_id, value)
    new_ids = [row["appId"] for row in rows if row["appId"] not in records]
    metadata = lookup(new_ids + ["6767834940"])
    assert new_ids == ["6741674823"], new_ids
    asset_bundle, companies, trends, games = {}, {}, {}, []
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id in records:
            original, company, analysis = records[app_id]
            game = deepcopy(original)
            if app_id == "6767834940":
                current = metadata[app_id]
                game["updatedDate"] = (current.get("currentVersionReleaseDate") or "")[:10]
                game["description"] = current.get("description", game.get("description", ""))
                game["shortDescription"] = game["description"].replace("\n", " ")[:220]
                analysis = refresh_audit_dates(deepcopy(analysis))
                analysis["sections"]["rankPath"] = "本次重返iOS美国策略畅销榜第56名，仍处首轮商业化验证的榜尾区间；由于缺少2026-05-23同口径基准，本次回榜不标为近三个月新上榜。"
                analysis["sections"]["turningPoints"] = "首发获量由滑动扩军和救回领民承担，随后用封地、税收、领主与狮鹫养成承接长期循环；8月20日版本新增开服第4天解锁的Trade Wagon科技树，是当前可确认的系统扩展节点。"
        else:
            game, company, analysis, icon, screenshot = watcher_record(row, metadata[app_id], 64)
            asset_bundle["64_icon"] = data_uri(icon, (256, 256))
            asset_bundle["64_store"] = data_uri(screenshot, (720, 720))
        game.update(
            rank=rank, gameName=row["gameName"], developer=row["developer"],
            dailyChange=delta_label(old_rank.get(app_id), rank),
            comparison90d=comparison(None, rank, IOS_DATE, IOS_BASELINE, True),
        )
        companies[str(rank)] = deepcopy(company)
        trends[str(rank)] = deepcopy(analysis)
        games.append(game)
    enrichment = deepcopy(load("data/ios-enrichment-20260820.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260821.json", games)
    save("data/ios-enrichment-20260821.json", enrichment)
    save("data/ios-trends-20260821.json", trends)
    save("assets/ios-assets-08.json", asset_bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if "ios-assets-08.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-08.json")
    save("assets/ios-manifest.json", manifest)
    save("data/history/ios/2026-08-21.json", {
        "store": "ios", "country": "US", "device": "iPhone",
        "category": "Games > Strategy > Top Grossing", "date": IOS_DATE,
        "sourceUpdated": source_updated, "sourceUrl": source_url,
        "rankings": [{
            "rank": game["rank"], "appId": game["appId"],
            "gameName": game["gameName"], "sourceUrl": game["storeUrl"],
        } for game in games],
    })
    return games


def main():
    google_url, google_rows = parse_google()
    ios_url, ios_updated, ios_rows = parse_ios()
    google = build_google(google_rows, google_url)
    ios = build_ios(ios_rows, ios_url, ios_updated)
    print("Google anchors:", [(g["rank"], g["gameName"]) for g in google if g["rank"] in (1, 25, 60)])
    print("iOS updated:", ios_updated)
    print("iOS anchors:", [(g["rank"], g["gameName"]) for g in ios if g["rank"] in (1, 25, 60)])
    print("iOS entrants:", [g["gameName"] for g in ios if g["dailyChange"] == "NEW"])


if __name__ == "__main__":
    main()
