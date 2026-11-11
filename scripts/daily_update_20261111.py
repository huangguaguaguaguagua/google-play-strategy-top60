#!/usr/bin/env python3
"""Build the Beijing 2026-11-11 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
import unicodedata
from zoneinfo import ZoneInfo

import daily_update_20261110 as prior
from daily_update_20261028 import prepare_analysis
from daily_update_20261026 import enforce_required_product_language
from daily_update_20260820 import comparison, delta_label, lookup


updater = prior.updater
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-11-11"
updater.STAMP = "20261111"
updater.PREVIOUS_STAMP = "20261110"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-08-13"
updater.GOOGLE_DATES = ("20261110",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261110",) + updater.IOS_DATES


def build_google_today(rows, source):
    current = updater.records("data/games-20261110.json", "data/enrichment-20261110.json", "data/trends-20261110.json", "packageName")
    historical = updater.merged_records(updater.history_specs("", updater.GOOGLE_DATES), "packageName")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    games, companies, analyses = [], {}, {}
    for row in rows:
        package, rank = row["packageName"], row["rank"]
        source_record = current.get(package) or historical.get(package)
        if not source_record:
            raise RuntimeError(f"Unexpected Google entrant: {row}")
        game, company, analysis = map(deepcopy, source_record)
        change = delta_label(old_rank.get(package), rank)
        comp = comparison(None, rank, updater.GOOGLE_DATE, updater.GOOGLE_BASELINE, True, game.get("releaseDateIso"))
        game.update(rank=rank, gameName=row["gameName"], developer=row.get("developer", game.get("developer", "")),
                    store="googlePlay", storeUrl=row["storeUrl"], iconUrl=row["iconUrl"], rankIconUrl=row["iconUrl"],
                    screenshotUrl=row["screenshotUrl"], totalInstalls=str(row.get("downloads") or game.get("totalInstalls") or "").replace("+", " +"),
                    dailyChange=change, comparison90d=comp)
        analysis = updater.refresh_daily_rank_path(prepare_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", ""))
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game); companies[str(rank)] = company; analyses[str(rank)] = analysis
    enrichment = deepcopy(updater.load("data/enrichment-20261110.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(baselineDate=updater.GOOGLE_BASELINE, currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。")
    updater.save("data/games-20261111.json", games); updater.save("data/enrichment-20261111.json", enrichment); updater.save("data/trends-20261111.json", analyses)
    manifest = updater.load("assets/manifest.json"); manifest["date"] = updater.GOOGLE_DATE; updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-11-11.json", {
        "store":"google-play","country":"US","category":"Games > Strategy > Top Grossing","date":updater.GOOGLE_DATE,"dataDate":updater.GOOGLE_DATE,
        "sourceCapturedAt":source["capturedAt"],"sourceUrl":source["sourceUrl"],"sourceEndpoint":source["sourceEndpoint"],"sourceMethod":source["sourceMethod"],
        "freshnessNote":"Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。","crossCheck":audit,
        "rankings":[{"rank":g["rank"],"packageName":g["packageName"],"gameName":g["gameName"],"sourceUrl":g["storeUrl"]} for g in games]})
    return games, audit


def build_ios_today(rows, source_url, source_updated):
    current = updater.records("data/ios-games-20261110.json", "data/ios-enrichment-20261110.json", "data/ios-trends-20261110.json", "appId")
    historical = updater.merged_records(updater.history_specs("ios-", updater.IOS_DATES), "appId")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    games, companies, analyses = [], {}, {}
    for row in rows:
        app_id, rank = row["appId"], row["rank"]
        source_record = current.get(app_id) or historical.get(app_id)
        if not source_record and app_id == "1571873795":
            source_record = (
                {
                    "rank": rank, "appId": app_id, "packageName": app_id,
                    "gameName": row["gameName"], "developer": row["developer"],
                    "totalInstalls": "", "recentInstalls30d": "", "dailyChange": "NEW",
                    "storeUrl": f"https://apps.apple.com/us/app/id{app_id}",
                    "iconUrl": "https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/ff/b0/84/ffb084e9-ec77-c8cb-b98a-4457835275a7/AppIcon-0-0-1x_U007emarketing-0-8-0-85-220.png/512x512bb.jpg",
                    "rankIconUrl": "https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/ff/b0/84/ffb084e9-ec77-c8cb-b98a-4457835275a7/AppIcon-0-0-1x_U007emarketing-0-8-0-85-220.png/512x512bb.jpg",
                    "screenshotUrl": "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource221/v4/ea/92/af/ea92af08-00d5-9c6b-7200-57e010220126/BA__Ub9c8_Ucf13_Uc2a4_Ud06c_Ub9b0_Uc0f701_EN_2208x1242.png/406x228bb.png",
                    "shortDescription": "Anime tactical RPG set in Kivotos, combining squad formation, character collection, relationship stories and event-driven live operations.",
                    "description": "在学园都市Kivotos编成学生小队，以角色技能、队伍协同和战术战斗推进剧情，并通过招募、关系故事与限时活动进行长线运营。",
                    "releaseDate": "2021-11-07", "releaseDateIso": "2021-11-07", "updatedDate": "2026-11-10",
                    "genre": "二次元战术RPG", "keywords": "学园；小队编成；角色收集；战术战斗；剧情；限时招募",
                    "note": "", "assetRank": 107, "store": "ios",
                },
                {
                    "en": "NEXON Korea Corporation / NEXON Company",
                    "cn": "NEXON（韩国）",
                    "confidence": "已确认",
                    "basis": "Apple Lookup显示店铺发行名NEXON Company、法律销售主体NEXON Korea Corporation；官方站点同属NEXON产品体系。",
                    "source": f"https://apps.apple.com/us/app/id{app_id}",
                },
                {
                    "summary": "趋势：2021年全球上线后以学园角色、剧情与小队战术战斗建立二次元长线运营；关键转折：2026年11月10日开启200次免费招募、限定选择券与新主线，本期回榜与活动窗口相邻；主力素材：学生角色立绘、编队战斗、剧情演出与免费招募福利。",
                    "sections": {
                        "development": "全球版上线后围绕Kivotos学园群像、角色收集、关系故事与小队战术战斗持续更新，成熟期由新角色招募、主线章节和周期战斗活动共同支撑。",
                        "rankPath": "本次回到iOS美国策略畅销榜；精确名次与90天状态将在本次快照中写入。",
                        "turningPoints": "本期可核验节点是11月10日版本同步开启200次免费招募、Fest学生选择券、泳装角色Pick-Up和新主线；回榜与活动同窗，但不据此断言单一因果。",
                        "creative": "当前商品页以学生角色群像、3D小队战斗、剧情演出与关系互动为主；活动公告强化免费招募、限定角色和选择券。",
                        "watch": "观察免费招募与Fest活动结束后能否连续留在TOP60；若下一有效快照迅速回落，则更接近活动峰值信号。",
                    },
                    "sourceAudit": {
                        "reviewedAt": "2026-11-11", "status": "已核验", "confidence": "中",
                        "basis": "核心玩法、发行主体、版本内容与素材均来自Apple商品页和Lookup。",
                        "changeReason": "iOS新回榜产品首次建档；活动与榜位仅写为时间相邻。",
                        "sources": [{"label":"Apple App Store美国区商品页","url":f"https://apps.apple.com/us/app/id{app_id}","type":"primary"}],
                    },
                    "lifecycleAudit": {
                        "reviewedAt": "2026-11-11", "status": "已复核", "confidence": "中",
                        "scope": "从2021年全球上架到当前Fest活动窗口。",
                        "evidenceNote": "以Apple商品页版本说明、描述与商店素材归纳；未将同日活动与回榜写成确定因果。",
                        "sources": [{"label":"Apple App Store美国区商品页","url":f"https://apps.apple.com/us/app/id{app_id}","type":"primary"}],
                    },
                },
            )
        if not source_record and app_id == "6761043541":
            source_record = (
                {
                    "rank": rank, "appId": app_id, "packageName": app_id,
                    "gameName": row["gameName"], "developer": row["developer"],
                    "totalInstalls": "", "recentInstalls30d": "", "dailyChange": "NEW",
                    "storeUrl": f"https://apps.apple.com/us/app/id{app_id}",
                    "iconUrl": "https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/d3/c6/eb/d3c6eb44-2b7b-d605-6564-b2bf5bebe70d/AppIcon-0-0-1x_U007emarketing-0-8-0-85-220.png/512x512bb.jpg",
                    "rankIconUrl": "https://is1-ssl.mzstatic.com/image/thumb/Purple211/v4/d3/c6/eb/d3c6eb44-2b7b-d605-6564-b2bf5bebe70d/AppIcon-0-0-1x_U007emarketing-0-8-0-85-220.png/512x512bb.jpg",
                    "screenshotUrl": "https://is1-ssl.mzstatic.com/image/thumb/PurpleSource221/v4/a0/4f/3b/a04f3b00-2bd4-3456-37cf-c4456d12e03d/1.jpg/320x480bb.jpg",
                    "shortDescription": "Post-apocalyptic ocean survival strategy game about floating shelters, resource production, fleet exploration and alliance warfare.",
                    "description": "海平面淹没世界后，玩家建设漂浮庇护所、组织资源生产与科技发展，派遣舰队探索海域，并通过联盟争夺海上要塞。",
                    "releaseDate": "2026-09-19", "releaseDateIso": "2026-09-19", "updatedDate": "2026-11-04",
                    "genre": "海洋生存SLG", "keywords": "末日海洋；漂浮庇护所；舰队探索；联盟；要塞争夺；资源经营",
                    "note": "", "assetRank": 108, "store": "ios",
                },
                {
                    "en": "YG Technology FZ-LLC",
                    "cn": "YG Technology FZ-LLC（最终集团待核验）",
                    "confidence": "待核验",
                    "basis": "Apple Lookup确认店铺发行名与法律销售主体均为YG Technology FZ-LLC；暂未找到足够的一手证据继续穿透最终集团。",
                    "source": f"https://apps.apple.com/us/app/id{app_id}",
                },
                {
                    "summary": "趋势：2026年9月上线后仍处首发验证，以海面漂流庇护所和资源求生切入，再承接舰队探索、联盟与海域争夺；关键转折：尚未发现可确认的重大转折，本期首次进入iOS TOP60；主力素材：末日海洋、漂浮基地扩建、舰队出航与巨型海怪危机。",
                    "sections": {
                        "development": "上线时间不足两个月，当前从漂浮庇护所建设、资源生产和灾害求生切入，后续系统延展至舰队探索、科技、联盟要塞与全球海域争夺；仍处首发验证。",
                        "rankPath": "本次首次进入iOS美国策略畅销榜；精确名次与90天新品状态将在本次快照中写入。",
                        "turningPoints": "未发现可确认的重大转折；11月4日2.7.0版本主要为VIP点数、行军皮肤、雷达挑战与社交体验优化。",
                        "creative": "商品页以被海水淹没的世界、漂浮庇护所扩建、舰队探索、海怪与海盗危机为主要视觉；联盟争夺承担中后期SLG表达。",
                        "watch": "观察首次进入#60后能否连续留榜，以及漂浮基地求生素材能否有效承接联盟和海域争夺的中重度循环。",
                    },
                    "sourceAudit": {
                        "reviewedAt": "2026-11-11", "status": "已核验", "confidence": "中",
                        "basis": "核心玩法、上架日期、版本与素材来自Apple商品页和Lookup；最终公司归属证据不足。",
                        "changeReason": "近90天上架的新进榜产品首次建档。",
                        "sources": [{"label":"Apple App Store美国区商品页","url":f"https://apps.apple.com/us/app/id{app_id}","type":"primary"}],
                    },
                    "lifecycleAudit": {
                        "reviewedAt": "2026-11-11", "status": "已复核", "confidence": "中",
                        "scope": "从2026年9月上架至首次进入iOS TOP60。",
                        "evidenceNote": "仅按商店公开资料归纳首发期玩法与素材，未推演未来增长。",
                        "sources": [{"label":"Apple App Store美国区商品页","url":f"https://apps.apple.com/us/app/id{app_id}","type":"primary"}],
                    },
                },
            )
        if not source_record:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")
        game, company, analysis = map(deepcopy, source_record)
        change = delta_label(old_rank.get(app_id), rank)
        comp = comparison(None, rank, updater.IOS_DATE, updater.IOS_BASELINE, True, game.get("releaseDateIso"))
        game.update(rank=rank, gameName=row["gameName"], developer=row["developer"], store="ios",
                    storeUrl=f"https://apps.apple.com/us/app/id{app_id}", totalInstalls="", recentInstalls30d="", dailyChange=change, comparison90d=comp)
        analysis = updater.refresh_daily_rank_path(prepare_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", ""))
        analysis = enforce_required_product_language(game["gameName"], analysis)
        games.append(game); companies[str(rank)] = company; analyses[str(rank)] = analysis
    enrichment = deepcopy(updater.load("data/ios-enrichment-20261110.json")); enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(baselineDate=updater.IOS_BASELINE, currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。")
    updater.save("data/ios-games-20261111.json", games); updater.save("data/ios-enrichment-20261111.json", enrichment); updater.save("data/ios-trends-20261111.json", analyses)
    manifest = updater.load("assets/ios-manifest.json"); manifest["date"] = updater.IOS_DATE; updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-11-11.json", {"store":"ios","country":"US","device":"iPhone","category":"Games > Strategy > Top Grossing",
        "date":source_date,"dataDate":source_date,"sourceUpdated":source_updated,"sourceUrl":source_url,
        "rankings":[{"rank":g["rank"],"appId":g["appId"],"gameName":g["gameName"],"sourceUrl":g["storeUrl"]} for g in games]})
    return games, source_date


updater.build_google = build_google_today
updater.build_ios = build_ios_today


def refresh_ios_metadata():
    path = "data/ios-games-20261111.json"; games = updater.load(path)
    meta = lookup([str(g["appId"]) for g in games])
    if len(meta) != 60: raise RuntimeError(f"Apple Lookup returned {len(meta)} of 60 products")
    for game in games:
        item = meta[str(game["appId"])]; icon = item.get("artworkUrl512") or item.get("artworkUrl100"); shots = item.get("screenshotUrls") or item.get("ipadScreenshotUrls") or []
        release = (item.get("releaseDate") or "")[:10]
        if not icon or not release: raise RuntimeError(f"Incomplete Apple metadata: {game['gameName']}")
        game.update(developer=item.get("artistName") or game.get("developer", ""), iconUrl=icon, rankIconUrl=icon,
                    screenshotUrl=shots[0] if shots else game.get("screenshotUrl") or icon, releaseDate=release, releaseDateIso=release,
                    updatedDate=(item.get("currentVersionReleaseDate") or "")[:10])
    updater.save(path, games)


def refresh_rank_paths():
    for gp,tp,store,basis in (("data/games-20261111.json","data/trends-20261111.json","Google Play","Google Play美国区商品页released日期"),
                              ("data/ios-games-20261111.json","data/ios-trends-20261111.json","iOS","Apple Lookup releaseDate")):
        games=updater.load(gp); trends=updater.load(tp)
        for game in games:
            ch=game["dailyChange"]
            movement = "较2026-11-10前一有效快照回榜" if ch=="NEW" else ("较2026-11-10前一有效快照持平" if ch=="=" else f"较2026-11-10前一有效快照{'上升' if ch.startswith('+') else '下降'}{ch[1:]}位")
            st=game["comparison90d"]
            if st["status"]=="new": status=f"按{basis}{game['releaseDateIso']}计算，位于{st['baselineDate']}至{st['currentDate']}的90天窗口内，归类为近三个月新上榜。"
            elif st["status"]=="surge": status=f"精确90天基准名次为#{st['baselineRank']}，至当前提升{st['delta']}位，归类为近三个月飙升。"
            else: status=f"上架早于90天窗口；因缺少{st['baselineDate']}同口径完整TOP60基准，不判断近三个月飙升，页面按常规在榜展示。"
            trends[str(game["rank"])]["sections"]["rankPath"] = f"本次位于{store}美国策略畅销榜第{game['rank']}名（{movement}）。{status}"
        updater.save(tp,trends)


def normalize_summaries():
    aliases={"mobile legends bang bang us":"mobile legends bang bang.us","kingdom guard tower defense td":"kingdom guard tower defense","rise of castles fire and war":"rise of castles ice and fire"}
    def key(name):
        s=unicodedata.normalize("NFKD",str(name)).encode("ascii","ignore").decode().lower(); s=re.sub(r"[^a-z0-9.]+"," ",s).strip(); return aliases.get(s,s)
    gg=updater.load("data/games-20261111.json"); ii=updater.load("data/ios-games-20261111.json")
    maps={"Google":{key(g["gameName"]):g for g in gg},"iOS":{key(g["gameName"]):g for g in ii}}
    for gp,tp,own,other in (("data/games-20261111.json","data/trends-20261111.json","Google","iOS"),("data/ios-games-20261111.json","data/ios-trends-20261111.json","iOS","Google")):
        games=updater.load(gp); trends=updater.load(tp)
        for g in games:
            s=trends[str(g["rank"])]["summary"]; ch=g["dailyChange"]
            own_phrase=f"本期{own}回榜#{g['rank']}" if ch=="NEW" else (f"本期{own}持平于#{g['rank']}" if ch=="=" else f"本期{own}{'上升' if ch.startswith('+') else '下跌'}{ch[1:]}位至#{g['rank']}")
            s=re.sub(rf"本期(?:首次进入项目)?{own}(?:榜)?(?:回榜|回到|持平于|位于|上升|下跌|升|跌)?\s*#?\d+(?:位至#\d+)?",own_phrase,s)
            counterpart=maps[other].get(key(g["gameName"])); other_phrase=f"{other}位于#{counterpart['rank']}" if counterpart else f"{other}未入榜"
            s=re.sub(rf"{other}(?:(?:同产品|当前|同期|反向)?(?:上升|下跌)\d+位至|(?:同产品|当前|同期|反向)?(?:升|跌)至|(?:同产品|当前|同期|反向)?(?:回榜|位于|仍高居|仍在|榜)?\s*)#\d+",other_phrase,s)
            s=re.sub(rf"{other}(?:策略榜)?未入榜",other_phrase,s)
            trends[str(g["rank"])]["summary"]=s
        updater.save(tp,trends)


if __name__ == "__main__":
    updater.main()
    refresh_ios_metadata()
    refresh_rank_paths()
    normalize_summaries()
