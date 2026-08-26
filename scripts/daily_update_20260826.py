#!/usr/bin/env python3
"""Build the Beijing 2026-08-26 direct Google Play and Apple RSS snapshots."""
from copy import deepcopy

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_ios, save, trend
from daily_update_20260821 import play_metadata
from daily_update_20260825 import add_primary_source, appbrain_audit, merged_records, records, refresh_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-08-26"
GOOGLE_DATE = "2026-08-26"
GOOGLE_BASELINE = "2026-05-28"
IOS_DATE = "2026-08-26"
IOS_BASELINE = "2026-05-28"


def clean_analysis(analysis):
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


def build_google(rows, source_info):
    historical = merged_records([
        ("data/games-20260825.json", "data/enrichment-20260825.json", "data/trends-20260825.json"),
        ("data/games-20260824.json", "data/enrichment-20260824.json", "data/trends-20260824.json"),
        ("data/games-20260821.json", "data/enrichment-20260821.json", "data/trends-20260821.json"),
        ("data/games-20260820.json", "data/enrichment-20260820.json", "data/trends-20260820.json"),
    ], "packageName")
    current = records("data/games-20260825.json", "data/enrichment-20260825.json", "data/trends-20260825.json", "packageName")
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
            game["assetRank"] = 67
            bundle["67_icon"] = data_uri(row["iconUrl"], (256, 256))
            bundle["67_store"] = data_uri(row["screenshotUrl"], (720, 720))
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
    enrichment = deepcopy(load("data/enrichment-20260825.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260826.json", games)
    save("data/enrichment-20260826.json", enrichment)
    save("data/trends-20260826.json", trends)
    save("assets/assets-07.json", bundle)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    if "assets-07.json" not in manifest["files"]:
        manifest["files"].append("assets-07.json")
    save("assets/manifest.json", manifest)
    cross_check = appbrain_audit(rows)
    save("data/history/google-play/2026-08-26.json", {
        "store": "google-play", "country": "US", "category": "Games > Strategy > Top Grossing",
        "date": CAPTURE, "dataDate": GOOGLE_DATE, "sourceCapturedAt": source_info["capturedAt"],
        "sourceUrl": source_info["sourceUrl"], "sourceEndpoint": source_info["sourceEndpoint"],
        "sourceMethod": source_info["sourceMethod"],
        "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。",
        "crossCheck": cross_check,
        "rankings": [{"rank": game["rank"], "packageName": game["packageName"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]} for game in games],
    })
    return games, cross_check


def dc_dark_legion(meta, asset_rank):
    store = "https://apps.apple.com/us/app/id6479020757"
    game = {
        "appId": "6479020757", "packageName": "6479020757", "store": "ios", "assetRank": asset_rank,
        "genre": "卡牌RPG / 策略 / 基地经营", "keywords": "DC；蝙蝠侠；小丑；黑暗多元宇宙；英雄收集；蝙蝠洞；PvP",
    }
    company = {
        "en": "FunPlus International AG / FunPlus (DC licensed by Warner Bros. Interactive Entertainment)",
        "cn": "趣加游戏（FunPlus；华纳兄弟互动娱乐代表DC授权）",
        "confidence": "已确认",
        "basis": "Apple店铺主体为FunPlus International AG；FunPlus官方发行公告确认产品由FunPlus推出，并由Warner Bros. Interactive Entertainment代表DC授权。",
        "source": "https://funplus.com/dc-dark-legion-global-launch-lead-the-league/",
    }
    analysis = trend(
        "趋势：2025年借蝙蝠侠、小丑和黑暗多元宇宙完成强IP首发，英雄编队与蝙蝠洞经营承接中长期付费；关键转折：上线六周突破500万玩家后，运营从基础DC角色认知转向电影事件和长尾角色更新，2026年Supergirl电影活动与Cassandra Cain入场继续制造回流；主力素材：超级英雄危机、正邪混编、角色强度对比、蝙蝠洞扩建与联盟PvP。",
        "2025年3月全球上线时，以《Dark Nights: Metal》黑暗多元宇宙危机和蝙蝠侠/小丑等高认知角色降低获量门槛，再把用户导入英雄收集、队伍协同、蝙蝠洞设施和PvE/PvP。官方在上线约六周宣布超过500万玩家，之后进入以角色池和IP事件维持活跃的运营阶段。",
        "本次进入iOS美国策略畅销榜第43名；产品上架已超过90天，按成熟产品阶段性回榜处理。缺少2026-05-28同口径TOP60快照，暂不判断近三个月飙升。",
        "首发重点是黑暗骑士入侵、正邪英雄首次联手和50名角色阵容；成熟期逐渐转向具体角色与影视节点。2026年6月Supergirl电影主题活动加入新Champion与基地外观，7月继续推出Cassandra Cain，说明当前主要依赖DC内容节奏、角色收集与核心联盟/PvP用户，而非重新更换底层玩法。",
        "蝙蝠侠、小丑、超人和神奇女侠同屏，黑暗多元宇宙危机倒计时，英雄克制与阵容组合、抽取/升星、蝙蝠洞房间扩建、联盟共同作战，以及Supergirl等影视同步角色。",
        "观察Cassandra Cain等角色更新后的TOP60留存，以及影视事件结束后英雄收集和联盟PvP能否维持付费强度。",
        store,
        [
            {"label": "FunPlus全球发行公告", "url": "https://funplus.com/dc-dark-legion-global-launch-lead-the-league/", "type": "primary"},
            {"label": "FunPlus 500万玩家里程碑", "url": "https://funplus.com/dc-dark-legion-hits-5-million-players-in-a-flash/", "type": "lifecycle-analysis"},
            {"label": "Supergirl电影主题活动", "url": "https://funplus.com/funplus-brings-supergirl-to-dc-dark-legion/", "type": "lifecycle-analysis"},
            {"label": "DC Dark Legion官方站", "url": "https://dcdarklegion.com/", "type": "primary"},
        ],
    )
    return game, company, analysis


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260825.json", "data/ios-enrichment-20260825.json", "data/ios-trends-20260825.json", "appId")
    historical_ios = merged_records([
        ("data/ios-games-20260825.json", "data/ios-enrichment-20260825.json", "data/ios-trends-20260825.json"),
        ("data/ios-games-20260824.json", "data/ios-enrichment-20260824.json", "data/ios-trends-20260824.json"),
        ("data/ios-games-20260821.json", "data/ios-enrichment-20260821.json", "data/ios-trends-20260821.json"),
        ("data/ios-games-20260819.json", "data/ios-enrichment-20260819.json", "data/ios-trends-20260819.json"),
    ], "appId")
    historical_google = merged_records([
        ("data/games-20260825.json", "data/enrichment-20260825.json", "data/trends-20260825.json"),
        ("data/games-20260824.json", "data/enrichment-20260824.json", "data/trends-20260824.json"),
        ("data/games-20260821.json", "data/enrichment-20260821.json", "data/trends-20260821.json"),
        ("data/games-20260820.json", "data/enrichment-20260820.json", "data/trends-20260820.json"),
    ], "packageName")
    google_fallback = {
        "1529067679": "com.wondergames.warpath.gp",
        "1570095804": "com.tap4fun.odin.kingdomguard",
    }
    old_rank = {app_id: value[0]["rank"] for app_id, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in current]
    metadata = lookup(entrant_ids)
    games, companies, trends, bundle = [], {}, {}, {}
    next_asset = 74
    for row in rows:
        rank, app_id, name = row["rank"], row["appId"], row["gameName"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        else:
            meta = metadata[app_id]
            if app_id == "6479020757":
                game, company, analysis = dc_dark_legion(meta, next_asset)
            elif app_id in google_fallback:
                game, company, analysis = map(deepcopy, historical_google[google_fallback[app_id]])
                game.pop("appId", None)
            elif app_id in historical_ios:
                game, company, analysis = map(deepcopy, historical_ios[app_id])
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
        analysis = refresh_rank_path(clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", ""))
        if app_id == "1529067679":
            analysis["summary"] = "趋势：2021年先以电影化狙击任务和二战军团切入，随后扩展自由行军、联盟战与海陆空战场；关键转折：获量重心由单人狙击慢镜逐渐转向大地图实时RTS，当前通过Warbound全球邀请赛与年度BattleFest强化成熟联盟用户；主力素材：狙击慢镜、坦克集群、自由缩放战场、舰队封锁和赛事对抗。"
            analysis["sections"]["rankPath"] = "2021年上线后由狙击入口逐步转向大地图RTS，本次回到iOS美国策略畅销榜第56名；当前榜位更接近Warbound全球邀请赛、年度BattleFest和成熟联盟竞争共同形成的阶段位置。"
            analysis["sections"]["turningPoints"] = "早期广告常用单枪爆破桥梁和子弹慢镜吸引泛战争用户，随后逐步强化可自由移动的军团、地形包围和多人联盟战，把传播重点从单人射击迁到实时RTS。海军地图又把战场由陆空扩至海域；2026年版本进一步用Warbound全球邀请赛、年度BattleFest、赛事竞猜和观战承接成熟核心用户。"
            analysis["sections"]["creative"] = "狙击瞄准与子弹慢镜、坦克列阵、自由缩放大地图、桥梁爆破、联盟包围、海军舰队争夺战略点，以及Warbound赛事队伍和冠军奖励。"
            analysis["sections"]["watch"] = "关注全球邀请赛与BattleFest结束后的榜位留存，以及射击入口、海陆空RTS和成熟联盟赛事三层用户能否持续衔接。"
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)
    enrichment = deepcopy(load("data/ios-enrichment-20260825.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260826.json", games)
    save("data/ios-enrichment-20260826.json", enrichment)
    save("data/ios-trends-20260826.json", trends)
    save("assets/ios-assets-11.json", bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if "ios-assets-11.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-11.json")
    save("assets/ios-manifest.json", manifest)
    save("data/history/ios/2026-08-26.json", {
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
