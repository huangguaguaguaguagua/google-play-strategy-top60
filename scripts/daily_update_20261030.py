#!/usr/bin/env python3
"""Build the Beijing 2026-10-30 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
import unicodedata
from zoneinfo import ZoneInfo

import daily_update_20261029 as prior
from daily_update_20260820 import comparison, data_uri, delta_label, lookup, trend
from daily_update_20260821 import play_metadata


updater = prior.updater
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-10-30"
updater.STAMP = "20261030"
updater.PREVIOUS_STAMP = "20261029"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-08-01"
updater.GOOGLE_DATES = ("20261029",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261029",) + updater.IOS_DATES


def west_game_google_profile(row):
    """Create West Game's first Google record from Google and Leyi sources."""
    metadata = play_metadata(row["packageName"])
    release = metadata.get("released") or ""
    if release != "2019-03-14":
        raise RuntimeError(f"West Game Google released date requires review: {release!r}")
    game = {
        "rank": row["rank"],
        "packageName": row["packageName"],
        "gameName": row["gameName"],
        "developer": row.get("developer") or metadata.get("developer", "LeyiGames"),
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
            "以美国西部城镇、警长与帮派冲突建立题材入口，再由城镇扩建、兵种训练、"
            "联盟集结和世界地图战争承接长线SLG循环。"
        ),
        "releaseDate": release,
        "releaseDateIso": release,
        "updatedDate": metadata.get("updated", ""),
        "assetRank": 85,
        "genre": "SLG / 4X / 西部城镇经营",
        "keywords": "美国西部；城镇建设；警长；牛仔与亡命徒；帮派；联盟集结；铁路战场",
        "note": "Google美国区商品页序列化released为2019-03-14；90天状态只使用本商店日期。",
    }
    company = {
        "en": "LeyiGames / Shenzhen Leyi Network Co., Ltd.",
        "cn": "LeyiGames（发行品牌）/ 深圳乐易网络（产品体系）",
        "confidence": "已确认",
        "basis": "Google Play开发者为LeyiGames；Leyi官方产品页直接列出West Game，官方隐私声明说明Shenzhen Leyi Network Co., Ltd.及其关联方以LeyiGames开发和发行移动游戏。未据此延伸推断更上层集团。",
        "source": "https://www.leyinetwork.com/en/products/",
    }
    analysis = trend(
        "趋势：2019年以美国西部城镇、警长与帮派冲突切入，再由兵种扩张、联盟集结和世界地图战争形成长线SLG循环；关键转折：本期首次进入项目Google榜#56，产品上架已久且缺少精确90天基准，只按榜尾回补观察；主力素材：荒漠城镇、警长与牛仔、亡命徒、枪战、帮派集结和铁路战场。",
        "Google美国区于2019年3月14日上架。产品先用西部边疆、警长、牛仔与亡命徒建立题材认知，再通过城镇建设、兵种训练、科技、世界玩家对抗和联盟集结承接长期SLG循环；现阶段属于成熟长线运营。",
        "本次首次进入项目保存的Google Play美国策略畅销TOP60，位列第56名；产品上架早于90天窗口，且项目缺少2026-08-01精确同口径完整基准，因此内部保留pending、页面按常规在榜展示。iOS同日策略TOP60未收录。",
        "可确认节点包括2019年Google上架及商品页2026年10月22日更新；公开商品页未披露足以解释本次入榜的重大系统转折，因此不把更新时间写成确定拉升原因。",
        "Google当前商品图以西部荒漠、城镇扩建、警长、牛仔与亡命徒、枪械和帮派战争建立题材识别，再以联盟集结和世界地图承接。素材判断只有Google与厂商产品页证据，可信度为中。",
        "未来1—2个有效快照观察能否连续留榜并离开后十名；若快速退出，只记录为成熟产品的榜尾轮换，不外推为长期增长。",
        metadata["url"],
        [
            {"label": "Leyi官方West Game产品页", "url": "https://www.leyinetwork.com/en/products/", "type": "primary"},
            {"label": "LeyiGames官方隐私与主体页", "url": "https://www.leyinetwork.com/en/privacy/", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-30",
        status="已复核",
        confidence="中",
        basis="上架日、更新时间、玩法、图标和商店图来自Google美国区商品页；发行链由Google开发者信息、Leyi官方产品页和官方隐私声明交叉核验。素材只有Google与厂商产品页证据，不标高可信度。",
        changeReason="首次进入项目保存的Google榜，按Google美国区released建立独立档案；未借用iOS上架日期或第三方榜位。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-30",
        status="已复核",
        confidence="中",
        scope="从2019年Google上架和西部题材城建入口梳理到2026年10月商品页更新及本次首次项目收录。",
        evidenceNote="官方资料支持产品结构、更新时间与发行链；缺少公开收入和投放数据，本次只按成熟产品榜尾回补处理。",
    )
    return game, company, analysis, metadata


def avatar_ios_profile(row, meta):
    """Create Avatar: Realms Collide from Apple and first-party publisher records."""
    icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
    screenshots = meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or []
    screenshot = screenshots[0] if screenshots else icon
    release = (meta.get("releaseDate") or "")[:10]
    if release != "2025-03-18":
        raise RuntimeError(f"Avatar iOS release date requires review: {release!r}")
    store_url = f"https://apps.apple.com/us/app/id{row['appId']}"
    game = {
        "rank": row["rank"],
        "appId": row["appId"],
        "packageName": row["appId"],
        "gameName": row["gameName"],
        "developer": row["developer"],
        "totalInstalls": "",
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "storeUrl": store_url,
        "iconUrl": icon,
        "rankIconUrl": icon,
        "screenshotUrl": screenshot,
        "shortDescription": (meta.get("description") or "").replace("\n", " ")[:220],
        "description": meta.get("description", ""),
        "releaseDate": release,
        "releaseDateIso": release,
        "updatedDate": (meta.get("currentVersionReleaseDate") or "")[:10],
        "genre": "4X / IP策略 / 城建联盟战争",
        "keywords": "Avatar；Aang；Korra；元素弯曲；城市扩张；英雄编队；同伴；联盟战争；跨服战",
        "note": "Apple Lookup显示iOS美国区于2025-03-18上架；90天状态只使用本商店日期。",
        "assetRank": 105,
        "store": "ios",
    }
    company = {
        "en": "Tilting Point LLC / AN Games Co., Ltd.",
        "cn": "Tilting Point LLC（发行）/ AN Games Co., Ltd.（研发与运营）",
        "confidence": "已确认",
        "basis": "Apple美国区Lookup列Tilting Point LLC为seller；Tilting Point官方工作室页明确其为Avatar: Realms Collide发行商，并列AN Games为研发方；产品官方运营政策进一步列AN Games Co., Ltd.为运营主体。未把IP授权方误写为发行或研发主体。",
        "source": "https://www.tiltingpoint.com/studios",
    }
    analysis = trend(
        "趋势：2025年借Avatar IP、Aang/Korra等角色与元素弯曲切入，再由城市扩张、英雄编队、同伴养成和联盟4X承接；关键转折：本期首次进入项目iOS榜#60，10月SvS预赛仍在活动窗口，但榜尾入榜只记为待验证信号；主力素材：Aang与Korra、元素战斗、四国城市、同伴、世界地图与联盟会战。",
        "2025年3月全球上线。早期用Avatar: The Last Airbender与The Legend of Korra角色、原作配音和元素战斗降低4X理解门槛；进入长期运营后，以城市研究、资源扩张、英雄装备、同伴成长、联盟冲突和跨服竞争承接核心策略用户。",
        "本期首次进入项目保存的iOS美国策略畅销TOP60，位列第60名；产品上架早于90天窗口，项目缺少2026-08-01同口径完整基准，因此内部保留pending、页面按常规在榜展示。Google Play同日策略TOP60未收录。",
        "可确认节点包括2025年全球首发、联盟大规模对抗MGM，以及2026年10月3日至30日的SvS预赛Glowworm's Ruse；Apple Lookup记录10月28日版本更新。活动与本次入榜时间相邻，但没有证据证明其单独造成榜位变化。",
        "Apple当前商品图以Aang、Korra、Zuko等IP角色、元素技能、四国场景和英雄编队建立识别，再以城建、伙伴、联盟与世界地图承接4X深度。素材依据为Apple商品页及发行商官方资料，可信度为中。",
        "未来1—2个有效快照观察能否连续留榜并脱离第60名；同时在10月30日SvS预赛结束后核验是否回落，单日入榜不外推为长期增长。",
        store_url,
        [
            {"label": "Tilting Point官方产品页", "url": "https://www.tiltingpoint.com/games/avatar", "type": "primary"},
            {"label": "Tilting Point官方工作室与发行链", "url": "https://www.tiltingpoint.com/studios", "type": "company-audit"},
            {"label": "Avatar官方运营政策", "url": "https://avatarrc.zendesk.com/hc/en-us/articles/8911297780495-Game-Operation-Policy", "type": "company-audit"},
        ],
    )
    analysis = updater.clean_analysis(analysis)
    analysis["sourceAudit"].update(
        reviewedAt="2026-10-30",
        status="已复核",
        confidence="中",
        basis="上架日、版本日期、玩法、图标和商店图来自Apple美国区Lookup/商品页；发行、研发与运营链由Tilting Point官方工作室页和产品官方运营政策交叉核验。素材只有Apple与发行方资料，不标高可信度。",
        changeReason="首次进入项目保存的iOS榜，按iOS自身releaseDate建立独立档案；10月SvS节点仅作相邻背景，不写成本次入榜的确定原因。",
    )
    analysis["lifecycleAudit"].update(
        reviewedAt="2026-10-30",
        status="已复核",
        confidence="中",
        scope="从2025年3月iOS上线与IP获量入口梳理到联盟跨服玩法、2026年10月SvS预赛和本次首次项目收录。",
        evidenceNote="官方资料支持产品结构、活动时间与发行链；缺少公开收入和投放数据，本次只按榜尾待验证信号处理。",
    )
    return game, company, analysis, icon, screenshot


def build_google_today(rows, source):
    current = updater.records(
        "data/games-20261029.json",
        "data/enrichment-20261029.json",
        "data/trends-20261029.json",
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
        elif package == "leyi.westgame":
            game, company, analysis, metadata = west_game_google_profile(row)
            bundle["85_icon"] = data_uri(metadata["icon"], (256, 256))
            bundle["85_store"] = data_uri(metadata["screenshot"], (720, 720))
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
            prior.prior.prepare_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = prior.prior.prior.prior.enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis
    enrichment = deepcopy(updater.load("data/enrichment-20261029.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.GOOGLE_BASELINE,
        currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/games-20261030.json", games)
    updater.save("data/enrichment-20261030.json", enrichment)
    updater.save("data/trends-20261030.json", analyses)
    manifest = updater.load("assets/manifest.json")
    manifest["date"] = updater.GOOGLE_DATE
    if bundle:
        updater.save("assets/assets-22.json", bundle)
        if "assets-22.json" not in manifest["files"]:
            manifest["files"].append("assets-22.json")
    updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-10-30.json", {
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
        "data/ios-games-20261029.json",
        "data/ios-enrichment-20261029.json",
        "data/ios-trends-20261029.json",
        "appId",
    )
    historical = updater.merged_records(updater.history_specs("ios-", updater.IOS_DATES), "appId")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in current and row["appId"] not in historical]
    metadata = lookup(entrant_ids) if entrant_ids else {}
    if set(metadata) != set(entrant_ids):
        raise RuntimeError(f"Apple Lookup did not return every new product: {entrant_ids}")
    games, companies, analyses, bundle = [], {}, {}, {}
    for row in rows:
        app_id, rank = row["appId"], row["rank"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        elif app_id in historical:
            game, company, analysis = map(deepcopy, historical[app_id])
        elif app_id == "6479603752":
            game, company, analysis, icon, screenshot = avatar_ios_profile(row, metadata[app_id])
            bundle["105_icon"] = data_uri(icon, (256, 256))
            bundle["105_store"] = data_uri(screenshot, (720, 720))
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
            prior.prior.prepare_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        analysis = prior.prior.prior.prior.enforce_required_product_language(game["gameName"], analysis)
        games.append(game)
        companies[str(rank)] = company
        analyses[str(rank)] = analysis
    enrichment = deepcopy(updater.load("data/ios-enrichment-20261029.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=updater.IOS_BASELINE,
        currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    updater.save("data/ios-games-20261030.json", games)
    updater.save("data/ios-enrichment-20261030.json", enrichment)
    updater.save("data/ios-trends-20261030.json", analyses)
    manifest = updater.load("assets/ios-manifest.json")
    manifest["date"] = updater.IOS_DATE
    if bundle:
        updater.save("assets/ios-assets-32.json", bundle)
        if "ios-assets-32.json" not in manifest["files"]:
            manifest["files"].append("ios-assets-32.json")
    updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-10-30.json", {
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


def refresh_rank_paths():
    first_time = {("Google Play", "leyi.westgame")}
    for games_path, trends_path, store_label, release_basis, id_key in (
        ("data/games-20261030.json", "data/trends-20261030.json", "Google Play", "Google Play美国区商品页released日期", "packageName"),
        ("data/ios-games-20261030.json", "data/ios-trends-20261030.json", "iOS", "Apple Lookup releaseDate", "appId"),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        for game in games:
            change = game["dailyChange"]
            if change == "NEW":
                movement = "项目历史首次收录" if (store_label, str(game[id_key])) in first_time else "2026-10-29前一有效快照未入榜，回榜"
            elif change == "=":
                movement = "较2026-10-29前一有效快照持平"
            elif change.startswith("+"):
                movement = f"较2026-10-29前一有效快照上升{change[1:]}位"
            else:
                movement = f"较2026-10-29前一有效快照下降{change[1:]}位"
            status = game["comparison90d"]
            if status["status"] == "new":
                status_text = (
                    f"按{release_basis}{game['releaseDateIso']}计算，位于"
                    f"{status['baselineDate']}至{status['currentDate']}的90天窗口内，归类为近三个月新上榜。"
                )
            elif status["status"] == "surge":
                status_text = (
                    f"精确90天基准名次为#{status['baselineRank']}，至当前提升{status['delta']}位，"
                    "归类为近三个月飙升。"
                )
            else:
                status_text = (
                    f"上架早于90天窗口；因缺少{status['baselineDate']}同口径完整TOP60基准，"
                    "不判断近三个月飙升，页面按常规在榜展示。"
                )
            trends[str(game["rank"])]["sections"]["rankPath"] = (
                f"本次位于{store_label}美国策略畅销榜第{game['rank']}名（{movement}）。{status_text}"
            )
        updater.save(trends_path, trends)


def normalize_summary_rank_references():
    aliases = {
        "last war survival game": "last war survival",
        "evony the king s return": "evony",
        "rise of kingdoms lost crusade": "rise of kingdoms",
        "age of origins tower defense": "age of origins",
        "forge master idle rpg": "forge master",
        "marvel snap hero strategy ccg": "marvel snap",
        "marvel snap hero card game": "marvel snap",
        "top force commander": "top force",
        "kingdom guard tower defense td": "kingdom guard tower defense",
        "rise of castles ice and fire": "rise of castles",
        "rise of castles fire and war": "rise of castles",
    }

    def product_key(name):
        plain = unicodedata.normalize("NFKD", str(name)).encode("ascii", "ignore").decode().lower()
        normalized = re.sub(r"[^a-z0-9]+", " ", plain).strip()
        return aliases.get(normalized, normalized)

    google_games = updater.load("data/games-20261030.json")
    ios_games = updater.load("data/ios-games-20261030.json")
    by_store = {
        "Google": {product_key(game["gameName"]): game for game in google_games},
        "iOS": {product_key(game["gameName"]): game for game in ios_games},
    }
    first_time = {("Google", "leyi.westgame")}

    def current_phrase(store_label, game, id_key):
        change = game["dailyChange"]
        if change == "NEW":
            if (store_label, str(game[id_key])) in first_time:
                return f"本期首次进入项目{store_label}榜#{game['rank']}"
            return f"本期回到{store_label} #{game['rank']}"
        if change == "=":
            return f"本期{store_label}持平于#{game['rank']}"
        direction = "上升" if change.startswith("+") else "下跌"
        return f"本期{store_label}{direction}{change[1:]}位至#{game['rank']}"

    for games_path, trends_path, store_label, counterpart_label, id_key in (
        ("data/games-20261030.json", "data/trends-20261030.json", "Google", "iOS", "packageName"),
        ("data/ios-games-20261030.json", "data/ios-trends-20261030.json", "iOS", "Google", "appId"),
    ):
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        own_pattern = re.compile(
            rf"本期(?:首次进入项目{store_label}榜#\d+|回到{store_label}\s*#\d+|"
            rf"{store_label}(?:再)?(?:上升|下跌|回落|升|跌)\d+位至#\d+|{store_label}持平于#\d+|{store_label}位于#\d+)"
        )
        counterpart_pattern = re.compile(
            rf"{counterpart_label}(?:(?:同产品|当前|同期|反向)?(?:上升|下跌)\d+位至|(?:同产品|当前|同期|反向)?(?:升|跌)至|"
            rf"(?:同产品|当前|同期|反向)?(?:回榜|位于|仍高居|仍在|榜)?\s*)#\d+"
        )
        counterpart_absent_pattern = re.compile(rf"{counterpart_label}(?:策略榜)?未入榜")
        for game in games:
            summary = trends[str(game["rank"])]["summary"]
            summary = own_pattern.sub(current_phrase(store_label, game, id_key), summary)
            counterpart = by_store[counterpart_label].get(product_key(game["gameName"]))
            replacement = f"{counterpart_label}位于#{counterpart['rank']}" if counterpart else f"{counterpart_label}未入榜"
            summary = counterpart_pattern.sub(replacement, summary)
            summary = counterpart_absent_pattern.sub(replacement, summary)
            trends[str(game["rank"])]["summary"] = summary
        updater.save(trends_path, trends)


def refresh_semantic_summaries():
    """Repair product-specific clauses whose old directional wording is no longer true."""
    updates = {
        "data/trends-20261030.json": {
            "com.run.tower.defense": "趋势：2024年先行测投、2025年全球上线后，塔防/类Thronefall移动塔防/昼建夜守的获量层承接城镇经营与联盟4X，形成快速头部增长；关键转折：本期Google持平于#2、iOS上升1位至#2，双端重新并列第二但仍需下一快照确认；主力素材：骑马领主走位、昼建夜守、低多边形城镇、英雄与联盟战争。",
            "com.lilithgame.roc.gp": "趋势：2018年以文明选择与自由行军建立长线4X盘，后期素材转向战力逆袭情景剧，近期更多展示城建资源和真实会战；关键转折：本期Google持平于#19、iOS持平于#27，未发现可确认的重大转折，继续由成熟联盟与核心用户盘支撑；主力素材：文明选择、自由行军、战力逆袭情景剧、城建资源与真实联盟会战。",
            "com.gtarcade.ioe.global": "趋势：2021年以卡通文明、英灵和龙养成承接联盟4X；关键转折：本期Google持平于#18、iOS持平于#30，双端均无位移，未发现可确认的重大转折；主力素材：跨文明英灵、巨龙、卡通城建、元素编队与联盟攻城。",
            "com.wb.goog.got.conquest": "趋势：2017年借Game of Thrones IP、城堡建设与联盟4X建立长线盘；关键转折：九周年2026_10更新仍在近期窗口，本期Google上升4位至#36、iOS下跌3位至#38，跨端反向不能写成版本确定拉动；主力素材：剧集角色、巨龙、城堡扩建、研究树与联盟战争。",
            "com.snowprintstudios.tacticus": "趋势：2022年以Warhammer 40K正版阵营和短局六角战术切入，成熟期由新派系、限定角色和活动轮换支撑；关键转折：本期Google上升3位至#38、iOS下跌3位至#51，跨端反向且iPhone已接近榜尾，继续按待验证信号处理；主力素材：战锤单位、六角格部署、派系克制、Boss与限定角色。",
            "com.YoStarEN.Arknights": "趋势：2020年以干员收集、格子塔防和章节叙事建立长线核心盘，成熟期由主线、限时活动与干员轮换支撑；关键转折：10月28日Reclamation Algorithm活动开启，本期Google持平于#17、iOS下跌14位至#46，平台表现分化且不能写成统一拉升；主力素材：干员编队、格子部署、技能爆发、活动地图与异常环境。",
            "com.justgame.jails": "趋势：2025年以监狱建设、犯人管理和轻量经营承接策略用户，再由人员调度、资源循环与冲突事件延长经营；关键转折：本期Google持平于#27、iOS上升1位至#37，两端位移有限且未发现同步重大节点；主力素材：监狱扩建、人员调度、资源循环、冲突事件与经营升级。",
            "com.camelgames.aoz": "趋势：2018年以末日城建、兵种与联盟战争形成长线4X循环，成熟期由英雄、跨服竞争与活动轮换支撑；关键转折：本期Google持平于#29、iOS下跌2位至#21，平台位移有限且未发现可确认的重大转折；主力素材：丧尸压力、城市扩张、兵种编队、英雄与联盟大地图。",
            "com.farlightgames.warline.gp.global": "趋势：2026年先以可直接操控的狙击任务降低现代战争4X入门门槛，再由联合兵种、基地恢复与联盟大地图承接；关键转折：本期Google上升5位至#20、iOS上升3位至#44，双端同向但名次层级差异仍大；主力素材：第一视角狙击、慢镜击杀、桥梁与载具爆破、坦克、联合兵种和军事基地。",
            "com.more.lastshelter.gp": "趋势：2026年以地下庇护所剖面、营救幸存者与僵尸压力承接房间建设、英雄编队和联盟战争，目前仍处上线早期验证；关键转折：本期Google上升4位至#28、iOS上升7位至#50，双端改善但iPhone仍在后十名附近；主力素材：地下庇护所剖面、救援抉择、僵尸追击、房间扩建与英雄小队。",
            "com.igg.android.lordsmobile": "趋势：2016年以奇幻英雄、领主城堡和大规模联盟战建立长线4X盘，成熟期由跨服竞争和IP联动支撑；关键转折：本期Google下跌5位至#33、iOS同步下跌5位至#60，iPhone已压线留榜；主力素材：英雄军团、夸张兵力、城堡扩建、联盟集结、跨服战争与联动角色。",
            "com.bw.ud.googleplay": "趋势：2023年以潜艇瞄准和鱼雷命中提供直接的动作入口，再由舰队、海上基地与联盟战争承接SLG循环；关键转折：本期Google上升9位至#48、iOS同步上升6位至#28，是本日较清晰的双端共同信号但仍待连续快照确认；主力素材：潜望镜、鱼雷命中、潜艇编队、舰队齐射、海军基地与联盟海战。",
            "com.tap4fun.kissofwar.googleplay": "趋势：2019年以二战战场、女性军官和坦克军团切入，成熟期由国家阵营、军官收集与联盟竞争维持；关键转折：本期Google回榜#54、iOS上升10位至#39，双端改善但Android仍处后十名；主力素材：女性军官、二战坦克、国家阵营、战场选择与军团集结。",
            "com.mrtgd2us.google": "趋势：2025年用武装鸭子和昼建夜守形成高识别的末日塔防，再由武器等级和随机技能构筑延长短局变化；关键转折：本期Google下跌7位至#59、iOS未入榜，已接近掉榜线且未发现同步重大官方节点；主力素材：鸭子小队、昼建夜守、尸潮、武器等级与Roguelike组合。",
            "com.fiveminlab.overgeared.hero.backpack.merge": "趋势：2026年以像素背包装备合并、肉鸽短局和自动战斗进入榜单，成熟承接依赖角色、装备与联动轮换；关键转折：本期Google下跌5位至#42、iOS同步下跌3位至#57，双端同向回落且iPhone接近榜尾；主力素材：像素英雄、背包摆位、装备合成、联动角色与季节皮肤。",
            "com.topwar.gp": "趋势：2019年以单位合成升级、英雄与联盟战争形成成熟4X盘，用短路径合成降低传统SLG理解门槛；关键转折：本期Google上升1位至#45、iOS下跌5位至#49，跨端反向且未发现同步重大节点；主力素材：单位合成、数字门、英雄、基地扩建、跨服战与IP联动。",
            "com.wireless.defenseland": "趋势：2023年以英雄放置、塔防路线与装备成长切入，成熟期依靠英雄收集、挑战关和活动维持；关键转折：本期Google下跌1位至#60、iOS下跌3位至#42，双端同向回落且Android已压线留榜；主力素材：英雄编队、塔防路线、技能爆发、装备养成与Boss关卡。",
        },
        "data/ios-trends-20261030.json": {
            "6739554056": "趋势：2024年先行测投、2025年全球上线后，塔防/类Thronefall移动塔防/昼建夜守的获量层承接城镇经营与联盟4X，形成快速头部增长；关键转折：本期iOS上升1位至#2、Google持平于#2，双端重新并列第二但仍需下一快照确认；主力素材：骑马领主走位、昼建夜守、低多边形城镇、英雄与联盟战争。",
            "1354260888": "趋势：2018年以文明选择、自由行军和联盟大地图建立长线4X盘，后期素材转向战力逆袭情景剧，近期更多展示城建资源与真实会战；关键转折：本期iOS持平于#27、Google持平于#19，未发现可确认的重大转折，继续由成熟联盟与核心用户盘支撑；主力素材：文明选择、自由行军、战力逆袭情景剧、城建资源与真实联盟会战。",
            "6738469826": "趋势：2025年以监狱建设、犯人管理和轻量经营承接策略用户；关键转折：本期iOS上升1位至#37、Google持平于#27，双端位移有限，未发现可确认的重大转折；主力素材：监狱扩建、人员调度、资源循环、冲突事件与经营升级。",
            "1342290011": "趋势：2018年以末日采集、基地建设和联盟战争形成长线生存盘；关键转折：本期iOS下跌7位至#53、Google持平于#51，iPhone已回到后十名，当前只记为榜尾风险信号；主力素材：丧尸压迫、荒野采集、基地扩建、兵种编队与联盟大地图。",
            "6447612873": "趋势：2022年以潜艇编队、海上基地与舰长经营建立海战SLG核心盘；关键转折：1.175.0加入精英招募角色与回归福利，本期iOS上升6位至#28、Google同步上升9位至#48，时间相邻但仍不作确定归因；主力素材：潜艇编队、海上基地、舰长招募、航线争夺与联盟海战。",
            "6444112366": "趋势：2023年以12名罪人、技能连锁与Clash硬币判定切入Project Moon核心用户，成熟期由章节、赛季、Identity与E.G.O更新支撑；关键转折：10月29日定期更新与本期iOS回榜#35时间相邻，Google未入榜，当前只作待验证信号；主力素材：反乌托邦都市、巴士小队、技能链、硬币判定、E.G.O爆发与异常体Boss。",
            "1465860096": "趋势：2019年以二战战场、女性军官和实时军团战争建立军事4X用户盘，长期由国家阵营和联盟竞争维持；关键转折：本期iOS上升10位至#39、Google回榜#54，双端同向改善但Android仍在榜尾；主力素材：二战机械、军官收集、坦克、国家阵营、军团集结与实时大地图。",
            "6751086804": "趋势：2026年以龙族角色收集、战术编队和奇幻叙事进入首发验证；关键转折：本期iOS上升12位至#41、Google未入榜，单日跳升只记为待验证信号；主力素材：龙族角色、技能演出、编队克制、Boss战与章节剧情。",
            "1464872022": "趋势：2020年全球上线后以职业克制、部署顺序与技能时机构成长线塔防核心；关键转折：10月28日Reclamation Algorithm活动开启，本期iOS下跌14位至#46、Google持平于#17，平台表现分化且不能写成统一拉升；主力素材：干员编队、格子部署、技能爆发、活动地图与异常环境。",
            "1071976327": "趋势：2016年以城堡扩建、英雄和联盟战争建立长线4X盘，成熟期由跨服竞争和IP联动支撑；关键转折：本期iOS下跌5位至#60、Google同步下跌5位至#33，iPhone已压线留榜；主力素材：英雄、城堡扩建、联盟集结、跨服战与联动角色。",
            "6755585789": "趋势：2025年以Overgeared IP、背包合成与角色养成切入，再由关卡Boss、装备升级和角色轮换承接；关键转折：本期iOS下跌3位至#57、Google同步下跌5位至#42，双端同向回落且iPhone接近榜尾；主力素材：Grid角色、背包合成、装备升级、技能爆发与关卡Boss。",
            "6479020757": "趋势：2025年以DC角色收集、地下基地经营和联盟PvP切入，再由阵容克制、房间扩建与活动角色承接；关键转折：本期iOS下跌1位至#52、Google下跌1位至#46，双端同向小幅回落且未发现同步重大节点；主力素材：Batman等DC英雄、Dark Multiverse、基地房间、阵容克制与联盟战。",
        },
    }
    for trends_path, summaries in updates.items():
        ios = trends_path.startswith("data/ios-")
        games_path = "data/ios-games-20261030.json" if ios else "data/games-20261030.json"
        key = "appId" if ios else "packageName"
        games = updater.load(games_path)
        trends = updater.load(trends_path)
        by_id = {str(game[key]): game for game in games}
        for product_id, summary in summaries.items():
            trends[str(by_id[product_id]["rank"])]["summary"] = summary
        updater.save(trends_path, trends)


if __name__ == "__main__":
    updater.main()
    refresh_rank_paths()
    normalize_summary_rank_references()
    refresh_semantic_summaries()
