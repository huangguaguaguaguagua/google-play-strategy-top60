#!/usr/bin/env python3
"""Generate the Beijing 2026-10-19 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-19", "20261019"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261019.json"), "prior": load("data/games-20261016.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261019.json"), "prior": load("data/ios-games-20261016.json"), "id": "appId"},
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


def card(store, prefix, tone, analysis):
    data, ident = datasets[store], datasets[store]["id"]
    row = find_game(store, prefix)
    product_id = str(row[ident])
    current = next((item for item in data["now"] if str(item[ident]) == product_id), None)
    previous = next((item for item in data["prior"] if str(item[ident]) == product_id), None)
    if tone == "entry" and current and not previous:
        label = f"回榜 · #{current['rank']}"
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
        icon = local[store].get(f"{rank}_icon") or local[store].get(f"{rank:02d}_icon")
        if not icon or not icon.startswith("data:image/"):
            raise RuntimeError(f"No local icon for {item['iconKey']}")
        bundle[item["iconKey"]] = icon
    if len(bundle) != len(products):
        raise RuntimeError("Duplicate market-card product keys")
    save(f"assets/market-icons-{STAMP}.json", bundle, compact=True)
    return bundle


google_products = [
    card("googlePlay", "Limbus Company", "entry", "回到Google #60，iOS则从上期#35掉榜。双端方向相反且Google恰处最后一名，未发现与今天同步的官方重大节点，先记录为榜尾回补。"),
    card("googlePlay", "Sea of Conquest", "exit", "从Google上期#57掉榜，iOS当前未进入TOP60。产品此前已在截线附近，本次只能确认榜尾退出，不能据一个快照推断长线收入走弱。"),
    card("googlePlay", "League of Legends: Wild Rift", "up", "Google上升13位至#47，iOS小幅回落至#54。7.3b仍是最近可确认版本背景，但跨端方向不同，不能把Google改善写成双端趋势。"),
    card("googlePlay", "Call of Dragons", "up", "Google上升8位至#45，但iOS从上期#60掉榜。两端从同步回榜转为分化，说明上期榜尾共同进入尚未形成稳定跨端承接。"),
    card("googlePlay", "Age of Empires Mobile", "up", "Google上升7位至#34，iOS当前#26。双端都在中段、名次差8位；未发现与源更新时间同步的官方大版本，先按改善信号观察。"),
    card("googlePlay", "Stormshot", "down", "Google下跌9位至#53，为本端最大回落并进入榜尾风险区；iOS未进入TOP60。没有同日重大节点证据，不对单次下跌作原因判断。"),
    card("googlePlay", "Rise of Castles", "down", "Google下跌7位至#46，iOS未进入TOP60。成熟4X仍在中后段，变动需由后续快照确认，未发现可确认的生命周期转折。"),
    card("googlePlay", "Warhammer 40,000: Tacticus", "down", "Google下跌5位至#43，iOS却上升12位至#46。两端名次接近但方向相反，更适合解释为平台端短时差异，而不是产品整体趋势。"),
]


ios_products = [
    card("ios", "Watcher of Realms", "entry", "回到iOS #48，Google未进入TOP60。官方社区同期存在召唤活动，但只有单端回榜且仍在后段，暂不认定为活动拉动。"),
    card("ios", "Overgeared Hero", "entry", "回到iOS #57，Google当前#38。Raven联动与万圣节内容仍在，本次仅隔一个有效快照回归，但iOS仍靠近截线。"),
    card("ios", "SD Gundam G Generation ETERNAL", "entry", "回到iOS #58，Google未进入TOP60。IP与战术编队能解释产品定位，但未发现与今天同步的重大节点，先按榜尾回补处理。"),
    card("ios", "Plants on Fire", "entry", "回到iOS #59；因8月26日上架，仍按releaseDate归类为近三个月新上榜。10月15日版本加入Pirate Captain、新植物与Ace Plan活动，但榜尾回归仍需连续快照确认。"),
    card("ios", "Bloons TD 6", "entry", "回到iOS #60，Google未进入TOP60。57.2于10月15日加入Sniper Paragon与新地图，时间相邻但产品恰处最后一名，仍是版本窗口内的待验证信号。"),
    card("ios", "Limbus Company", "exit", "从iOS上期#35掉榜，却回到Google #60。跨端方向相反，说明上期iOS中段位置未延续，也不支持把单端变化归因于统一运营节点。"),
    card("ios", "Game of Thrones: Conquest", "exit", "从iOS上期#43掉榜，Google当前#36。九周年月内容仍在推进，但两端表现分化，不能把iOS退出外推为产品整体走弱。"),
    card("ios", "Evo Defense", "exit", "从iOS上期#53掉榜，Google未进入TOP60。此前已接近截线，未发现同日重大节点；本次按榜尾风险兑现记录。"),
    card("ios", "Last Shelter: War Z", "exit", "上期回到iOS #54后本期即掉榜，对应Google同名产品仍在#39。iPhone端回补只维持一个快照，尚未形成稳定跨端承接。"),
    card("ios", "Call of Dragons", "exit", "上期回到iOS #60后本期掉榜，Google反而升至#45。双端共同回归没有延续，当前应改记为平台分化而非长期回升。"),
    card("ios", "Mobile Legends", "up", "iOS上升18位至#15，为本端最大上涨；Google未进同口径TOP60。10周年Layla活动仍在进行，但该产品本质是MOBA分类边界，单端跃升仍需复核。"),
    card("ios", "Fire Emblem Heroes", "up", "iOS上升16位至#41。10月16日新英雄与“A Prince Lost”章节时间相邻，是可核验背景；仍需下一快照判断是否能脱离后20名。"),
    card("ios", "War and Order", "up", "iOS上升12位至#37，Google当前#33。双端名次接近且都在中段，但未发现同日可确认的重大内容节点，先记录为同步在榜而非确定拉升。"),
    card("ios", "Warhammer 40,000: Tacticus", "up", "iOS上升12位至#46，Google却下跌5位至#43。两端名次相近、方向相反，当前不支持活动峰值或整体回升判断。"),
    card("ios", "Arknights", "down", "iOS从#7回落21位至#28，Google仍在#8。Episode 17窗口仍在，但iOS回吐明显；这更像活动高位后的待验证回落，不能换算为收入跌幅。"),
    card("ios", "Hearthstone", "down", "iOS从#31回落19位至#50。37.0已预载新资料片内容，正式节点临近；当前回落发生在发布窗口内，不能据此判断资料片最终表现。"),
    card("ios", "Dragon Traveler", "down", "iOS下跌12位至#38，仍高于榜尾。上期大涨后本期继续回吐，最近可确认节点仍是BUFF 101合作内容，尚不足以定义长线拐点。"),
    card("ios", "Summoners War", "down", "iOS下跌10位至#34，Google未进入TOP60。SWC2026区域赛是近期运营背景，但没有证据把本次单日回落直接归因于赛事节点。"),
]


news = [
    {
        "category": "实时PvP塔防 / 新品", "date": "2026-10-15",
        "title": "Plants on Fire更新2.0.2870并回到iOS TOP60",
        "summary": "Apple官方版本记录显示2.0.2870加入回归的Pirate Captain、Chuckleberry与Thornmelon两种新植物、四种变体和Ace Plan活动，并改善匹配稳定性。",
        "impact": f"产品8月26日上架，本期回到iOS #{current_rank('ios', 'Plants on Fire')}；属于近90天新品，但榜尾回归仍需下一快照验证留存。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id6776076449",
    },
    {
        "category": "战术RPG / 新英雄", "date": "2026-10-15",
        "title": "报道：Fire Emblem Heroes 10月16日加入新双人英雄与新章节",
        "summary": "Final Weapon引用Nintendo Mobile公告称，10月16日更新加入Duo CYL Dimitri、Duo CYL Edelgard、Vista Hero Gullveig与“A Prince Lost”章节，活动持续至11月初。",
        "impact": f"产品本期iOS升16位至#{current_rank('ios', 'Fire Emblem Heroes')}；节点与上涨时间相邻，但报道本身不能证明榜位因果。",
        "source": "Final Weapon（报道；引用Nintendo Mobile公告）", "url": "https://finalweapon.net/2026/10/15/fire-emblem-heroes-releases-duo-cyl-dimitri-duo-cyl-edelgard-on-october-16/",
    },
    {
        "category": "MOBA / 十周年长线运营", "date": "2026-09-04",
        "title": "Mobile Legends十周年Layla活动持续至11月19日",
        "summary": "MOONTON官方ALL IN MLBB十周年计划包含9月4日至11月1日Celebration Pass，以及10月9日至11月19日Layla's Stellar Gala和皮肤试用。",
        "impact": f"产品本期iOS跃升至#{current_rank('ios', 'Mobile Legends')}；活动仍在窗口内，但它属于MOBA分类边界且只有iOS进入当前策略TOP60。",
        "source": "MOONTON Games官方", "url": "https://en.moonton.com/news/372.html",
    },
    {
        "category": "塔防RPG / 主线大版本", "date": "2026-10-14",
        "title": "Arknights Episode 17窗口进入回吐阶段",
        "summary": "官方公告将Episode 17开放时间定为10月14日，并在10月28日前临时降低主线解锁要求；Apple版本记录也显示10月14日强制更新。",
        "impact": f"产品仍居Google #{current_rank('googlePlay', 'Arknights')}，但iOS从#7回落至#{current_rank('ios', 'Arknights')}；活动存在不等于两端同步上涨。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4814",
    },
    {
        "category": "卡牌策略 / 资料片", "date": "2026-10-13",
        "title": "Hearthstone 37.0预载Reign of the Black Empire",
        "summary": "Blizzard官方37.0加入新资料片卡牌、Assemble关键词、新竞技场卡池与Journal更新，正式资料片窗口紧随本期榜单。",
        "impact": f"产品本期iOS回落至#{current_rank('ios', 'Hearthstone')}；发布窗口内的一次回撤不能定义资料片承接，需看后续1—2个快照。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "IP 4X / 限时版本", "date": "2026-10-15",
        "title": "Star Trek Fleet Command Division 12继续提供活动背景",
        "summary": "Scopely官方说明Division 12加入SNW Rose Harper、Haven Exchange及多组Heroic Solo Milestone，限时活动于10月15日开启。",
        "impact": f"产品本期Google升至#{current_rank('googlePlay', 'Star Trek Fleet Command')}，iOS仍在#{current_rank('ios', 'Star Trek Fleet Command')}；跨端差34位，活动承接明显不均。",
        "source": "Star Trek Fleet Command官方", "url": "https://startrekfleetcommand.com/news/division-12-patch-notes/",
    },
    {
        "category": "MOBA / 平衡补丁", "date": "2026-10-14",
        "title": "Wild Rift 7.3b后Google改善、iOS回落",
        "summary": "Riot官方7.3b调整多名英雄、装备、符文与野区，并开放Legends Showdown Volibear限定兑换内容。",
        "impact": f"产品本期Google升至#{current_rank('googlePlay', 'League of Legends: Wild Rift')}，iOS回落至#{current_rank('ios', 'League of Legends: Wild Rift')}；跨端方向分化。",
        "source": "Wild Rift官方", "url": "https://wildrift.leagueoflegends.com/en-us/news/game-updates/wild-rift-patch-notes-7-3b/",
    },
    {
        "category": "塔防 / 大版本", "date": "2026-10-15",
        "title": "Bloons TD 6版本57.2加入Sniper Paragon",
        "summary": "Apple官方版本记录显示57.2加入S.P.I.D.E.R. Monkey Sniper Paragon、社区竞赛地图Ship Capture，以及平衡和体验优化。",
        "impact": f"产品本期回到iOS #{current_rank('ios', 'Bloons TD 6')}；版本与回榜时间相邻，但最后一名仍属于高掉榜风险。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id1118115766",
    },
    {
        "category": "城建策略 / 体验改版", "date": "2026-10-13",
        "title": "Clash of Clans重做Builder菜单与村庄管理入口",
        "summary": "Apple官方18.647.2重做Builder Suggestions并加入筛选和分类，同时调整Battle菜单、玩家资料、Clan Chat与多项体验细节。",
        "impact": f"产品当前Google #{current_rank('googlePlay', 'Clash of Clans')}、iOS #{current_rank('ios', 'Clash of Clans')}；头部稳定，改版更适合作为长期留存背景。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id529479190",
    },
    {
        "category": "全球市场 / 收入榜", "date": "2026-10",
        "title": "Sensor Tower最新官方全球收入榜仍为2026年9月",
        "summary": "官方9月全球手游收入TOP10中，核心策略子集为Whiteout Survival #6、Last War #7与Kingshot #9；统计覆盖Apple App Store和Google Play，并排除第三方Android商店。",
        "impact": "本工作日未发现更新一期官方完整图表，因此月榜数据保持9月真实统计期；该全球月度子集不能代替美国单区日榜。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google一进一出，主体稳定但中后段振幅扩大",
        "detail": "Google 59款共同产品中43款位移不超过2名，中位绝对变动1名；Limbus回榜、Sea of Conquest掉榜。Wild Rift +13与Stormshot −9集中在后20名，暂不构成长线趋势。",
    },
    {
        "type": "判断", "title": "iOS五进五出且26款变动至少5位，明显高于Google",
        "detail": "iOS 55款共同产品中仅16款位移不超过2名，中位绝对变动4名；Mobile Legends +18、Fire Emblem +16，而Arknights −21、Hearthstone −19，版本窗口与榜位方向并不一致。",
    },
    {
        "type": "判断", "title": "双端分化成为本期主线，新品信号仍集中在iOS榜尾",
        "detail": "Limbus在Google回榜却从iOS掉榜，Call of Dragons在Google上升却从iOS退出，Tacticus两端方向相反；Plants on Fire回到iOS #59，仍按上架日期归入近90天新品。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证Plants on Fire与四款iOS回榜产品",
        "detail": "Plants on Fire需连续留榜才能从首现升级为稳定信号；Watcher、Overgeared、SD Gundam与Bloons均在#48以后，若立即退出仍按榜尾轮换处理。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：区分版本高位回吐与持续承接",
        "detail": "观察Arknights iOS能否在Episode 17窗口守住前30、Hearthstone能否在资料片节点后回升，以及Fire Emblem新英雄窗口能否将#41继续推向中段。",
    },
    {
        "type": "关注", "title": "下周内：复核跨端差距最大的长线产品",
        "detail": "Star Trek当前Google #21、iOS #55，Top Heroes为#29/#56；若差距连续存在，再结合各端版本与商店活动证据判断是否为稳定的平台结构差异。",
    },
]


google_history = load("data/history/google-play/2026-10-19.json")
ios_history = load("data/history/ios/2026-10-19.json")
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
    "title": "Google主体稳定、iOS五进五出，Plants on Fire回到榜尾",
    "summary": "较10月16日前一有效快照，Google Play一进一出：Limbus回榜、Sea of Conquest掉榜，Wild Rift +13、Stormshot −9。iOS五进五出：Watcher、Overgeared、SD Gundam、Plants on Fire与Bloons回榜，Limbus、Game of Thrones: Conquest、Evo Defense、Last Shelter: War Z与Call of Dragons退出；Mobile Legends +18、Fire Emblem +16，Arknights −21、Hearthstone −19。近90天新品为Google 1款、iOS 2款；两端缺少7月21日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261019.json",
    "rankingSources": {"googlePlay": "data/games-20261019.json", "ios": "data/ios-games-20261019.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261016.json", "ios": "data/ios-games-20261016.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Tiles Survive! · #60 Limbus Company",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Kingshot · #25 X-Clash: Survival Challenge · #60 Bloons TD 6",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-21"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-21"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-19.md", "json": "data/market-brief-20261019.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-16；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-21精确同口径TOP60基准，较老产品暂不判断飙升。",
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
        f"- 市场总览：全球手游消费者支出约${revenue['marketSummary']['globalConsumerSpendingUsd'] / 1_000_000_000:g}B，环比{revenue['marketSummary']['monthOverMonthPercent']:g}%，全市场同比约{revenue['marketSummary']['yearOverYearPercentApprox']:g}%",
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


save("data/market-brief-20261019.json", brief)
(ROOT / "reports/2026-10-19.md").write_text(build_markdown(brief), encoding="utf-8")
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
