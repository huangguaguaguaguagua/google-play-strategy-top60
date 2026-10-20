#!/usr/bin/env python3
"""Generate the Beijing 2026-10-20 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-20", "20261020"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261020.json"), "prior": load("data/games-20261019.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261020.json"), "prior": load("data/ios-games-20261019.json"), "id": "appId"},
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
    card("googlePlay", "Age of Spirits", "entry", "回到Google #58，并因9月16日上架继续按releaseDate归为近90天新品。10月16日更新加入萨满俘获、定向迁城和新装备槽，但回榜仍在截线附近，先视为首发验证期信号。"),
    card("googlePlay", "Limbus Company", "exit", "昨日刚回到Google #60，本期立即掉榜；iOS也已在前一快照退出。两端连续出现榜尾进出，说明回补尚未形成稳定承接。"),
    card("googlePlay", "Foundation: Galactic Frontier", "up", "Google上升6位至#29，iOS同时上升8位至#24，是本期少数双端共同改善产品；Fusion Seed科技、第四战斗队列与赛季调整是近期可核验背景，但仍不写成确定因果。"),
    card("googlePlay", "Infinity Kingdom", "down", "Google下跌4位至#35，iOS却上升6位至#43。两端都在中后段但方向相反，当前更像平台端短时差异，不足以定义产品整体转折。"),
]


ios_products = [
    card("ios", "Kingdom Clash", "entry", "回到iOS #45。10月19日3.3.0加入冰系史诗Boss Shai-Khold、新传奇兵种与银行平衡，版本和回榜时间相邻；仍需下一快照确认是否能留在中后段。"),
    card("ios", "Rise of Castles", "entry", "回到iOS #49，Google当前#43。10月19日版本说明只确认性能优化与修复，没有重大内容证据，因此不把本次成熟4X回榜归因于更新。"),
    card("ios", "Aliens vs Zombies", "entry", "回到iOS #51。官方排期的Halloween Boss Hunt于10月19日开启，与回榜相邻；活动可能提供观察背景，但单一快照不能证明拉动。"),
    card("ios", "Guns of Glory", "entry", "回到iOS #55，Google当前#39。10月19日14.3.0仅写界面与体验优化，缺少重大版本依据，本次先按成熟产品榜尾回补处理。"),
    card("ios", "Star Trek Fleet Command", "exit", "从iOS上期#55掉榜，Google仍在#21，跨端差距进一步扩大。Division 12活动仍在，但iPhone端退出不支持双端同步承接判断。"),
    card("ios", "SD Gundam", "exit", "上期回到iOS #58后本期即掉榜，只维持一个有效快照。IP与战术编队定位未变，当前更接近榜尾轮换，而非稳定复苏。"),
    card("ios", "Plants on Fire", "exit", "上期回到iOS #59后本期再次掉榜。产品仍处上架不足90天的首发验证期，但当前已不在TOP60，不能继续计入今日近90天新品数量。"),
    card("ios", "Bloons TD 6", "exit", "上期以#60回榜后本期掉榜；57.2版本窗口仍在，但最后一名回补只维持一个快照，版本时间相邻没有转化为可确认留位。"),
    card("ios", "Overgeared Hero", "up", "iOS上升16位至#41，Google当前#36。Raven联动皮肤、三款万圣节传奇皮肤和装备工坊是近期背景；双端名次接近，但活动贡献仍待复核。"),
    card("ios", "Top Heroes", "up", "iOS上升12位至#44，Google当前#28。两端都在榜但相差16位，未找到与今天同步的重大官方节点，先记录为单端改善。"),
    card("ios", "Foundation: Galactic Frontier", "up", "iOS上升8位至#24，Google同时升6位至#29，形成本期最清晰的双端共同改善；仍需连续快照区分赛季承接与单日波动。"),
    card("ios", "Summoners War", "down", "iOS下跌13位至#47。10月14日9.3.6加入Cosmic Worm并改善体验，但更新存在不等于收入上升；本次回落需与后续活动快照一起判断。"),
    card("ios", "Fire Emblem Heroes", "down", "iOS下跌12位至#53。10月16日新英雄与新章节窗口后快速回落到榜尾，像一次待验证的高位回吐，但不能换算成收入降幅。"),
    card("ios", "Watcher of Realms", "down", "上期回榜#48后本期下跌9位至#57，仍处高掉榜风险区；现有召唤活动背景不足以证明持续承接。"),
]


news = [
    {
        "category": "轻量策略 / Boss更新", "date": "2026-10-19",
        "title": "Kingdom Clash 3.3.0加入史诗Boss与新传奇兵种",
        "summary": "Apple官方版本记录显示3.3.0加入冰系Boss Shai-Khold、新传奇兵种，并重新平衡银行金币礼包。",
        "impact": f"产品本期回到iOS #{current_rank('ios', 'Kingdom Clash')}；版本与回榜时间相邻，但需要连续留榜才能确认承接。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id1611722542",
    },
    {
        "category": "塔防 / 万圣节活动", "date": "2026-10-19",
        "title": "Aliens vs Zombies开启Halloween Boss Hunt",
        "summary": "Apple官方1.22b说明将Boss Hunt定于10月19日开启，奖励包含Antigraviton防御塔；10月26日还将开启含七类活动的Halloween Night。",
        "impact": f"产品回到iOS #{current_rank('ios', 'Aliens vs Zombies')}；活动是时间背景，不足以单独解释回榜。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id6740232087",
    },
    {
        "category": "原始部落4X / 新品", "date": "2026-10-16",
        "title": "Age of Spirits加入萨满俘获与定向迁城",
        "summary": "Google Play官方更新说明加入PvP萨满俘获系统、7日增益与定向迁城，开放第七个萨满装备槽和更多集结队列，并提前Lv.9/Lv.10兵种。",
        "impact": f"产品本期回到Google #{current_rank('googlePlay', 'Age of Spirits')}，且按9月16日released日期归入近90天新品；榜尾回归仍需验证。",
        "source": "Google Play美国区商品页", "url": "https://play.google.com/store/apps/details?id=leyi.ageofspirits&hl=en_US&gl=US",
    },
    {
        "category": "合并RPG / IP联动", "date": "2026-10-13",
        "title": "Overgeared Hero上线Raven联动与万圣节皮肤",
        "summary": "Apple官方1.41.0记录加入Raven联动皮肤、三款万圣节传奇皮肤，并开放装备拆解与Gear Workshop材料交换。",
        "impact": f"产品本期iOS升16位至#{current_rank('ios', 'Overgeared Hero')}、Google位于#{current_rank('googlePlay', 'Overgeared Hero')}；双端名次趋近。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id6755585789",
    },
    {
        "category": "回合RPG / 长线运营", "date": "2026-10-14",
        "title": "Summoners War 9.3.6加入Cosmic Worm",
        "summary": "Apple官方版本记录显示9.3.6加入新魔灵Cosmic Worm，并同步改善体验和修复问题。",
        "impact": f"产品本期iOS回落13位至#{current_rank('ios', 'Summoners War')}；更新与榜位方向相反，不能把版本直接等同于收入抬升。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id852912420",
    },
    {
        "category": "战术RPG / 新英雄", "date": "2026-10-15",
        "title": "报道：Fire Emblem Heroes加入新双人英雄与新章节",
        "summary": "Final Weapon引用Nintendo Mobile公告称，10月16日更新加入Duo CYL Dimitri、Duo CYL Edelgard、Vista Hero Gullveig与“A Prince Lost”章节。",
        "impact": f"产品本期iOS跌12位至#{current_rank('ios', 'Fire Emblem Heroes')}；节点后回吐仍需后续快照确认。",
        "source": "Final Weapon（报道；引用Nintendo Mobile公告）", "url": "https://finalweapon.net/2026/10/15/fire-emblem-heroes-releases-duo-cyl-dimitri-duo-cyl-edelgard-on-october-16/",
    },
    {
        "category": "塔防RPG / 主线大版本", "date": "2026-10-14",
        "title": "Arknights Episode 17继续处于开放窗口",
        "summary": "官方公告将Episode 17开放日定为10月14日，并在10月28日前临时降低主线解锁要求；Apple端同期执行强制更新。",
        "impact": f"产品当前Google #{current_rank('googlePlay', 'Arknights')}、iOS #{current_rank('ios', 'Arknights')}；双端仍有25位差距。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4814",
    },
    {
        "category": "卡牌策略 / 资料片", "date": "2026-10-13",
        "title": "Hearthstone 37.0预载Reign of the Black Empire",
        "summary": "Blizzard官方37.0加入新资料片卡牌、Assemble关键词、新竞技场卡池和Journal更新。",
        "impact": f"产品本期iOS位于#{current_rank('ios', 'Hearthstone')}；正式发布窗口前的单日名次不能代表资料片最终表现。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "科幻4X / 赛季系统", "date": "2026-10-09",
        "title": "Foundation继续推进Fusion Seed科技与第四战斗队列",
        "summary": "产品官网近期资料聚焦Fusion Seed科技、35级建筑与第四战斗队列；Apple端版本同时调整科技解锁门槛、Shadowfront奖励与S2港口奖励。",
        "impact": f"产品本期Google升至#{current_rank('googlePlay', 'Foundation: Galactic Frontier')}、iOS升至#{current_rank('ios', 'Foundation: Galactic Frontier')}，需观察双端改善能否持续。",
        "source": "Foundation: Galactic Frontier官方", "url": "https://www.foundation.game/en/news",
    },
    {
        "category": "全球市场 / 收入榜", "date": "2026-10",
        "title": "Sensor Tower最新官方全球收入榜仍为2026年9月",
        "summary": "官方9月全球手游收入TOP10中，核心策略子集为Whiteout Survival #6、Last War #7与Kingshot #9；统计覆盖Apple App Store和Google Play，并排除第三方Android商店。",
        "impact": "本工作日未发现更新一期官方完整图表，因此继续保留9月真实统计期；全球月度子集不代替美国单区日榜。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google一进一出且50款位移不超过2名，稳定度进一步提高",
        "detail": "Google 59款共同产品中仅Foundation移动超过5位；Age of Spirits回榜#58、Limbus掉榜。除榜尾轮换外，主体结构没有明显重排。",
    },
    {
        "type": "判断", "title": "iOS四进四出，版本节点与名次方向继续错位",
        "detail": "iOS 56款共同产品中28款位移不超过2名、17款至少移动5位。Kingdom Clash与Aliens在活动窗口回榜，但Summoners War和Fire Emblem在内容更新后分别下跌13位、12位，不能用“有版本”概括走势。",
    },
    {
        "type": "判断", "title": "Foundation形成双端共同改善，榜尾新品则快速轮换",
        "detail": "Foundation升至Google #29与iOS #24，是本期最一致的跨端信号；Age of Spirits作为近90天新品回到Google #58，而Plants on Fire从iOS #59退出，首发期产品仍主要在截线附近换位。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证四款iOS回榜能否连续留榜",
        "detail": "Kingdom Clash、Rise of Castles、Aliens vs Zombies与Guns of Glory均在#45以后；若快速退出，仍按成熟产品或活动期榜尾轮换处理。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：跟踪Foundation的双端同步性",
        "detail": "若Google与iOS继续同时处于前30，可再结合Fusion Seed、S2奖励和活动证据判断阶段承接；若单端回落，则维持短时改善口径。",
    },
    {
        "type": "关注", "title": "至10月26日：复核万圣节内容与榜尾产品",
        "detail": "观察Aliens vs Zombies的Boss Hunt能否维持#51附近，并在Halloween Night开启后复核；Overgeared的Raven/万圣节内容也需看iOS能否守住中段。",
    },
]


google_history = load("data/history/google-play/2026-10-20.json")
ios_history = load("data/history/ios/2026-10-20.json")
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
    "title": "Google主体稳定，iOS四进四出；Foundation双端同步改善",
    "summary": "较10月19日前一有效快照，Google Play一进一出：Age of Spirits回到#58、Limbus掉榜，59款共同产品中50款位移不超过2名；Foundation +6至#29。iOS四进四出：Kingdom Clash、Rise of Castles、Aliens vs Zombies与Guns of Glory回榜，Star Trek、SD Gundam、Plants on Fire与Bloons退出；Overgeared +16、Top Heroes +12，Summoners War −13、Fire Emblem −12。近90天新品为Google 2款、iOS 1款；两端缺少7月22日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261020.json",
    "rankingSources": {"googlePlay": "data/games-20261020.json", "ios": "data/ios-games-20261020.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261019.json", "ios": "data/ios-games-20261019.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Rise of Kingdoms: Lost Crusade · #60 Raid Rush: Tower Defense TD",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Police Chief · #60 Last Day on Earth: Survival",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-22"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-22"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-20.md", "json": "data/market-brief-20261020.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-19；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-22精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261020.json", brief)
(ROOT / "reports/2026-10-20.md").write_text(build_markdown(brief), encoding="utf-8")
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
