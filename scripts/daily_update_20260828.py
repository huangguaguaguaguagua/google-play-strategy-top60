#!/usr/bin/env python3
"""Build the Beijing 2026-08-28 Google Play and Apple App Store snapshots."""
from copy import deepcopy
from datetime import datetime
import re
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_ios, save, trend
from daily_update_20260821 import play_metadata
from daily_update_20260825 import add_primary_source, appbrain_audit, merged_records, records
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-08-28"
GOOGLE_DATE = "2026-08-28"
GOOGLE_BASELINE = "2026-05-30"
IOS_DATE = "2026-08-28"
IOS_BASELINE = "2026-05-30"


def clean_analysis(analysis):
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


def refresh_daily_rank_path(analysis, store_label, rank, change, status, release_date):
    """Replace stale current-rank sentences while retaining the product history."""
    path = analysis["sections"].get("rankPath", "")
    path = re.sub(r"(?:本次|当前|目前)[^。]{0,240}?(?:畅销榜|TOP)[^。]*。", "", path, count=1).strip()
    path = re.sub(r"本次iOS第\d+", f"当前iOS第{rank}", path)
    path = re.sub(r"本次Google Play第\d+", f"当前Google Play第{rank}", path)
    if "增长通常经历玩法验证" in path or "当前观察重点是上行斜率" in path:
        path = analysis["sections"].get("development", path)
    if change == "NEW":
        movement = "首次进入本期榜单"
    elif change == "=":
        movement = "较前一榜单持平"
    elif change.startswith("+"):
        movement = f"较前一榜单上升{change[1:]}位"
    else:
        movement = f"较前一榜单下降{change.lstrip('-')}位"
    prefix = f"本次位于{store_label}美国策略畅销榜第{rank}名（{movement}）。"
    if status == "new":
        prefix += f"按{store_label}商品页上架日期{release_date}计算，属于近三个月新上榜。"
    analysis["sections"]["rankPath"] = prefix + path
    return analysis


def gfl2_profile(asset_rank):
    game = {
        "assetRank": asset_rank,
        "genre": "战棋 / 策略RPG / 角色养成",
        "keywords": "少女前线；战术人形；3D掩体；高低差；枪械改装；宿舍互动；地格衍变",
    }
    company = {
        "en": "Sunborn Network Technology / MICA Team / Darkwinter Software",
        "cn": "上海散爆网络（MICA Team研发；暗冬网络海外运营）",
        "confidence": "已确认",
        "basis": "Apple店铺主体为Sunborn Network Technology，Google Play由Darkwinter Software发行；产品官方隐私声明将Darkwinter与上海散爆列为共同数据控制方。",
        "source": "https://gf2exilium.sunborngame.com/privacy_notice",
    }
    analysis = trend(
        "趋势：2024年全球上线以《少女前线》IP、三维掩体战棋和高规格人形互动承接二次元策略用户，当前主要由角色、剧情与系统扩展支撑；关键转折：从回合制掩体战斗和枪械改装扩展到宿舍、契约及地格衍变，8月27日Tile Transformation更新是本轮可核验节点；主力素材：3D战术人形、掩体与高低差、技能演出、枪械改装、宿舍互动和限定角色。",
        "中国版在多轮测试后于2023年上线，北美等区域于2024年末推出全球版。产品用可破坏掩体、地形和角色技能建立战棋差异，同时以武器配件、宿舍互动、契约及高规格角色演出维持二次元养成层。",
        "本次同时进入Google Play美国策略畅销榜第35名和iOS第21名；两端上架均早于90天，按成熟产品版本期进入处理。双端同日进入降低了单一平台噪声解释，但仍不能把一天排名直接归因于版本。",
        "长期结构从纯回合制掩体战斗扩展到宿舍与契约互动；官方8月26日维护后于8月27日加入Tile Transformation地格衍变系统，是当前可确认的系统级节点。",
        "战术人形立绘与3D技能演出、掩体和高低差选择、枪械360度展示与配件改装、宿舍近距离互动、契约角色内容，以及新地格效果组合。",
        "观察未来3个工作日双端能否继续留在TOP60，并区分新系统体验、角色卡池和版本剧情对Google与iOS付费峰值的不同承接。",
        "https://gf2exilium.sunborngame.com/",
        [
            {"label": "GIRLS' FRONTLINE 2官方站", "url": "https://gf2exilium.sunborngame.com/", "type": "primary"},
            {"label": "官方英文账号8月更新", "url": "https://x.com/GFL2EXILIUM_EN", "type": "lifecycle-analysis"},
            {"label": "Sunborn与Darkwinter主体说明", "url": "https://gf2exilium.sunborngame.com/privacy_notice", "type": "company-research"},
        ],
    )
    return game, company, analysis


def tft_profile(asset_rank):
    game = {
        "assetRank": asset_rank,
        "genre": "自走棋 / 卡牌构筑 / 实时PvP",
        "keywords": "League of Legends；八人自走棋；共享卡池；阵容羁绊；装备；Little Legends；Enchanted Wilds；Wisps",
    }
    company = {
        "en": "Riot Games / Tencent",
        "cn": "拳头游戏（腾讯旗下）",
        "confidence": "已确认",
        "basis": "Apple店铺主体及产品官网均为Riot Games；Riot官方管理层页面确认2015年向Tencent完成股权出售。",
        "source": "https://www.riotgames.com/en/who-we-are/riot-games-leadership/dylan-jadeja",
    }
    analysis = trend(
        "趋势：2020年移动版以《英雄联盟》英雄共享卡池和八人自走棋承接PC用户，长期由赛季换盘、阵容研究、通行证及小小英雄外观维持；关键转折：每套Set重置主题和机制，18.1于8月26日上线Enchanted Wilds并迁移Unreal引擎，构成本轮回榜节点；主力素材：羁绊成型、临场转阵、三星英雄、Little Legends、Wisps和新森林棋盘。",
        "2020年移动版与PC跨平台上线，用共享卡池、站位、装备和经济运营把传统卡牌构筑压缩为八人自动战斗。此后以整套Set轮换重置英雄、羁绊和核心机制，排名与社交内容围绕版本解题和赛季爬分展开。",
        "本次从榜外进入iOS美国策略畅销榜第50名；产品上架已超过90天。18.1版本与回榜时间重合，但单日数据只记为待验证的版本付费信号。",
        "从早期固定棋盘和羁绊构筑转向每套Set独立世界观及机制；18.1 Enchanted Wilds在8月26日上线Wisps、森林阵营与新外观，同时由Hextech迁移到Unreal，8月27日已追加内存泄漏和终结动画音效修复。",
        "共享卡池抢牌、最后一轮转阵、三星英雄爆发、羁绊图标快速成型、Little Legends和终结特效、Enchanted Wilds森林主题、Wisps辅助与新赛季爬分。",
        "观察首周能否从#50脱离榜尾，并结合18.1后续平衡补丁判断当前收入主要来自新Set回流、通行证还是Little Legends外观。",
        "https://apps.apple.com/us/app/id1480616748",
        [
            {"label": "TFT 18.1官方补丁说明", "url": "https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1/", "type": "lifecycle-analysis"},
            {"label": "Riot Games产品页", "url": "https://www.riotgames.com/en", "type": "company-research"},
            {"label": "Riot管理层股权出售说明", "url": "https://www.riotgames.com/en/who-we-are/riot-games-leadership/dylan-jadeja", "type": "company-research"},
        ],
    )
    return game, company, analysis


def last_light_profile(asset_rank):
    game = {
        "assetRank": asset_rank,
        "genre": "SLG / 避难所经营 / 生存管理",
        "keywords": "丧尸末世；避难所；幸存者分工；士气；资源站；废墟探索；联盟；领地扩张",
    }
    company = {
        "en": "BINGCHUAN NETWORK (HONG KONG) COMPANY LIMITED / Shenzhen Bingchuan Network",
        "cn": "冰川网络（香港发行主体；深圳冰川网络全资子公司）",
        "confidence": "已确认",
        "basis": "Apple店铺主体为Hong Kong Bingchuan Network；冰川网络公开报告将BINGCHUAN NETWORK (HONG KONG) COMPANY LIMITED列为全资子公司。",
        "source": "https://static.cninfo.com.cn/finalpage/2025-08-29/1224602690.PDF",
    }
    analysis = trend(
        "趋势：2026年2月上线后以丧尸围城、避难所建造和幸存者分工切入，目前仍处上线首年的商业化验证；关键转折：未发现可确认的重大转折，现有结构仍由资源站、防线、士气决策、废墟探索和联盟扩张逐层展开；主力素材：破败避难所、丧尸潮、防墙升级、幸存者岗位、废墟搜刮与联盟领地。",
        "产品于2026年2月在iOS上线，以避难所墙体和资源站建设建立安全感，再通过幸存者技能、士气及生死决策增加管理压力，外层则用废墟远征、领地回收和联盟战承接4X循环。",
        "本次从榜外进入iOS美国策略畅销榜第56名；上架已超过90天，因此属于日榜进入而非近三个月新上榜。当前靠近榜尾，只能记为待验证信号。",
        "未发现可确认的重大系统或发行转折。7月24日1.0.18为最近可核验版本时间，商店结构仍围绕基地防守、社区管理、远征和联盟统治，没有证据支持把此次进榜写成特定活动因果。",
        "丧尸撞击防线、破败据点逐级修复、食物与能源短缺、幸存者岗位分配、士气选择、废墟搜刮遭遇和联盟共同防守。当前公开证据主要来自单一商店，素材判断保持中等可信度。",
        "观察未来2—3个工作日能否守住TOP60，并继续核验是否存在未公开的大区开服、买量扩张或版本活动；若迅速掉榜，优先按榜尾投放脉冲处理。",
        "https://apps.apple.com/us/app/id6754545818",
        [
            {"label": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id6754545818", "type": "primary"},
            {"label": "冰川网络2025年半年度报告", "url": "https://static.cninfo.com.cn/finalpage/2025-08-29/1224602690.PDF", "type": "company-research"},
        ],
    )
    return game, company, analysis


def build_google(rows, source_info):
    historical = merged_records([
        ("data/games-20260827.json", "data/enrichment-20260827.json", "data/trends-20260827.json"),
        ("data/games-20260826.json", "data/enrichment-20260826.json", "data/trends-20260826.json"),
        ("data/games-20260825.json", "data/enrichment-20260825.json", "data/trends-20260825.json"),
        ("data/games-20260824.json", "data/enrichment-20260824.json", "data/trends-20260824.json"),
        ("data/games-20260821.json", "data/enrichment-20260821.json", "data/trends-20260821.json"),
        ("data/games-20260820.json", "data/enrichment-20260820.json", "data/trends-20260820.json"),
        ("data/games-20260819d.json", "data/enrichment-20260819d.json", "data/trends-20260819d.json"),
    ], "packageName")
    current = records("data/games-20260827.json", "data/enrichment-20260827.json", "data/trends-20260827.json", "packageName")
    ios_current = records("data/ios-games-20260827.json", "data/ios-enrichment-20260827.json", "data/ios-trends-20260827.json", "appId")
    old_rank = {package: value[0]["rank"] for package, value in current.items()}
    games, companies, trends, bundle = [], {}, {}, {}
    next_asset = 69
    for row in rows:
        rank, package = row["rank"], row["packageName"]
        if package in current:
            game, company, analysis = map(deepcopy, current[package])
        elif package in historical:
            game, company, analysis = map(deepcopy, historical[package])
        else:
            metadata = play_metadata(package)
            if package == "com.Sunborn.SnqxExilium.Glo":
                game, company, analysis = gfl2_profile(next_asset)
            elif package == "com.gamespark.topking.gp":
                game, company, analysis = map(deepcopy, ios_current["6767834940"])
                game.pop("appId", None)
                game["assetRank"] = next_asset
            else:
                raise RuntimeError(f"Unexpected Google entrant: {row}")
            game.update(
                packageName=package, assetRank=next_asset, description=metadata.get("description", ""),
                shortDescription=metadata.get("description", "").replace("\n", " ")[:220],
                releaseDate=metadata.get("released", ""), releaseDateIso=metadata.get("released", ""),
                updatedDate=metadata.get("updated", ""), iconUrl=row["iconUrl"], screenshotUrl=row["screenshotUrl"],
            )
            bundle[f"{next_asset}_icon"] = data_uri(row["iconUrl"], (256, 256))
            bundle[f"{next_asset}_store"] = data_uri(row["screenshotUrl"], (720, 720))
            add_primary_source(analysis, "Google Play美国区商品页", row["storeUrl"])
            next_asset += 1
        change = delta_label(old_rank.get(package), rank)
        comp = comparison(None, rank, GOOGLE_DATE, GOOGLE_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank, gameName=row["gameName"], developer=row.get("developer", ""), store="googlePlay",
            storeUrl=row["storeUrl"], iconUrl=row["iconUrl"], screenshotUrl=row["screenshotUrl"],
            totalInstalls=str(row.get("downloads") or "").replace("+", " +"), dailyChange=change,
            comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(clean_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", ""))
        if package == "com.Sunborn.SnqxExilium.Glo":
            analysis["sections"]["rankPath"] += "iOS同日以第21名进入；双端共同进入减少了单平台噪声，但仍需连续数据确认版本峰值能否沉淀。"
        elif package == "com.gamespark.topking.gp":
            analysis["sections"]["rankPath"] = (
                "本次位于Google Play美国策略畅销榜第60名（首次进入本期榜单）。"
                "按Google Play商品页上架日期2026-06-25计算，属于近三个月新上榜；iOS同日位于第51名，"
                "两端仍处首轮商业化验证且Google为压线位置。"
            )
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)
    enrichment = deepcopy(load("data/enrichment-20260827.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/games-20260828.json", games)
    save("data/enrichment-20260828.json", enrichment)
    save("data/trends-20260828.json", trends)
    save("assets/assets-09.json", bundle)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    if "assets-09.json" not in manifest["files"]:
        manifest["files"].append("assets-09.json")
    save("assets/manifest.json", manifest)
    cross_check = appbrain_audit(rows)
    save("data/history/google-play/2026-08-28.json", {
        "store": "google-play", "country": "US", "category": "Games > Strategy > Top Grossing",
        "date": CAPTURE, "dataDate": GOOGLE_DATE, "sourceCapturedAt": source_info["capturedAt"],
        "sourceUrl": source_info["sourceUrl"], "sourceEndpoint": source_info["sourceEndpoint"],
        "sourceMethod": source_info["sourceMethod"],
        "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。",
        "crossCheck": cross_check,
        "rankings": [{"rank": game["rank"], "packageName": game["packageName"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]} for game in games],
    })
    return games, cross_check


def build_ios(rows, source_url, source_updated):
    current = records("data/ios-games-20260827.json", "data/ios-enrichment-20260827.json", "data/ios-trends-20260827.json", "appId")
    historical = merged_records([
        ("data/ios-games-20260827.json", "data/ios-enrichment-20260827.json", "data/ios-trends-20260827.json"),
        ("data/ios-games-20260826.json", "data/ios-enrichment-20260826.json", "data/ios-trends-20260826.json"),
        ("data/ios-games-20260825.json", "data/ios-enrichment-20260825.json", "data/ios-trends-20260825.json"),
        ("data/ios-games-20260824.json", "data/ios-enrichment-20260824.json", "data/ios-trends-20260824.json"),
        ("data/ios-games-20260821.json", "data/ios-enrichment-20260821.json", "data/ios-trends-20260821.json"),
        ("data/ios-games-20260820.json", "data/ios-enrichment-20260820.json", "data/ios-trends-20260820.json"),
        ("data/ios-games-20260819.json", "data/ios-enrichment-20260819.json", "data/ios-trends-20260819.json"),
    ], "appId")
    old_rank = {app_id: value[0]["rank"] for app_id, value in current.items()}
    entrant_ids = [row["appId"] for row in rows if row["appId"] not in current]
    metadata = lookup(entrant_ids)
    if set(metadata) != set(entrant_ids):
        raise RuntimeError(f"Apple Lookup did not return every entrant: {entrant_ids}")
    games, companies, trends, bundle = [], {}, {}, {}
    next_asset = 81
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        else:
            meta = metadata[app_id]
            if app_id in historical:
                game, company, analysis = map(deepcopy, historical[app_id])
            elif app_id == "6502505286":
                game, company, analysis = gfl2_profile(next_asset)
            elif app_id == "1480616748":
                game, company, analysis = tft_profile(next_asset)
            elif app_id == "6754545818":
                game, company, analysis = last_light_profile(next_asset)
            else:
                raise RuntimeError(f"Unexpected iOS entrant: {row}")
            icon = meta.get("artworkUrl512") or meta.get("artworkUrl100")
            screenshot = (meta.get("screenshotUrls") or meta.get("ipadScreenshotUrls") or [icon])[0]
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
            rank=rank, gameName=row["gameName"], developer=row["developer"], store="ios",
            storeUrl=f"https://apps.apple.com/us/app/id{app_id}", dailyChange=change, comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", ""))
        if app_id == "6502505286":
            analysis["sections"]["rankPath"] += "Google Play同日以第35名进入；双端共同进入减少了单平台噪声，但仍需连续数据确认版本峰值能否沉淀。"
        elif app_id == "6767834940":
            analysis["sections"]["rankPath"] = (
                "本次位于iOS美国策略畅销榜第51名（较前一榜单下降1位）。"
                "按iOS商品页上架日期2026-05-31计算，属于近三个月新上榜；Google Play同日首次进入第60名，"
                "两端仍处首轮商业化验证。"
            )
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)
    enrichment = deepcopy(load("data/ios-enrichment-20260827.json"))
    enrichment["productCompaniesByRank"] = companies
    save("data/ios-games-20260828.json", games)
    save("data/ios-enrichment-20260828.json", enrichment)
    save("data/ios-trends-20260828.json", trends)
    save("assets/ios-assets-13.json", bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if "ios-assets-13.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-13.json")
    save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    save("data/history/ios/2026-08-28.json", {
        "store": "ios", "country": "US", "device": "iPhone", "category": "Games > Strategy > Top Grossing",
        "date": source_date, "dataDate": source_date, "sourceUpdated": source_updated, "sourceUrl": source_url,
        "rankings": [{"rank": game["rank"], "appId": game["appId"], "gameName": game["gameName"], "sourceUrl": game["storeUrl"]} for game in games],
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
    google, audit = build_google(google_source["rows"], google_source)
    ios, _ = build_ios(ios_rows, ios_url, ios_updated)
    print("Google", google_source["capturedAt"], [(g["rank"], g["gameName"]) for g in google if g["rank"] in (1, 25, 60)])
    print("AppBrain audit", audit)
    print("iOS", ios_updated, [(g["rank"], g["gameName"]) for g in ios if g["rank"] in (1, 25, 60)])


if __name__ == "__main__":
    main()
