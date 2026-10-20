#!/usr/bin/env python3
"""Build the Beijing 2026-10-20 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
from zoneinfo import ZoneInfo

import daily_update_20261019 as prior
from daily_update_20260820 import comparison, delta_label


updater = prior.updater
base_enforce_required_product_language = prior.enforce_required_product_language
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-20"
updater.STAMP = "20261020"
updater.PREVIOUS_STAMP = "20261019"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-22"
updater.GOOGLE_DATES = ("20261019",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261019",) + updater.IOS_DATES


def enforce_required_product_language(game_name, analysis):
    """Keep required narratives explicit while making daily rewrites idempotent."""
    analysis = base_enforce_required_product_language(game_name, analysis)
    if game_name != "Kingshot":
        return analysis

    def rewrite(value):
        if isinstance(value, dict):
            return {key: rewrite(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rewrite(item) for item in value]
        if isinstance(value, str):
            return re.sub(r"(?:城镇经营、)+居民分工", "城镇经营、居民分工", value)
        return value

    return rewrite(analysis)


def prepare_analysis(analysis):
    """Remove expired 90-day labels before rebuilding the current rank path."""
    analysis = updater.clean_analysis(analysis)
    path = analysis["sections"].get("rankPath", "")
    path = re.sub(
        r"(?:按(?:Google Play|iOS)商品页上架日期[^。；]*?属于近三个月新上榜[。；]?)+",
        "",
        path,
    )
    path = re.sub(r"按上架日期口径属于近三个月新上榜[。；]?", "", path)
    path = re.sub(r"[，；]{2,}", "；", path).strip("，；。 ")
    analysis["sections"]["rankPath"] = path
    return analysis


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20261019.json",
        "data/enrichment-20261019.json",
        "data/trends-20261019.json",
        "packageName",
    )
    historical = updater.merged_records(updater.history_specs("", updater.GOOGLE_DATES), "packageName")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    games, companies, analyses = [], {}, {}

    for row in rows:
        package, rank = row["packageName"], row["rank"]
        if package in current:
            game, company, analysis = map(deepcopy, current[package])
        elif package in historical:
            game, company, analysis = map(deepcopy, historical[package])
        else:
            raise RuntimeError(f"Unexpected Google entrant: {row}")

        change = delta_label(old_rank.get(package), rank)
        comp = comparison(None, rank, updater.GOOGLE_DATE, updater.GOOGLE_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row.get("developer", game.get("developer", "")),
            store="googlePlay",
            storeUrl=row["storeUrl"],
            iconUrl=row["iconUrl"],
            rankIconUrl=row["iconUrl"],
            screenshotUrl=row["screenshotUrl"],
            totalInstalls=str(row.get("downloads") or game.get("totalInstalls") or "").replace("+", " +"),
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = updater.refresh_daily_rank_path(
            prepare_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/enrichment-20261019.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261020.json", games)
    updater.save("data/enrichment-20261020.json", enrichment)
    updater.save("data/trends-20261020.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-20.json", {
        "store": "google-play",
        "country": "US",
        "category": "Games > Strategy > Top Grossing",
        "date": updater.GOOGLE_DATE,
        "dataDate": updater.GOOGLE_DATE,
        "sourceCapturedAt": source["capturedAt"],
        "sourceUrl": source["sourceUrl"],
        "sourceEndpoint": source["sourceEndpoint"],
        "sourceMethod": source["sourceMethod"],
        "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。",
        "crossCheck": audit,
        "rankings": [
            {"rank": game["rank"], "packageName": game["packageName"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]}
            for game in games
        ],
    })
    return games, audit


def build_ios_today(rows, source_url, source_updated):
    current = updater.records(
        "data/ios-games-20261019.json",
        "data/ios-enrichment-20261019.json",
        "data/ios-trends-20261019.json",
        "appId",
    )
    historical = updater.merged_records(updater.history_specs("ios-", updater.IOS_DATES), "appId")
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
        comp = comparison(None, rank, updater.IOS_DATE, updater.IOS_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row["developer"],
            store="ios",
            storeUrl=f"https://apps.apple.com/us/app/id{app_id}",
            totalInstalls="",
            recentInstalls30d="",
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = updater.refresh_daily_rank_path(
            prepare_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261019.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261020.json", games)
    updater.save("data/ios-enrichment-20261020.json", enrichment)
    updater.save("data/ios-trends-20261020.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-20.json", {
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
    })
    return games, source_date


updater.build_google = build_google_today
updater.build_ios = build_ios_today


def apply_verified_return_updates():
    """Remove stale first-entry language from returning products."""

    def update(store, product_id, rank_path, summary=None, turning=None, watch=None):
        if store == "googlePlay":
            games_path, trends_path, key = (
                "data/games-20261020.json", "data/trends-20261020.json", "packageName"
            )
        else:
            games_path, trends_path, key = (
                "data/ios-games-20261020.json", "data/ios-trends-20261020.json", "appId"
            )
        games = updater.load(games_path)
        game = next(item for item in games if str(item[key]) == product_id)
        trends = updater.load(trends_path)
        analysis = trends[str(game["rank"])]
        analysis["sections"]["rankPath"] = rank_path.format(rank=game["rank"])
        if summary:
            analysis["summary"] = summary.format(rank=game["rank"])
        if turning:
            analysis["sections"]["turningPoints"] = turning.format(rank=game["rank"])
        if watch:
            analysis["sections"]["watch"] = watch.format(rank=game["rank"])
        analysis["sourceAudit"]["reviewedAt"] = updater.CAPTURE
        analysis["sourceAudit"]["changeReason"] = (
            "2026-10-20按对应商店官方榜单复核回榜与当前排名；沿用已核验的产品、公司和素材证据。"
        )
        analysis["lifecycleAudit"]["reviewedAt"] = updater.CAPTURE
        analysis["lifecycleAudit"]["evidenceNote"] = (
            "回榜来自相邻有效快照对比；运营节点只作为时间背景，不写成榜位变化的确定原因。"
        )
        updater.save(trends_path, trends)

    update(
        "googlePlay", "leyi.ageofspirits",
        "本次回到Google Play美国策略畅销榜第{rank}名（前一有效快照未入榜，回榜）。Google Play美国区released日期为2026-09-16，位于2026-07-22至2026-10-20的90天窗口内，因此按releaseDate归类为近三个月新上榜；回榜仍在榜尾，不代表已形成稳定走势。",
        summary="趋势：2026年9月以原始部落篝火、萨满和联盟4X进入首发验证，本期回到Google #{rank}；关键转折：首发版本同步新增七种语言、11级兵种与萨满伤势机制，尚无更长期转折可确认；主力素材：从单一篝火扩建部落、萨满编队、巨兽威胁和联盟世界地图争夺。",
        watch="未来1—2个有效快照观察能否脱离榜尾并连续留榜；若再次退出，只记录为首发验证期的榜尾轮换，不推演后续走势。",
    )
    update(
        "ios", "1611722542",
        "本次回到iOS美国策略畅销榜第{rank}名（前一有效快照未入榜，回榜）。iOS上架日期为2022-06-15，早于90天窗口；因缺少2026-07-22精确同口径基准，内部保持pending、页面按常规在榜展示。",
    )
    update(
        "ios", "1411917616",
        "本次回到iOS美国策略畅销榜第{rank}名（前一有效快照未入榜，回榜）。iOS上架日期为2018-10-20，早于90天窗口；缺少2026-07-22精确基准，因此不判断近三个月飙升。",
        watch="未来1—2个有效快照观察能否从后12名继续上行；若迅速掉榜，只记录为成熟产品短期回补，不把旧版本更新时间与本次回榜写成确定因果。",
    )
    update(
        "ios", "6740232087",
        "本次回到iOS美国策略畅销榜第{rank}名（前一有效快照未入榜，回榜）。Apple上架日为2025-02-18，早于90天窗口；缺少2026-07-22精确基准，内部保持pending、页面按常规在榜展示。",
        turning="10月6日1.22b把装备改为配方制作、一键合成、槽位升级与最高Cosmic稀有度；官方版本说明把Boss Hunt排在10月19日、Halloween Night排在10月26日。Boss Hunt与本次回榜时间相邻，但没有证据证明它单独造成名次变化。",
        watch="观察未来1—2个有效快照能否连续留榜，并在10月26日Halloween Night开启后复核位置；活动排期与榜位仅作时间对照。",
    )
    update(
        "ios", "1274354704",
        "本次回到iOS美国策略畅销榜第{rank}名（前一有效快照未入榜，回榜）。2017年上线，早于90天窗口；因缺少2026-07-22精确同口径基准，不判断近三个月飙升。",
    )


if __name__ == "__main__":
    updater.main()
    apply_verified_return_updates()
