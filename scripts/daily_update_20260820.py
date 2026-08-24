#!/usr/bin/env python3
import base64
import io
import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image

from google_play_direct import fetch_top_grossing_strategy

ROOT = Path(__file__).resolve().parents[1]
TODAY = "2026-08-20"
GOOGLE_DATA_DATE = "2026-08-19"
IOS_UPDATED = "2026-08-19T18:48:18-07:00"


def fetch(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; StrategyChartUpdater/1.0)"})
    with urlopen(req, timeout=60) as response:
        return response.read()


def load(rel):
    return json.loads((ROOT / rel).read_text())


def save(rel, obj):
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n")


def delta_label(old_rank, new_rank):
    if old_rank is None:
        return "NEW"
    d = old_rank - new_rank
    return "=" if d == 0 else (f"+{d}" if d > 0 else str(d))


def comparison(old_comp, current_rank, current_date, baseline_date, pending=False, release_date=None):
    """Classify a chart row using release date first, then the 90-day rank baseline.

    A product released inside the 90-day window and currently in TOP60 is a
    ``new`` entry. Older products still need the exact same-store baseline to
    determine whether they surged by more than five positions.
    """
    try:
        released = datetime.fromisoformat(str(release_date)[:10]).date()
        current = datetime.fromisoformat(current_date).date()
        baseline = datetime.fromisoformat(baseline_date).date()
    except (TypeError, ValueError):
        released = current = baseline = None
    if released and baseline <= released <= current:
        return {
            "baselineDate": baseline_date,
            "baselineRank": None,
            "currentDate": current_date,
            "currentRank": current_rank,
            "delta": None,
            "status": "new",
            "classificationBasis": "releaseDate",
            "releaseDate": released.isoformat(),
            "evidence": f"产品于{released.isoformat()}上架，位于{baseline_date}至{current_date}的90天窗口内，且当前进入TOP60。",
        }
    if pending or not old_comp:
        return {
            "baselineDate": baseline_date,
            "baselineRank": None,
            "currentDate": current_date,
            "currentRank": current_rank,
            "delta": None,
            "status": "pending",
            "evidence": f"上架日期早于{baseline_date}；未取得该日同商店、同地区、同设备/品类的完整TOP60快照，因此暂不判断飙升。",
        }
    if old_comp.get("status") == "new":
        return {
            "baselineDate": baseline_date,
            "baselineRank": None,
            "currentDate": current_date,
            "currentRank": current_rank,
            "delta": None,
            "status": "new",
            "evidence": old_comp.get("evidence", "同口径90天基准榜单未进入TOP60。"),
        }
    base = old_comp.get("baselineRank")
    if base is None:
        return comparison(None, current_rank, current_date, baseline_date, True, release_date)
    d = base - current_rank
    status = "surge" if d > 5 else "normal"
    return {
        "baselineDate": baseline_date,
        "baselineRank": base,
        "currentDate": current_date,
        "currentRank": current_rank,
        "delta": d,
        "status": status,
        "evidence": old_comp.get("evidence", "同口径90天历史榜单对比。"),
    }


def parse_google():
    result = fetch_top_grossing_strategy(limit=60)
    return result["sourceUrl"], result["rows"]


def parse_ios():
    url = "https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json"
    feed = json.loads(fetch(url))["feed"]
    rows = []
    for i, e in enumerate(feed["entry"][:60], 1):
        rows.append({
            "rank": i,
            "appId": e["id"]["attributes"]["im:id"],
            "gameName": e["im:name"]["label"],
            "developer": e["im:artist"]["label"],
        })
    assert len(rows) == 60
    return url, feed["updated"]["label"], rows


def lookup(ids):
    url = "https://itunes.apple.com/lookup?id=" + ",".join(ids) + "&country=us"
    return {str(x["trackId"]): x for x in json.loads(fetch(url))["results"]}


def data_uri(url, max_size):
    raw = fetch(url)
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    image.thumbnail(max_size, Image.Resampling.LANCZOS)
    out = io.BytesIO()
    image.save(out, "WEBP", quality=76, method=6)
    return "data:image/webp;base64," + base64.b64encode(out.getvalue()).decode()


def trend(summary, development, rank_path, turning, creative, watch, store_url, extra_sources=None):
    sources = [{"label": "商店美国区商品页", "url": store_url, "type": "primary"}]
    if extra_sources:
        sources.extend(extra_sources)
    return {
        "summary": summary,
        "sections": {
            "development": development,
            "rankPath": rank_path,
            "turningPoints": turning,
            "creative": creative,
            "watch": watch,
        },
        "sourceAudit": {
            "reviewedAt": TODAY,
            "status": "已复核",
            "confidence": "中",
            "basis": "核心玩法以商店描述和官方资料为主；素材判断结合当前商店图与公开产品节点。",
            "changeReason": "当日进榜产品首次建档，未将缺少证据的相关性写成确定因果。",
            "sources": sources,
        },
        "lifecycleAudit": {
            "reviewedAt": TODAY,
            "confidence": "中",
            "scope": "从上架期归纳产品改动、榜位阶段与素材迁移。",
            "evidenceNote": "仅记录可由商品页、官方站点和公开产品节点支撑的变化。",
            "sources": sources,
        },
    }


def main():
    google_url, google_rows = parse_google()
    ios_url, ios_updated, ios_rows = parse_ios()
    print("Google anchors", [(r["rank"], r["gameName"]) for r in google_rows if r["rank"] in (1,25,60)])
    print("iOS updated", ios_updated, "anchors", [(r["rank"], r["gameName"]) for r in ios_rows if r["rank"] in (1,25,60)])

    # Google Play: remap all rank-keyed enrichment/trends by package, keeping the
    # source's real Aug 19 date even though this capture runs on Beijing Aug 20.
    old_g = load("data/games-20260819d.json")
    old_g_by_pkg = {x["packageName"]: x for x in old_g}
    old_rank_by_pkg = {x["packageName"]: x["rank"] for x in old_g}
    old_ge = load("data/enrichment-20260819d.json")
    old_gt = load("data/trends-20260819d.json")
    companies_g, trends_g, games_g = {}, {}, []
    resident_base = next(x for x in load("data/games.json") if x["packageName"] == "com.aniplex.resu")
    for row in google_rows:
        pkg, rank = row["packageName"], row["rank"]
        if pkg in old_g_by_pkg:
            x = deepcopy(old_g_by_pkg[pkg])
            old_rank = old_rank_by_pkg[pkg]
            x["assetRank"] = x.get("assetRank") or old_rank
            companies_g[str(rank)] = deepcopy(old_ge["productCompaniesByRank"][str(old_rank)])
            trends_g[str(rank)] = deepcopy(old_gt[str(old_rank)])
            x["comparison90d"] = comparison(x.get("comparison90d"), rank, GOOGLE_DATA_DATE, "2026-05-21", release_date=x.get("releaseDateIso"))
        elif pkg == "com.aniplex.resu":
            x = deepcopy(resident_base)
            x["assetRank"] = 58
            x["genre"] = "SLG / 生存 / 基地建设"
            x["keywords"] = "Resident Evil；丧尸；生存恐怖；庇护所；英雄；联盟"
            x["comparison90d"] = comparison(None, rank, GOOGLE_DATA_DATE, "2026-05-21", True, x.get("releaseDateIso"))
            companies_g[str(rank)] = {
                "en": "Aniplex / JOYCITY / Capcom",
                "cn": "Aniplex（索尼音乐娱乐日本旗下；发行）/ JOYCITY（研发）/ 卡普空（Resident Evil IP）",
                "confidence": "已确认",
                "basis": "官方产品站列明 Aniplex 与 JOYCITY 权利标识；产品公告说明由 JOYCITY 联合开发、Aniplex 发行，并获 Capcom 授权。",
                "source": "https://www.residentevil-survivalunit.com/",
            }
            store = "https://play.google.com/store/apps/details?id=com.aniplex.resu&hl=en_US&gl=US"
            trends_g[str(rank)] = trend(
                "趋势：2025年以《生化危机》角色、生存恐怖与废弃宅邸探索吸引IP用户，随后把入口承接到基地扩建和联盟SLG；关键转折：全球上线后从解谜/恐怖氛围展示转向幸存者编队、防线与庇护所经营；主力素材：经典角色、丧尸压迫、宅邸探索、基地防线和联盟协作。",
                "2025年公布并于同年11月全球上线，首发借《生化危机》角色、丧尸危机和废弃宅邸的生存恐怖认知降低理解门槛；实际长期循环则由幸存者收集、设施扩建、资源调度与联盟实时战略承接。",
                "2025年11月上架，早于本期90天窗口；本次回到Google Play美国策略畅销榜第60名，处于榜尾观察位。因缺少精确90天同口径快照，暂不判断近三个月飙升。",
                "首发传播重点是IP角色、密闭空间压力和探索/解谜，正式运营后商店表达更突出基地防线、幸存者队伍与联盟协作，意味着获量钩子与中后期付费循环已分层。",
                "里昂等经典角色、丧尸追逐与压迫镜头、废弃宅邸、据点扩建、英雄编队、防线战斗和联盟地图。",
                "观察榜尾回归是否由版本/IP活动形成短峰，以及基地SLG循环能否把IP导入用户稳定留在TOP60。",
                store,
                [{"label": "Resident Evil Survival Unit 官方站", "url": "https://www.residentevil-survivalunit.com/", "type": "primary"}],
            )
        else:
            raise RuntimeError(f"Unexpected Google entrant {row}")
        x.update(rank=rank, gameName=row["gameName"], developer=row["developer"], dailyChange=delta_label(old_rank_by_pkg.get(pkg), rank))
        x["storeUrl"] = f"https://play.google.com/store/apps/details?id={pkg}&hl=en_US&gl=US"
        x.pop("iconImageRaw", None); x.pop("storeImageRaw", None); x.pop("iconImage", None); x.pop("storeImage", None)
        games_g.append(x)
    ge = deepcopy(old_ge)
    ge["productCompaniesByRank"] = companies_g
    save("data/games-20260820.json", games_g)
    save("data/enrichment-20260820.json", ge)
    save("data/trends-20260820.json", trends_g)

    # iOS: existing rows retain metadata and local assetRank; three entrants use
    # official Lookup metadata and a new local data-URI bundle.
    old_i = load("data/ios-games-20260819.json")
    old_i_by_id = {x["appId"]: x for x in old_i}
    old_i_rank = {x["appId"]: x["rank"] for x in old_i}
    old_ie = load("data/ios-enrichment-20260819.json")
    old_it = load("data/ios-trends-20260819.json")
    new_ids = [r["appId"] for r in ios_rows if r["appId"] not in old_i_by_id]
    meta = lookup(new_ids)
    assert set(meta) == set(new_ids), (new_ids, meta.keys())
    asset_ranks = {"913292932": 61, "6746465127": 62, "6751086804": 63}
    asset_bundle = {}
    companies_i, trends_i, games_i = {}, {}, []
    for row in ios_rows:
        app_id, rank = row["appId"], row["rank"]
        store = f"https://apps.apple.com/us/app/id{app_id}"
        if app_id in old_i_by_id:
            old_rank = old_i_rank[app_id]
            x = deepcopy(old_i_by_id[app_id])
            companies_i[str(rank)] = deepcopy(old_ie["productCompaniesByRank"][str(old_rank)])
            trends_i[str(rank)] = deepcopy(old_it[str(old_rank)])
        else:
            m = meta[app_id]
            shots = m.get("screenshotUrls") or m.get("ipadScreenshotUrls") or []
            icon = m.get("artworkUrl512") or m.get("artworkUrl100")
            screenshot = shots[0] if shots else icon
            ar = asset_ranks[app_id]
            asset_bundle[f"{ar}_icon"] = data_uri(icon, (256, 256))
            asset_bundle[f"{ar}_store"] = data_uri(screenshot, (720, 720))
            x = {
                "rank": rank, "appId": app_id, "packageName": app_id,
                "gameName": m.get("trackName", row["gameName"]), "developer": m.get("sellerName") or row["developer"],
                "totalInstalls": "", "recentInstalls30d": "", "dailyChange": "NEW", "storeUrl": store,
                "iconUrl": icon, "screenshotUrl": screenshot,
                "shortDescription": (m.get("description") or "").replace("\n", " ")[:220],
                "description": m.get("description", ""),
                "releaseDate": (m.get("releaseDate") or "")[:10], "releaseDateIso": (m.get("releaseDate") or "")[:10],
                "updatedDate": (m.get("currentVersionReleaseDate") or "")[:10], "note": "", "assetRank": ar, "store": "ios",
            }
            if app_id == "913292932":
                x.update(genre="模拟经营 / 城市建设", keywords="SimCity；城市规划；生产链；地标；市长竞赛；设计挑战")
                companies_i[str(rank)] = {"en":"Electronic Arts / TrackTwenty", "cn":"艺电（EA；TrackTwenty赫尔辛基工作室研发）", "confidence":"已确认", "basis":"EA官方工作室页面确认TrackTwenty为SimCity BuildIt研发团队。", "source":"https://www.ea.com/ea-studios/tracktwenty"}
                trends_i[str(rank)] = trend(
                    "趋势：2014年以触屏城市建设和生产链起量，成熟期通过市长竞赛、俱乐部战争与设计挑战转成长线活动型经营；关键转折：从单机扩城逐步加入联盟竞赛和赛季通行证；主力素材：城市天际线、灾害治理、地标布局、生产瓶颈和设计挑战。",
                    "2014年上线时以触屏城市规划、工厂生产与服务覆盖承接SimCity品牌用户；随后加入市长俱乐部、市长竞赛、俱乐部战争、赛季与设计挑战，把单人扩城扩展为周期竞赛和主题收藏。",
                    "2014年12月上架，早于本期90天窗口；本次进入iOS美国策略畅销榜第49名，属于成熟长线产品的阶段性回榜。因缺少精确90天基准，暂不判断近三个月飙升。",
                    "早期重点是道路、住宅、消防和污染等经典城市问题；中期俱乐部/竞赛引入排名和协作；设计挑战与赛季通行证又把展示重点转向主题城市、限时地标及外观收藏。",
                    "空地到天际线的前后对比、交通/火灾/污染危机、地标拼图、生产链卡点、市长竞赛和俱乐部战争。",
                    "观察本轮榜位能否跨过活动结算期，以及设计赛季对老用户付费和回流的持续性。", store,
                    [{"label":"EA TrackTwenty工作室页", "url":"https://www.ea.com/ea-studios/tracktwenty", "type":"primary"}],
                )
            elif app_id == "6746465127":
                x.update(genre="塔防 / 生存射击 / 肉鸽", keywords="细胞防线；病毒；固定炮台；武器进化；肉鸽技能；生存波次")
                companies_i[str(rank)] = {"en":"Snap Brain Games / WeDoBest (suspected)", "cn":"疑似WeDoBest中国团队（Snap Brain Games海外发行账号）", "confidence":"疑似", "basis":"Apple店铺主体为Snap Brain Games；公开应用情报将同名产品开发者标为中国WeDoBest，尚缺法律主体或官网交叉确认。", "source":"https://appmagic.rocks/google-play/cell-survivor/defense.roguelike.cell.shoot.survivor/?hl=en"}
                trends_i[str(rank)] = trend(
                    "趋势：以细胞对抗病毒的竖屏生存射击快速进入iOS榜尾，核心是短局波次和肉鸽武器成长；关键转折：当前仍处首发验证，尚未发现可确认的成熟期素材迁移；主力素材：固定火力点、病毒雨、弹幕清屏、武器合成和数值成长。",
                    "产品以上方持续落下的病毒/敌群和底部细胞火力点构成单屏战斗，用自动射击、技能选择、装备与局外成长降低操作门槛；当前公开时间线较短，仍处首发验证。",
                    "本次进入iOS美国策略畅销榜第51名，是当日TOP60新面孔；由于iOS同口径90天历史尚未积累，页面状态保持pending并按常规样式展示。",
                    "尚未发现可确认的重大转折。当前可见变化集中在武器/技能组合和局外培养，而非从早期素材到成熟期素材的明确迁移。",
                    "大量病毒压向单个细胞、枪口升级、弹幕范围扩大、三选一技能、合成/装备数值跳升和Boss波次。",
                    "观察首发买量停止后能否留在TOP60，以及商店素材是否从即时清屏转向更深的英雄、装备或长期养成。", store,
                    [{"label":"AppMagic产品归属页", "url":"https://appmagic.rocks/google-play/cell-survivor/defense.roguelike.cell.shoot.survivor/?hl=en", "type":"company-research"}],
                )
            elif app_id == "6751086804":
                x.update(genre="卡牌RPG / 放置 / 二次元", keywords="异世界；龙；恋爱喜剧；角色收集；放置；BUFF 101联动")
                companies_i[str(rank)] = {"en":"HongKong GameTree Limited / GameTree Entertainment", "cn":"香港GameTree（游戏树；独立发行主体）", "confidence":"已确认", "basis":"官方站版权信息列明HongKong GameTree Limited，Apple店铺品牌为GameTree Entertainment；未发现可确认的更上层集团归属。", "source":"https://dt.game-tree.com/"}
                trends_i[str(rank)] = trend(
                    "趋势：2026年以异世界恋爱喜剧和轻量放置卡牌切入，角色收集与夸张剧情承担首发获量；关键转折：近期BUFF 101联动强化限定角色和事件传播；主力素材：动画角色、龙与勇者反差、恋爱桥段、抽卡阵容和放置奖励。",
                    "2026年上线后以勇者与龙的身份反转、恋爱喜剧对白和二次元角色收集作为入口，战斗与养成则采用较轻的放置卡牌结构，降低追剧情用户的操作负担。",
                    "2026年1月上架，早于本期90天窗口；本次进入iOS美国策略畅销榜第60名，仍是活动驱动的榜尾验证位。因缺少90天同口径基准，暂不判断近三个月飙升。",
                    "目前可确认的节点是BUFF 101合作内容进入商店标题与传播主位，获量重点由基础世界观进一步转向限定角色/事件；除此之外尚未发现可确认的重大系统转折。",
                    "动画立绘、勇者与龙的反差关系、恋爱喜剧对白、限定角色、十连抽/阵容展示、离线收益和联动视觉。",
                    "观察联动结束后的榜位留存，以及轻量卡牌循环能否承接由剧情与角色素材带来的新增用户。", store,
                    [{"label":"Dragon Traveler官方站", "url":"https://dt.game-tree.com/", "type":"primary"}],
                )
        x.update(rank=rank, gameName=row["gameName"], developer=row["developer"], dailyChange=delta_label(old_i_rank.get(app_id), rank))
        x["comparison90d"] = comparison(None, rank, TODAY, "2026-05-22", True, x.get("releaseDateIso"))
        games_i.append(x)
    ie = deepcopy(old_ie); ie["productCompaniesByRank"] = companies_i
    save("data/ios-games-20260820.json", games_i)
    save("data/ios-enrichment-20260820.json", ie)
    save("data/ios-trends-20260820.json", trends_i)
    save("assets/ios-assets-07.json", asset_bundle)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = TODAY
    if "ios-assets-07.json" not in manifest["files"]:
        manifest["files"].append("ios-assets-07.json")
    save("assets/ios-manifest.json", manifest)

    # Store-isolated snapshots. Google records both capture date and actual
    # source date so the UI can truthfully remain on Aug 19.
    legacy = load("data/history/2026-08-19.json")
    save("data/history/google-play/2026-08-19.json", {
        "store":"google-play", "country":"US", "category":"Games > Strategy > Top Grossing",
        "date":"2026-08-19", "dataDate":"2026-08-19",
        "sourceLastUpdated":legacy.get("sourceLastUpdated", "August 19, 2026"),
        "sourceUrl":legacy.get("source", google_url),
        "rankings":[{
            "rank":x["rank"], "packageName":x["packageName"], "gameName":x["gameName"],
            "sourceUrl":x["storeUrl"],
        } for x in old_g],
    })
    save("data/history/google-play/2026-08-20.json", {
        "store":"google-play", "country":"US", "category":"Games > Strategy > Top Grossing",
        "date":TODAY, "dataDate":GOOGLE_DATA_DATE, "sourceLastUpdated":"August 19, 2026", "sourceUrl":google_url,
        "rankings":[{"rank":x["rank"], "packageName":x["packageName"], "gameName":x["gameName"], "sourceUrl":x["storeUrl"]} for x in games_g],
    })
    save("data/history/ios/2026-08-20.json", {
        "store":"ios", "country":"US", "device":"iPhone", "category":"Games > Strategy > Top Grossing",
        "date":TODAY, "sourceUpdated":ios_updated, "sourceUrl":ios_url,
        "rankings":[{"rank":x["rank"], "appId":x["appId"], "gameName":x["gameName"], "sourceUrl":x["storeUrl"]} for x in games_i],
    })
    print("Google entrants", [x["gameName"] for x in games_g if x["dailyChange"] == "NEW"])
    print("iOS entrants", [x["gameName"] for x in games_i if x["dailyChange"] == "NEW"])


if __name__ == "__main__":
    main()
