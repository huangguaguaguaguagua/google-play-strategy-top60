#!/usr/bin/env python3
"""Build the Beijing 2026-10-02 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

import daily_update_20261001 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, trend
from daily_update_20260821 import play_metadata


updater = prior.updater
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-02"
updater.STAMP = "20261002"
updater.PREVIOUS_STAMP = "20261001"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-07-04"
updater.GOOGLE_DATES = ("20261001",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261001",) + updater.IOS_DATES


def enforce_required_product_language(game_name, analysis):
    """Keep the three explicitly audited lifecycle narratives consistent across stores."""
    replacements = {}
    if game_name == "Kingshot":
        replacements = {
            "类《Thronefall》的移动英雄塔防": "类Thronefall移动塔防",
            "类《Thronefall》的移动领主守城": "类Thronefall移动塔防",
            "类《Thronefall》的低多边形移动塔防": "类Thronefall移动塔防",
            "类Thronefall守城／昼建夜战": "类Thronefall移动塔防／昼建夜守",
        }
    elif "Rise of Kingdoms" in game_name:
        replacements = {
            "收留难民、资源管理、科技树和多人会战": "收留难民、城建资源管理、科技树和真实会战",
            "大规模联盟会战": "大规模真实联盟会战",
        }
    elif game_name.replace(" ", "").startswith("DarkWar"):
        replacements = {
            "串成连续高压剧情": "串成连续剧情的高压冲突",
            "素材重心明显转向庇护所：清理废墟、扩建房间": "成熟期素材重心明显转向庇护所扩建：清理废墟、扩建房间",
            "社交或恋爱地位": "关系/地位叙事",
        }

    def rewrite(value):
        if isinstance(value, dict):
            return {key: rewrite(item) for key, item in value.items()}
        if isinstance(value, list):
            return [rewrite(item) for item in value]
        if isinstance(value, str):
            for old, new in replacements.items():
                value = value.replace(old, new)
        return value

    return rewrite(analysis)


def _the_ants_google(row):
    """Build a Google-specific profile from the US product page and official StarUnion sources."""
    metadata = play_metadata(row["packageName"])
    release = metadata.get("released") or ""
    if release != "2021-04-23":
        raise RuntimeError(f"The Ants Google released date requires review: {release!r}")
    game = {
        "rank": row["rank"],
        "packageName": row["packageName"],
        "gameName": row["gameName"],
        "developer": row.get("developer") or metadata.get("developer", "StarUnion"),
        "totalInstalls": metadata.get("downloads", ""),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"],
        "store": "googlePlay",
        "storeUrl": metadata["url"],
        "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"],
        "shortDescription": metadata.get("description", ""),
        "description": (
            "经营真实蚁穴、保护蚁后并规划巢道，孵化特化蚁、驯服其他昆虫，加入联盟争夺资源、"
            "赛季据点与丰饶之树的写实动物题材4X。"
        ),
        "releaseDate": release,
        "releaseDateIso": release,
        "updatedDate": metadata.get("updated", ""),
        "assetRank": 81,
        "genre": "SLG / 4X / 蚁巢经营",
        "keywords": "蚂蚁；写实动物；蚁穴建设；特化蚁；昆虫驯养；联盟；赛季；丰饶之树；4X",
        "note": "Google美国区商品页序列化released为2021-04-23；90天状态只使用本商店日期。",
    }
    company = {
        "en": "StarUnion / ChengDu Starunion Interactive Entertainment Technology Co., Ltd. / StarFortune Interactive Entertainment Technology Co., Limited",
        "cn": "星合互娱（成都星合互娱科技有限公司；Google开发者法律主体为StarFortune Interactive Entertainment Technology Co., Limited）",
        "confidence": "已确认",
        "basis": "Google Play店铺发行名为StarUnion、开发者信息列StarFortune香港主体；星合互娱官网把The Ants列为自有产品并披露成都公司。官网仅披露三七互娱投资，未据此把产品归入三七体系。",
        "source": "https://www.staruniongame.com/cn",
    }
    analysis = trend(
        "趋势：2021年以真实蚁穴经营、特化蚁养成和联盟4X上线，长期扩展至赛季据点与跨服竞争，本次首次进入项目Google #57；关键转折：9月28日版本优化赛季塔/要塞遣散、特化蚁技能与觉醒展示，当前另有The Ants × Gamera活动，但未发现可确认的结构性改版；主力素材：蚁穴剖面、蚁后与工蚁分工、特化蚁孵化、昆虫驯养、联盟争夺丰饶之树和巨型天敌压力。",
        "Google美国区于2021年4月上架，首层以巢穴剖面、蚁后存活、资源采集和巢道规划建立写实蚂蚁经营入口，再由特化蚁、昆虫驯养、联盟互助和领土争夺承接长期4X循环。产品已属成熟长线运营，不按新品解释本次入榜。",
        "本次首次进入项目自2026年8月19日起保存的Google Play美国策略畅销TOP60，位列第57名；上架远早于90天窗口且缺少2026年7月4日同口径基准，因此内部状态为pending、页面按常规在榜展示。iOS同口径本期未收录。",
        "当前可核验节点包括9月28日更新对赛季塔/要塞遣散、特化蚁技能升阶与觉醒展示的优化，以及商店正在展示的The Ants × Gamera活动；尚无公开证据证明活动直接造成本次#57，未发现可确认的重大生命周期转折。",
        "Google商店图以蚁穴内部建设、蚁后与工蚁分工、特化蚁孵化、巨型昆虫编队、联盟战场和真实比例天敌压力为主；当前活动再加入巨型蜥蜴/Gamera对抗。素材判断基于单一Google商店证据，可信度为中。",
        "观察未来1—2个有效快照能否脱离Google后五名，以及Gamera活动开启后是否连续留榜；没有连续数据前不把首次#57写成活动驱动或长期增长。",
        metadata["url"],
        [
            {"label": "The Ants产品官网", "url": "https://theants.allstarunion.com/en", "type": "primary"},
            {"label": "星合互娱官网", "url": "https://www.staruniongame.com/cn", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-02",
        status="已复核",
        confidence="中",
        basis="上架日、版本、玩法和当前素材来自Google美国区商品页；产品及公司关系由The Ants与星合互娱官网交叉确认。",
        changeReason="首次进入项目Google榜，按Google US released建立独立商店档案，未借用Apple日期或第三方榜位。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-02",
        status="已复核",
        confidence="中",
        scope="从2021年Google上架梳理到2026年9月28日维护版本、Gamera活动窗口与本次首次进入项目TOP60。",
        evidenceNote="活动与首次入榜时间相邻，但没有公开收入或投放数据证明因果；按成熟期榜尾待验证信号处理。",
    )
    return game, company, analysis, metadata


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20261001.json",
        "data/enrichment-20261001.json",
        "data/trends-20261001.json",
        "packageName",
    )
    historical = updater.merged_records(updater.history_specs("", updater.GOOGLE_DATES), "packageName")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    games, companies, analyses, bundle = [], {}, {}, {}

    for row in rows:
        package, rank = row["packageName"], row["rank"]
        if package in current:
            game, company, analysis = map(deepcopy, current[package])
        elif package in historical:
            game, company, analysis = map(deepcopy, historical[package])
        elif package == "com.star.union.planetant":
            game, company, analysis, metadata = _the_ants_google(row)
            bundle["81_icon"] = data_uri(metadata["icon"], (256, 256))
            bundle["81_store"] = data_uri(metadata["screenshot"], (720, 720))
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
            updater.clean_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/enrichment-20261001.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261002.json", games)
    updater.save("data/enrichment-20261002.json", enrichment)
    updater.save("data/trends-20261002.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    if bundle:
        updater.save("assets/assets-18.json", bundle)
        if "assets-18.json" not in manifest["files"]:
            manifest["files"].append("assets-18.json")
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-02.json", {
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
        "data/ios-games-20261001.json",
        "data/ios-enrichment-20261001.json",
        "data/ios-trends-20261001.json",
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
            updater.clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis

    enrichment = deepcopy(updater.load("data/ios-enrichment-20261001.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261002.json", games)
    updater.save("data/ios-enrichment-20261002.json", enrichment)
    updater.save("data/ios-trends-20261002.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-02.json", {
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


if __name__ == "__main__":
    updater.main()
