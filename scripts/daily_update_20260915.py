#!/usr/bin/env python3
"""Build the Beijing 2026-09-15 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_ios, save, trend
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from daily_update_20260821 import play_metadata
from daily_update_20260910 import ios_game_from_metadata
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-09-15"
GOOGLE_DATE = "2026-09-15"
GOOGLE_BASELINE = "2026-06-17"
IOS_DATE = "2026-09-15"
IOS_BASELINE = "2026-06-17"

GOOGLE_HISTORY = [
    (f"data/games-{date}.json", f"data/enrichment-{date}.json", f"data/trends-{date}.json")
    for date in (
        "20260914", "20260911", "20260910", "20260909", "20260908", "20260907", "20260904", "20260903",
        "20260902", "20260901", "20260831", "20260828", "20260827", "20260826",
        "20260825", "20260824", "20260821", "20260820", "20260819d",
    )
]
IOS_HISTORY = [
    (f"data/ios-games-{date}.json", f"data/ios-enrichment-{date}.json", f"data/ios-trends-{date}.json")
    for date in (
        "20260914", "20260911", "20260910", "20260909", "20260908", "20260907", "20260904", "20260903",
        "20260902", "20260901", "20260831", "20260828", "20260827", "20260826",
        "20260825", "20260824", "20260821", "20260820", "20260819",
    )
]


def clean_analysis(analysis):
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


def pokemon_google_profile(row, metadata, asset_rank):
    """Keep Google's verified US release date independent of the iOS date."""
    if metadata["released"] != "2026-06-11":
        raise RuntimeError(f"Pokémon Champions Google released date requires review: {metadata['released']!r}")
    game = {
        "rank": row["rank"], "packageName": row["packageName"], "gameName": row["gameName"],
        "developer": row.get("developer") or "The Pokémon Company",
        "totalInstalls": metadata["downloads"], "recentInstalls30d": "", "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"], "storeUrl": metadata["url"],
        "iconUrl": metadata["icon"], "screenshotUrl": metadata["screenshot"],
        "shortDescription": "Pokémon对战、跨平台回合制竞技与队伍构筑。",
        "description": "通过属性、招式、特性与队伍搭配参与宝可梦对战；可与Nintendo Switch玩家跨平台竞技，并通过Pokémon HOME扩展队伍。",
        "releaseDate": metadata["released"], "releaseDateIso": metadata["released"],
        "updatedDate": metadata["updated"], "assetRank": asset_rank,
        "genre": "回合制战术 / 队伍构筑 / PvP",
        "keywords": "宝可梦；属性克制；特性；招式；队伍构筑；排位；跨平台；Pokémon HOME",
        "note": "Google美国区商品页序列化released为2026-06-11；宝可梦官方标注移动版正式上线2026-06-17。90天状态按本商店元数据日期计算，不混用Apple日期。",
    }
    company = {
        "en": "The Pokémon Company / The Pokémon Works / GAME FREAK",
        "cn": "宝可梦公司（移动版发行）／The Pokémon Works（开发）／GAME FREAK（企划制作）",
        "confidence": "已确认",
        "basis": "美国Google Play商品页显示The Pokémon Company发行；宝可梦官方产品资料逐项列出企划制作、开发、发行及移动平台销售主体。",
        "source": "https://www.pokemon.co.jp/ex/pokemon_champions/sc/",
    }
    analysis = trend(
        "趋势：以宝可梦属性、招式和队伍配置切入移动端回合制竞技，首发阶段通过Switch跨平台对战及Pokémon HOME连接既有用户；关键转折：9月2日官方公布Regulation Set M-C规则调整，今日Google首次进入项目TOP60，但iOS同期退出；主力素材：宝可梦编队、属性克制、对战技能、跨平台竞技与熟悉的角色形象。",
        "2026年上架后以宝可梦标准对战规则建立入口，队伍可从游戏内招募并借Pokémon HOME连接既有积累；官方支持移动设备与Switch跨平台对战。当前尚处移动端上线早期的竞技与付费验证，不能把一天的名次变化写成稳定获量。",
        "今日首次进入Google Play美国策略畅销榜#58，同时从iOS策略TOP60退出。美国Google商品页序列化released日期为2026-06-11，早于本次90天窗口起点2026-06-17；宝可梦官网标注移动版正式上线6月17日，两种日期口径不同。状态遵守本商店元数据规则，不与iOS Lookup上架日混用。",
        "9月2日官方公布Regulation Set M-C，为可核验的竞技规则节点；公开资料不足以证明本次Google进榜由该节点直接推动，亦无法从榜位计算收入。",
        "Google商店图与官方站重点展示宝可梦对战、技能释放、队伍组建和Switch／手机跨平台场景；未取得独立广告投放素材核验，素材可信度为中。",
        "未来2—3个工作日观察Google能否从#58脱离后十名，以及iOS能否重新进入榜单；若仅Android末段短暂回榜，保留单平台付费波动判断。",
        metadata["url"],
        [
            {"label": "Pokémon Champions官方产品站", "url": "https://champions.pokemon.com/en-us/", "type": "primary"},
            {"label": "Pokémon Champions官方中文产品资料（开发/发行/移动版正式上线日）", "url": "https://www.pokemon.co.jp/ex/pokemon_champions/sc/", "type": "company-research"},
            {"label": "Pokémon Champions规则公告", "url": "https://www.pokemon.com/us/news/get-ready-for-regulation-set-m-c-in-pokemon-champions", "type": "lifecycle-analysis"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(confidence="中", basis="发行与玩法见Google美国区商品页及宝可梦官方网站；没有独立可核验广告库素材证据。", changeReason="Google首次入榜，独立核验Google US released并建立本商店生命周期档案。")
    analysis["lifecycleAudit"].update(confidence="中", scope="2026年移动端上线至9月初竞技规则更新。", evidenceNote="今日榜位仅是单快照信号；未发现可确认的收入或投放因果证据。")
    return game, company, analysis


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


def coop_td_profile(row, metadata, asset_rank):
    game = ios_game_from_metadata(
        row,
        metadata,
        asset_rank,
        "合作塔防 / 生存防守 / 轻度策略",
        "双人合作；塔防；战略布阵；城墙防守；怪物；卡组搭配；赛季通行证；传奇皮肤",
    )
    company = {
        "en": "SuperMagic Inc.",
        "cn": "SuperMagic（韩国研发与发行主体）",
        "confidence": "已确认",
        "basis": "Apple美国区店铺主体为Supermagic Inc.；SuperMagic官网将Coop TD列入自研及发行产品，并显示公司版权与首尔办公地址。未发现足够证据证明其归属于更大集团。",
        "source": "https://www.supermagic.io/",
    }
    analysis = trend(
        "趋势：2024年以双人协作塔防、短局布阵和卡组组合上线，成熟阶段通过新军团、赛季通行证与外观内容维持；关键转折：1.6.8加入Demon Legion城墙防守、Golden Draw Board及三款传奇皮肤，但未发现可确认的商业化重大转折；主力素材：双人同屏守线、可爱怪物潮、单位合成与布阵、城墙攻防、传奇皮肤和协作胜利。",
        "产品于2024年10月上线，用双人合作而不是单人守塔作为第一识别点：双方配置单位、选择站位并共同抵挡怪物波次。上线后围绕卡组成长、关卡、赛季与外观扩展，当前属于已进入常态内容运营的轻度塔防产品。",
        "本次首次进入本项目iOS美国策略畅销榜第55名；Apple上架日期为2024年10月28日，早于90天窗口，因此属于成熟产品日榜进入，不标记为近三个月新品。Google Play同口径策略TOP60当前没有对应排名。",
        "未发现可确认的重大产品或发行转折。Apple 1.6.8版本于8月24日加入Demon Legion“Defend the Wall”、Golden Draw Board、传奇皮肤与Season Pass内容；这些节点与本次进榜相隔两周以上，不能直接认定为榜位原因。",
        "Apple商店图和描述突出双人同时守线、怪物波次、战略放置和合作胜利；1.6.8进一步用恶魔军团、城墙防守、抽奖盘、传奇皮肤和通行证展示活动层。当前素材证据以官方商店与产品官网为主，可信度为中。",
        "观察下一个2—3个工作日能否从#55脱离榜尾，并核对Demon Legion与Season Pass是否持续更新；若快速退出，只记录为成熟产品的单日付费脉冲。",
        game["storeUrl"],
        [
            {"label": "SuperMagic官方网站", "url": "https://www.supermagic.io/", "type": "company-research"},
            {"label": "Google Play同产品商品页", "url": "https://play.google.com/store/apps/details?id=com.percent.aos.cooptd&hl=en_US&gl=US", "type": "lifecycle-analysis"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="上架日期、版本说明、玩法与素材来自Apple美国区商品页；公司主体由SuperMagic官网交叉确认。",
        changeReason="首次进入项目iOS榜，独立建立商店素材、发行归属与生命周期档案；未把8月版本内容写成确定进榜原因。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2024年10月上架梳理到2026年8月Demon Legion、皮肤与赛季通行证更新。",
        evidenceNote="玩法、版本和公司信息有官方来源；公开材料未披露本次榜位变化对应的收入或投放原因。",
    )
    return game, company, analysis


def last_shelter_warz_ios_profile(row, metadata, asset_rank):
    """Build an iOS-only profile from Apple metadata without borrowing Android dates."""
    game = ios_game_from_metadata(
        row,
        metadata,
        asset_rank,
        "SLG / 4X / 城建生存 / 塔防",
        "末日丧尸；地下庇护所；房间建设；荒原探索；英雄编队；塔防；联盟战争",
    )
    game["shortDescription"] = "地下庇护所城建、荒原探索、英雄编队与联盟战争结合的末日生存SLG。"
    game["note"] = "Apple Lookup显示iOS美国区于2026-06-14上架；早于本期90天窗口起点2026-06-17，页面按常规在榜展示，内部保留pending。"
    company = {
        "en": "LAST ORIGIN STUDIO LIMITED",
        "cn": "LAST ORIGIN STUDIO LIMITED（商店发行主体；最终集团待确认）",
        "confidence": "疑似",
        "basis": "Apple美国区商品页、Apple Lookup与开发者隐私政策均确认LAST ORIGIN STUDIO LIMITED直接提供《Last Shelter: War Z》。隐私政策说明其主要经营地在中国；产品品牌、lastshelter.net域名及com.more命名空间与既有Last Shelter产品存在关联线索，但没有找到明确披露最终集团的第一方材料，因此不合并到IM30或其他集团。",
        "source": "https://www.lastshelter.net/privacy.html",
    }
    analysis = trend(
        "趋势：2026年6月以地下庇护所房间建设、荒原探索与英雄防线切入，随后开放世界地图、联盟集结和跨服对抗；关键转折：9月10日26.0902.001加入四周制联盟决斗锦标赛，首轮于9月13日匹配，本次在该节点后首次进入iOS榜尾；主力素材：地下房间扩建、幸存者分工、丧尸防守、英雄编队、荒原探索与联盟战争。",
        "iOS美国区于2026年6月14日上架，先用纵向地下庇护所扩建和幸存者房间管理建立首发入口，再把玩家导向荒原探索、英雄养成、基地防御与联盟地图竞争。当前上线约三个月，已经从首发城建验证进入联盟与跨服内容运营，但公开资料不足以确认其买量规模。",
        "本次首次进入本项目iOS美国策略畅销榜第60名；Apple上架日期早于本期90天窗口起点三天，按规则不标记为近三个月新品。Google Play当前同名产品未进入美国策略TOP60，不能把iOS榜尾信号外推成双端趋势。",
        "9月10日官方版本说明新增四周制Alliance Duel Tournament，并明确首轮9月13日开始匹配；它与本次进榜时间相邻，是可继续核对的运营节点，但没有官方收入或投放数据证明二者存在因果关系。",
        "Apple商店图与描述主要展示纵向地下房间、建筑升级、幸存者岗位、荒原小队、英雄对战和丧尸防线；近期版本说明转向联盟决斗、跨服运输和联盟活跃奖励。证据来自单一商店及产品隐私站，素材可信度为中。",
        "未来2—3个工作日观察是否脱离第60名，并在首轮联盟决斗推进后核对后续版本说明；如迅速退出，只记录为首轮赛事窗口的待验证榜尾信号。公司层面继续寻找可明确连接最终集团的第一方披露。",
        game["storeUrl"],
        [
            {"label": "Apple美国区商品页", "url": "https://apps.apple.com/us/app/last-shelter-war-z/id6760406772", "type": "primary"},
            {"label": "LAST ORIGIN隐私政策", "url": "https://www.lastshelter.net/privacy.html", "type": "company-research"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="上架日、玩法、版本和商店素材来自Apple美国区商品页与Lookup；公司直接主体由产品隐私政策确认，最终集团缺少第一方披露。",
        changeReason="首次进入项目iOS榜，按本商店资料建立独立素材、发行主体与生命周期档案；没有借用Google或旧版Last Shelter的上架日期。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2026年6月iOS上架梳理至9月联盟决斗锦标赛首轮匹配。",
        evidenceNote="版本节点与入榜时间相邻，但尚无公开收入或投放证据证明因果；最终集团归属继续标记待确认。",
    )
    return game, company, analysis


def build_google(rows, source_info):
    current = records("data/games-20260914.json", "data/enrichment-20260914.json", "data/trends-20260914.json", "packageName")
    historical = merged_records(GOOGLE_HISTORY, "packageName")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    games, companies, trends, bundle = [], {}, {}, {}
    for row in rows:
        rank, package = row["rank"], row["packageName"]
        if package == "jp.pokemon.pokemonchampions" and package not in historical:
            metadata = play_metadata(package)
            game, company, analysis = pokemon_google_profile(row, metadata, 74)
            bundle["74_icon"] = data_uri(metadata["icon"], (256, 256))
            bundle["74_store"] = data_uri(metadata["screenshot"], (720, 720))
        elif package in historical:
            game, company, analysis = map(deepcopy, current.get(package, historical[package]))
        else:
            raise RuntimeError(f"Unexpected Google entrant: {row}")
        change = delta_label(old_rank.get(package), rank)
        comp = comparison(None, rank, GOOGLE_DATE, GOOGLE_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row.get("developer", ""),
            store="googlePlay",
            storeUrl=row["storeUrl"],
            iconUrl=row["iconUrl"],
            screenshotUrl=row["screenshotUrl"],
            totalInstalls=str(row.get("downloads") or "").replace("+", " +"),
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(
            clean_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        if package == "com.readygo.dark.gp":
            analysis["summary"] = analysis["summary"].replace("黑暗丧尸压力", "暗黑压力")
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)

    enrichment = deepcopy(load("data/enrichment-20260914.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=GOOGLE_BASELINE,
        currentDate=GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/games-20260915.json", games)
    save("data/enrichment-20260915.json", enrichment)
    save("data/trends-20260915.json", trends)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    if bundle:
        save("assets/assets-13.json", bundle)
        if "assets-13.json" not in manifest["files"]:
            manifest["files"].append("assets-13.json")
    save("assets/manifest.json", manifest)
    cross_check = audit_google(rows)
    save(
        "data/history/google-play/2026-09-15.json",
        {
            "store": "google-play",
            "country": "US",
            "category": "Games > Strategy > Top Grossing",
            "date": CAPTURE,
            "dataDate": GOOGLE_DATE,
            "sourceCapturedAt": source_info["capturedAt"],
            "sourceUrl": source_info["sourceUrl"],
            "sourceEndpoint": source_info["sourceEndpoint"],
            "sourceMethod": source_info["sourceMethod"],
            "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。",
            "crossCheck": cross_check,
            "rankings": [
                {"rank": game["rank"], "packageName": game["packageName"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]}
                for game in games
            ],
        },
    )
    return games, cross_check


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260914.json", "data/ios-enrichment-20260914.json", "data/ios-trends-20260914.json", "appId")
    historical = merged_records(IOS_HISTORY, "appId")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    unknown_ids = [row["appId"] for row in rows if row["appId"] not in historical]
    metadata_by_id = lookup(unknown_ids) if unknown_ids else {}
    if set(metadata_by_id) != set(unknown_ids):
        raise RuntimeError(f"Apple Lookup did not return every new product: {unknown_ids}")
    games, companies, trends, bundle = [], {}, {}, {}
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id in historical:
            game, company, analysis = map(deepcopy, current.get(app_id, historical[app_id]))
        elif app_id == "6503702666":
            metadata = metadata_by_id[app_id]
            if str(metadata.get("releaseDate", ""))[:10] != "2024-10-28":
                raise RuntimeError(f"Coop TD iOS release date missing or changed: {metadata.get('releaseDate')}")
            game, company, analysis = coop_td_profile(row, metadata, 92)
            bundle["92_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle["92_store"] = data_uri(game["screenshotUrl"], (720, 720))
        elif app_id == "6760406772":
            metadata = metadata_by_id[app_id]
            if str(metadata.get("releaseDate", ""))[:10] != "2026-06-14":
                raise RuntimeError(f"Last Shelter: War Z iOS release date missing or changed: {metadata.get('releaseDate')}")
            game, company, analysis = last_shelter_warz_ios_profile(row, metadata, 93)
            bundle["93_icon"] = data_uri(game["iconUrl"], (256, 256))
            bundle["93_store"] = data_uri(game["screenshotUrl"], (720, 720))
        else:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")
        change = delta_label(old_rank.get(app_id), rank)
        comp = comparison(None, rank, IOS_DATE, IOS_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row["developer"],
            store="ios",
            storeUrl=f"https://apps.apple.com/us/app/id{app_id}",
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(
            clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)

    enrichment = deepcopy(load("data/ios-enrichment-20260914.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=IOS_BASELINE,
        currentDate=IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/ios-games-20260915.json", games)
    save("data/ios-enrichment-20260915.json", enrichment)
    save("data/ios-trends-20260915.json", trends)
    if bundle:
        save("assets/ios-assets-20.json", bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if bundle and "ios-assets-20.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-20.json")
    save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save(
        "data/history/ios/2026-09-15.json",
        {
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
        },
    )
    return games, source_date


def main():
    google_source = fetch_top_grossing_strategy()
    ios_url, ios_updated, ios_rows = parse_ios()
    ios_source_date = datetime.fromisoformat(ios_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    if google_source["dataDate"] != GOOGLE_DATE:
        raise RuntimeError(f"Google capture date is {google_source['dataDate']}, expected {GOOGLE_DATE}")
    if ios_source_date != IOS_DATE:
        raise RuntimeError(f"Apple source is still dated {ios_source_date}; keep the previous valid iOS snapshot")
    google, audit = build_google(google_source["rows"], google_source)
    ios, _ = build_ios(ios_rows, ios_url, ios_updated)
    print("Google", google_source["capturedAt"], [(g["rank"], g["gameName"]) for g in google if g["rank"] in (1, 25, 60)])
    print("AppBrain audit", audit)
    print("iOS", ios_updated, [(g["rank"], g["gameName"]) for g in ios if g["rank"] in (1, 25, 60)])


if __name__ == "__main__":
    main()
