#!/usr/bin/env python3
"""Build the Beijing 2026-08-25 direct Google Play and Apple RSS snapshots."""
import re
from copy import deepcopy

from lxml import html

from daily_update_20260820 import comparison, data_uri, delta_label, fetch, load, lookup, parse_ios, save, trend
from daily_update_20260821 import play_metadata, refresh_audit_dates
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-08-25"
GOOGLE_DATE = "2026-08-25"
GOOGLE_BASELINE = "2026-05-27"
IOS_DATE = "2026-08-25"
IOS_BASELINE = "2026-05-27"
APPBRAIN_URL = "https://www.appbrain.com/stats/google-play-rankings/top_grossing/strategy/us"


def records(games_path, enrichment_path, trends_path, id_key):
    games = load(games_path)
    companies = load(enrichment_path)["productCompaniesByRank"]
    trends = load(trends_path)
    return {
        str(game[id_key]): (game, companies[str(game["rank"])], trends[str(game["rank"])])
        for game in games
    }


def merged_records(specs, id_key):
    result = {}
    for games_path, enrichment_path, trends_path in reversed(specs):
        result.update(records(games_path, enrichment_path, trends_path, id_key))
    return result


def clean_analysis(analysis):
    analysis = refresh_audit_dates(deepcopy(analysis))
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


def refresh_rank_path(analysis, store_label, rank, change, status, release_date):
    path = analysis["sections"].get("rankPath", "")
    band = min(60, ((rank + 9) // 10) * 10)
    path = re.sub(r"((?:当前|本次|目前)[^。；]{0,120}?TOP)\d+", rf"\g<1>{band}", path, count=1)
    replacement = rf"\g<1>{rank}\g<2>"
    path, count = re.subn(r"((?:当前|本次|目前)[^。；]{0,120}?第)\d+(名)", replacement, path, count=1)
    if not count:
        movement = "首次进入本期榜单" if change == "NEW" else ("较前一榜单持平" if change == "=" else f"较前一榜单{change}位")
        path = f"本次位于{store_label}美国策略畅销榜第{rank}名（{movement}）。" + path
    if status == "new" and "按上架日期口径" not in path:
        path = f"{release_date}上架后进入{store_label}美国策略畅销榜第{rank}名，按上架日期口径属于近三个月新上榜。" + path
    analysis["sections"]["rankPath"] = path
    return analysis


def add_primary_source(analysis, label, url):
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        audit = analysis.get(audit_name, {})
        sources = audit.setdefault("sources", [])
        if not any(source.get("url") == url for source in sources):
            sources.insert(0, {"label": label, "url": url, "type": "primary"})


def appbrain_audit(google_rows):
    document = html.fromstring(fetch(APPBRAIN_URL))
    audit_rows = []
    for tr in document.xpath("//table//tr"):
        links = tr.xpath('.//a[contains(@href,"/app/")]/@href')
        if not links:
            continue
        package = links[0].rstrip("/").split("/")[-1]
        cells = [" ".join(td.text_content().split()) for td in tr.xpath("./td")]
        if package and cells:
            audit_rows.append({"rank": len(audit_rows) + 1, "packageName": package})
        if len(audit_rows) == 60:
            break
    updated_nodes = document.xpath('//*[contains(text(),"Last updated:")]')
    updated = " ".join(updated_nodes[0].text_content().split()).replace("Last updated:", "").strip() if updated_nodes else ""
    direct = {row["packageName"]: row["rank"] for row in google_rows}
    audit = {row["packageName"]: row["rank"] for row in audit_rows}
    common = sorted(set(direct) & set(audit))
    diffs = [abs(direct[package] - audit[package]) for package in common]
    return {
        "sourceRole": "audit-only",
        "sourceUrl": APPBRAIN_URL,
        "sourceLastUpdated": updated,
        "rowCount": len(audit_rows),
        "overlapCount": len(common),
        "sameRankCount": sum(direct[package] == audit[package] for package in common),
        "maxAbsRankDifference": max(diffs) if diffs else None,
        "note": "仅用于交叉检查，不覆盖Google Play直连排名、日期或产品字段。",
    }


def build_google(rows, source_info):
    historical = merged_records([
        ("data/games-20260824.json", "data/enrichment-20260824.json", "data/trends-20260824.json"),
        ("data/games-20260821.json", "data/enrichment-20260821.json", "data/trends-20260821.json"),
        ("data/games-20260820.json", "data/enrichment-20260820.json", "data/trends-20260820.json"),
        ("data/games-20260819d.json", "data/enrichment-20260819d.json", "data/trends-20260819d.json"),
    ], "packageName")
    current = records("data/games-20260824.json", "data/enrichment-20260824.json", "data/trends-20260824.json", "packageName")
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
            game["assetRank"] = 66
            bundle["66_icon"] = data_uri(row["iconUrl"], (256, 256))
            bundle["66_store"] = data_uri(row["screenshotUrl"], (720, 720))
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
    enrichment = deepcopy(load("data/enrichment-20260824.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260825.json", games)
    save("data/enrichment-20260825.json", enrichment)
    save("data/trends-20260825.json", trends)
    save("assets/assets-06.json", bundle)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    if "assets-06.json" not in manifest["files"]:
        manifest["files"].append("assets-06.json")
    save("assets/manifest.json", manifest)
    cross_check = appbrain_audit(rows)
    save("data/history/google-play/2026-08-25.json", {
        "store": "google-play", "country": "US", "category": "Games > Strategy > Top Grossing",
        "date": CAPTURE, "dataDate": GOOGLE_DATE, "sourceCapturedAt": source_info["capturedAt"],
        "sourceUrl": source_info["sourceUrl"], "sourceEndpoint": source_info["sourceEndpoint"],
        "sourceMethod": source_info["sourceMethod"],
        "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。",
        "crossCheck": cross_check,
        "rankings": [{"rank": game["rank"], "packageName": game["packageName"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]} for game in games],
    })
    return games, cross_check


def boom_beach(meta, asset_rank):
    store = "https://apps.apple.com/us/app/id672150402"
    game = {
        "appId": "672150402", "packageName": "672150402", "store": "ios", "assetRank": asset_rank,
        "genre": "SLG / RTS / 基地攻防", "keywords": "海岛；登陆战；侦察；基地攻防；特遣队；Warships；HQ29",
    }
    company = {
        "en": "Supercell Oy / Tencent-controlled consortium", "cn": "芬兰Supercell（腾讯控股财团控股）",
        "confidence": "已确认", "basis": "Apple店铺主体为Supercell Oy；腾讯牵头财团取得Supercell控制权，Supercell继续独立运营。",
        "source": "https://group.softbank/en/news/press/20160621",
    }
    analysis = trend(
        "趋势：2014年以侦察海岛、规划登陆路线和摧毁敌方基地建立异步攻防；关键转折：特遣队把单人掠夺扩为协作行动，Warships增加独立赛季竞争，近期HQ29与驻防建筑继续加深成熟用户养成；主力素材：登陆艇排兵、海滩火力网、基地布局、英雄技能与战舰赛季。",
        "2014年上线后把Clash式基地经营改造成先侦察、再选择登陆点和火力支援的海岛攻防，依靠玩家基地互攻、资源掠夺和地图解锁形成长线。特遣队行动随后加入协作目标，Warships再提供独立赛季地图，产品由单一基地攻防扩展为多条成熟用户循环。",
        "本次回到iOS美国策略畅销榜第31名；作为十年以上长线产品，榜位主要由版本更新、特遣队和核心用户付费支撑，而非新品买量。",
        "特遣队行动是从单人异步掠夺转向社交协作的重要节点；Warships把固定主基地之外加入赛季化科技树和即时配对。2026年夏季版本开放HQ29、Garrison驻防建筑和新Laser Ranger领队，当前回榜与高等级内容更新同期出现，但不把相关性写成已证实因果。",
        "侦察后选择登陆点、登陆艇兵种组合、火炮/震爆支援、密集防御建筑被逐个拆解、特遣队巨型基地，以及Warships赛季科技树与HQ29驻防展示。",
        "观察HQ29升级周期结束后是否仍能保持TOP60，以及驻防单位是否改变成熟基地的攻守配置与付费深度。",
        store,
        [
            {"label": "Supercell官方Boom Beach页面", "url": "https://supercell.com/en/games/boombeach/", "type": "primary"},
            {"label": "Supercell控制权公告", "url": "https://group.softbank/en/news/press/20160621", "type": "company-research"},
        ],
    )
    return game, company, analysis


def kingdom_clash(meta, asset_rank):
    store = "https://apps.apple.com/us/app/id1611722542"
    game = {
        "appId": "1611722542", "packageName": "1611722542", "store": "ios", "assetRank": asset_rank,
        "genre": "塔防 / 合并 / 战术对战", "keywords": "中世纪；军团布阵；合并升级；Boss；PvP；氏族；神话英雄",
    }
    company = {
        "en": "AI GAMES FZ LLC / AZUR GAMES", "cn": "AI Games（Azur Games海外发行体系）",
        "confidence": "已确认", "basis": "Apple店铺主体为AI GAMES FZ LLC；Azur Games官方产品列表及产品社区入口均将Kingdom Clash列为旗下产品。",
        "source": "https://azurgames.com/games/",
    }
    analysis = trend(
        "趋势：2022年以小兵合并、军团布阵和自动交战切入轻量中世纪策略；关键转折：2025年新增神话英雄、主题通行证与活动后出现四年内最大收入峰值，当前再用氏族Boss、聊天互动和复仇规则强化社交；主力素材：小兵合并升级、阵型克制、巨型Boss、神话英雄和氏族协作。",
        "2022年上线时把中世纪军团战压缩成布阵、合并同类单位和自动交战，先用清晰的数量与等级变化承接休闲用户，再加入英雄、竞技场、Boss与长期养成。当前产品已从单局战斗扩展到氏族协作和持续活动运营。",
        "本次进入iOS美国策略畅销榜第47名；产品上架已超过90天，本次按成熟产品回榜处理，缺少2026-05-27同口径基准时暂不判断飙升。",
        "Azur Games披露2025年神话英雄新稀有度、主题Battle Pass和新活动带来产品四年内最大收入峰值，是可确认的商业化转折。2026年8月版本继续加入氏族Boss、聊天表情和更公平的复仇占用规则，运营重点由个人合并战斗进一步转向社交留存。",
        "低级小兵合并为高阶单位、战前阵型调整、双方军团自动碰撞、Boss体型压迫、神话英雄解锁，以及氏族成员共同击杀Boss和领取金币。",
        "观察氏族更新能否把阶段性回榜转成稳定留存，以及社交循环相对神话英雄付费层的持续贡献。",
        store,
        [
            {"label": "Azur Games官方产品列表", "url": "https://azurgames.com/games/", "type": "primary"},
            {"label": "Azur Games神话英雄更新复盘", "url": "https://azurgames.com/blog/a-new-progression-layer-in-a-midcore-battler/", "type": "lifecycle-analysis"},
        ],
    )
    return game, company, analysis


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260824.json", "data/ios-enrichment-20260824.json", "data/ios-trends-20260824.json", "appId")
    historical_ios = merged_records([
        ("data/ios-games-20260824.json", "data/ios-enrichment-20260824.json", "data/ios-trends-20260824.json"),
        ("data/ios-games-20260821.json", "data/ios-enrichment-20260821.json", "data/ios-trends-20260821.json"),
        ("data/ios-games-20260820.json", "data/ios-enrichment-20260820.json", "data/ios-trends-20260820.json"),
        ("data/ios-games-20260819.json", "data/ios-enrichment-20260819.json", "data/ios-trends-20260819.json"),
    ], "appId")
    historical_google = merged_records([
        ("data/games-20260824.json", "data/enrichment-20260824.json", "data/trends-20260824.json"),
        ("data/games-20260821.json", "data/enrichment-20260821.json", "data/trends-20260821.json"),
        ("data/games-20260820.json", "data/enrichment-20260820.json", "data/trends-20260820.json"),
    ], "packageName")
    google_fallback = {
        "966810173": "com.plarium.vikings",
        "1274354704": "com.diandian.gog",
    }
    old_rank = {app_id: value[0]["rank"] for app_id, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in current]
    metadata = lookup(entrant_ids)
    games, companies, trends, bundle = [], {}, {}, {}
    next_asset = 69
    for row in rows:
        rank, app_id, name = row["rank"], row["appId"], row["gameName"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        else:
            meta = metadata[app_id]
            if app_id in historical_ios:
                game, company, analysis = map(deepcopy, historical_ios[app_id])
            elif app_id in google_fallback:
                game, company, analysis = map(deepcopy, historical_google[google_fallback[app_id]])
                game.pop("appId", None)
                if app_id == "966810173":
                    company["source"] = "https://www.mtg.com/press-releases/mtg-completes-the-acquisition-of-plarium-and-becomes-a-scaled-midcore-gaming-leader/"
            elif app_id == "672150402":
                game, company, analysis = boom_beach(meta, next_asset)
            elif app_id == "1611722542":
                game, company, analysis = kingdom_clash(meta, next_asset)
            else:
                raise RuntimeError(f"Unexpected iOS entrant: {row}")
            icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
            screenshot = (meta.get("screenshotUrls") or [icon])[0]
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
        analysis = clean_analysis(analysis)
        if app_id == "6767834940":
            analysis["sections"]["rankPath"] = "2026年5月31日上架后，以滑动扩军和领地经营进入iOS美国策略畅销榜第55名；按上架日期口径属于近三个月新上榜。当前仍处首轮商业化验证，榜尾位置对买量和开服活动较敏感。"
        else:
            analysis = refresh_rank_path(analysis, "iOS", rank, change, comp["status"], game.get("releaseDateIso", ""))
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)
    enrichment = deepcopy(load("data/ios-enrichment-20260824.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260825.json", games)
    save("data/ios-enrichment-20260825.json", enrichment)
    save("data/ios-trends-20260825.json", trends)
    save("assets/ios-assets-10.json", bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if "ios-assets-10.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-10.json")
    save("assets/ios-manifest.json", manifest)
    save("data/history/ios/2026-08-25.json", {
        "store": "ios", "country": "US", "device": "iPhone", "category": "Games > Strategy > Top Grossing",
        "date": IOS_DATE, "sourceUpdated": source_updated, "sourceUrl": source_url,
        "rankings": [{"rank": game["rank"], "appId": game["appId"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]} for game in games],
    })
    return games


def main():
    google_source = fetch_top_grossing_strategy()
    ios_url, ios_updated, ios_rows = parse_ios()
    google, audit = build_google(google_source["rows"], google_source)
    ios = build_ios(ios_rows, ios_url, ios_updated)
    print("Google", google_source["capturedAt"], [(game["rank"], game["gameName"]) for game in google if game["rank"] in (1, 25, 60)])
    print("AppBrain audit", audit)
    print("iOS", ios_updated, [(game["rank"], game["gameName"]) for game in ios if game["rank"] in (1, 25, 60)])


if __name__ == "__main__":
    main()
