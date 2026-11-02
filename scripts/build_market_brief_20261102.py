#!/usr/bin/env python3
"""Generate the Beijing 2026-11-02 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-11-02", "20261102"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261102.json"), "prior": load("data/games-20261030.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261102.json"), "prior": load("data/ios-games-20261030.json"), "id": "appId"},
}


def product(game_name, product_id, store, tone, label, analysis):
    return {
        "gameName": game_name,
        "productId": product_id,
        "iconKey": f"{store}:{product_id}",
        "tone": tone,
        "changeLabel": label,
        "analysis": analysis,
    }


def find_game(store, prefix, include_prior=True):
    data, ident = datasets[store], datasets[store]["id"]
    pool = data["now"] + (data["prior"] if include_prior else [])
    found = [row for row in pool if row["gameName"].startswith(prefix)]
    ids = {str(row[ident]) for row in found}
    if len(ids) != 1:
        raise RuntimeError(f"Ambiguous product {store}:{prefix}: {ids}")
    product_id = ids.pop()
    return next(row for row in pool if str(row[ident]) == product_id)


def current_rank(store, prefix):
    return find_game(store, prefix, include_prior=False)["rank"]


def card(store, prefix, tone, analysis, first_time_ids=None):
    data, ident = datasets[store], datasets[store]["id"]
    row = find_game(store, prefix)
    product_id = str(row[ident])
    current = next((item for item in data["now"] if str(item[ident]) == product_id), None)
    previous = next((item for item in data["prior"] if str(item[ident]) == product_id), None)
    if tone == "entry" and current and not previous:
        first = product_id in (first_time_ids or set())
        label = f"{'首次收录' if first else '回榜'} · #{current['rank']}"
    elif tone == "exit" and previous and not current:
        label = f"掉榜 · 上期#{previous['rank']}"
    elif tone in ("up", "down") and current and previous:
        change = previous["rank"] - current["rank"]
        if (change > 0) != (tone == "up"):
            raise RuntimeError(f"Incorrect direction {store}:{prefix}: {change}")
        label = f"{'+' if change > 0 else '−'}{abs(change)} · #{current['rank']}"
    else:
        raise RuntimeError(f"Incorrect membership for {store}:{prefix}:{tone}")
    return product((current or previous)["gameName"], product_id, store, tone, label, analysis)


def asset_icons(manifest_path):
    result = {}
    for filename in load(manifest_path)["files"]:
        result.update(load(f"assets/{filename}"))
    return result


def build_market_icons(products):
    local = {"googlePlay": asset_icons("assets/manifest.json"), "ios": asset_icons("assets/ios-manifest.json")}
    bundle = {}
    for item in products:
        store, product_id = item["iconKey"].split(":", 1)
        data = datasets[store]
        game = next((row for row in data["now"] + data["prior"] if str(row[data["id"]]) == product_id), None)
        if not game:
            raise RuntimeError(f"No game record for {item['iconKey']}")
        rank = int(game["assetRank"])
        icon = game.get("iconData") or local[store].get(f"{rank}_icon") or local[store].get(f"{rank:02d}_icon")
        if not icon or not icon.startswith("data:image/"):
            raise RuntimeError(f"No local icon for {item['iconKey']}")
        bundle[item["iconKey"]] = icon
    if len(bundle) != len(products):
        raise RuntimeError("Duplicate market-card product keys")
    save(f"assets/market-icons-{STAMP}.json", bundle, compact=True)
    return bundle


# 2026-11-02 weekend-change cards, source-backed news and closing read.
google_products = [
    card("googlePlay", "GIRLS' FRONTLINE 2", "entry", "回到Google #32，iOS同名产品从上期#58掉榜。10月29日新活动与角色轮换仍在窗口，但跨端反向只记为待验证信号。"),
    card("googlePlay", "Raid Rush", "exit", "上期Google #60后掉榜，iOS反向上升6位至#36。塔防产品出现平台换位，不把iPhone回升外推为整体收入改善。"),
    card("googlePlay", "Mafia City", "up", "Google上升7位至#46，iOS未入榜。成熟黑帮SLG仍处后十五名，当前只作周末回补信号。"),
    card("googlePlay", "Narco Empire", "up", "Google上升7位至#19，首次进入前20附近；产品已早于90天窗口，缺少同步官方节点，不推演长期稳定性。"),
    card("googlePlay", "Clash of Clans", "up", "Google上升6位至#9，iOS同步上升11位至#4。双端共同改善清晰，但10月21日Builder菜单改版只能作为近期背景。"),
    card("googlePlay", "Age of Spirits", "up", "Google上升6位至#49，iOS回榜#58。9月上架新品出现双端改善，但两端均在后十二名，仍处首发验证。"),
    card("googlePlay", "DC: Dark Legion", "down", "Google下跌12位至#58，iOS反向小升2位至#50。Android已接近掉榜线，平台分化需下一快照验证。"),
    card("googlePlay", "Arknights", "down", "Google下跌11位至#28，iOS从上期#46掉榜。10月28日活动仍在窗口，但双端回落不能直接归因于活动。"),
    card("googlePlay", "Top Heroes", "down", "Google下跌11位至#48，iOS未入榜。Q版英雄与联动长线盘回到后十三名，只记录为单期风险信号。"),
    card("googlePlay", "Game of Thrones: Conquest", "down", "Google下跌7位至#43，iOS同步下跌13位至#51。九周年更新仍在近期窗口，但双端回落仍需连续快照确认。"),
]

ios_products = [
    card("ios", "Watcher of Realms", "entry", "回到iOS #31，Google未入榜。10月27日版本加入Gadrien's Tales测试季、The Bone Diaries与Aspect增强，时间相邻但仍需验证留位。"),
    card("ios", "The Battle Cats", "entry", "回到iOS #44，Google未入榜。成熟横版塔防重新进入中后段，未发现与本次回榜同步的重大官方节点。"),
    card("ios", "Kingdom Clash", "entry", "回到iOS #48，Google未入榜。中世纪塔防与英雄经营仍处后十三名，先按榜尾轮换处理。"),
    card("ios", "Fire Emblem Heroes", "entry", "回到iOS #49，Google未入榜。10.10.1只披露未来数据分发支持，不能据此解释回榜。"),
    card("ios", "Guns of Glory", "entry", "回到iOS #53，Google位于#39。成熟火枪时代4X在iPhone后八名回补，需验证能否连续留榜。"),
    card("ios", "The Tower", "entry", "回到iOS #54，Google未入榜。v29加入全局预设、Mythic联赛与Vault重做，但榜尾回归仍只记为待验证信号。"),
    card("ios", "Star Trek Fleet Command", "entry", "回到iOS #57，Google下跌3位至#24。近期Alliance Tournaments调整与回榜时间相邻，但双端并未同步改善。"),
    card("ios", "Age of Spirits", "entry", "回到iOS #58，Google同步上升6位至#49。近90天新品双端改善，但仍在榜尾区域。"),
    card("ios", "Limbus Company", "exit", "上期iOS #35后掉榜，Google未入榜。10月29日更新后的回榜未连续保留，不能据此判断长期运营表现。"),
    card("ios", "Kiss of War", "exit", "上期iOS #39后掉榜，Google仍位于#51。上期双端改善未延续为iPhone连续留位。"),
    card("ios", "Arknights", "exit", "上期iOS #46后掉榜，Google同步下跌11位至#28。10月28日活动开启后榜位回落，只记录时间相邻。"),
    card("ios", "Plants on Fire", "exit", "上期iOS #47后掉榜，Google未入榜。8月上架的近90天新品失去TOP60席位，下一快照观察是否快速回补。"),
    card("ios", "Last Shelter: War Z", "exit", "上期iOS #50后掉榜，Google同名条目仍位于#27。iPhone后十名改善未连续保持。"),
    card("ios", "Last Fortress", "exit", "上期iOS #55后掉榜，Google未入榜。地下堡垒经营上期回榜仅维持一个有效快照。"),
    card("ios", "Overgeared", "exit", "上期iOS #57后掉榜，Google同步下跌5位至#47。背包合成产品双端同向回落。"),
    card("ios", "GIRLS' FRONTLINE 2", "exit", "上期iOS #58后掉榜，Google反向回榜#32。10月29日活动与角色轮换窗口出现平台分化。"),
    card("ios", "Age of Empires Mobile", "up", "iOS上升20位至#34，Google未入榜。文明4X回到中段，但单期跳升不等于长期收入趋势。"),
    card("ios", "Mobile Legends", "up", "iOS上升15位至#17，Google未入榜。MOBA在策略分类中的周末跃升只作平台内信号。"),
    card("ios", "Summoners War", "up", "iOS上升12位至#28，Google未入榜。10月28日9.3.8加入Frieren联动原创魔灵，节点相邻但不作确定归因。"),
    card("ios", "Kingdom Guard", "up", "iOS上升12位至#47，Google未入榜。Gold Miner与Witch's Night活动刚结束，后续留位是更关键验证条件。"),
    card("ios", "Clash of Clans", "up", "iOS上升11位至#4，Google同步上升6位至#9。双端改善明确，但仍需下一有效快照确认持续性。"),
    card("ios", "Sea War", "down", "iOS下跌32位至#60，Google反向上升4位至#44。海战SLG是本日最强跨端分化，不能用单一版本节点解释。"),
    card("ios", "Infinity Kingdom", "down", "iOS下跌16位至#46，Google同步下跌2位至#20。iPhone回落显著，9月版本已不足以解释本次变化。"),
    card("ios", "Game of Thrones: Conquest", "down", "iOS下跌13位至#51，Google同步下跌7位至#43。九周年更新窗口内出现双端回落，需连续观察。"),
    card("ios", "Forge Master", "down", "iOS下跌11位至#35，Google同步下跌5位至#57。双端同向回落，但未发现同步重大内容节点。"),
]

news = [
    {
        "category": "战棋 / 角色运营", "date": "2026-10-29",
        "title": "GIRLS' FRONTLINE 2开启Themis' Game与Dreambound Neverland",
        "summary": "官方更新总览显示两项限时活动、Voyage Logs、Arclight Logs及Welrod、Faelynn等角色轮换自10月29日开启，主要窗口持续至11月18日。",
        "impact": "本期Google回榜#32、iOS从#58掉榜；相同内容窗口下出现平台分化，不能写成版本统一拉升。",
        "source": "SUNBORN官方Steam动态", "url": "https://steamcommunity.com/app/3308670/allnews/",
    },
    {
        "category": "回合战棋 / 版本", "date": "2026-10-30",
        "title": "Fire Emblem Heroes 10.10.1为后续数据分发做准备",
        "summary": "Apple美国区版本记录显示10.10.1于10月30日更新，公开说明仅为支持未来数据分发。",
        "impact": "产品本期回榜iOS #49；版本说明没有新增玩法信息，因此不把回榜归因于该维护更新。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/fire-emblem-heroes/id1181774280",
    },
    {
        "category": "塔防RPG / 版本", "date": "2026-10-27",
        "title": "Watcher of Realms美国版加入Gadrien's Tales测试季",
        "summary": "1.6.46.841版本加入Gadrien's Tales首个测试季、The Bone Diaries模式、Hero Aspect增强与商店。",
        "impact": "美国专属客户端本期回榜iOS #31；属于进入中段的信号，但仍需下一快照确认。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/watcher-of-realms-us/id6741674823",
    },
    {
        "category": "魔灵RPG / IP联动", "date": "2026-10-28",
        "title": "Summoners War 9.3.8加入Frieren联动原创魔灵",
        "summary": "Apple版本记录确认9.3.8加入Frieren联动原创魔灵，并包含体验优化和错误修复。",
        "impact": "产品本期iOS上升12位至#28；联动与位移时间相邻，但公开资料不足以证明单一因果。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/summoners-war/id852912420",
    },
    {
        "category": "部落战争 / 长线运营", "date": "2026-10-21",
        "title": "Clash of Clans重做Builder建议与多项菜单",
        "summary": "18.647.5版本重做Builder Suggestions，增加筛选与分类，并调整战斗菜单、玩家资料和部落聊天。",
        "impact": "本期Google +6至#9、iOS +11至#4；双端同向改善，但版本已发布十余天，只作近期运营背景。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/clash-of-clans/id529479190",
    },
    {
        "category": "新品4X / 版本", "date": "2026-10-26",
        "title": "Age of Spirits 1.1.2扩充Hero Shell与便利性功能",
        "summary": "版本记录列出Hero Shell兑换、充值奖励调整、营地保护、Captive Pit一键释放和远征快捷功能。",
        "impact": "产品本期Google +6至#49、iOS回榜#58；近90天新品出现双端改善，但仍在榜尾验证。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/age-of-spirits/id6805006706",
    },
    {
        "category": "塔防4X / 节日活动", "date": "2026-10-26",
        "title": "Kingdom Guard开放Gold Miner与Witch's Night活动",
        "summary": "1.0.598版本公告列出10月26日至11月1日的Gold Miner与Witch's Night，并加入联盟公告原文查看功能。",
        "impact": "产品本期iOS上升12位至#47；活动刚结束，后续是否留榜比单日跃升更具验证价值。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/kingdom-guard-tower-defense-td/id1570095804",
    },
    {
        "category": "放置塔防 / 大版本", "date": "2026-10-21",
        "title": "The Tower v29加入全局预设与Mythic联赛",
        "summary": "v29新增Global Presets与Preset Lab、Mythic锦标赛联赛，并重做Vault和Harmony Tree。",
        "impact": "产品本期回榜iOS #54；大版本已运行十余天，榜尾回归仍需连续快照确认。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/the-tower-idle-tower-defense/id1575590830",
    },
    {
        "category": "文明4X / 版本运营", "date": "2026-10-08",
        "title": "Age of Empires Mobile近期版本加入Stormlands与Mounted Hunt",
        "summary": "1.14.202版本延续此前Stormlands、Mounted Hunt和Emergency Aid Queue内容，并处理已有问题。",
        "impact": "产品本期iOS上升20位至#34、Google未入榜；版本时间较早，不能解释本次周末跃升。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/age-of-empires-mobile/id6476261995",
    },
    {
        "category": "塔防RPG / 活动运营", "date": "2026-10-28",
        "title": "Arknights Reclamation Algorithm活动仍在进行",
        "summary": "官方公告确认活动与Orienteering定向寻访于10月28日开启，寻访窗口持续至11月11日。",
        "impact": "本期Google下跌11位至#28、iOS掉榜；平台同步回落不能直接解释为活动效果。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4980",
    },
    {
        "category": "全球市场 / 收入榜", "date": "2026-10-01",
        "title": "Sensor Tower最新完整全球收入榜仍为2026年9月",
        "summary": "官方最新完整图表仍为9月全球手游收入TOP10；其中核心策略子集为Whiteout Survival #6、Last War #7与Kingshot #9。",
        "impact": "11月2日单次检查未发现更新一期完整图表，因此继续保留9月真实统计期；全球月榜不替代美国单区日榜。",
        "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank

closing = [
    {
        "type": "判断", "title": "Google一进一出，但周末后中段波动明显放大",
        "detail": "Google由GFL2回榜#32、Raid Rush掉榜；59款共同产品中30款位移不超过2名，稳定度低于10月30日。DC −12、Arknights与Top Heroes各−11，Mafia City与Narco Empire各+7。",
    },
    {
        "type": "判断", "title": "iOS八进八出，换位和极端位移均显著高于Google",
        "detail": "iOS有8款进入/回榜、8款掉榜，52款共同产品中仅23款位移不超过2名；Sea War −32、Age of Empires +20和Infinity Kingdom −16构成主要波动。",
    },
    {
        "type": "判断", "title": "跨端共同信号有限，平台分化更值得优先验证",
        "detail": "Clash of Clans与Age of Spirits双端改善；GFL2在Google回榜、iOS掉榜，Sea War则Google +4、iOS −32。Google近90天新品2款、iOS 1款；两端仍无可判定的90天飙升。",
    },
    {
        "type": "关注", "title": "下一有效快照：核验九款回榜产品的留位",
        "detail": "观察Google的GFL2 #32，以及iOS的Watcher #31、Battle Cats #44、Kingdom Clash #48、Fire Emblem #49、Guns of Glory #53、The Tower #54、Star Trek #57和Age of Spirits #58；快速退出则继续按榜尾轮换记录。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：复核双端共振与极端分化",
        "detail": "重点看Clash of Clans、Age of Spirits能否延续双端改善，以及Sea War、GFL2、Dragonfire和Raid Rush的跨端反向是否收敛。",
    },
    {
        "type": "关注", "title": "至11月11日和11月18日：分开观察活动窗口",
        "detail": "Arknights寻访持续至11月11日，GFL2主要活动与角色轮换持续至11月18日；仅当后续多份有效快照与运营节点同向时，才提高关联判断。",
    },
]

google_history = load("data/history/google-play/2026-11-02.json")
ios_history = load("data/history/ios/2026-11-02.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Google一进一出、iOS八进八出；Sea War跨端极端分化",
    "summary": "较10月30日前一有效快照，Google Play一进一出，59款共同产品中30款位移不超过2名；GFL2回榜#32，DC −12、Arknights与Top Heroes各−11。iOS八进八出，52款共同产品中23款位移不超过2名；Age of Empires +20、Sea War −32。Clash of Clans与Age of Spirits双端改善，Sea War和GFL2跨端反向。Google近90天新品2款、iOS 1款；两端缺少8月4日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261102.json",
    "rankingSources": {"googlePlay": "data/games-20261102.json", "ios": "data/ios-games-20261102.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261030.json", "ios": "data/ios-games-20261030.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Lands of Jail · #60 West Game",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Game of Thrones: Dragonfire · #60 Sea War: Uboat Raid",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-08-04"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-08-04"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-11-02.md", "json": "data/market-brief-20261102.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-30；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-08-04精确同口径TOP60基准，较老产品暂不判断飙升。",
        "", "## 1. 双榜当日异动产品", "",
    ]
    for store in ("googlePlay", "ios"):
        section = value["rankingDynamics"][store]
        lines += [f"### {section['label']}", "", f"{section['sourceTime']}。", ""]
        for item in section["products"]:
            lines += [f"#### {item['gameName']}｜{item['changeLabel']}", "", item["analysis"], ""]
    lines += ["## 2. 策略手游市场热点", "", value["newsMethod"], ""]
    for index, item in enumerate(value["marketNews"], 1):
        lines += [
            f"### {index}. [{item['title']}]({item['url']})", "",
            f"- 类别：{item['category']}｜发布日期：{item['date']}｜来源：{item['source']}",
            f"- 事实摘要：{item['summary']}", f"- 市场含义：{item['impact']}", "",
        ]
    lines += ["## 3. 综合判断与后续关注", ""]
    for item in value["closing"]:
        lines += [f"### {item['type']}｜{item['title']}", "", item["detail"], ""]
    revenue = value["globalStrategyRevenue"]
    lines += [
        "## 4. Sensor Tower 全球收入榜中的策略产品", "",
        f"- 数据期：{revenue['periodLabel']}｜官方页面：{revenue['publicationLabel']}｜估算截至：{revenue['estimateAsOf']}",
        f"- 口径：{revenue['scope']['region']}｜{revenue['scope']['stores']}｜{revenue['scope']['exclusions']}",
        f"- 策略筛选：官方全球收入TOP10中命中{revenue['scope']['strategyMatches']}款核心策略产品；这不是完整策略品类TOP10",
        f"- 市场总览：全球手游消费者支出约${revenue['marketSummary']['globalConsumerSpendingUsd'] / 1_000_000_000:g}B，环比{revenue['marketSummary']['monthOverMonthPercent']:g}%，全市场同比（约）{revenue['marketSummary']['yearOverYearPercentApprox']:g}%",
        f"- 原始来源：[{revenue['source']}]({revenue['sourceUrl']})", "",
        "| 全球总榜 | 游戏 | 发行商 | 策略类型 | 较上月榜位 | 单品收入同比 |",
        "|---:|---|---|---|---|---|",
    ]
    for item in revenue["rankings"]:
        lines.append(f"| {item['rank']} | {item['gameName']} | {item['publisher']} | {item['strategyGenre']} | {item['movementLabel']} | {item['yoyRevenueLabel']} |")
    lines += ["", "### 策略产品与同比口径", ""] + [f"- {item}" for item in revenue["officialHighlights"]]
    lines += [
        "", revenue["methodologyNote"], "", "## 下载与来源", "",
        f"- JSON：`{value['downloads']['json']}`",
        f"- Sensor Tower上月对照：{revenue['previousPeriodSourceUrl']}",
        f"- Sensor Tower同比对照：{revenue['yearOverYearSourceUrl']}",
        "- Google Play直连源：https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US",
        "- Apple官方RSS：https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json", "",
    ]
    return "\n".join(lines)


save("data/market-brief-20261102.json", brief)
(ROOT / "reports/2026-11-02.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {
    "date": DATE,
    "title": brief["title"],
    "summary": brief["summary"],
    "markdown": brief["downloads"]["markdown"],
    "json": brief["downloads"]["json"],
}
manifest["updated"] = DATE
manifest["reports"] = sorted(
    [entry] + [item for item in manifest["reports"] if item["date"] != DATE],
    key=lambda item: item["date"], reverse=True,
)
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
