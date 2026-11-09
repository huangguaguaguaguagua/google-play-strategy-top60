#!/usr/bin/env python3
"""Build the Beijing 2026-11-09 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
import re
import unicodedata
from zoneinfo import ZoneInfo

import daily_update_20261106 as prior
from daily_update_20261028 import prepare_analysis
from daily_update_20261026 import enforce_required_product_language
from daily_update_20260820 import comparison, delta_label, lookup


updater = prior.updater
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-11-09"
updater.STAMP = "20261109"
updater.PREVIOUS_STAMP = "20261106"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-08-11"
updater.GOOGLE_DATES = ("20261106",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261106",) + updater.IOS_DATES


def build_google_today(rows, source):
    current = updater.records("data/games-20261106.json", "data/enrichment-20261106.json", "data/trends-20261106.json", "packageName")
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
    enrichment = deepcopy(updater.load("data/enrichment-20261106.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(baselineDate=updater.GOOGLE_BASELINE, currentDate=updater.GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。")
    updater.save("data/games-20261109.json", games); updater.save("data/enrichment-20261109.json", enrichment); updater.save("data/trends-20261109.json", analyses)
    manifest = updater.load("assets/manifest.json"); manifest["date"] = updater.GOOGLE_DATE; updater.save("assets/manifest.json", manifest)
    audit = updater.audit_google(rows)
    updater.save("data/history/google-play/2026-11-09.json", {
        "store":"google-play","country":"US","category":"Games > Strategy > Top Grossing","date":updater.GOOGLE_DATE,"dataDate":updater.GOOGLE_DATE,
        "sourceCapturedAt":source["capturedAt"],"sourceUrl":source["sourceUrl"],"sourceEndpoint":source["sourceEndpoint"],"sourceMethod":source["sourceMethod"],
        "freshnessNote":"Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。","crossCheck":audit,
        "rankings":[{"rank":g["rank"],"packageName":g["packageName"],"gameName":g["gameName"],"sourceUrl":g["storeUrl"]} for g in games]})
    return games, audit


def build_ios_today(rows, source_url, source_updated):
    current = updater.records("data/ios-games-20261106.json", "data/ios-enrichment-20261106.json", "data/ios-trends-20261106.json", "appId")
    historical = updater.merged_records(updater.history_specs("ios-", updater.IOS_DATES), "appId")
    old_rank = {key: value[0]["rank"] for key, value in current.items()}
    games, companies, analyses = [], {}, {}
    for row in rows:
        app_id, rank = row["appId"], row["rank"]
        source_record = current.get(app_id) or historical.get(app_id)
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
    enrichment = deepcopy(updater.load("data/ios-enrichment-20261106.json")); enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(baselineDate=updater.IOS_BASELINE, currentDate=updater.IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。")
    updater.save("data/ios-games-20261109.json", games); updater.save("data/ios-enrichment-20261109.json", enrichment); updater.save("data/ios-trends-20261109.json", analyses)
    manifest = updater.load("assets/ios-manifest.json"); manifest["date"] = updater.IOS_DATE; updater.save("assets/ios-manifest.json", manifest)
    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai")).date().isoformat()
    updater.save("data/history/ios/2026-11-09.json", {"store":"ios","country":"US","device":"iPhone","category":"Games > Strategy > Top Grossing",
        "date":source_date,"dataDate":source_date,"sourceUpdated":source_updated,"sourceUrl":source_url,
        "rankings":[{"rank":g["rank"],"appId":g["appId"],"gameName":g["gameName"],"sourceUrl":g["storeUrl"]} for g in games]})
    return games, source_date


updater.build_google = build_google_today
updater.build_ios = build_ios_today


def refresh_ios_metadata():
    path = "data/ios-games-20261109.json"; games = updater.load(path)
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
    for gp,tp,store,basis in (("data/games-20261109.json","data/trends-20261109.json","Google Play","Google Play美国区商品页released日期"),
                              ("data/ios-games-20261109.json","data/ios-trends-20261109.json","iOS","Apple Lookup releaseDate")):
        games=updater.load(gp); trends=updater.load(tp)
        for game in games:
            ch=game["dailyChange"]
            movement = "较2026-11-06前一有效快照回榜" if ch=="NEW" else ("较2026-11-06前一有效快照持平" if ch=="=" else f"较2026-11-06前一有效快照{'上升' if ch.startswith('+') else '下降'}{ch[1:]}位")
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
    gg=updater.load("data/games-20261109.json"); ii=updater.load("data/ios-games-20261109.json")
    maps={"Google":{key(g["gameName"]):g for g in gg},"iOS":{key(g["gameName"]):g for g in ii}}
    for gp,tp,own,other in (("data/games-20261109.json","data/trends-20261109.json","Google","iOS"),("data/ios-games-20261109.json","data/ios-trends-20261109.json","iOS","Google")):
        games=updater.load(gp); trends=updater.load(tp)
        for g in games:
            s=trends[str(g["rank"])]["summary"]
            ch=g["dailyChange"]
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
