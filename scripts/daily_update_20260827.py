#!/usr/bin/env python3
"""Build the Beijing 2026-08-27 direct Google Play and Apple RSS snapshots."""
from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_ios, save, trend
from daily_update_20260821 import play_metadata
from daily_update_20260825 import add_primary_source, appbrain_audit, merged_records, records, refresh_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-08-27"
GOOGLE_DATE = "2026-08-27"
GOOGLE_BASELINE = "2026-05-29"
IOS_DATE = "2026-08-27"
IOS_BASELINE = "2026-05-29"


def clean_analysis(analysis):
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


def build_google(rows, source_info):
    historical = merged_records([
        ("data/games-20260826.json", "data/enrichment-20260826.json", "data/trends-20260826.json"),
        ("data/games-20260825.json", "data/enrichment-20260825.json", "data/trends-20260825.json"),
        ("data/games-20260824.json", "data/enrichment-20260824.json", "data/trends-20260824.json"),
        ("data/games-20260821.json", "data/enrichment-20260821.json", "data/trends-20260821.json"),
        ("data/games-20260820.json", "data/enrichment-20260820.json", "data/trends-20260820.json"),
        ("data/games-20260819d.json", "data/enrichment-20260819d.json", "data/trends-20260819d.json"),
    ], "packageName")
    current = records("data/games-20260826.json", "data/enrichment-20260826.json", "data/trends-20260826.json", "packageName")
    old_rank = {package: value[0]["rank"] for package, value in current.items()}
    games, companies, trends, bundle = [], {}, {}, {}
    for row in rows:
        rank, package = row["rank"], row["packageName"]
        if package not in historical:
            raise RuntimeError(f"Unexpected Google entrant: {row}")
        game, company, analysis = map(deepcopy, historical[package])
        if package not in current:
            metadata = play_metadata(package)
            game["releaseDate"] = metadata.get("released") or game.get("releaseDate", "")
            game["releaseDateIso"] = metadata.get("released") or game.get("releaseDateIso", "")
            game["assetRank"] = 68
            bundle["68_icon"] = data_uri(row["iconUrl"], (256, 256))
            bundle["68_store"] = data_uri(row["screenshotUrl"], (720, 720))
        change = delta_label(old_rank.get(package), rank)
        comp = comparison(None, rank, GOOGLE_DATE, GOOGLE_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank, gameName=row["gameName"], developer=row.get("developer", ""),
            storeUrl=row["storeUrl"], iconUrl=row["iconUrl"], screenshotUrl=row["screenshotUrl"],
            totalInstalls=str(row.get("downloads") or "").replace("+", " +"), dailyChange=change,
            comparison90d=comp,
        )
        analysis = refresh_rank_path(clean_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", ""))
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)
    enrichment = deepcopy(load("data/enrichment-20260826.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260827.json", games)
    save("data/enrichment-20260827.json", enrichment)
    save("data/trends-20260827.json", trends)
    save("assets/assets-08.json", bundle)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    if "assets-08.json" not in manifest["files"]:
        manifest["files"].append("assets-08.json")
    save("assets/manifest.json", manifest)
    cross_check = appbrain_audit(rows)
    save("data/history/google-play/2026-08-27.json", {
        "store": "google-play", "country": "US", "category": "Games > Strategy > Top Grossing",
        "date": CAPTURE, "dataDate": GOOGLE_DATE, "sourceCapturedAt": source_info["capturedAt"],
        "sourceUrl": source_info["sourceUrl"], "sourceEndpoint": source_info["sourceEndpoint"],
        "sourceMethod": source_info["sourceMethod"],
        "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。",
        "crossCheck": cross_check,
        "rankings": [{"rank": game["rank"], "packageName": game["packageName"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]} for game in games],
    })
    return games, cross_check


def hearthstone(asset_rank):
    store = "https://apps.apple.com/us/app/id625257520"
    game = {
        "appId": "625257520", "packageName": "625257520", "store": "ios", "assetRank": asset_rank,
        "genre": "卡牌策略 / CCG / 自走棋", "keywords": "Warcraft；套牌构筑；标准模式；酒馆战棋；竞技场；36.4；Class Sets",
    }
    company = {
        "en": "Blizzard Entertainment / Activision Blizzard / Microsoft",
        "cn": "暴雪娱乐（Activision Blizzard；微软旗下）",
        "confidence": "已确认",
        "basis": "Apple店铺主体为Blizzard Entertainment, Inc.；微软官方确认已于2023年完成对Activision Blizzard的收购。",
        "source": "https://blogs.microsoft.com/on-the-issues/2024/10/15/one-year-activision-blizzard/",
    }
    analysis = trend(
        "趋势：2014年以易上手的Warcraft卡牌对战切入，标准轮换和持续扩展包维持CCG核心，酒馆战棋再拓宽自走棋人群；关键转折：模式层从单一构筑对战扩成标准/狂野/竞技场/酒馆战棋并行，2026年36.4以四组职业套牌、免费事件和新竞技场赛季制造回流；主力素材：Warcraft英雄、职业套牌联动、稀有卡开包、残局翻盘、八人酒馆战棋与限时奖励。",
        "2014年移动端上线时以Warcraft英雄、30张套牌和短时PvP降低传统集换式卡牌门槛；2016年标准模式与年度轮换建立长期内容节奏，2019年酒馆战棋把产品从构筑CCG拓展为八人自走棋平台。此后扩展包、平衡补丁、竞技场赛季与免费事件共同承接不同活跃层。",
        "本次从榜外进入iOS美国策略畅销榜第44名；产品上架已超过90天，按成熟产品阶段性回榜处理。回榜时间与8月25日36.4版本上线重合，但单日相关性不写成已证实因果。",
        "可确认的长期转折是标准轮换稳定卡池更新节奏，以及酒馆战棋新增独立玩法人群。2026年《Escape from Violet Hold》后，36.4追加牧师、潜行者、术士和战士四套Class Sets，并同步新竞技场赛季、Rulebreaker Revelry免费奖励与世界冠军乱斗，当前更依赖内容消费、回流与核心卡牌用户。",
        "Warcraft高认知英雄、职业套牌连锁、单回合斩杀与残局反转、传奇卡开包、八人酒馆战棋阵容成长、Class Sets合集、Rulebreaker Revelry奖励轨和Kel'Thuzad变形皮肤。",
        "观察36.4上线后未来2—3个工作日能否守住TOP60，并区分职业套牌付费高点、免费活动回流与竞技场新赛季带来的不同持续性。",
        store,
        [
            {"label": "Hearthstone 36.4官方补丁说明", "url": "https://news.blizzard.com/en-us/article/24293283/36-4-patch-notes", "type": "lifecycle-analysis"},
            {"label": "微软完成Activision Blizzard收购", "url": "https://blogs.microsoft.com/on-the-issues/2024/10/15/one-year-activision-blizzard/", "type": "company-research"},
        ],
    )
    return game, company, analysis


def jurassic_world_alive(asset_rank):
    store = "https://apps.apple.com/us/app/id1231085864"
    game = {
        "appId": "1231085864", "packageName": "1231085864", "store": "ios", "assetRank": asset_rank,
        "genre": "位置服务 / 收集养成 / 回合制PvP", "keywords": "Jurassic World；GPS探索；DNA；混种恐龙；AR；实时PvP；Travel Hub；Mattel活动",
    }
    company = {
        "en": "Ludia Inc. (independent Canadian ownership) / Universal Jurassic World licensed IP",
        "cn": "Ludia（加拿大独立手游工作室；Universal《侏罗纪世界》授权）",
        "confidence": "已确认",
        "basis": "Apple店铺主体为Ludia Games inc.；Ludia官方确认2025年从Jam City回购后由加拿大本地股东与管理层控股，产品官方页列明Universal/Amblin IP权利。",
        "source": "https://www.ludia.com/press-release/press-release",
    }
    analysis = trend(
        "趋势：2018年以GPS地图找恐龙、无人机采集DNA和AR展示切入，再用混种合成与实时PvP承接长期养成；关键转折：联盟、赛事与Travel Hub逐步降低纯户外限制，3.22又以Mattel收集活动和更长远程采集时段强化成熟用户回访；主力素材：现实地图恐龙遭遇、无人机射镖、DNA孵化、混种进化、巨兽对战与IP活动收藏。",
        "2018年上线时把《Jurassic World》IP与位置服务结合，玩家在现实地图发现恐龙、用无人机采集DNA，并通过实验室创造混种后进入实时PvP。后续联盟、赛事、Raid、季节活动与Travel Hub让产品从单人户外收集扩展为社交竞争和可远程补充的长线养成。",
        "本次从榜外进入iOS美国策略畅销榜第55名；产品上架已超过90天，属于成熟产品榜尾回榜。8月3.22版本和Mattel收集活动提供了同期运营节点，但尚不能据单日榜位确认直接驱动。",
        "早期传播重点是‘恐龙出现在现实街区’和AR震撼，随后逐步转向DNA稀有度、混种队伍、实时PvP与联盟赛事。3.22在8月12日开启Mattel Toy Collection，加入两只活动恐龙、Toy Chips与限时成长路径，同时把Travel Hub普通采集时长从10秒提高到16秒，明显服务长期收集效率。",
        "现实地图上发现霸王龙、无人机射镖采集DNA、实验室合成混种、巨型恐龙AR合影、属性克制与实时PvP、Mattel玩具主题恐龙、Toy Chips兑换及Travel Hub远程采集。",
        "观察Mattel活动结束后能否继续留榜，并核对3.22的Travel Hub效率提升和后续平衡调整是否改善成熟收藏用户的付费与回访。",
        store,
        [
            {"label": "Jurassic World Alive 3.22官方说明", "url": "https://jurassicworldalive.com/release-notes/update-3-22-release-notes/", "type": "lifecycle-analysis"},
            {"label": "Ludia恢复加拿大独立所有权公告", "url": "https://www.ludia.com/press-release/press-release", "type": "company-research"},
        ],
    )
    return game, company, analysis


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260826.json", "data/ios-enrichment-20260826.json", "data/ios-trends-20260826.json", "appId")
    historical_ios = merged_records([
        ("data/ios-games-20260826.json", "data/ios-enrichment-20260826.json", "data/ios-trends-20260826.json"),
        ("data/ios-games-20260825.json", "data/ios-enrichment-20260825.json", "data/ios-trends-20260825.json"),
        ("data/ios-games-20260824.json", "data/ios-enrichment-20260824.json", "data/ios-trends-20260824.json"),
        ("data/ios-games-20260821.json", "data/ios-enrichment-20260821.json", "data/ios-trends-20260821.json"),
        ("data/ios-games-20260820.json", "data/ios-enrichment-20260820.json", "data/ios-trends-20260820.json"),
        ("data/ios-games-20260819.json", "data/ios-enrichment-20260819.json", "data/ios-trends-20260819.json"),
    ], "appId")
    old_rank = {app_id: value[0]["rank"] for app_id, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in current]
    metadata = lookup(entrant_ids)
    if set(metadata) != set(entrant_ids):
        raise RuntimeError(f"Apple Lookup did not return every entrant: {entrant_ids}")
    games, companies, trends, bundle = [], {}, {}, {}
    next_asset = 77
    for row in rows:
        rank, app_id, name = row["rank"], row["appId"], row["gameName"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        else:
            meta = metadata[app_id]
            if app_id == "625257520":
                game, company, analysis = hearthstone(next_asset)
            elif app_id == "1231085864":
                game, company, analysis = jurassic_world_alive(next_asset)
            elif app_id in historical_ios:
                game, company, analysis = map(deepcopy, historical_ios[app_id])
            else:
                raise RuntimeError(f"Unexpected iOS entrant: {row}")
            icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
            screenshot = (meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or [icon])[0]
            game.update(
                appId=app_id, packageName=app_id, store="ios", assetRank=next_asset,
                iconUrl=icon, screenshotUrl=screenshot, rankIconUrl=icon,
                description=meta.get("description", ""), shortDescription=meta.get("description", "").replace("\n", " ")[:220],
                releaseDate=(meta.get("releaseDate") or "")[:10], releaseDateIso=(meta.get("releaseDate") or "")[:10],
                updatedDate=(meta.get("currentVersionReleaseDate") or "")[:10], totalInstalls="", recentInstalls30d="",
            )
            bundle[f"{next_asset}_icon"] = data_uri(icon, (256, 256))
            bundle[f"{next_asset}_store"] = data_uri(screenshot, (720, 720))
            add_primary_source(analysis, "Apple App Store美国区商品页", f"https://apps.apple.com/us/app/id{app_id}")
            next_asset += 1
        change = delta_label(old_rank.get(app_id), rank)
        comp = comparison(None, rank, IOS_DATE, IOS_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank, gameName=name, developer=row["developer"], store="ios",
            storeUrl=f"https://apps.apple.com/us/app/id{app_id}", dailyChange=change, comparison90d=comp,
        )
        analysis = refresh_rank_path(clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", ""))
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)
    enrichment = deepcopy(load("data/ios-enrichment-20260826.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260827.json", games)
    save("data/ios-enrichment-20260827.json", enrichment)
    save("data/ios-trends-20260827.json", trends)
    save("assets/ios-assets-12.json", bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if "ios-assets-12.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-12.json")
    save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save("data/history/ios/2026-08-27.json", {
        "store": "ios", "country": "US", "device": "iPhone", "category": "Games > Strategy > Top Grossing",
        "date": source_date, "dataDate": source_date, "sourceUpdated": source_updated, "sourceUrl": source_url,
        "rankings": [{"rank": game["rank"], "appId": game["appId"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]} for game in games],
    })
    return games, source_date


def main():
    google_source = fetch_top_grossing_strategy()
    ios_url, ios_updated, ios_rows = parse_ios()
    if google_source["dataDate"] != GOOGLE_DATE:
        raise RuntimeError(f"Google capture date is {google_source['dataDate']}, expected {GOOGLE_DATE}")
    google, audit = build_google(google_source["rows"], google_source)
    ios, ios_source_date = build_ios(ios_rows, ios_url, ios_updated)
    if ios_source_date != IOS_DATE:
        raise RuntimeError(f"Apple source is still dated {ios_source_date}; keep the previous valid iOS snapshot")
    print("Google", google_source["capturedAt"], [(game["rank"], game["gameName"]) for game in google if game["rank"] in (1, 25, 60)])
    print("AppBrain audit", audit)
    print("iOS", ios_updated, [(game["rank"], game["gameName"]) for game in ios if game["rank"] in (1, 25, 60)])


if __name__ == "__main__":
    main()
