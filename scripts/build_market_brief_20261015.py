#!/usr/bin/env python3
"""Generate the Beijing 2026-10-15 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-15", "20261015"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261015.json"), "prior": load("data/games-20261014.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261015.json"), "prior": load("data/ios-games-20261014.json"), "id": "appId"},
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
    row = find_game(store, prefix, include_prior=False)
    return row["rank"]


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
        game = next(
            (row for row in data["now"] + data["prior"] if str(row[data["id"]]) == product_id),
            None,
        )
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
    card("googlePlay", "Arknights", "entry", "回到Google前15，同时回到iOS前10。Episode 17《Critical Phase Transition》于10月14日开放，时间高度重合；仍需连续快照验证活动承接，不能把一天名次直接写成收入增长。"),
    card("googlePlay", "Ant Legion", "exit", "从Google上期#57掉榜，iOS当前也未进入TOP60。产品此前已靠近截线，今天只确认榜尾滑出，未发现同日可确认的重大节点。"),
    card("googlePlay", "Game of Thrones: Conquest", "down", "Google下跌11位至#53，为本端最大跌幅；iOS反而上升至前45。九周年月内容仍在运行，跨端相反方向不支持把单日变化统一归因于活动。"),
    card("googlePlay", "Age of Empires Mobile", "up", "Google上升7位至#47，iOS则回落至前30，仍呈平台分化。10月8日官方版本只披露错误修复，暂不据此判断内容拉动。"),
    card("googlePlay", "Auto Drill", "up", "Google上升4位至#46，iOS未进入TOP60。10月2日版本只写修复与性能改善，今天仍是待验证的中后段改善。"),
    card("googlePlay", "Game of Thrones: Dragonfire", "down", "Google与iOS均出现回落，但两端仍分别位于前30与前20附近。产品仍处首发后验证期，单日同向下降不等于长期衰退。"),
]


ios_products = [
    card("ios", "Arknights", "entry", "回到iOS前10，并同步回到Google前15。主线Episode 17与配套限时内容已开放；双端同日进入增强了活动窗口解释，但仍只有一个截面。"),
    card("ios", "Summoners War", "entry", "回到iOS #21。SWC2026美洲杯结果与亚太杯赛程于10月14日集中发布，赛事曝光是可核验背景；是否转化为持续消费仍待后续榜位。"),
    card("ios", "SimCity BuildIt", "entry", "回到iOS后十名。Haunted Metropolis赛季10月14日开启，加入Rift Tower、永久夜景与主题道路；当前位置仍有掉榜风险。"),
    card("ios", "Kiss of War", "entry", "回到iOS #59，恰处榜尾。未发现与源更新日同步的可确认重大版本节点，先按成熟军事4X的短时回补处理。"),
    card("ios", "War Machines", "entry", "回到iOS #60，位于最后一名。9月29日版本仅披露修复与性能优化，下一快照能否留榜比单日进入更有解释力。"),
    card("ios", "Guns of Glory", "exit", "从iOS上期#55掉榜，Google当前也未进入TOP60。此前已处后六名，本次更接近榜尾自然轮换，未发现同日可确认节点。"),
    card("ios", "Watcher of Realms", "exit", "继上一快照大幅下跌至#56后掉榜，形成连续走弱信号；但它属于RPG分类边界产品，仍不把两日榜位直接换算为收入跌幅。"),
    card("ios", "Last Shelter: War Z", "exit", "从iOS上期#58掉榜，而Google仍在前40附近。跨端差距扩大，说明本次更像iPhone端榜尾退出，原因仍待验证。"),
    card("ios", "Kingdom Clash", "exit", "从iOS上期#59掉榜，Google当前未进入TOP60。产品一直贴近截线，本次不据此推断长线运营转折。"),
    card("ios", "Plants on Fire", "exit", "从iOS上期#60掉榜；8月26日上架，仍是近90天新品，但一次榜尾回榜只维持一个快照，首发验证尚未转为稳定留榜。"),
    card("ios", "Sea War: Uboat Raid", "up", "iOS上升19位至#38，为本端最大上涨；Google仅小幅改善且仍在后四名。跨端幅度差异大，先按iPhone端待验证信号记录。"),
    card("ios", "The Battle Cats", "down", "iOS下跌14位至#57，进入掉榜风险区。未发现与今天同日的可确认联动或重大版本节点，不对单日回落强行归因。"),
    card("ios", "Last Day on Earth", "down", "iOS下跌10位至#50，Google当前未进入TOP60。成熟生存产品常随赛季与内容窗口波动，本期先记录为待验证回落。"),
    card("ios", "Hearthstone", "up", "37.0上线后继续改善至iOS前25，延续上一快照的明显上涨；10月20日资料片正式发布前后仍需区分预发布、竞技场新赛季与正式内容承接。"),
    card("ios", "The Tower - Idle Tower Defense", "down", "昨日+25后本期回落9位至#43，部分回吐峰值。v29是可核验背景，但一升一降更像短时活动窗口，尚非稳定趋势。"),
]


news = [
    {
        "category": "塔防RPG / 主线大版本", "date": "2026-10-14",
        "title": "Arknights开放Episode 17《Critical Phase Transition》",
        "summary": "官方公告将Episode 17开放时间定为10月14日08:00（UTC-7），并在10月28日前临时降低主线解锁要求，部分内容限时开放。",
        "impact": f"产品本期同步回到Google #{current_rank('googlePlay', 'Arknights')}与iOS #{current_rank('ios', 'Arknights')}；这是今天最强双端共同信号，但仍需连续快照确认。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4814",
    },
    {
        "category": "城市经营 / 万圣节赛季", "date": "2026-10-13",
        "title": "SimCity BuildIt开启Haunted Metropolis 28日赛季",
        "summary": "EA官方说明赛季从10月14日至11月11日运行，加入13级Rift Tower、全城02:00夜景效果、Haunted Street及多组哥特建筑。",
        "impact": f"产品本期回到iOS #{current_rank('ios', 'SimCity BuildIt')}；赛季首日与回榜相邻，但后十名位置仍要求下一快照验证留存。",
        "source": "Electronic Arts官方", "url": "https://www.ea.com/games/simcity/simcity-buildit/news/welcome-to-haunted-metropolis-streets-of-fright",
    },
    {
        "category": "回合制策略RPG / 电竞", "date": "2026-10-14",
        "title": "Summoners War发布SWC2026美洲杯结果并预告亚太杯",
        "summary": "Com2uS官方公布美洲杯前三名晋级世界总决赛，并将亚太杯直播安排在10月16日，区域杯进入最后席位争夺。",
        "impact": f"产品本期回到iOS #{current_rank('ios', 'Summoners War')}；赛事曝光与回榜同期，但是否形成付费承接仍需下一有效快照。",
        "source": "Summoners War官方", "url": "https://summonerswar.com/en/skyarena/news",
    },
    {
        "category": "卡牌策略 / 资料片预发布", "date": "2026-10-12",
        "title": "Hearthstone 37.0进入Black Empire预发布窗口",
        "summary": "Blizzard官方37.0于10月13日上线，加入新竞技场卡池、预发布乱斗、Journal与奖励内容；Reign of the Black Empire定于10月20日正式发布。",
        "impact": f"产品本期继续改善至iOS #{current_rank('ios', 'Hearthstone')}；连续两份快照上行，但正式资料片前后仍要验证持续性。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "全球市场 / 收入榜", "date": "2026-10-01",
        "title": "Sensor Tower 9月全球收入TOP10策略子集仍为3款",
        "summary": "官方全球手游收入TOP10图中，核心策略产品为Whiteout Survival #6、Last War #7与Kingshot #9；统计覆盖Apple App Store与Google Play并排除第三方Android商店。",
        "impact": "月榜显示三款策略头部仍在全球收入总榜，但不能把该全球月度结果当作美国单区日榜变化，也不能重新编号成策略第1至第3名。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
    {
        "category": "增量塔防 / 大版本", "date": "2026-10-06",
        "title": "The Tower v29峰值后出现回吐",
        "summary": "Apple官方v29加入Global Presets、Preset Lab、Mythic联赛、重做Vault与Harmony Tree，以及新卡牌和模块内容。",
        "impact": f"产品昨日大涨后本期回落至iOS #{current_rank('ios', 'The Tower')}；版本存在不等于榜位单向上涨，当前更适合按短峰观察。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1575590830",
    },
    {
        "category": "长线4X / 九周年", "date": "2026-10-05",
        "title": "Game of Thrones: Conquest推进九周年月内容",
        "summary": "官方10月预览列出Military III、Dragon Combat研究树、Old Nan's Tales、Viserion与Free Folk装备，以及10月26日英雄活动。",
        "impact": f"产品本期Google #{current_rank('googlePlay', 'Game of Thrones: Conquest')}、iOS #{current_rank('ios', 'Game of Thrones: Conquest')}且方向相反；活动体量明确，单日承接仍未一致。",
        "source": "Game of Thrones: Conquest官方", "url": "https://www.gotconquest.com/news/2026/10/05/october-preview-9th-anniversary-celebration/",
    },
    {
        "category": "背包策略 / IP联动", "date": "2026-10-13",
        "title": "Overgeared Hero加入Raven联动与万圣节内容",
        "summary": "Apple官方1.41.0加入Raven联动皮肤、三款万圣节传奇皮肤，以及装备分解与材料兑换的Gear Workshop。",
        "impact": f"产品当前Google #{current_rank('googlePlay', 'Overgeared Hero')}、iOS #{current_rank('ios', 'Overgeared Hero')}；双端位置差距仍大，不据此断言统一拉动。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6755585789",
    },
    {
        "category": "城建策略 / 体验改版", "date": "2026-10-13",
        "title": "Clash of Clans重做Builder菜单与村庄管理入口",
        "summary": "Apple官方18.647.2重做Builder Suggestions并增加筛选与分类，同时调整Battle菜单、玩家资料与Clan Chat。",
        "impact": f"产品当前Google #{current_rank('googlePlay', 'Clash of Clans')}、iOS #{current_rank('ios', 'Clash of Clans')}；头部位置仍稳，改版更适合作为长期留存背景。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id529479190",
    },
    {
        "category": "4X / 赛季体验", "date": "2026-10-13",
        "title": "Top Heroes继续调整Lord Runes与赛季交互",
        "summary": "Apple官方1.124.6优化Lord Runes、Castle Gifting、Romance in Bloom排名页，并调整Cloudsea Odyssey赛季后的遗迹放弃时间。",
        "impact": f"产品当前Google #{current_rank('googlePlay', 'Top Heroes')}、iOS #{current_rank('ios', 'Top Heroes')}；两端均在中后段，需分别验证版本后的留榜。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6450953550",
    },
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google一进一出，整体稳定但出现单个11位下跌",
        "detail": "Google 59款共同产品中44款位移不超过2名，中位绝对变动1名；Arknights回榜前15，Ant Legion从#57掉榜，Game of Thrones: Conquest −11是唯一两位数变化。",
    },
    {
        "type": "判断", "title": "iOS五进五出，榜尾轮换与中段振幅同时扩大",
        "detail": "iOS 55款共同产品中29款位移不超过2名，中位绝对变动2名，13款变动至少5位；Sea War +19、The Battle Cats −14、Last Day on Earth −10。",
    },
    {
        "type": "判断", "title": "Arknights形成双端共同信号，其余跨端仍明显分化",
        "detail": f"Arknights随Episode 17同步进入Google #{current_rank('googlePlay', 'Arknights')}与iOS #{current_rank('ios', 'Arknights')}；Age of Empires为Google上升、iOS回落，Game of Thrones: Conquest亦呈相反方向。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证Arknights主线更新承接",
        "detail": "若Google仍在前20、iOS仍在前10，双端共同信号才具连续性；若任一端迅速退出，则维持为Episode 17开放窗口内的短峰。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：检查iOS后十名回榜产品",
        "detail": "SimCity、Kiss of War与War Machines均在#52以后；重点看万圣节赛季能否让SimCity脱离榜尾，以及另外两款是否立即再掉榜。",
    },
    {
        "type": "关注", "title": "10月20日前后：区分Hearthstone持续改善与The Tower短峰",
        "detail": "Hearthstone需在正式资料片发布前后保持前25；The Tower若继续从#43走弱，则把昨日+25视为v29窗口内的一次性峰值。",
    },
]


google_history = load("data/history/google-play/2026-10-15.json")
ios_history = load("data/history/ios/2026-10-15.json")
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
    "title": "Arknights双端强势回榜，iOS五进五出并扩大波动",
    "summary": "较10月14日前一有效快照，Google Play一进一出：Arknights回榜前15、Ant Legion从#57掉榜；Game of Thrones: Conquest −11，Age of Empires +7。iOS五进五出：Arknights、Summoners War、SimCity、Kiss of War与War Machines回榜，另有5款掉榜；Sea War +19、The Battle Cats −14、Last Day on Earth −10。近90天新品为Google 1款、iOS 2款；两端缺少7月17日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261015.json",
    "rankingSources": {"googlePlay": "data/games-20261015.json", "ios": "data/ios-games-20261015.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261014.json", "ios": "data/ios-games-20261014.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Lands of Jail · #60 Doomsday: Undead Bride",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": f"榜单锚点：#1 Kingshot · #25 {datasets['ios']['now'][24]['gameName']} · #60 War Machines：Battle Tank Games",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-17"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-17"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-15.md", "json": "data/market-brief-20261015.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-14；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-17精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261015.json", brief)
(ROOT / "reports/2026-10-15.md").write_text(build_markdown(brief), encoding="utf-8")
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
