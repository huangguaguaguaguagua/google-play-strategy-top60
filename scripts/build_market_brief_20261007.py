#!/usr/bin/env python3
"""Generate the Beijing 2026-10-07 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, CURRENT, PREVIOUS = "2026-10-07", "20261007", "20261007", "20261006"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261007.json"), "prior": load("data/games-20261006.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261007.json"), "prior": load("data/ios-games-20261006.json"), "id": "appId"},
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


google_history = load("data/history/google-play/2026-10-07.json")
ios_history = load("data/history/ios/2026-10-07.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Game of Thrones: Conquest", "entry", "回到Google #55，同时iOS上升11位至#39；Dragonseeds仍是最近可核验内容节点，但两端同步改善只有一个快照，先记为待验证信号。"),
    card("googlePlay", "Last Shelter: Survival", "entry", "回到Google #59。iOS榜内的Last Shelter: War Z是另一应用、另一产品ID与版本线，不把两者合并为同一跨端信号。"),
    card("googlePlay", "MARVEL SNAP", "exit", "从Google上期#55掉榜，iOS却上升18位至#23；Vampires vs Zombies赛季只提供iOS端内容背景，今天首先体现为明显的平台分化。"),
    card("googlePlay", "Sea of Conquest", "exit", "从Google上期#58掉榜，iOS则回到#59。联动活动接近结束是可核验背景，但相反方向不支持写成统一活动拉动。"),
    card("googlePlay", "League of Legends: Wild Rift", "down", "Google下跌8位至#52，iOS上一期已掉榜；该产品属于MOBA分类边界，本次只记录美国策略分类榜中的双端走弱。"),
]


ios_products = [
    card("ios", "Yu-Gi-Oh", "entry", "回到iOS #29，是七款回榜产品中唯一直接进入前30者；当前版本仍为7月的动画与界面更新，未发现与今天同日的重大节点。"),
    card("ios", "Sea War", "entry", "回到iOS #41，Google仍未进入TOP60；9月22日版本只有界面与错误修复，本次先按单端回补处理。"),
    card("ios", "Hearthstone", "entry", "回到iOS #52。Reign of the Black Empire预览卡、平衡调整与Battlegrounds Aberrations是近期背景，但仍处后九名。"),
    card("ios", "Galaxy Defense", "entry", "回到iOS #55。Season: Expedition测试期持续至10月15日，Kronos Exploration也在运行；内容窗口明确，但榜位仍接近截线。"),
    card("ios", "Plants on Fire", "entry", "回到iOS #56。产品8月26日上架，仍按近90天新品展示；Pirate Captain、两名新Minion与Ace Plan是近期版本背景，留榜尚待验证。"),
    card("ios", "Draft Showdown", "entry", "回到iOS #58。10月5日1.17.1主要修复技能、冻结、等级与本地化问题，并新增Discord入口；缺少足以解释回榜的新增核心内容。"),
    card("ios", "Sea of Conquest", "entry", "回到iOS #59，而Google从上期#58掉榜；联动活动接近结束，今天呈现平台分化且iPhone端仍属高掉榜风险。"),
    card("ios", "Overgeared Hero", "exit", "从iOS上期#46掉榜，Google仍位于中段；前一期上涨没有形成连续留榜，单日改善信号失效。"),
    card("ios", "Warpath", "exit", "从iOS上期#48掉榜；Age of Artisans版本后的榜尾回补只持续一个有效快照，暂未形成稳定承接。"),
    card("ios", "Kingdom Clash", "exit", "从iOS上期#51掉榜；成熟塔防产品继续在榜尾与榜外切换，未发现可确认的同日重大转折。"),
    card("ios", "Star Trek Fleet Command", "exit", "从iOS上期#52掉榜，Google仍为#19；同一产品跨端差异扩大，当前走弱只见于iPhone端。"),
    card("ios", "Boom Beach", "exit", "从iOS上期#57掉榜。10月5日Blitz版本后的回榜未延续到第二个有效快照，不能据此写成版本驱动增长。"),
    card("ios", "Lords Mobile", "exit", "从iOS上期#59掉榜，Google为#28；Transformers联动窗口仍在，但iPhone端已跌出策略TOP60。"),
    card("ios", "Top Heroes", "exit", "从iOS上期#60掉榜，Google为#43；Cloudsea Odyssey更新后的末位回补未延续，继续按榜尾轮换判断。"),
    card("ios", "MARVEL SNAP", "up", "iOS上升18位至#23，为本端最大上涨；Google却从#55掉榜。Vampires vs Zombies赛季是近期背景，但不能解释两端相反方向。"),
    card("ios", "Kingdom Guard", "down", "iOS下跌17位至#51，Google仍在#56；昨日双端改善未延续，且两端都回到榜尾风险区。"),
    card("ios", "Star Wars", "up", "iOS上升15位至#11，接近前10；9月15日版本只披露后端与性能优化，未发现可确认的同日内容转折。"),
    card("ios", "Age of Empires", "down", "iOS下跌14位至#57，Google为#58；Stormlands与Mounted Hunt版本背景没有阻止两端同时落入后四名。"),
    card("ios", "Evo Defense", "up", "iOS上升13位至#40。Everbloom限时活动与Style Switch是最近版本节点，但相隔近三周，今天仍按待验证峰值处理。"),
    card("ios", "Game of Thrones: Conquest", "up", "iOS上升11位至#39，同时Google回榜#55；Dragonseeds版本提供内容背景，但需要下一快照确认双端改善能否持续。"),
    card("ios", "Fire Emblem Heroes", "up", "iOS上升11位至#44。10月6日更新增加七名英雄的武器精炼与限时战斗手册，时间相邻但不能仅凭一天确认因果。"),
    card("ios", "Warhammer 40,000", "up", "iOS上升11位至#45，Google为#41；Ûthar活动已开始、Terminus生存活动排期10月10日，两端当前同处中段。"),
    card("ios", "Tiles Survive", "down", "iOS下跌8位至#32，Google为#21；两端仍在前32，但iPhone端未延续昨日温和改善。"),
    card("ios", "Summoners War", "down", "iOS下跌8位至#47。9月30日版本调整怪物平衡与制作体验，当前变化仍是单日回吐。"),
    card("ios", "Last Day on Earth", "down", "iOS下跌6位至#60且恰处末位；10月5日版本只简化授权与进度恢复，下一快照面临最高掉榜风险。"),
]


news = [
    {
        "category": "全球收入月榜", "date": "2026-10-01",
        "title": "Sensor Tower 9月全球收入TOP10的核心策略子集仍为3款",
        "summary": "官方完整图表显示Whiteout Survival全球总榜#6、Last War: Survival #7、Kingshot #9；全球App Store与Google Play消费者支出约61.3亿美元，排除第三方Android商店。",
        "impact": "截至本次检查未见更新月份；Last War为新进入全球TOP10，Whiteout与Kingshot较8月分别下降3位、2位。名次变化不等于单品收入同比。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
    {
        "category": "战棋RPG / 版本", "date": "2026-10-06",
        "title": "Fire Emblem Heroes新增武器精炼后iOS上升11位",
        "summary": "Apple官方10.10.0版本为Emblem Hero Ike等七名英雄加入可精炼武器技能，并更新Divine Codes: Ephemera 10限时战斗手册。",
        "impact": "产品本期升至iOS #44，更新时间相邻；仍需后续快照确认是版本承接还是单日峰值。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1181774280",
    },
    {
        "category": "战术竞技 / 修复", "date": "2026-10-05",
        "title": "Draft Showdown发布1.17.1后回到iOS #58",
        "summary": "官方版本修复Captain钩子、法术冻结、单位等级异常和本地化问题，并增加直达Discord的入口。",
        "impact": "更新主要是修复而非新增核心系统，且回榜位置处于后三名；不能据此确认内容拉动。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6743368869",
    },
    {
        "category": "末日生存 / 账户体验", "date": "2026-10-05",
        "title": "Last Day on Earth简化恢复流程但跌至iOS末位",
        "summary": "官方1.52.9版本仅披露简化授权和进度恢复流程。",
        "impact": "产品本期下跌6位至#60，说明体验修复与短期畅销名次并非单向对应；下一快照面临掉榜风险。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1241932094",
    },
    {
        "category": "新品 / 卡牌塔防", "date": "2026-09-29",
        "title": "Plants on Fire以Pirate Captain版本回到iOS后段",
        "summary": "官方2.0.2810版本让Pirate Captain回归，加入Chuckleberry、Thornmelon、四种Variant和Ace Plan活动。",
        "impact": "该产品8月26日上架，本期回到iOS #56并继续按近90天新品展示；首发验证尚未脱离榜尾。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6776076449",
    },
    {
        "category": "长线RPG / 平衡", "date": "2026-09-30",
        "title": "Summoners War调整怪物平衡后本期回吐8位",
        "summary": "官方9.3.4版本调整怪物技能平衡，并改善Magic Crafting与其他使用体验。",
        "impact": "产品本期跌至iOS #47；版本节点可作背景，但不能替代榜位连续性判断。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id852912420",
    },
    {
        "category": "塔防 / 赛季", "date": "2026-09-22",
        "title": "Galaxy Defense在Season: Expedition测试期回到iOS #55",
        "summary": "官方1.0.1版本加入Season: Expedition测试赛季，Expedition阶段为9月21日至10月15日，并上线Kronos Exploration。",
        "impact": "活动仍在运行，但产品只回到后六名；10月15日前的留榜情况将验证赛季承接。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6740189002",
    },
    {
        "category": "卡牌 / 新资料片预热", "date": "2026-09-24",
        "title": "Hearthstone以Black Empire预览内容回到iOS #52",
        "summary": "官方36.6版本提供Reign of the Black Empire免费预览卡，调整Standard与Battlegrounds平衡，并加入Aberrations随从类型。",
        "impact": "产品重新进入TOP60但仍在后九名，资料片预热是否形成持续付费可见度仍待观察。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id625257520",
    },
    {
        "category": "海盗SLG / 联动", "date": "2026-09-24",
        "title": "Sea of Conquest联动收尾期出现跨端反向变化",
        "summary": "Apple官方1.1.800版本提示联动活动接近结束，并提醒获取联动英雄与奖励。",
        "impact": "产品本期回到iOS #59，却从Google上期#58掉榜；相反方向不支持写成统一活动拉动。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6463715971",
    },
    {
        "category": "战术RPG / 活动", "date": "2026-09-04",
        "title": "Tacticus在Ûthar与Terminus活动之间上升11位",
        "summary": "官方版本说明列出10月4日Ûthar传奇活动，并排期10月10日Terminus生存活动。",
        "impact": "产品本期升至iOS #45、Google #41；10月10日前后能否继续改善可检验活动窗口的承接。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1599937506",
    },
]


closing = [
    {
        "type": "判断", "title": "Google保持稳定，iOS中后段换位继续放大",
        "detail": "Google两进两出，58款共同产品中53款变动不超过2位，中位绝对变动1位；iOS七进七出，53款共同产品仅30款变动不超过2位，中位绝对变动2位，且单品最大波动达到18位。",
    },
    {
        "type": "判断", "title": "Game of Thrones双端改善，但MARVEL SNAP与Sea of Conquest分化",
        "detail": "Game of Thrones: Conquest回到Google #55并在iOS +11至#39；MARVEL SNAP从Google掉榜却在iOS +18至#23，Sea of Conquest从Google掉榜却回到iOS #59。单日跨端相反方向不能合并成统一产品趋势。",
    },
    {
        "type": "判断", "title": "明确内容节点仍需由连续榜位验证",
        "detail": "Fire Emblem在10月6日更新后上涨11位；Draft Showdown在修复版本后仅回到#58，Last Day on Earth在账户体验更新后跌至#60。版本时间相邻只能作为背景，不足以证明收入驱动。",
    },
    {
        "type": "关注", "title": "下一有效快照：复核Google两款回榜与Wild Rift",
        "detail": "Game of Thrones #55、Last Shelter: Survival #59均在后六名，Wild Rift跌至#52；若无法连续留榜或回升，应维持榜尾回补与走弱判断。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：检验iOS七款回榜产品",
        "detail": "Yu-Gi-Oh回到#29，其余六款位于#41—#59。至少连续两次留榜，且有后段产品进入前45，才说明本轮换榜形成承接。",
    },
    {
        "type": "关注", "title": "10月10日至15日：核对Tacticus与Galaxy Defense活动窗口",
        "detail": "Tacticus的Terminus活动排期10月10日，Galaxy Defense的Expedition测试期至10月15日；分别观察能否从#45与#55继续改善，而不是只出现一次回补。",
    },
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Game of Thrones双端改善，MARVEL SNAP跨端分化，iOS七进七出",
    "summary": "较10月6日前一有效快照，Google Play两进两出：Game of Thrones: Conquest #55、Last Shelter: Survival #59回榜，MARVEL SNAP与Sea of Conquest掉榜；Wild Rift −8至#52。iOS七进七出：Yu-Gi-Oh #29、Sea War #41、Hearthstone #52、Galaxy Defense #55、Plants on Fire #56、Draft Showdown #58、Sea of Conquest #59回榜，Overgeared Hero、Warpath、Kingdom Clash、Star Trek、Boom Beach、Lords Mobile、Top Heroes掉榜；MARVEL SNAP +18、Kingdom Guard −17、Star Wars +15、Age of Empires −14。近90天新品为Google 2款、iOS 3款，较老产品因缺少7月9日精确基准不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261007.json",
    "rankingSources": {"googlePlay": "data/games-20261007.json", "ios": "data/ios-games-20261007.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261006.json", "ios": "data/ios-games-20261006.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Top Girl · #60 GIRLS’ FRONTLINE 2: EXILIUM",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Kingshot · #25 Top Force: Commander · #60 Last Day on Earth: Survival",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-09"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-09"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-07.md", "json": "data/market-brief-20261007.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-06；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-09精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261007.json", brief)
(ROOT / "reports/2026-10-07.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {
    "date": DATE,
    "title": brief["title"],
    "summary": brief["summary"],
    "markdown": brief["downloads"]["markdown"],
    "json": brief["downloads"]["json"],
}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
