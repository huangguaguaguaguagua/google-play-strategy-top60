#!/usr/bin/env python3
"""Generate the Beijing 2026-11-03 market brief and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-11-03", "20261103"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261103.json"), "prior": load("data/games-20261102.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261103.json"), "prior": load("data/ios-games-20261102.json"), "id": "appId"},
}


def find(store, prefix):
    data = datasets[store]
    rows = [row for row in data["now"] + data["prior"] if row["gameName"].startswith(prefix)]
    ids = {str(row[data["id"]]) for row in rows}
    if len(ids) != 1:
        raise RuntimeError(f"Ambiguous {store}:{prefix}: {ids}")
    product_id = ids.pop()
    return product_id, next(row for row in rows if str(row[data["id"]]) == product_id)


def card(store, prefix, tone, analysis):
    data = datasets[store]
    product_id, row = find(store, prefix)
    current = next((x for x in data["now"] if str(x[data["id"]]) == product_id), None)
    previous = next((x for x in data["prior"] if str(x[data["id"]]) == product_id), None)
    if tone == "entry" and current and not previous:
        label = f"回榜 · #{current['rank']}"
    elif tone == "exit" and previous and not current:
        label = f"掉榜 · 上期#{previous['rank']}"
    elif tone in ("up", "down") and current and previous:
        delta = previous["rank"] - current["rank"]
        if (delta > 0) != (tone == "up"):
            raise RuntimeError(f"Direction mismatch {store}:{prefix}:{delta}")
        label = f"{'+' if delta > 0 else '−'}{abs(delta)} · #{current['rank']}"
    else:
        raise RuntimeError(f"Membership mismatch {store}:{prefix}:{tone}")
    return {
        "gameName": (current or previous)["gameName"], "productId": product_id,
        "iconKey": f"{store}:{product_id}", "tone": tone,
        "changeLabel": label, "analysis": analysis,
    }


google_products = [
    card("googlePlay", "Duck Survival", "up", "上升9位至#44，是Google本期最大升幅；产品仍在后十七名，暂按单日回补信号处理。"),
    card("googlePlay", "Clash Royale", "up", "上升6位至#17，iOS同步上升6位至#7；双端同向改善成立，但仍需后续快照确认持续性。"),
    card("googlePlay", "Overgeared", "up", "上升4位至#43，同时iOS同产品回榜#47；联动版本时间相邻，但不据单日榜位断言因果。"),
    card("googlePlay", "Game of Thrones: Conquest", "down", "下跌9位至#52，而iOS反向上升19位至#32；这是本期最明显的跨端分化之一。"),
    card("googlePlay", "Arknights", "down", "下跌5位至#33，iOS仍未进榜；近期活动窗口存在，但单期回落不能直接解释为活动效果。"),
    card("googlePlay", "Sea War", "down", "下跌4位至#48，iOS未进榜；进入Google后十三名后，下一有效快照将决定是否形成榜尾风险。"),
]

ios_products = [
    card("ios", "Draft Showdown", "entry", "回榜#31并直接进入中段。近期版本替换League为Draft Pass，但本次回榜仍只记为待验证信号。"),
    card("ios", "Overgeared", "entry", "回榜#47，Google同步上升4位至#43；与新联动版本时间相邻，下一快照重点验证双端留位。"),
    card("ios", "Rise of Castles", "entry", "回榜#56，处于后五名；成熟城建4X先按榜尾轮换记录。"),
    card("ios", "Aliens vs Zombies", "entry", "回榜#60，恰处掉榜线；万圣节活动与Equipment 2.0为近期背景，能否连续留榜更关键。"),
    card("ios", "Kingdom Clash", "exit", "上期#48后掉榜，上期回补未延续为连续留位。"),
    card("ios", "Fire Emblem Heroes", "exit", "上期#49后掉榜；维护版本未披露足以解释榜位的新增玩法。"),
    card("ios", "Guns of Glory", "exit", "上期#53后掉榜，Google仍在榜；iPhone榜尾回补只维持一个有效快照。"),
    card("ios", "Lords Mobile", "exit", "上期#59后掉榜，成熟4X在iPhone掉榜线未能留位。"),
    card("ios", "Game of Thrones: Conquest", "up", "上升19位至#32，Google却下跌9位至#52；跨端反向显著，暂不归因于单一运营节点。"),
    card("ios", "Top War", "up", "上升8位至#34，Google未入榜；单日跃升先视为平台内信号。"),
    card("ios", "Forge Master", "down", "下跌13位至#48，仍在Google后段；iOS已接近榜尾风险区。"),
    card("ios", "RAID", "down", "下跌11位至#43，Google未入榜；回落幅度较大，但没有同步证据可判定原因。"),
]

news = [
    {"category":"全球市场 / 收入榜","date":"2026-11-03","title":"Sensor Tower发布2026年10月全球手游收入榜","summary":"官方完整图表显示ROBLOX、Honor of Kings、Gossip Harbor、Royal Match与Whiteout Survival位列前五，全球App Store与Google Play手游支出约62.6亿美元。","impact":"核心策略子集缩至Whiteout Survival #5与Kingshot #9；Last War从9月第7名退出全球TOP10。","source":"Sensor Tower官方","url":"https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-october-2026"},
    {"category":"卡牌 / 版本","date":"2026-10-30","title":"Draft Showdown近期版本继续调整Draft Pass与账号体验","summary":"Apple版本记录显示1.15.3继续进行平衡与错误修复；此前1.15.2用Draft Pass替代League并支持免登录保存进度。","impact":"产品本期回榜iOS #31；进入中段值得关注，但不能把回榜直接归因于版本。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/draft-showdown/id6743368869"},
    {"category":"放置RPG / IP联动","date":"2026-10-31","title":"Overgeared Hero加入Surviving the Game as a Barbarian联动","summary":"1.40版本加入Bjorn、Missha、Erwen等联动角色、Labyrinth与伙伴招募，后续1.40.1追加Erwen及Chapter 225。","impact":"iOS回榜#47、Google升至#43，双端同向但仍需下一快照确认。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/overgeared-hero-merge-rpg/id6755585789"},
    {"category":"城建生存 / 节日活动","date":"2026-10-26","title":"Aliens vs Zombies推进万圣节活动与Equipment 2.0","summary":"版本记录列出Halloween Boss Hunt、Halloween Night与Equipment 2.0等近期内容。","impact":"产品回榜iOS #60，仍位于掉榜线，活动峰值只能作为待验证背景。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/aliens-vs-zombies-invasion/id6740232087"},
    {"category":"部落战争 / 长线运营","date":"2026-10-21","title":"Clash of Clans重做Builder建议与多项菜单","summary":"18.647.5版本重做Builder Suggestions，增加筛选与分类，并调整战斗菜单、玩家资料和部落聊天。","impact":"本期Google与iOS均上升6位，形成较清晰的双端共同信号，但版本仅作近期背景。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/clash-of-clans/id529479190"},
    {"category":"新品4X / 版本","date":"2026-10-26","title":"Age of Spirits 1.1.2扩充Hero Shell与便利性功能","summary":"版本记录列出Hero Shell兑换、营地保护、Captive Pit一键释放与远征快捷功能。","impact":"产品本期iOS上升5位至#53，Google仍在榜；近90天新品继续处于后段验证。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/age-of-spirits/id6805006706"},
    {"category":"魔灵RPG / IP联动","date":"2026-10-28","title":"Summoners War加入Frieren联动原创魔灵","summary":"Apple版本记录确认9.3.8加入Frieren联动原创魔灵，并包含体验优化和错误修复。","impact":"本期iOS下跌7位至#35，表明活动窗口与单日榜位并非必然同向。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/summoners-war/id852912420"},
    {"category":"塔防RPG / 活动运营","date":"2026-10-28","title":"Arknights Reclamation Algorithm活动继续运行","summary":"官方公告确认活动与Orienteering定向寻访于10月28日开启，寻访持续至11月11日。","impact":"Google本期下跌5位至#33、iOS未入榜；只记录为时间相邻，不作负向因果判断。","source":"Arknights官方","url":"https://www.arknights.global/news/4980"},
    {"category":"塔防RPG / 版本","date":"2026-10-27","title":"Watcher of Realms美国版加入Gadrien's Tales测试季","summary":"1.6.46.841版本加入测试季、The Bone Diaries模式、Hero Aspect增强与商店。","impact":"产品本期iOS下跌7位至#38，回榜后的留位仍在中段波动。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/watcher-of-realms-us/id6741674823"},
    {"category":"文明4X / 版本运营","date":"2026-10-08","title":"Age of Empires Mobile近期版本延续Stormlands与Mounted Hunt","summary":"1.14.202版本延续Stormlands、Mounted Hunt与Emergency Aid Queue内容，并处理已有问题。","impact":"产品本期iOS下跌8位至#42；版本时间较早，不能解释本次单日回落。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/age-of-empires-mobile/id6476261995"},
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank

closing = [
    {"type":"判断","title":"Google无进出，前段稳定、后段换位加大","detail":"Google完整TOP60成员不变；Duck Survival +9、GOT Conquest −9构成最大位移，Clash Royale +6进入前20。"},
    {"type":"判断","title":"iOS四进四出，榜尾轮换仍是主要波动来源","detail":"Draft Showdown直接回到#31，其余三款回榜均在#47以后；四款掉榜产品上期也都位于#48以后。"},
    {"type":"判断","title":"跨端共同改善少于平台分化","detail":"Clash Royale双端均+6；Overgeared双端改善。GOT Conquest则iOS +19、Google −9，单日信号不可外推为长期趋势。"},
    {"type":"关注","title":"下一有效快照：核验四款iOS回榜产品留位","detail":"重点看Draft Showdown #31能否保持中段，以及Overgeared #47、Rise of Castles #56、Aliens vs Zombies #60是否快速退出。"},
    {"type":"关注","title":"未来1—2个快照：复核GOT Conquest跨端反向","detail":"若iOS继续改善且Google继续回落，才提高平台分化判断；若迅速收敛，则仍按单日换位记录。"},
    {"type":"关注","title":"至11月11日：分开观察活动与榜位","detail":"Arknights活动窗口持续至11月11日；只有后续多份有效快照与活动节点同向，才提高关联判断。"},
]

google_history = load("data/history/google-play/2026-11-03.json")
ios_history = load("data/history/ios/2026-11-03.json")
global_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
google_new = sum(x["comparison90d"]["status"] == "new" for x in datasets["googlePlay"]["now"])
ios_new = sum(x["comparison90d"]["status"] == "new" for x in datasets["ios"]["now"])

brief = {
    "date": DATE, "timezone": "Asia/Shanghai",
    "title": "Google成员稳定、iOS四进四出；GOT Conquest跨端反向",
    "summary": "较11月2日前一有效快照，Google Play无进出，Duck Survival +9、GOT Conquest −9，Clash Royale双端均+6。iOS四进四出，Draft Showdown回榜#31，GOT Conquest +19；其余进出集中于后十三名。Google近90天新品2款、iOS 1款；两端缺少8月5日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261103-01.json",
    "iconOverrideBundles": [f"assets/market-icons-20261103-{i:02d}.json" for i in range(2, 6)],
    "rankingSources": {"googlePlay":"data/games-20261103.json","ios":"data/ios-games-20261103.json"},
    "previousRankingSources": {"googlePlay":"data/games-20261102.json","ios":"data/ios-games-20261102.json"},
    "rankingDynamics": {
        "googlePlay": {"label":"Google Play · Android","sourceTime":f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取","anchors":"榜单锚点：#1 Whiteout Survival · #25 Age of Origins · #60 West Game","products":google_products},
        "ios": {"label":"App Store · iPhone/iOS","sourceTime":f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）","anchors":"榜单锚点：#1 Kingshot · #25 Magic: The Gathering Arena · #60 Aliens vs Zombies: Invasion","products":ios_products},
    },
    "marketNews": news, "closing": closing, "globalStrategyRevenue": global_revenue,
    "status": {
        "googlePlay":{"top60":60,"newRelease90d":google_new,"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-05"},
        "ios":{"top60":60,"newRelease90d":ios_new,"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-05"},
    },
    "sources": [
        {"label":"Google Play美国区策略畅销榜直连","url":google_history["sourceUrl"],"capturedAt":google_history["sourceCapturedAt"]},
        {"label":"Apple官方美国区iPhone策略畅销RSS","url":ios_history["sourceUrl"],"updated":ios_history["sourceUpdated"],"sourceDateBeijing":ios_history["dataDate"]},
        {"label":"Sensor Tower全球收入榜中的策略产品","url":global_revenue["sourceUrl"],"period":global_revenue["period"],"estimateAsOf":global_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown":"reports/2026-11-03.md","json":"data/market-brief-20261103.json"},
}


def markdown(value):
    lines = [f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "", "## 数据源与口径", "",
             f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
             f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
             f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}", f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
             "- 对比基准：各自上一份最终有效快照为2026-11-02；升降为相邻有效快照变化，不等于收入增减。",
             f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-08-05精确同口径TOP60基准，较老产品暂不判断飙升。", "", "## 1. 双榜当日异动产品", ""]
    for store in ("googlePlay", "ios"):
        section = value["rankingDynamics"][store]
        lines += [f"### {section['label']}", "", f"{section['sourceTime']}。", ""]
        for item in section["products"]:
            lines += [f"#### {item['gameName']}｜{item['changeLabel']}", "", item["analysis"], ""]
    lines += ["## 2. 策略手游市场热点", "", value["newsMethod"], ""]
    for item in value["marketNews"]:
        lines += [f"### {item['rank']}. [{item['title']}]({item['url']})", "", f"- 类别：{item['category']}｜发布日期：{item['date']}｜来源：{item['source']}", f"- 事实摘要：{item['summary']}", f"- 市场含义：{item['impact']}", ""]
    lines += ["## 3. 综合判断与后续关注", ""]
    for item in value["closing"]:
        lines += [f"### {item['type']}｜{item['title']}", "", item["detail"], ""]
    revenue = value["globalStrategyRevenue"]
    lines += ["## 4. Sensor Tower 全球收入榜中的策略产品", "", f"- 数据期：{revenue['periodLabel']}｜官方页面：{revenue['publicationLabel']}｜估算截至：{revenue['estimateAsOf']}", f"- 口径：{revenue['scope']['region']}｜{revenue['scope']['stores']}｜{revenue['scope']['exclusions']}", f"- 策略筛选：官方全球收入TOP10中命中{revenue['strategyMatches']}款核心策略产品；这不是完整策略品类TOP10", f"- 市场总览：全球手游消费者支出约${revenue['marketSummary']['globalConsumerSpendingUsd']/1_000_000_000:g}B，环比{revenue['marketSummary']['monthOverMonthPercent']:g}%；本期不展示全市场同比约值", f"- 原始来源：[{revenue['source']}]({revenue['sourceUrl']})", "", "| 全球总榜 | 游戏 | 发行商 | 策略类型 | 较上月榜位 | 单品收入同比 |", "|---:|---|---|---|---|---|"]
    for item in revenue["rankings"]:
        lines.append(f"| {item['rank']} | {item['gameName']} | {item['publisher']} | {item['strategyGenre']} | {item['movementLabel']} | {item['yoyRevenueLabel']} |")
    lines += ["", "### 策略产品与同比口径", ""] + [f"- {x}" for x in revenue["officialHighlights"]]
    lines += ["", revenue["methodologyNote"], "", "## 下载与来源", "", f"- JSON：`{value['downloads']['json']}`", f"- Sensor Tower上月对照：{revenue['previousPeriodSourceUrl']}", "- Google Play直连源：https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US", "- Apple官方RSS：https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json", ""]
    return "\n".join(lines)


save("data/market-brief-20261103.json", brief)
(ROOT / "reports/2026-11-03.md").write_text(markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date":DATE,"title":brief["title"],"summary":brief["summary"],"markdown":brief["downloads"]["markdown"],"json":brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = sorted([entry] + [x for x in manifest["reports"] if x["date"] != DATE], key=lambda x: x["date"], reverse=True)
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(google_products)+len(ios_products)} cards and {len(news)} news items")
