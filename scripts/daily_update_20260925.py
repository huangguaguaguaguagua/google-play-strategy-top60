#!/usr/bin/env python3
"""Build the Beijing 2026-09-25 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import daily_update_20260924 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend


updater = prior.updater
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-09-25"
updater.STAMP = "20260925"
updater.PREVIOUS_STAMP = "20260924"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-06-27"
updater.GOOGLE_DATES = ("20260924",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20260924",) + updater.IOS_DATES


def _kingdom_rush_genesis(meta):
    game = prior._new_game(
        meta,
        "6759664029",
        96,
        "塔防 / 战术布阵 / 单机策略",
        "Kingdom Rush；经典塔防；Linirea；前传；15座塔；双英雄；法术；离线",
    )
    company = {
        "en": "Ironhide S.A. / Ironhide Game Studio",
        "cn": "Ironhide Game Studio（乌拉圭独立研发发行；Apple店铺主体Ironhide S.A.）",
        "confidence": "已确认",
        "basis": "Apple Lookup列明Ironhide S.A.为seller；产品官网和商品页均明确由Ironhide Game Studio研发发行，未发现更上层集团归属披露。",
        "source": "https://www.kingdomrushgenesis.com/",
    }
    analysis = trend(
        "趋势：9月24日全球上架后以Kingdom Rush经典塔防回归、Linirea前传和离线单机承接系列用户，首个完整榜单日进入iOS #26；关键转折：上线即提供15座塔、双英雄、9种法术与18个手工关卡，仍处首发验证；主力素材：经典四类塔协同、分路怪潮、双英雄技能、Vez'nan前传与Boss破线。",
        "2026年9月24日上架，定位为系列前传：回到Linirea早期，以弓箭、法师、兵营、火炮等15座塔的组合覆盖路线，再由每局两名英雄和9种法术处理高压波次。上线时间不足两天，当前只能确认首发内容与初始榜位，不能推演长期表现。",
        "首个完整Apple美国策略畅销榜快照进入第26名；按Apple Lookup releaseDate落在90天窗口内，归类为近三个月新上榜。Google Play同口径当前未进入TOP60。",
        "可确认节点是9月24日正式上架，并一次性开放18个战役关卡、40余种敌人、6个Boss、双英雄与离线模式；尚未发现上线后的玩法重构或长期运营转折。",
        "当前商品图集中展示经典塔位覆盖、不同兵种协同、双英雄同场、法术清屏、密集波次和巨型Boss；系列角色与Vez'nan前传负责IP识别。素材判断基于Apple商品页、产品官网与商店图，可信度为中。",
        "观察未来1—2个有效快照能否守住前35，以及首发IP用户在完成战役内容后是否仍能维持策略畅销榜可见度；没有连续数据前不把首日#26写成稳定趋势。",
        "https://apps.apple.com/us/app/id6759664029",
        [
            {"label": "Kingdom Rush 6: Genesis官网", "url": "https://www.kingdomrushgenesis.com/", "type": "primary"},
            {"label": "Apple App Store商品页", "url": "https://apps.apple.com/us/app/id6759664029", "type": "primary"},
        ],
    )
    return game, company, analysis


def build_ios_today(rows, source_url, source_updated):
    current = updater.records(
        "data/ios-games-20260924.json",
        "data/ios-enrichment-20260924.json",
        "data/ios-trends-20260924.json",
        "appId",
    )
    historical = updater.merged_records(updater.history_specs("ios-", updater.IOS_DATES), "appId")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in current]
    metadata = lookup(entrant_ids)
    games, companies, analyses, bundle = [], {}, {}, {}

    for row in rows:
        app_id, rank = row["appId"], row["rank"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        elif app_id in historical:
            game, company, analysis = map(deepcopy, historical[app_id])
        elif app_id == "6759664029":
            game, company, analysis = _kingdom_rush_genesis(metadata[app_id])
        else:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")

        meta = metadata.get(app_id)
        if meta:
            icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
            screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
            game.update(
                appId=app_id,
                packageName=app_id,
                iconUrl=icon,
                rankIconUrl=icon,
                screenshotUrl=screenshots[0] if screenshots else icon,
                description=meta.get("description", game.get("description", "")),
                shortDescription=meta.get("description", "").replace("\n", " ")[:220],
                releaseDate=(meta.get("releaseDate") or game.get("releaseDate", ""))[:10],
                releaseDateIso=(meta.get("releaseDate") or game.get("releaseDateIso", ""))[:10],
                updatedDate=(meta.get("currentVersionReleaseDate") or "")[:10],
            )
        if app_id == "6759664029":
            game["assetRank"] = 96
            bundle["96_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle["96_store"] = data_uri(game["screenshotUrl"], (720, 720))

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
            updater.clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/ios-enrichment-20260924.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20260925.json", games)
    updater.save("data/ios-enrichment-20260925.json", enrichment)
    updater.save("data/ios-trends-20260925.json", analyses)
    updater.save("assets/ios-assets-24.json", bundle)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if "ios-assets-24.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-24.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-09-25.json", {
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


updater.build_ios = build_ios_today


if __name__ == "__main__":
    updater.main()
