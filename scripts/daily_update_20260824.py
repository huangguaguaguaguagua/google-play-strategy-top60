#!/usr/bin/env python3
"""Build the Beijing 2026-08-24 capture after the weekend."""
from copy import deepcopy

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_google, parse_ios, save, trend
from daily_update_20260821 import play_metadata, refresh_audit_dates

CAPTURE = "2026-08-24"
GOOGLE_DATE = "2026-08-23"
GOOGLE_BASELINE = "2026-05-25"
IOS_DATE = "2026-08-24"
IOS_BASELINE = "2026-05-26"


def records(games_path, enrichment_path, trends_path, id_key):
    games = load(games_path)
    companies = load(enrichment_path)["productCompaniesByRank"]
    trends = load(trends_path)
    return {
        str(game[id_key]): (game, companies[str(game["rank"])], trends[str(game["rank"])])
        for game in games
    }


def clean_analysis(analysis):
    analysis = refresh_audit_dates(deepcopy(analysis))
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    return analysis


def build_google(rows, source_url):
    current = records("data/games-20260821.json", "data/enrichment-20260821.json", "data/trends-20260821.json", "packageName")
    older = records("data/games-20260820.json", "data/enrichment-20260820.json", "data/trends-20260820.json", "packageName")
    ios_old = records("data/ios-games-20260819.json", "data/ios-enrichment-20260819.json", "data/ios-trends-20260819.json", "appId")
    ios_by_name = {v[0]["gameName"].lower(): v for v in ios_old.values()}
    old_rank = {k: v[0]["rank"] for k, v in current.items()}
    games, companies, trends, bundle = [], {}, {}, {}
    for row in rows:
        rank, package = row["rank"], row["packageName"]
        if package in current:
            game, company, analysis = map(deepcopy, current[package])
        elif package in older:
            game, company, analysis = map(deepcopy, older[package])
        elif row["gameName"].lower() == "warpath: ace shooter":
            prior, company, analysis = map(deepcopy, ios_by_name[row["gameName"].lower()])
            meta = play_metadata(package)
            game = deepcopy(prior)
            game.pop("appId", None)
            game.update(packageName=package, assetRank=65, iconUrl=meta["icon"], screenshotUrl=meta["screenshot"],
                        rankIconUrl=meta["icon"], totalInstalls=meta["downloads"], recentInstalls30d="",
                        shortDescription=meta["description"], description=meta["description"], updatedDate=meta["updated"])
            bundle["65_icon"] = data_uri(meta["icon"], (256, 256))
            bundle["65_store"] = data_uri(meta["screenshot"], (720, 720))
        else:
            raise RuntimeError(f"Unexpected Google entrant: {row}")
        game.update(rank=rank, gameName=row["gameName"], developer=row.get("developer", ""),
                    storeUrl=f"https://play.google.com/store/apps/details?id={package}&hl=en_US&gl=US",
                    dailyChange=delta_label(old_rank.get(package), rank),
                    comparison90d=comparison(None, rank, GOOGLE_DATE, GOOGLE_BASELINE, True))
        companies[str(rank)] = company
        trends[str(rank)] = clean_analysis(analysis)
        games.append(game)
    enrichment = deepcopy(load("data/enrichment-20260821.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260824.json", games)
    save("data/enrichment-20260824.json", enrichment)
    save("data/trends-20260824.json", trends)
    save("assets/assets-05.json", bundle)
    manifest = load("assets/manifest.json"); manifest["date"] = GOOGLE_DATE
    if "assets-05.json" not in manifest["files"]: manifest["files"].append("assets-05.json")
    save("assets/manifest.json", manifest)
    save("data/history/google-play/2026-08-24.json", {
        "store": "google-play", "country": "US", "category": "Games > Strategy > Top Grossing",
        "date": CAPTURE, "dataDate": GOOGLE_DATE, "sourceLastUpdated": "August 23, 2026", "sourceUrl": source_url,
        "rankings": [{"rank": g["rank"], "packageName": g["packageName"], "gameName": g["gameName"], "sourceUrl": g["storeUrl"]} for g in games],
    })
    return games


def overmortal(row, meta, asset_rank):
    app_id = row["appId"]
    store = f"https://apps.apple.com/us/app/id{app_id}"
    game = {
        "rank": row["rank"], "appId": app_id, "packageName": app_id, "gameName": row["gameName"],
        "developer": meta.get("sellerName", row["developer"]), "genre": "放置RPG / 卡牌 / 修仙",
        "keywords": "修仙；境界突破；文字冒险；伙伴；灵兽；双修；离线收益",
        "totalInstalls": "", "recentInstalls30d": "", "dailyChange": "NEW", "storeUrl": store,
        "iconUrl": meta["artworkUrl512"], "screenshotUrl": (meta.get("screenshotUrls") or [meta["artworkUrl512"]])[0],
        "shortDescription": meta.get("description", "").replace("\n", " ")[:220], "description": meta.get("description", ""),
        "releaseDate": meta["releaseDate"][:10], "releaseDateIso": meta["releaseDate"][:10],
        "updatedDate": meta.get("currentVersionReleaseDate", "")[:10], "note": "", "assetRank": asset_rank, "store": "ios",
    }
    company = {
        "en": "Hongkong Leiting Information Technology / Leiting Games / G-bits",
        "cn": "香港雷霆信息科技 / 雷霆游戏（吉比特旗下）/ 吉比特",
        "confidence": "已确认",
        "basis": "Apple店铺主体为Hongkong Leiting Information Technology；吉比特与雷霆游戏官方资料确认雷霆游戏为吉比特子公司。",
        "source": "https://www.g-bits.com/",
    }
    analysis = trend(
        "趋势：2023年以文字修仙、境界突破和离线成长切入，长期由伙伴/灵兽收集、跨服竞争与周期主题活动维持；关键转折：当前Devil Unbound限时活动把常规修炼叙事转成魔道主题回流节点；主力素材：凡人到仙人的境界跃迁、水墨角色、战力暴涨、道侣灵兽与离线资源。",
        "2023年上线后用‘凡人逆袭成仙’的低门槛文本叙事、自动修炼与境界突破承接放置用户，再逐步叠加伙伴、灵兽、宗门、跨服竞争和双修关系，把单线数值成长扩展为角色收集与社交竞争。",
        "本次进入iOS美国策略畅销榜第49名，属于成熟产品在限时活动期间的榜尾回归；缺少2026-05-26同口径基准，因此不标近三个月新上榜。",
        "未发现核心循环发生重大重构。可确认的当前节点是8月21日至27日Devil Unbound限时活动，以魔道主题签到、任务与限定奖励刺激回流；素材仍围绕境界和战力跃迁，而非转向新的玩法入口。",
        "水墨/国风仙侠立绘、凡人到仙人的身份跃迁、境界连续突破、战力数字跳升、伙伴与道侣关系、灵兽进化、离线收益及魔道限时角色。",
        "观察限时活动结束后能否继续留在TOP60，以及偏东方文字修仙题材在美国区的稳定核心用户规模。",
        store,
        [{"label": "吉比特官网", "url": "https://www.g-bits.com/", "type": "company-research"},
         {"label": "雷霆游戏官网", "url": "https://www.leiting.com/en/index.html", "type": "company-research"}],
    )
    return game, company, refresh_audit_dates(analysis)


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260821.json", "data/ios-enrichment-20260821.json", "data/ios-trends-20260821.json", "appId")
    old20 = records("data/ios-games-20260820.json", "data/ios-enrichment-20260820.json", "data/ios-trends-20260820.json", "appId")
    old19 = records("data/ios-games-20260819.json", "data/ios-enrichment-20260819.json", "data/ios-trends-20260819.json", "appId")
    google = records("data/games-20260821.json", "data/enrichment-20260821.json", "data/trends-20260821.json", "packageName")
    google_by_name = {v[0]["gameName"].lower(): v for v in google.values()}
    historical = dict(old19); historical.update(old20); historical.update(current)
    old_rank = {k: v[0]["rank"] for k, v in current.items()}
    entrant_ids = [r["appId"] for r in rows if r["appId"] not in historical]
    meta = lookup(entrant_ids)
    asset_ranks = {"6450879111": 65, "6755585789": 66, "1427744264": 67, "6742809194": 68}
    games, companies, trends, bundle = [], {}, {}, {}
    for row in rows:
        rank, app_id, name = row["rank"], row["appId"], row["gameName"]
        if app_id in historical:
            game, company, analysis = map(deepcopy, historical[app_id])
        elif app_id == "6450879111":
            game, company, analysis = overmortal(row, meta[app_id], asset_ranks[app_id])
            bundle["65_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle["65_store"] = data_uri(game["screenshotUrl"], (720, 720))
        elif name.lower() in google_by_name:
            prior, company, analysis = map(deepcopy, google_by_name[name.lower()])
            m, ar = meta[app_id], asset_ranks[app_id]
            icon = m.get("artworkUrl512") or m.get("artworkUrl100"); shot = (m.get("screenshotUrls") or [icon])[0]
            game = deepcopy(prior)
            game.update(appId=app_id, packageName=app_id, store="ios", assetRank=ar, iconUrl=icon, screenshotUrl=shot,
                        totalInstalls="", recentInstalls30d="", description=m.get("description", ""),
                        shortDescription=m.get("description", "").replace("\n", " ")[:220],
                        releaseDate=m.get("releaseDate", "")[:10], releaseDateIso=m.get("releaseDate", "")[:10],
                        updatedDate=m.get("currentVersionReleaseDate", "")[:10])
            bundle[f"{ar}_icon"] = data_uri(icon, (256, 256)); bundle[f"{ar}_store"] = data_uri(shot, (720, 720))
        else:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")
        game.update(rank=rank, gameName=name, developer=row["developer"],
                    storeUrl=f"https://apps.apple.com/us/app/id{app_id}", dailyChange=delta_label(old_rank.get(app_id), rank),
                    comparison90d=comparison(None, rank, IOS_DATE, IOS_BASELINE, True))
        analysis = clean_analysis(analysis)
        if app_id not in current:
            analysis["sections"]["rankPath"] = f"本次进入iOS美国策略畅销榜第{rank}名；由于缺少{IOS_BASELINE}同口径TOP60快照，只记录本次日榜进入，不标为近三个月新上榜。"
        companies[str(rank)] = company; trends[str(rank)] = analysis; games.append(game)
    enrichment = deepcopy(load("data/ios-enrichment-20260821.json")); enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260824.json", games); save("data/ios-enrichment-20260824.json", enrichment); save("data/ios-trends-20260824.json", trends)
    save("assets/ios-assets-09.json", bundle)
    manifest = load("assets/ios-manifest.json"); manifest["date"] = IOS_DATE
    if "ios-assets-09.json" not in manifest["files"]: manifest["files"].append("ios-assets-09.json")
    save("assets/ios-manifest.json", manifest)
    save("data/history/ios/2026-08-24.json", {
        "store": "ios", "country": "US", "device": "iPhone", "category": "Games > Strategy > Top Grossing",
        "date": IOS_DATE, "sourceUpdated": source_updated, "sourceUrl": source_url,
        "rankings": [{"rank": g["rank"], "appId": g["appId"], "gameName": g["gameName"], "sourceUrl": g["storeUrl"]} for g in games],
    })
    return games


def main():
    gu, gr = parse_google(); iu, updated, ir = parse_ios()
    google = build_google(gr, gu); ios = build_ios(ir, iu, updated)
    print("Google", [(g["rank"], g["gameName"]) for g in google if g["rank"] in (1,25,60)])
    print("iOS", updated, [(g["rank"], g["gameName"]) for g in ios if g["rank"] in (1,25,60)])


if __name__ == "__main__": main()
