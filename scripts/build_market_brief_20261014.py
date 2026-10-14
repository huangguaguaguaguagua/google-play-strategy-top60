#!/usr/bin/env python3
"""Generate the Beijing 2026-10-14 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-14", "20261014"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {
        "now": load("data/games-20261014.json"),
        "prior": load("data/games-20261013.json"),
        "id": "packageName",
    },
    "ios": {
        "now": load("data/ios-games-20261014.json"),
        "prior": load("data/ios-games-20261013.json"),
        "id": "appId",
    },
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


def card(store, prefix, tone, analysis, first=False):
    data, ident = datasets[store], datasets[store]["id"]
    found = [row for row in data["now"] + data["prior"] if row["gameName"].startswith(prefix)]
    ids = {str(row[ident]) for row in found}
    if len(ids) != 1:
        raise RuntimeError(f"Ambiguous market card {store}:{prefix}: {ids}")
    product_id = ids.pop()
    current = next((row for row in data["now"] if str(row[ident]) == product_id), None)
    previous = next((row for row in data["prior"] if str(row[ident]) == product_id), None)
    if tone == "entry" and current and not previous:
        label = f"{'首次进入' if first else '回榜'} · #{current['rank']}"
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
    card("googlePlay", "Age of Empires Mobile", "entry", "回到Google #54，且iOS同步回榜#21，但两端相差33位。10月8日官方1.14.202仅披露错误修复，双端回补先记为待验证信号，不据此认定内容拉动。"),
    card("googlePlay", "Call of Dragons", "exit", "从Google上期#60掉榜，iOS当前也未进入TOP60。它只是从截线位置滑出，未发现与今天同日的可确认重大产品节点。"),
    card("googlePlay", "Overgeared Hero", "up", "Google上升5位至#34，而iOS下跌6位至#54。10月13日Raven联动皮肤、三款万圣节传奇皮肤与装备工坊已上线；相反方向说明单日榜位不能统一归因。"),
    card("googlePlay", "Lords Mobile", "up", "Google上升5位至#35，iOS也上升6位但仅到#52。Transformers联动仍在产品标题与商店展示中，两端同向改善仍需下一有效快照确认。"),
    card("googlePlay", "MARVEL SNAP", "down", "Google下跌10位至#47，为本端最大下跌；iOS反而上升2位至#38。两端相反方向且未发现同日可确认转折，先按平台分化记录。"),
    card("googlePlay", "Rise of Castles", "down", "Google下跌5位至#31，iOS未进入TOP60。当前仍在前半榜，未发现与单日回落对应的可确认重大版本节点。"),
]


ios_products = [
    card("ios", "Age of Empires Mobile", "entry", "回到iOS #21，同时回到Google #54。iPhone端位置高33名，但官方10月8日版本只写错误修复；跨端同日回补需要连续快照验证。"),
    card("ios", "Evo Defense", "entry", "回到iOS #49，Google当前未进入TOP60。9月17日Everbloom限时活动与Style Switch已运行近四周，今天只能确认榜尾回补，不能断言活动造成。"),
    card("ios", "Plants on Fire", "entry", "回到iOS #60且恰处末位；产品8月26日上架，仍按近90天新品展示。Pirate Captain与Ace Plan是最近版本背景，留榜尚待下一快照验证。"),
    card("ios", "Kingdom Guard", "exit", "从iOS上期#45掉榜，Google当前也未进入TOP60。9月Fruit Market活动已经结束，未发现与今天掉榜同日的可确认节点。"),
    card("ios", "Summoners War", "exit", "从iOS上期#54掉榜。9月30日怪物技能平衡与制作体验更新未能让产品脱离榜尾，本次只记录截线失守，不把版本与掉榜写成因果。"),
    card("ios", "Cell Survivor", "exit", "从iOS上期#56掉榜；Apple官方10月14日4.1版本同日开启一周年活动并修复问题。活动上线与掉榜并存，后续若回榜再检验承接。"),
    card("ios", "The Tower", "up", "iOS上升25位至#34，为本端最大上涨。10月6日v29加入全局预设、Mythic赛事联赛、重做Vault与Harmony Tree；时间相邻但仍需连续榜位确认。"),
    card("ios", "Hearthstone", "up", "iOS上升22位至#31。10月13日37.0开启新竞技场赛季并预载Reign of the Black Empire内容，时间高度重合，但单次跃升仍只记为待验证活动峰值。"),
    card("ios", "Watcher of Realms", "down", "iOS下跌23位至#56，为本端最大下跌；9月22日Guild Boss、新阵营与公会战赛季已不属于同日节点，当前已落入后五名风险区。"),
    card("ios", "Warline", "down", "iOS下跌9位至#44，回吐上期7位上涨；Google则上升1位至#28。作为7月22日上架的近90天新品，仍处首发后波动而非成熟趋势。"),
    card("ios", "Lands of Jail", "down", "iOS下跌8位至#39，几乎回吐上期9位上涨；Google只下跌1位至#25。两端幅度分化且没有同日可确认节点。"),
]


news = [
    {
        "category": "全球收入月榜", "date": "2026-10-01",
        "title": "Sensor Tower最新官方月榜仍为9月，核心策略子集共3款",
        "summary": "官方完整全球收入TOP10中，Whiteout Survival为总榜#6、Last War: Survival #7、Kingshot #9；本次单次检查未发现更新月份。",
        "impact": "Last War为新进全球TOP10，Whiteout与Kingshot较8月分别下降3位和2位；这是全球总榜名次变化，不是单品收入同比。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
    {
        "category": "卡牌策略 / 新资料片", "date": "2026-10-12",
        "title": "Hearthstone 37.0开启Black Empire预发布与新竞技场赛季",
        "summary": "Blizzard官方说明37.0于10月13日上线，Reign of the Black Empire将于10月20日正式发布；补丁先行加入新竞技场卡池、预发布乱斗、Journal与奖励内容。",
        "impact": "产品本期iOS +22至#31；版本时间与跃升高度重合，但仍要看10月20日前后是否形成连续承接。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "长线4X / 周年", "date": "2026-10-05",
        "title": "Game of Thrones: Conquest进入九周年月",
        "summary": "官方10月预览宣布Military III与Dragon Combat两棵研究树、Old Nan's Tales内容，以及Viserion、Free Folk装备和10月26日英雄活动。",
        "impact": "产品当前Google #42、iOS #51且单日持平；九周年内容体量明确，但商业化承接仍需活动窗口后的榜位验证。",
        "source": "Game of Thrones: Conquest官方", "url": "https://www.gotconquest.com/news/2026/10/05/october-preview-9th-anniversary-celebration/",
    },
    {
        "category": "背包策略 / IP联动", "date": "2026-10-13",
        "title": "Overgeared Hero加入Raven联动皮肤与万圣节内容",
        "summary": "Apple官方1.41.0加入Raven联动皮肤、三款万圣节传奇皮肤，并开放装备分解与材料兑换的Gear Workshop。",
        "impact": "产品本期Google +5至#34、iOS −6至#54；内容上线与跨端反向变动并存，不能写成统一拉动。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6755585789",
    },
    {
        "category": "增量塔防 / 大版本", "date": "2026-10-06",
        "title": "The Tower v29后跃升至iOS #34",
        "summary": "Apple官方v29加入Global Presets与Preset Lab、Mythic锦标赛联赛、重做Vault、Harmony Tree升级及新卡牌和模块内容。",
        "impact": "本期单日+25为iOS最大上涨；版本已上线约一周，仍需下一有效快照排除一次性峰值。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1575590830",
    },
    {
        "category": "塔防 / 周年活动", "date": "2026-10-14",
        "title": "Cell Survivor开启一周年活动却从iOS TOP60掉榜",
        "summary": "Apple官方4.1版本在本次RSS更新前上线，说明一周年活动已开启并修复已知问题。",
        "impact": "活动与掉榜同日出现，说明节点存在不等于畅销名次即时上涨；未来1—2个快照若回榜才构成承接证据。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6746465127",
    },
    {
        "category": "卡牌策略 / 数字限定", "date": "2026-10-13",
        "title": "MTG Arena上线Alchemy: Reality Fracture",
        "summary": "Apple官方2026.64.0加入31张digital-only卡牌，并将其描述为最后一次Alchemy发布及配套庆祝内容。",
        "impact": "产品本期iOS −6至#26，仍在前半榜；新内容与单日回落并存，需观察后续构筑环境的持续性。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1496227521",
    },
    {
        "category": "城建策略 / 体验改版", "date": "2026-10-13",
        "title": "Clash of Clans重做Builder菜单与村庄管理入口",
        "summary": "Apple官方18.647.2重做Builder Suggestions，增加筛选与分类，并调整Battle菜单、玩家资料与Clan Chat。",
        "impact": "产品当前Google #8、iOS +1至#7；头部位置稳定，体验改版更适合作为长期留存背景而非单日收入解释。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id529479190",
    },
    {
        "category": "4X / 赛季体验", "date": "2026-10-13",
        "title": "Top Heroes继续调整Lord Runes与赛季交互",
        "summary": "Apple官方1.124.6优化Lord Runes、Castle Gifting、Romance in Bloom排名页，并调整Cloudsea Odyssey赛季后的遗迹放弃时间。",
        "impact": "产品本期Google +4至#40、iOS −6至#50；版本一致但平台方向相反，后续需分别验证。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6450953550",
    },
    {
        "category": "三消SLG / 万圣节版本", "date": "2026-10-12",
        "title": "Puzzles & Survival上线万圣节外观与Bomb Fusion",
        "summary": "Apple官方4.0.241加入万圣节外观、Gold M.Card、限时Match-3 Bomb Fusion，并增加Sorting Reagent与Gem Master关卡。",
        "impact": "产品当前Google +1至#13、iOS −2至#24；双端幅度温和且方向不同，暂不判断活动效果。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1517980891",
    },
]

for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google只有一进一出，但中段位移明显放大",
        "detail": "Google 59款共同产品中49款位移不超过2名，中位绝对变动1名；Age of Empires回到#54、Call of Dragons从#60掉榜，MARVEL SNAP −10远大于其余变动。",
    },
    {
        "type": "判断", "title": "iOS三进三出且出现两升一降的20位级波动",
        "detail": "iOS 57款共同产品中35款位移不超过2名，中位绝对变动2名；The Tower +25、Hearthstone +22、Watcher of Realms −23，榜面波动显著高于Google。",
    },
    {
        "type": "判断", "title": "同一内容节点在双端并不产生一致方向",
        "detail": "Age of Empires双端回榜但分别为iOS #21、Google #54；Overgeared在Raven与万圣节内容上线后Google +5、iOS −6，Top Heroes也呈Google +4、iOS −6。版本节点只能作背景。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证Age of Empires双端回榜",
        "detail": "重点看iOS #21能否守住前30、Google #54能否脱离后七名；若Google立即掉榜，应把本次判断维持为单日回补。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：复核Hearthstone、The Tower与Watcher",
        "detail": "Hearthstone需在37.0后保持前35，The Tower需维持前40；Watcher of Realms若从#56继续走弱，将面临直接掉榜风险。",
    },
    {
        "type": "关注", "title": "10月20日前后：区分新品波动与活动承接",
        "detail": "观察Hearthstone资料片正式上线后的持续性，以及近90天产品Warline #44、Plants on Fire #60是否留榜；后两者仍按首发验证而非成熟趋势处理。",
    },
]


google_history = load("data/history/google-play/2026-10-14.json")
ios_history = load("data/history/ios/2026-10-14.json")
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
    "title": "Age of Empires双端回榜，Hearthstone与The Tower跃升，iOS波动扩大",
    "summary": "较10月13日前一有效快照，Google Play一进一出：Age of Empires Mobile回榜#54、Call of Dragons从#60掉榜；Overgeared与Lords Mobile各+5，MARVEL SNAP −10。iOS三进三出：Age of Empires #21、Evo Defense #49、Plants on Fire #60回榜，Kingdom Guard、Summoners War、Cell Survivor掉榜；The Tower +25、Hearthstone +22、Watcher of Realms −23。近90天新品为Google 1款、iOS 3款；两端缺少7月16日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261014.json",
    "rankingSources": {"googlePlay": "data/games-20261014.json", "ios": "data/ios-games-20261014.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261013.json", "ios": "data/ios-games-20261013.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Lands of Jail · #60 Sea War: Uboat Raid",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Kingshot · #25 Mobile Legends: Bang Bang.US · #60 Plants on Fire",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-16"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-16"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-14.md", "json": "data/market-brief-20261014.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-13；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-16精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261014.json", brief)
markdown = build_markdown(brief)
(ROOT / "reports/2026-10-14.md").write_text(markdown, encoding="utf-8")
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
    key=lambda item: item["date"],
    reverse=True,
)
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
