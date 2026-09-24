#!/usr/bin/env python3
"""Build the Beijing 2026-09-24 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import daily_update_20260923 as updater
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend


updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-09-24"
updater.STAMP = "20260924"
updater.PREVIOUS_STAMP = "20260923"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-06-26"
updater.GOOGLE_DATES = ("20260923",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20260923",) + updater.IOS_DATES


def _new_game(meta, app_id, asset_rank, genre, keywords):
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
    return {
        "appId": app_id,
        "packageName": app_id,
        "store": "ios",
        "assetRank": asset_rank,
        "genre": genre,
        "keywords": keywords,
        "iconUrl": icon,
        "rankIconUrl": icon,
        "screenshotUrl": screenshots[0] if screenshots else icon,
        "description": meta.get("description", ""),
        "shortDescription": meta.get("description", "").replace("\n", " ")[:220],
        "releaseDate": (meta.get("releaseDate") or "")[:10],
        "releaseDateIso": (meta.get("releaseDate") or "")[:10],
        "updatedDate": (meta.get("currentVersionReleaseDate") or "")[:10],
        "totalInstalls": "",
        "recentInstalls30d": "",
        "note": "",
    }


def _honor_of_kings(meta):
    game = _new_game(
        meta,
        "1619254071",
        94,
        "MOBA / 团队竞技",
        "王者荣耀；5v5；三路推塔；英雄；团队竞技；赛季16",
    )
    company = {
        "en": "Proxima Beta Pte. Ltd. / Level Infinite / Tencent TiMi Studio Group",
        "cn": "腾讯游戏（Level Infinite发行；天美工作室群研发）",
        "confidence": "已确认",
        "basis": "Apple店铺主体为Proxima Beta，发行品牌为Level Infinite；商品页明确产品由腾讯天美工作室群研发。",
        "source": "https://www.honorofkings.com/",
    }
    analysis = trend(
        "趋势：2024年全球上线后以15分钟5v5、全球英雄阵容与电竞认知承接MOBA用户；关键转折：本期Season 16《Flow As One》于9月23日开启，产品随赛季切换进入iOS策略分类榜；主力素材：英雄技能、三路推塔、多人团战、赛季皮肤与电竞舞台。",
        "2015年在中国上线后形成成熟的移动MOBA体系，2024年国际版扩展到全球市场；长期循环围绕英雄熟练度、排位赛、皮肤和电竞内容，而不是SLG式城建与联盟扩张。",
        "本次进入iOS美国策略畅销榜第40名。产品属于MOBA，仅作为Apple Strategy分类边界产品记录，不纳入Sensor Tower核心策略收入子集。",
        "全球版上线把中国市场积累的英雄与赛事体系带到国际市场；2026年9月23日Season 16《Flow As One》开启，与本次入榜时间重合，但单个快照不足以证明长期抬升。",
        "英雄登场与连招、5v5团战、推塔逆转、限定皮肤、赛季开幕和电竞高光，核心传播集中在操作表现与团队配合。",
        "观察Season 16开启后一至两个有效快照能否继续留在TOP60；分类边界变化需与核心策略产品分开解读。",
        "https://apps.apple.com/us/app/id1619254071",
        [{"label": "Honor of Kings官方网站", "url": "https://www.honorofkings.com/", "type": "primary"}],
    )
    return game, company, analysis


def _lucky_defense(meta):
    game = _new_game(
        meta,
        "6482291732",
        95,
        "合作塔防 / 随机合成 / 轻度策略",
        "随机召唤；幸运值；合并单位；双人合作；轮盘；守怪；中秋活动",
    )
    company = {
        "en": "Crater Co., Ltd. / 111%",
        "cn": "韩国Crater（Apple店铺主体）/ 111%（发行品牌展示）",
        "confidence": "已确认",
        "basis": "Apple Lookup显示店铺主体为Crater Co., Ltd.、发行展示名为111%；未发现足够证据确认其归属于其他更大集团。",
        "source": "https://www.111percent.net/",
    }
    analysis = trend(
        "趋势：2024年以双人合作塔防叠加随机召唤、合并与轮盘，把失败和翻盘都交给可视化概率；关键转折：2.0.13加入Emily、极限突破和中秋Kingdom Festival后进入iOS TOP60；主力素材：随机抽取、单位合并、双人守线、怪潮压力和幸运翻盘。",
        "2024年上线后没有沿用传统固定塔防阵容，而是让双方在同一局中不断随机召唤、合并与赌轮盘，把合作沟通和不确定性变成每局内容。当前主要由持续角色更新、活动和成熟合作用户支撑。",
        "本次进入iOS美国策略畅销榜第54名，仍处榜尾观察区；Google同口径当前未收录。",
        "产品的核心差异从一开始就是把概率而非纯数值做成显性玩法。2026年9月23日2.0.13新增守护者Emily、极限突破、限定皮肤和中秋多人活动，节点与本次入榜相邻，但不把相关性写成确定因果。",
        "抽卡式随机召唤、相同单位合并、双人并排守线、密集怪潮、失败前的轮盘豪赌，以及节庆角色和限定皮肤。",
        "观察中秋活动结束后能否继续留榜，以及随机性内容能否把活动用户沉淀为长期合作与角色养成用户。",
        "https://apps.apple.com/us/app/id6482291732",
        [{"label": "111%官方网站", "url": "https://www.111percent.net/", "type": "company-research"}],
    )
    return game, company, analysis


def build_ios_today(rows, source_url, source_updated):
    current = updater.records(
        "data/ios-games-20260923.json",
        "data/ios-enrichment-20260923.json",
        "data/ios-trends-20260923.json",
        "appId",
    )
    historical = updater.merged_records(updater.history_specs("ios-", updater.IOS_DATES), "appId")
    google = updater.merged_records(updater.history_specs("", updater.GOOGLE_DATES), "packageName")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in current]
    metadata = lookup(entrant_ids)
    games, companies, analyses, bundle = [], {}, {}, {}
    new_asset_ranks = {"1605558677": 93, "1619254071": 94, "6482291732": 95}

    for row in rows:
        app_id, rank = row["appId"], row["rank"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        elif app_id in historical:
            game, company, analysis = map(deepcopy, historical[app_id])
        elif app_id == "1605558677":
            game, company, analysis = map(deepcopy, google["com.farlightgames.samo.gp"])
            game.pop("appId", None)
            game["assetRank"] = new_asset_ranks[app_id]
            analysis["sections"]["rankPath"] = "本次进入iOS美国策略畅销榜第56名。2023年全球上线后由首发高位转入成熟赛季运营，榜位主要随巨兽、战宠与联盟活动变化。"
        elif app_id == "1619254071":
            game, company, analysis = _honor_of_kings(metadata[app_id])
        elif app_id == "6482291732":
            game, company, analysis = _lucky_defense(metadata[app_id])
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
        if app_id in new_asset_ranks:
            game["assetRank"] = new_asset_ranks[app_id]
            bundle[f"{game['assetRank']}_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle[f"{game['assetRank']}_store"] = data_uri(game["screenshotUrl"], (720, 720))

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

    enrichment = deepcopy(updater.load("data/ios-enrichment-20260923.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20260924.json", games)
    updater.save("data/ios-enrichment-20260924.json", enrichment)
    updater.save("data/ios-trends-20260924.json", analyses)
    updater.save("assets/ios-assets-23.json", bundle)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if "ios-assets-23.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-23.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-09-24.json", {
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
