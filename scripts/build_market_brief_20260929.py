#!/usr/bin/env python3
"""Generate the Beijing 2026-09-29 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, CURRENT, PREVIOUS = "2026-09-29", "20260929", "20260929", "20260928"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load(f"data/games-{CURRENT}.json"), "prior": load(f"data/games-{PREVIOUS}.json"), "id": "packageName"},
    "ios": {"now": load(f"data/ios-games-{CURRENT}.json"), "prior": load(f"data/ios-games-{PREVIOUS}.json"), "id": "appId"},
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


google_history = load("data/history/google-play/2026-09-29.json")
ios_history = load("data/history/ios/2026-09-29.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Draft Showdown", "entry", "回到Google #55，iOS也回榜#29。9月25日Apple版本新增单位并修复问题，可作为近期内容背景，但双端回榜仍需下一有效快照验证。"),
    card("googlePlay", "Game of Thrones: Conquest", "entry", "回到Google #60，iOS同步回榜#36。9月21日Dragonseeds版本加入Alys Rivers、Hugh Hammer及新装备；内容节点明确，但Google仍处掉榜线。"),
    card("googlePlay", "Last Fortress", "exit", "从Google上期#56掉榜，iOS继续未进入TOP60；成熟生存SLG前一日回落后的榜尾风险兑现，未发现可确认的同日运营节点。"),
    card("googlePlay", "Limbus Company", "exit", "从Google上期#60掉榜，iOS前一日已退出。两端先后跌出TOP60，只能确认策略分类榜可见度回落，不能据此推算收入变化。"),
    card("googlePlay", "Lords Mobile", "up", "Google升6位至#29、iOS升5位至#48，是今天较清晰的双端同向改善；Transformers联动仍在运营窗口，但当前数据不足以确认因果。"),
    card("googlePlay", "Kingdom Rush 6", "up", "Google升5位至#52、iOS跌8位至#54。两端均处首发验证后段，Android改善未抵消iPhone端继续回落的分化。"),
    card("googlePlay", "League of Legends", "down", "Google跌9位至#56，iOS已连续缺席；该产品属于MOBA分类边界，今天只记录Google榜尾风险，不纳入核心策略收入判断。"),
    card("googlePlay", "Infinity Kingdom", "down", "Google跌5位至#36，iOS却升4位至#41；昨日双端共同回落未延续，今天应改记为平台分化而非持续走弱。"),
]


ios_products = [
    card("ios", "Draft Showdown", "entry", "回到iOS #29，Google也回榜#55。9月25日版本新增单位并修复问题；iPhone端位置明显高于Android，但仍需连续快照确认。"),
    card("ios", "Game of Thrones: Conquest", "entry", "回到iOS #36、Google #60。Dragonseeds版本提供可核验内容背景，双端回归成立，但Google端仍贴近掉榜线。"),
    card("ios", "Rise of Castles", "entry", "回到iOS #38，Google当前#16。9月26日版本只列性能优化与缺陷修复，无法把本次回榜归因于明确活动。"),
    card("ios", "Kingdom Guard", "entry", "回到iOS #55，Google未进入TOP60。Fruit Market活动已于9月27日结束，活动末期与回榜相邻但不构成因果证明。"),
    card("ios", "Summoners War", "exit", "从iOS上期#49掉榜，Google策略榜未收录；没有找到与本次退出同日的官方重大节点，先按榜尾轮换处理。"),
    card("ios", "Galaxy Defense", "exit", "从iOS上期#55掉榜。Season: Expedition与Kronos Exploration仍是近期内容背景，但没有形成连续留榜。"),
    card("ios", "Cell Survivor", "exit", "从iOS上期#59掉榜。3.9主题场景更新后的回榜只维持一个有效快照，榜尾承接尚不稳定。"),
    card("ios", "Sea of Conquest", "exit", "首次进入项目榜后次日即从#60退出；联动末期信号没有形成持续留榜，Google同口径也未收录。"),
    card("ios", "Watcher of Realms", "down", "iOS跌16位至#51，为本端最大回落之一；9月22日公会Boss、新阵营与公会战赛季仍在，但内容窗口未阻止单日回吐。"),
    card("ios", "Kiss of War", "down", "iOS跌16位至#52，Google却升3位至#46；昨日的双端共同改善没有延续，今天改记为平台分化。"),
    card("ios", "Kingdom Rush 6", "down", "iOS再跌8位至#54，Google升5位至#52。首发后两端都落在后十名附近，系列IP的持续付费承接仍处验证期。"),
    card("ios", "Sea War", "down", "iOS跌7位至#30，Google升3位至#35；昨日双端同步上涨未延续，单日峰值应继续按待验证信号处理。"),
    card("ios", "Star Trek Fleet Command", "down", "iOS跌7位至#57。M95.1 Haven基地版本虽在9月28日再次更新，但当前回榜后继续下移，尚未脱离榜尾风险。"),
    card("ios", "Supremacy", "down", "iOS跌6位至#43；0.242平衡更新仍是近期节点，但昨日上涨未延续，不能把短期波动写成长线转折。"),
    card("ios", "Raid Rush", "up", "iOS升5位至#35、Google升1位至#54。双端同向但幅度有限，暂按轻度改善信号处理。"),
    card("ios", "Boom Beach", "up", "iOS升5位至#53，九月Blitz活动仍在可核验窗口；产品仍处后十名，活动承接强度需继续观察。"),
]


news = [
    {
        "category": "双端回榜 / 新单位",
        "date": "2026-09-25",
        "title": "Draft Showdown更新新单位后双端回榜",
        "summary": "Apple官方1.17.0版本说明确认加入新单位，并包含体验改进与缺陷修复。",
        "impact": "本期iOS回到#29、Google回到#55；内容节点与回榜相邻，但需下一有效快照确认是否能连续留榜。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6743368869",
    },
    {
        "category": "IP 4X / 龙裔版本",
        "date": "2026-09-21",
        "title": "Game of Thrones: Conquest以Dragonseeds版本双端回归",
        "summary": "Apple官方版本说明加入Alys Rivers、Hugh Hammer、Dragonseed装备与新的龙装备。",
        "impact": "本期iOS回到#36、Google回到#60；IP版本仍提供召回入口，但Android端尚未脱离掉榜线。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1035712810",
    },
    {
        "category": "太空4X / 高等级基地",
        "date": "2026-09-28",
        "title": "Star Trek Fleet Command继续推进Haven基地版本",
        "summary": "M95.1.1继续围绕Ops 61+的Haven行星基地、全账号增益、Frontier Prestige与高阶成长展开。",
        "impact": "产品iOS跌至#57，说明明确版本节点尚未形成稳定榜位承接；仍需观察高等级内容覆盖面。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1427744264",
    },
    {
        "category": "城建生存 / 社交功能",
        "date": "2026-09-28",
        "title": "Tiles Survive加入世界地图表情互动",
        "summary": "2.6.200版本向达到指定Power Plant等级的玩家开放World Map Emoji，可在城镇与行军队列上使用。",
        "impact": "产品Google #19、iOS升至#26；新增的是社交表达层，是否增强联盟留存仍需后续数据验证。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6738109752",
    },
    {
        "category": "经典塔防 / 首发修复",
        "date": "2026-09-28",
        "title": "Kingdom Rush 6首发后继续修复，但双端落在后十名",
        "summary": "Apple 1.00.040版本标注缺陷修复与改进；产品仍以Linirea前传、15座塔、双英雄和离线战役为核心。",
        "impact": "Google升至#52、iOS跌至#54；双端可见但首发峰值后的持续付费承接仍未稳定。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6759664029",
    },
    {
        "category": "塔防SLG / 活动末期",
        "date": "2026-09-27",
        "title": "Kingdom Guard Fruit Market结束后回到iOS榜尾",
        "summary": "1.0.593版本说明显示Fruit Market活动期为9月22日至27日，并修复酒馆英雄与弹窗显示问题。",
        "impact": "产品本期回到iOS #55、Google未入榜；活动结束与回榜时间相邻，但不足以证明活动拉动。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1570095804",
    },
    {
        "category": "现代战争 / 平衡更新",
        "date": "2026-09-25",
        "title": "Supremacy调整兵种学说、动员与无障碍选项",
        "summary": "0.242版本调整Tank Destroyer学说与动员平衡，并修复飞机、导弹、情报人员及界面问题。",
        "impact": "产品iOS回落至#43；前一日上涨没有延续，版本影响仍需更长窗口判断。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1510997559",
    },
    {
        "category": "成熟4X / 性能维护",
        "date": "2026-09-26",
        "title": "Rise of Castles性能更新后回到iOS #38",
        "summary": "26.902.1版本仅披露性能优化和缺陷修复，没有列出新赛季或重大玩法系统。",
        "impact": "产品iOS回榜、Google位于#16；没有明确内容事件时，应把单日回归视为待验证信号。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1411917616",
    },
    {
        "category": "村庄经营 / 高本成长",
        "date": "2026-09-24",
        "title": "Clash of Clans继续扩展Town Hall 18成长线",
        "summary": "18.600.7版本加入新的宠物与Supercharge等级，并继续修复14周年皮肤显示问题。",
        "impact": "产品双端仍居前列；高本成长扩展属于长线付费与回流支撑，而非短期新品信号。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id529479190",
    },
    {
        "category": "全球收入月榜",
        "date": "2026-09-04",
        "title": "Sensor Tower最新官方月榜仍为2026年8月",
        "summary": "全球App Store与Google Play消费者支出估算约65.7亿美元；Whiteout Survival全球总榜#3、Kingshot #7。",
        "impact": "两款均较7月上升1位；官方未披露单品同比，不能把榜位变化换算成收入增幅。",
        "source": "Sensor Tower官方",
        "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026",
    },
]


closing = [
    {
        "type": "判断",
        "title": "Google继续稳定，iOS波动收窄但仍高于Android",
        "detail": "Google两进两出，58款共同产品中44款变动不超过2位，中位绝对变动1位且前10全部保留；iOS四进四出，56款共同产品中28款变动不超过2位，中位绝对变动2.5位、前10保留9款。",
    },
    {
        "type": "判断",
        "title": "双端共同回榜集中在IP与轻量对战产品",
        "detail": "Draft Showdown回到iOS #29与Google #55，Game of Thrones: Conquest回到iOS #36与Google #60；两款都有近期版本背景，但Android端均未脱离后六名，尚不能判断为稳定复苏。",
    },
    {
        "type": "判断",
        "title": "前一日多项同步信号未延续，单日波动需降级解读",
        "detail": "Kiss of War转为Google +3、iOS -16，Sea War转为Google +3、iOS -7，Infinity Kingdom转为Google -5、iOS +4；昨日的同向变化没有形成连续趋势。",
    },
    {
        "type": "关注",
        "title": "未来1—2个有效快照：检验双端回榜的持续性",
        "detail": "Draft Showdown需让Google脱离后五名，Game of Thrones: Conquest需让Google脱离#60，才把今天的双端回归升级为连续改善。",
    },
    {
        "type": "关注",
        "title": "未来两日：观察Kingdom Rush 6能否守住双端TOP60",
        "detail": "当前Google #52、iOS #54；若任一端继续回落并掉榜，更接近系列IP首发峰值后的正常衰减，若两端稳定在前50再评估持续承接。",
    },
    {
        "type": "关注",
        "title": "下一有效快照：核对iOS后十名的继续换榜风险",
        "detail": "Watcher、Kiss、Boom Beach、Kingdom Rush 6、Kingdom Guard、Star Trek与MARVEL SNAP集中在#51—#59；若版本产品继续退出，说明本周iOS榜尾轮换仍未稳定。",
    },
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Draft Showdown与Game of Thrones双端回榜，iOS波动仍高于Google",
    "summary": "较9月28日最终有效快照，Google Play两进两出：Draft Showdown、Game of Thrones: Conquest回榜，Last Fortress、Limbus Company掉榜；Lords Mobile +6，Wild Rift -9。iOS四进四出：Draft Showdown、Game of Thrones: Conquest、Rise of Castles、Kingdom Guard回榜，Summoners War、Galaxy Defense、Cell Survivor、Sea of Conquest掉榜；Watcher与Kiss各-16。Draft Showdown和Game of Thrones形成双端共同回归，但Google名次仍靠后；近90天新品两端各3款，较老产品因缺少7月1日精确基准不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": f"data/games-{CURRENT}.json", "ios": f"data/ios-games-{CURRENT}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREVIOUS}.json", "ios": f"data/ios-games-{PREVIOUS}.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Police Chief · #60 Game of Thrones: Conquest",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Rise of Kingdoms · #60 Guns of Glory: Lost Island",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-01"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-01"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-29.md", "json": "data/market-brief-20260929.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-09-28；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-01精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20260929.json", brief)
(ROOT / "reports/2026-09-29.md").write_text(build_markdown(brief), encoding="utf-8")
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
