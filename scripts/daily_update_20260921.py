#!/usr/bin/env python3
"""Build the Beijing 2026-09-21 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, parse_ios, save, trend
from daily_update_20260821 import play_metadata
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = GOOGLE_DATE = IOS_DATE = "2026-09-21"
GOOGLE_BASELINE = IOS_BASELINE = "2026-06-23"
GOOGLE_DATES = (
    "20260918", "20260917", "20260916", "20260915", "20260914", "20260911", "20260910",
    "20260909", "20260908", "20260907", "20260904", "20260903", "20260902", "20260901",
    "20260831", "20260828", "20260827", "20260826", "20260825", "20260824", "20260821",
    "20260820", "20260819d",
)
IOS_DATES = (
    "20260918", "20260917", "20260916", "20260915", "20260914", "20260911", "20260910",
    "20260909", "20260908", "20260907", "20260904", "20260903", "20260902", "20260901",
    "20260831", "20260828", "20260827", "20260826", "20260825", "20260824", "20260821",
    "20260820", "20260819",
)


def history_specs(prefix, dates):
    return [
        (f"data/{prefix}games-{date}.json", f"data/{prefix}enrichment-{date}.json", f"data/{prefix}trends-{date}.json")
        for date in dates
    ]


def clean_analysis(analysis):
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(name):
            analysis[name]["reviewedAt"] = CAPTURE
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


def dc_google_profile(row, metadata):
    release = metadata.get("released") or "2025-03-13"
    if release != "2025-03-13":
        raise RuntimeError(f"Unexpected DC: Dark Legion release date: {release}")
    game = {
        "rank": row["rank"],
        "packageName": row["packageName"],
        "gameName": row["gameName"],
        "developer": metadata.get("developer") or "FunPlus International AG",
        "totalInstalls": metadata.get("downloads", ""),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"],
        "store": "googlePlay",
        "storeUrl": metadata["url"],
        "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"],
        "shortDescription": metadata.get("description", ""),
        "description": "DC官方授权策略RPG：收集超级英雄与反派编队，扩建蝙蝠洞，并参与PvE、联盟与多人PvP。",
        "releaseDate": release,
        "updatedDate": metadata.get("updated", ""),
        "genre": "卡牌RPG / 策略 / 基地经营",
        "keywords": "DC；蝙蝠侠；小丑；黑暗多元宇宙；英雄收集；蝙蝠洞；PvP",
        "note": "",
        "releaseDateIso": release,
        "assetRank": 79,
        "comparison90d": comparison(None, row["rank"], GOOGLE_DATE, GOOGLE_BASELINE, True, release),
    }
    company = {
        "en": "FunPlus International AG / FunPlus (DC licensed by Warner Bros. Interactive Entertainment)",
        "cn": "趣加游戏（FunPlus；华纳兄弟互动娱乐代表DC授权）",
        "confidence": "已确认",
        "basis": "Google Play店铺主体为FunPlus International AG；FunPlus官方发行公告确认产品由FunPlus推出，并由Warner Bros. Interactive Entertainment代表DC授权。",
        "source": "https://funplus.com/dc-dark-legion-global-launch-lead-the-league/",
    }
    analysis = trend(
        "趋势：2025年借蝙蝠侠、小丑和黑暗多元宇宙完成强IP首发，英雄编队与蝙蝠洞经营承接中长期付费；关键转折：上线六周突破500万玩家后，运营从基础DC角色认知转向电影事件和长尾角色更新，2026年Supergirl电影活动与Cassandra Cain入场继续制造回流；主力素材：超级英雄危机、正邪混编、角色强度对比、蝙蝠洞扩建与联盟PvP。",
        "2025年3月全球上线时，以《Dark Nights: Metal》黑暗多元宇宙危机和蝙蝠侠/小丑等高认知角色降低获量门槛，再把用户导入英雄收集、队伍协同、蝙蝠洞设施和PvE/PvP。官方在上线约六周宣布超过500万玩家，之后进入以角色池和IP事件维持活跃的运营阶段。",
        "本次首次进入项目保存的Google Play美国策略畅销TOP60，位列第51名；Google本店上架日期早于90天窗口，因缺少2026-06-23精确同口径基准，内部保持pending并按常规展示。",
        "首发重点是黑暗骑士入侵、正邪英雄联手和角色阵容；成熟期转向具体角色与影视节点。2026年6月Supergirl电影主题活动加入新Champion与基地外观，7月继续推出Cassandra Cain；9月8日商品页更新没有披露可确认的底层玩法重构。",
        "蝙蝠侠、小丑、超人和神奇女侠同屏，黑暗多元宇宙危机倒计时，英雄克制与阵容组合、抽取/升星、蝙蝠洞房间扩建、联盟共同作战，以及Supergirl等影视同步角色。",
        "观察首次进入Google #51后能否连续留榜，以及iOS同步回榜#55是否形成两端共同改善；没有连续快照前不把单日进入写成长期趋势。",
        metadata["url"],
        [
            {"label": "FunPlus全球发行公告", "url": "https://funplus.com/dc-dark-legion-global-launch-lead-the-league/", "type": "primary"},
            {"label": "FunPlus 500万玩家里程碑", "url": "https://funplus.com/dc-dark-legion-hits-5-million-players-in-a-flash/", "type": "lifecycle-analysis"},
            {"label": "Supergirl电影主题活动", "url": "https://funplus.com/funplus-brings-supergirl-to-dc-dark-legion/", "type": "lifecycle-analysis"},
            {"label": "DC Dark Legion官方站", "url": "https://dcdarklegion.com/", "type": "primary"},
        ],
    )
    return game, company, clean_analysis(analysis)


def build_google(rows, source):
    current = records("data/games-20260918.json", "data/enrichment-20260918.json", "data/trends-20260918.json", "packageName")
    historical = merged_records(history_specs("", GOOGLE_DATES), "packageName")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    games, companies, analyses, assets = [], {}, {}, {}
    for row in rows:
        package, rank = row["packageName"], row["rank"]
        if package in current:
            game, company, analysis = map(deepcopy, current[package])
        elif package in historical:
            game, company, analysis = map(deepcopy, historical[package])
        elif package == "com.kingsgroup.dcdly":
            metadata = play_metadata(package)
            game, company, analysis = dc_google_profile(row, metadata)
            assets["79_icon"] = data_uri(metadata["icon"], (256, 256))
            assets["79_store"] = data_uri(metadata["screenshot"], (720, 720))
        else:
            raise RuntimeError(f"Unexpected Google entrant: {row}")
        change = delta_label(old_rank.get(package), rank)
        comp = comparison(None, rank, GOOGLE_DATE, GOOGLE_BASELINE, True, game.get("releaseDateIso"))
        if package == "com.run.tower.defense":
            analysis["summary"] = analysis["summary"].replace("类《Thronefall》的移动守城", "类Thronefall移动塔防")
            analysis["sections"] = {
                key: value.replace("类《Thronefall》的移动英雄塔防", "类Thronefall移动塔防").replace("类《Thronefall》的移动领主守城", "类Thronefall移动塔防").replace("类《Thronefall》的低多边形移动塔防", "类Thronefall移动塔防")
                for key, value in analysis["sections"].items()
            }
        game.update(
            rank=rank, gameName=row["gameName"], developer=row.get("developer", game.get("developer", "")),
            store="googlePlay", storeUrl=row["storeUrl"], iconUrl=row["iconUrl"], screenshotUrl=row["screenshotUrl"],
            totalInstalls=str(row.get("downloads") or game.get("totalInstalls") or "").replace("+", " +"),
            dailyChange=change, comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(clean_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", ""))
        games.append(game); companies[str(rank)] = company; analyses[str(rank)] = analysis
    enrichment = deepcopy(load("data/enrichment-20260918.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=GOOGLE_BASELINE, currentDate=GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/games-20260921.json", games); save("data/enrichment-20260921.json", enrichment); save("data/trends-20260921.json", analyses)
    manifest = load("assets/manifest.json"); manifest["date"] = GOOGLE_DATE
    if assets:
        save("assets/assets-16.json", assets)
        if "assets-16.json" not in manifest["files"]: manifest["files"].append("assets-16.json")
    save("assets/manifest.json", manifest)
    audit = audit_google(rows)
    save("data/history/google-play/2026-09-21.json", {
        "store": "google-play", "country": "US", "category": "Games > Strategy > Top Grossing",
        "date": CAPTURE, "dataDate": GOOGLE_DATE, "sourceCapturedAt": source["capturedAt"],
        "sourceUrl": source["sourceUrl"], "sourceEndpoint": source["sourceEndpoint"], "sourceMethod": source["sourceMethod"],
        "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。",
        "crossCheck": audit,
        "rankings": [{"rank": g["rank"], "packageName": g["packageName"], "gameName": g["gameName"], "sourceUrl": g["storeUrl"]} for g in games],
    })
    return games, audit


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260918.json", "data/ios-enrichment-20260918.json", "data/ios-trends-20260918.json", "appId")
    historical = merged_records(history_specs("ios-", IOS_DATES), "appId")
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
        comp = comparison(None, rank, IOS_DATE, IOS_BASELINE, True, game.get("releaseDateIso"))
        game.update(rank=rank, gameName=row["gameName"], developer=row["developer"], store="ios",
                    storeUrl=f"https://apps.apple.com/us/app/id{app_id}", dailyChange=change, comparison90d=comp)
        analysis = refresh_daily_rank_path(clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", ""))
        games.append(game); companies[str(rank)] = company; analyses[str(rank)] = analysis
    enrichment = deepcopy(load("data/ios-enrichment-20260918.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=IOS_BASELINE, currentDate=IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/ios-games-20260921.json", games); save("data/ios-enrichment-20260921.json", enrichment); save("data/ios-trends-20260921.json", analyses)
    manifest = load("assets/ios-manifest.json"); manifest["date"] = IOS_DATE; save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save("data/history/ios/2026-09-21.json", {
        "store": "ios", "country": "US", "device": "iPhone", "category": "Games > Strategy > Top Grossing",
        "date": source_date, "dataDate": source_date, "sourceUpdated": source_updated, "sourceUrl": source_url,
        "rankings": [{"rank": g["rank"], "appId": g["appId"], "gameName": g["gameName"], "sourceUrl": g["storeUrl"]} for g in games],
    })
    return games, source_date


def main():
    google_source = fetch_top_grossing_strategy()
    ios_url, ios_updated, ios_rows = parse_ios()
    ios_source_date = datetime.fromisoformat(ios_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    if google_source["dataDate"] != GOOGLE_DATE:
        raise RuntimeError(f"Google capture date is {google_source['dataDate']}, expected {GOOGLE_DATE}")
    if ios_source_date != IOS_DATE:
        raise RuntimeError(f"Apple source is still dated {ios_source_date}; keep the previous valid iOS snapshot")
    if len(google_source["rows"]) != 60 or len({r["packageName"] for r in google_source["rows"]}) != 60:
        raise RuntimeError("Google direct source is not a complete unique TOP60")
    if len(ios_rows) != 60 or len({r["appId"] for r in ios_rows}) != 60:
        raise RuntimeError("Apple RSS is not a complete unique TOP60")
    google, audit = build_google(google_source["rows"], google_source)
    ios, _ = build_ios(ios_rows, ios_url, ios_updated)
    print("Google", google_source["capturedAt"], [(g["rank"], g["gameName"]) for g in google if g["rank"] in (1, 25, 60)])
    print("AppBrain audit", audit)
    print("iOS", ios_updated, [(g["rank"], g["gameName"]) for g in ios if g["rank"] in (1, 25, 60)])


if __name__ == "__main__":
    main()
