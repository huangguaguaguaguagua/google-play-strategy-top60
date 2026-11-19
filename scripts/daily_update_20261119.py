#!/usr/bin/env python3
"""Build the Beijing 2026-11-19 dual-store snapshots from official sources."""

from copy import deepcopy
from datetime import datetime
import re
from zoneinfo import ZoneInfo

import daily_update_20261118 as prior
from daily_update_20260820 import data_uri, delta_label, lookup


updater = prior.updater
DATE = "2026-11-19"
STAMP = "20261119"
PREV = "20261118"
BASELINE = "2026-08-20"
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = DATE
updater.STAMP = STAMP
updater.PREVIOUS_STAMP = PREV
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = BASELINE
updater.GOOGLE_DATES = (PREV,) + updater.GOOGLE_DATES
updater.IOS_DATES = (PREV,) + updater.IOS_DATES


def source_records(prefix, id_key):
    current = updater.records(
        f"data/{prefix}games-{PREV}.json",
        f"data/{prefix}enrichment-{PREV}.json",
        f"data/{prefix}trends-{PREV}.json",
        id_key,
    )
    dates = updater.IOS_DATES if prefix else updater.GOOGLE_DATES
    historical = updater.merged_records(updater.history_specs(prefix, dates), id_key)
    return current, historical


def comparison_for(baseline_rank, rank, release_date, store_label):
    return prior.exact_comparison(baseline_rank, rank, DATE, BASELINE, release_date, store_label)


def movement(store, game):
    change = game["dailyChange"]
    if change == "NEW":
        return f"较{PREV[:4]}-{PREV[4:6]}-{PREV[6:]}前一有效快照进入/回榜#{game['rank']}"
    if change == "=":
        return f"较前一有效快照持平于#{game['rank']}"
    return f"较前一有效快照{'上升' if change.startswith('+') else '下降'}{change[1:]}位至#{game['rank']}"


def status_text(game, store_label, basis):
    comp = game["comparison90d"]
    if comp["status"] == "new":
        text = f"按{basis}{game.get('releaseDateIso','')}计算，归类为近三个月新上榜。"
        if comp.get("releaseDateConflict"):
            text += "当前官方上架字段与更早历史在榜记录冲突；标签仅反映当前字段，不代表首次全球上线。"
        return text
    if comp["status"] == "surge":
        return f"精确90天基准#{comp['baselineRank']}，当前提升{comp['delta']}位，归类为近三个月飙升。"
    if comp.get("baselineRank") is not None:
        return f"精确90天基准#{comp['baselineRank']}，baselineRank-currentRank={comp['delta']}，按常规在榜展示。"
    return f"上架早于窗口且{BASELINE}{store_label}同口径基准未在榜，不满足飙升条件，按常规在榜展示。"


def refresh_summary(trend, game, store_label):
    old = trend.get("summary", "")
    trend_match = re.search(r"趋势：(.*?)(?:；关键转折：|$)", old)
    creative_match = re.search(r"主力素材：(.*)$", old)
    trend_text = trend_match.group(1).strip() if trend_match else trend["sections"]["development"]
    creative = creative_match.group(1).strip() if creative_match else trend["sections"]["creative"]
    turning = trend["sections"]["turningPoints"].strip()
    turning = re.sub(r"本期[^。；]*[。；]?", "", turning).strip()
    if not turning:
        turning = "未发现可确认的重大转折/长期稳定运营。"
    daily = movement(store_label, game)
    trend["summary"] = f"趋势：{trend_text}；关键转折：{daily}。{turning}；主力素材：{creative}"
    for key in ("sourceAudit", "lifecycleAudit"):
        trend[key]["reviewedAt"] = DATE
    trend["sourceAudit"]["changeReason"] = "按11月19日官方榜单复核当前名次、相邻快照变化与商店元数据；单日位移仅作待验证信号。"
    return trend


def build_google(rows, source):
    current, historical = source_records("", "packageName")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    baseline = {x["packageName"]: x["rank"] for x in updater.load(f"data/history/google-play/{BASELINE}.json")["rankings"]}
    games, companies, trends = [], {}, {}
    for row in rows:
        product_id = row["packageName"]
        record = current.get(product_id) or historical.get(product_id)
        if not record:
            raise RuntimeError(f"Unexpected Google entrant requiring editorial review: {row}")
        game, company, trend = map(deepcopy, record)
        game.update(
            rank=row["rank"], gameName=row["gameName"], developer=row.get("developer") or game.get("developer", ""),
            store="googlePlay", storeUrl=row["storeUrl"], iconUrl=row["iconUrl"], rankIconUrl=row["iconUrl"],
            screenshotUrl=row["screenshotUrl"], totalInstalls=str(row.get("downloads") or game.get("totalInstalls") or "").replace("+", " +"),
            dailyChange=delta_label(old_rank.get(product_id), row["rank"]),
        )
        game["comparison90d"] = comparison_for(baseline.get(product_id), row["rank"], game.get("releaseDateIso"), "Google Play美国区策略畅销榜")
        trend["sections"]["rankPath"] = f"本次位于Google Play美国策略畅销榜第{row['rank']}名（{movement('Google', game)}）。{status_text(game, 'Google Play', 'Google Play美国区商品页released日期')}"
        trend = refresh_summary(trend, game, "Google")
        games.append(game); companies[str(row["rank"])] = company; trends[str(row["rank"])] = trend
    enrichment = deepcopy(updater.load(f"data/enrichment-{PREV}.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(baselineDate=BASELINE, currentDate=DATE, pending="精确同口径90天基准可用，无pending记录。")
    updater.save(f"data/games-{STAMP}.json", games)
    updater.save(f"data/enrichment-{STAMP}.json", enrichment)
    updater.save(f"data/trends-{STAMP}.json", trends)
    audit = updater.audit_google(rows)
    updater.save(f"data/history/google-play/{DATE}.json", {
        "store":"google-play", "country":"US", "category":"Games > Strategy > Top Grossing", "date":DATE, "dataDate":DATE,
        "sourceCapturedAt":source["capturedAt"], "sourceUrl":source["sourceUrl"], "sourceEndpoint":source["sourceEndpoint"], "sourceMethod":source["sourceMethod"],
        "freshnessNote":"Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。", "crossCheck":audit,
        "rankings":[{"rank":g["rank"],"packageName":g["packageName"],"gameName":g["gameName"],"sourceUrl":g["storeUrl"]} for g in games],
    })
    manifest = updater.load("assets/manifest.json"); manifest["date"] = DATE; updater.save("assets/manifest.json", manifest)
    return games, audit


def build_ios(rows, source_url, source_updated):
    current, historical = source_records("ios-", "appId")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    baseline = {str(x["appId"]): x["rank"] for x in updater.load(f"data/history/ios/{BASELINE}.json")["rankings"]}
    meta = lookup([row["appId"] for row in rows])
    games, companies, trends = [], {}, {}
    for row in rows:
        app_id = str(row["appId"])
        record = current.get(app_id) or historical.get(app_id)
        if not record:
            raise RuntimeError(f"Unexpected iOS entrant requiring editorial review: {row}")
        game, company, trend = map(deepcopy, record)
        info = meta.get(app_id, {})
        screenshots = info.get("screenshotUrls") or info.get("ipadScreenshotUrls") or []
        release = (info.get("releaseDate") or game.get("releaseDateIso") or "")[:10]
        game.update(
            rank=row["rank"], gameName=row["gameName"], developer=info.get("artistName") or row.get("developer") or game.get("developer", ""),
            store="ios", storeUrl=f"https://apps.apple.com/us/app/id{app_id}",
            iconUrl=info.get("artworkUrl512") or info.get("artworkUrl100") or game.get("iconUrl", ""),
            rankIconUrl=info.get("artworkUrl512") or info.get("artworkUrl100") or game.get("rankIconUrl", ""),
            screenshotUrl=screenshots[0] if screenshots else game.get("screenshotUrl", ""),
            releaseDate=release, releaseDateIso=release, updatedDate=(info.get("currentVersionReleaseDate") or game.get("updatedDate") or "")[:10],
            totalInstalls="", recentInstalls30d="", dailyChange=delta_label(old_rank.get(app_id), row["rank"]),
        )
        comp = comparison_for(baseline.get(app_id), row["rank"], release, "Apple iPhone美国区策略畅销榜")
        if comp["status"] == "new" and app_id in baseline:
            comp["releaseDateConflict"] = {"status":"source-metadata-conflict","historicalRank":baseline[app_id],"historicalDate":BASELINE,"historicalSnapshot":f"data/history/ios/{BASELINE}.json","note":"Apple当前releaseDate落入90天窗口，但同一appId在更早历史榜单已存在；仅按当前官方字段归类，不认定产品首次全球上线。"}
            comp["evidence"] += " Apple当前releaseDate与更早在榜历史冲突，已保留审计。"
        game["comparison90d"] = comp
        trend["sections"]["rankPath"] = f"本次位于iOS美国策略畅销榜第{row['rank']}名（{movement('iOS', game)}）。{status_text(game, 'iOS', 'Apple Lookup releaseDate')}"
        trend = refresh_summary(trend, game, "iOS")
        games.append(game); companies[str(row["rank"])] = company; trends[str(row["rank"])] = trend
    enrichment = deepcopy(updater.load(f"data/ios-enrichment-{PREV}.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(baselineDate=BASELINE, currentDate=DATE, pending="精确同口径90天基准可用，无pending记录。")
    updater.save(f"data/ios-games-{STAMP}.json", games)
    updater.save(f"data/ios-enrichment-{STAMP}.json", enrichment)
    updater.save(f"data/ios-trends-{STAMP}.json", trends)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save(f"data/history/ios/{DATE}.json", {
        "store":"ios", "country":"US", "device":"iPhone", "category":"Games > Strategy > Top Grossing", "date":source_date, "dataDate":source_date,
        "sourceUpdated":source_updated, "sourceUrl":source_url,
        "rankings":[{"rank":g["rank"],"appId":g["appId"],"gameName":g["gameName"],"sourceUrl":g["storeUrl"]} for g in games],
    })
    manifest = updater.load("assets/ios-manifest.json"); manifest["date"] = DATE; updater.save("assets/ios-manifest.json", manifest)
    return games, source_date


updater.build_google = build_google
updater.build_ios = build_ios


def ensure_ios_assets():
    manifest = updater.load("assets/ios-manifest.json")
    assets = {}
    for filename in manifest["files"]:
        assets.update(updater.load("assets/" + filename))
    additions = {}
    for game in updater.load(f"data/ios-games-{STAMP}.json"):
        for suffix, url, size in (("icon", game.get("iconUrl"), (256,256)), ("store", game.get("screenshotUrl"), (720,960))):
            key = f"{game['assetRank']:02d}_{suffix}"
            if key not in assets:
                additions[key] = data_uri(url, size)
    if additions:
        filename = f"ios-assets-refresh-{STAMP}.json"
        updater.save("assets/" + filename, additions)
        manifest["files"].append(filename)
        updater.save("assets/ios-manifest.json", manifest)


def repair_known_editorial_mismatch():
    """Repair the inherited RAID/Vikings product join with first-party evidence."""
    games = updater.load(f"data/ios-games-{STAMP}.json")
    enrichment = updater.load(f"data/ios-enrichment-{STAMP}.json")
    trends = updater.load(f"data/ios-trends-{STAMP}.json")
    game = next(item for item in games if str(item["appId"]) == "1371565796")
    rank = str(game["rank"])
    game.update(
        genre="回合制角色收集RPG",
        keywords="泰莱里亚；冠军收集；16阵营；回合战斗；地牢Boss；竞技场",
        shortDescription="Dark-fantasy collection RPG built around hundreds of Champions, 16 factions, turn-based squad tactics, PvE dungeons and PvP arenas.",
        description="在黑暗奇幻世界泰莱里亚召唤并培养16个阵营的冠军，通过回合制队伍协同推进剧情、阵营战争和地牢Boss，并参加异步及实时PvP竞技场。",
    )
    enrichment["productCompaniesByRank"][rank] = {
        "en":"Plarium Global Ltd / Plarium",
        "cn":"Plarium",
        "confidence":"已确认",
        "basis":"Apple美国区商品页列开发者Plarium Global Ltd；Plarium官方产品页将RAID明确列为旗下collection RPG。",
        "source":"https://company.plarium.com/en/game/mobile/raid-shadow-legends/",
    }
    trends[rank] = {
        "summary":"趋势：2019年全球上线后以高质感黑暗奇幻、冠军收集和回合制队伍协同建立长线RPG盘；关键转折：本期iOS上升4位至#39，Echoes of Oz已于11月10日结束，未发现可把本次位移归因于单一节点的证据；主力素材：传奇冠军立绘、阵营编队、技能连携、地牢Boss与竞技场对抗。",
        "sections":{
            "development":"2019年以16阵营冠军收集、回合制队伍搭配和泰莱里亚剧情切入，随后通过地牢、阵营战争、竞技场与持续新增冠军扩成长线产品；当前主要由成熟收藏与配队用户、周期活动和新冠军轮换支撑。",
            "rankPath":f"本次位于iOS美国策略畅销榜第{game['rank']}名（较前一有效快照上升4位至#{game['rank']}）。{status_text(game, 'iOS', 'Apple Lookup releaseDate')}",
            "turningPoints":"2019年首发以主机感角色美术和冠军收集区别于轻量卡牌；后续加入实时竞技场并持续扩充冠军与PvE内容。2026年8月19日至11月10日的Echoes of Oz联动是近期可核验节点，但活动已结束，不能直接解释今日单日上升。",
            "creative":"Apple当前商品页以高精度冠军角色、16阵营、技能连携、地牢Boss和PvP竞技场为主；官方素材强调收集、装备与队伍策略，而非城建或联盟4X。",
            "watch":"观察未来2—3个有效快照能否维持前40；若迅速回落，则只保留为单日波动，不升级为长期趋势判断。",
        },
        "sourceAudit":{
            "reviewedAt":DATE,"status":"已核验","confidence":"高",
            "basis":"玩法、阵营、发行主体与商品素材由Apple美国区商品页、Plarium官方产品页及官方首发公告交叉核验。",
            "changeReason":"修复历史数据把RAID错误连接到Vikings产品档案的问题。",
            "evidenceNote":"本条只描述可核验的RAID产品结构与已结束活动；没有把单日榜位变化写成活动效果。",
            "sources":[
                {"label":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/id1371565796","type":"store"},
                {"label":"Plarium官方产品页","url":"https://company.plarium.com/en/game/mobile/raid-shadow-legends/","type":"primary"},
                {"label":"Plarium官方首发公告","url":"https://company.plarium.com/en/articles/plarium-launches-collection-rpg-raid-shadow-legends-on-ios-and-android-devices/","type":"primary"},
            ],
        },
        "lifecycleAudit":{
            "reviewedAt":DATE,"status":"已复核","confidence":"高",
            "scope":"从2019年全球首发、冠军收藏与回合制配队，到长期PvE/PvP扩展和2026年Echoes of Oz活动。",
            "changeReason":"纠正产品串档并重建生命周期脉络。",
            "evidenceNote":"官方首发公告、当前商品页和官方活动资料支持上述节点；未使用Vikings的发行或素材记录。",
            "sources":[
                {"label":"Plarium官方RAID产品页","url":"https://company.plarium.com/en/game/mobile/raid-shadow-legends/","type":"primary"},
                {"label":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/id1371565796","type":"store"},
            ],
        },
    }
    updater.save(f"data/ios-games-{STAMP}.json", games)
    updater.save(f"data/ios-enrichment-{STAMP}.json", enrichment)
    updater.save(f"data/ios-trends-{STAMP}.json", trends)


def refresh_changed_icons():
    """Persist the three official icons flagged by the daily visual audit."""
    targets = {
        "googlePlay": {"com.lavalabs.autodrill", "com.more.lastfortress.gp"},
        "ios": {"6772922295"},
    }
    for store, games_path, manifest_path, filename, id_key in (
        ("googlePlay", f"data/games-{STAMP}.json", "assets/manifest.json", f"google-icons-refresh-{STAMP}.json", "packageName"),
        ("ios", f"data/ios-games-{STAMP}.json", "assets/ios-manifest.json", f"ios-icons-refresh-{STAMP}.json", "appId"),
    ):
        additions = {}
        for game in updater.load(games_path):
            if str(game[id_key]) in targets[store]:
                additions[f"{int(game['assetRank']):02d}_icon"] = data_uri(game["rankIconUrl"], (256,256))
        updater.save("assets/" + filename, additions)
        manifest = updater.load(manifest_path)
        if filename not in manifest["files"]:
            manifest["files"].append(filename)
        updater.save(manifest_path, manifest)


if __name__ == "__main__":
    updater.main()
    repair_known_editorial_mismatch()
    ensure_ios_assets()
    refresh_changed_icons()
