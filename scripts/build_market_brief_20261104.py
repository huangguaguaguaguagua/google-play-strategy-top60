#!/usr/bin/env python3
"""Generate the Beijing 2026-11-04 market brief and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-11-04", "20261104"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261104.json"), "prior": load("data/games-20261103.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261104.json"), "prior": load("data/ios-games-20261103.json"), "id": "appId"},
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
    card("googlePlay", "MARVEL SNAP", "entry", "回榜#56，iOS同产品上升29位至#20。当前赛季内容仍在窗口，但Android榜尾回归只记为待验证信号。"),
    card("googlePlay", "Age of Empires Mobile", "entry", "回榜#57，iOS仍位于#42；Google端处于后四名，下一快照重点验证留位。"),
    card("googlePlay", "Kingdom Guard", "entry", "回榜#59，而iOS下跌15位至#54；跨端节奏反向，不能用同一活动解释。"),
    card("googlePlay", "Kiss of War", "exit", "上期#54后掉榜，iOS未入榜；成熟二战SLG的Android榜尾回补未连续保持。"),
    card("googlePlay", "DC: Dark Legion", "exit", "上期#58后掉榜，iOS同步下跌6位至#60；两端都进入掉榜风险区。"),
    card("googlePlay", "West Game", "exit", "上期#60后掉榜；首次项目收录只保持一个有效快照，继续按成熟产品榜尾轮换记录。"),
    card("googlePlay", "Top Heroes", "up", "上升6位至#44并回榜iOS #50；11月2日Cloudsea Odyssey更新时间相邻，但仍需连续快照确认。"),
    card("googlePlay", "Arknights", "down", "下跌6位至#39，iOS未入榜；活动窗口仍在，但不把单日回落解释为活动效果。"),
    card("googlePlay", "Warhammer", "down", "下跌5位至#45，同时iOS从#52掉榜；双端同向回落属于风险信号，但不外推长期衰退。"),
    card("googlePlay", "Sea War", "down", "下跌6位至#54，iOS未入榜；Google已进入后七名，下一快照验证是否继续滑向掉榜线。"),
]

ios_products = [
    card("ios", "Hearthstone", "entry", "回榜#38。Reign of the Black Empire扩展与新Arena赛季仍在运营窗口，但本次回榜只记为待验证信号。"),
    card("ios", "Top Heroes", "entry", "回榜#50，Google同步上升6位至#44；双端改善与11月2日版本相邻，但不作确定归因。"),
    card("ios", "Kingdom Clash", "entry", "回榜#53；10月新Boss与兵种版本是近期背景，当前仍处后八名。"),
    card("ios", "Lords Mobile", "entry", "回榜#58，Google仍在榜；成熟4X重新压线进入，需验证能否连续保留。"),
    card("ios", "Vikings", "entry", "回榜#59。11月2日加入Jötunn Rubies，但榜尾回归仍需下一快照确认。"),
    card("ios", "Warhammer", "exit", "上期#52后掉榜，Google同步下跌5位至#45；双端同向回落但不能外推长期趋势。"),
    card("ios", "Rise of Castles", "exit", "上期回榜#56后立即掉榜，成熟城建4X的榜尾回补未连续保持。"),
    card("ios", "The Tower", "exit", "上期#58后掉榜；大版本后的榜尾回归未延续。"),
    card("ios", "Star Trek Fleet Command", "exit", "上期#59后掉榜，Google仍在榜；iPhone端回补只保持一个快照。"),
    card("ios", "Aliens vs Zombies", "exit", "上期回榜#60后立即掉榜，万圣节活动窗口未形成连续TOP60席位。"),
    card("ios", "MARVEL SNAP", "up", "上升29位至#20，同时回榜Google #56；iOS中段跃升清晰，但Android仍在榜尾。"),
    card("ios", "Forge Master", "up", "上升18位至#30，扭转昨日下跌；单日反弹幅度较大，仍需下一快照排除短期轮换。"),
    card("ios", "Star Wars", "up", "上升17位至#11，接近前十；未发现与本次跃升同步的单一官方节点。"),
    card("ios", "Summoners War", "down", "下跌16位至#51；Frieren联动仍在近期窗口，但活动与榜位并非必然同向。"),
    card("ios", "Kingdom Guard", "down", "下跌15位至#54，而Google回榜#59；两端均在后段且节奏不同。"),
    card("ios", "Watcher of Realms", "down", "下跌9位至#47；此前回榜后的中段席位未稳定，当前接近后十四名。"),
]

news = [
    {"category":"全球市场 / 收入榜","date":"2026-11-03","title":"Sensor Tower最新完整全球收入榜仍为2026年10月","summary":"官方榜显示ROBLOX、Honor of Kings、Gossip Harbor、Royal Match与Whiteout Survival位列收入前五，全球App Store与Google Play手游支出约62.6亿美元。","impact":"11月4日单次检查未发现更新一期；策略子集继续保留Whiteout Survival #5与Kingshot #9。","source":"Sensor Tower官方","url":"https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-october-2026"},
    {"category":"卡牌竞技 / 赛季","date":"2026-11-03","title":"Clash Royale公布11月赛季新进化与Daily Puzzles","summary":"官方11月说明列出Evolved Giant、Evolved Mirror与Daily Puzzles，Mirror进化自11月9日起开放。","impact":"产品目前Google #15、iOS #7；需在11月9日后观察新内容是否带来双端持续位移。","source":"Supercell官方支持页","url":"https://support.supercell.com/clash-royale/en/articles/whats-new-november-2026.html"},
    {"category":"卡牌RPG / 新扩展","date":"2026-10-23","title":"Hearthstone进入Reign of the Black Empire扩展窗口","summary":"Apple版本记录确认新扩展加入Old God卡牌与Assemble关键词，并开启新Arena赛季和新版Journal。","impact":"产品本期回榜iOS #38；内容窗口与回榜相邻，但不据单期认定因果。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/hearthstone/id625257520"},
    {"category":"英雄4X / 版本","date":"2026-11-02","title":"Top Heroes更新Cloudsea Odyssey占领规则","summary":"1.127.7版本调整首个公会占领Capital两小时后的归属，并修正Lite Mode与Rose Princess技能说明。","impact":"本期回榜iOS #50、Google上升6位至#44，双端同向但仍待连续验证。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/top-heroes-kingdom-saga/id6450953550"},
    {"category":"联盟4X / 版本","date":"2026-11-02","title":"Vikings: War of Clans加入Jötunn Rubies","summary":"7.3.0版本新增Jötunn Rubies，由氏族在Jotunheim竞赛中获取并兑换高级商品。","impact":"产品本期回榜iOS #59；处于掉榜线附近，版本只能作为近期背景。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/vikings-war-of-clans-pvp/id966810173"},
    {"category":"超级英雄卡牌 / 赛季","date":"2026-10-20","title":"MARVEL SNAP推进Vampires vs Zombies赛季","summary":"58.15.1版本列出Vampire Killmonger、Zombie Venom等新角色，以及Grand Arena、Team Clash与Deadpool's Diner模式。","impact":"本期iOS +29至#20并回榜Google #56，双端层级差异仍大。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/marvel-snap-hero-card-game/id1592081003"},
    {"category":"长线4X / 新系统","date":"2026-10-21","title":"Lords Mobile加入Heroic Saga与Battle Spirit","summary":"2.208版本为Rank 8并装备完整的英雄开放Battle Spirit与Heroic Saga任务系统。","impact":"产品本期回榜iOS #58；成熟产品仍处榜尾轮换，不能由系统更新推断长期抬升。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/lords-mobile-kingdom-wars/id1071976327"},
    {"category":"塔防 / 内容更新","date":"2026-10-19","title":"Kingdom Clash加入Shai-Khold Boss与传奇兵种","summary":"3.3.0版本加入冰矛Boss Shai-Khold、新传奇兵种，并调整Bank金币礼包。","impact":"产品本期回榜iOS #53；仍在后八名，下一快照留位比单日回归更重要。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/kingdom-clash-medieval-defense/id1611722542"},
    {"category":"新品4X / 版本","date":"2026-11-02","title":"Age of Spirits 1.1.3扩充Crystal与离线收益","summary":"版本新增第七件Shaman Gear的Crystal槽，将基础离线收益时长翻倍至四小时，并调整VIP点数、月卡宝石与传送成本。","impact":"产品仍是双端近90天新品，当前Google #47、iOS #55；继续处首发验证。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/age-of-spirits/id6805006706"},
    {"category":"魔灵RPG / IP联动","date":"2026-10-28","title":"Summoners War的Frieren联动仍在近期窗口","summary":"9.3.8加入Frieren联动原创魔灵，并包含体验优化和错误修复。","impact":"本期iOS下跌16位至#51，说明联动窗口与单日榜位并非必然同向。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/summoners-war/id852912420"},
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank

closing = [
    {"type":"判断","title":"Google三进三出，成员变化集中在后七名","detail":"MARVEL SNAP、Age of Empires Mobile与Kingdom Guard回榜#56—#59；Kiss of War、DC: Dark Legion与West Game掉榜。前段依旧稳定。"},
    {"type":"判断","title":"iOS五进五出，日内换位强于Google","detail":"MARVEL SNAP +29、Forge Master +18、Star Wars +17；Summoners War −16、Kingdom Guard −15。全部进出仍集中于#38以后。"},
    {"type":"判断","title":"双端共同信号有限，平台层级差异仍大","detail":"Top Heroes双端改善；MARVEL SNAP虽双端改善，但iOS已到#20、Google仅#56。Kingdom Guard则Google回榜、iOS大跌。"},
    {"type":"关注","title":"下一有效快照：核验八款榜尾回榜产品","detail":"Google关注MARVEL SNAP、Age of Empires Mobile、Kingdom Guard；iOS关注Hearthstone、Top Heroes、Kingdom Clash、Lords Mobile与Vikings。"},
    {"type":"关注","title":"11月9日后：观察Clash Royale新进化内容","detail":"Mirror进化自11月9日起开放；只有双端后续多份快照与内容窗口同向，才提高关联判断。"},
    {"type":"关注","title":"未来1—2个快照：复核MARVEL SNAP与Kingdom Guard跨端差异","detail":"若MARVEL SNAP的Android留位抬升、Kingdom Guard两端重新收敛，才认为今日信号具备持续性。"},
]

google_history = load("data/history/google-play/2026-11-04.json")
ios_history = load("data/history/ios/2026-11-04.json")
global_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
google_new = sum(x["comparison90d"]["status"] == "new" for x in datasets["googlePlay"]["now"])
ios_new = sum(x["comparison90d"]["status"] == "new" for x in datasets["ios"]["now"])

brief = {
    "date": DATE, "timezone": "Asia/Shanghai",
    "title": "Google三进三出、iOS五进五出；MARVEL SNAP跨端同升不同层",
    "summary": "较11月3日前一有效快照，Google Play三进三出，变化集中在#54以后；Top Heroes +6、Arknights与Sea War各−6。iOS五进五出，MARVEL SNAP +29、Forge Master +18、Summoners War −16。Top Heroes双端改善，MARVEL SNAP虽双端同升但iOS已到#20、Google仅回榜#56。Google近90天新品2款、iOS 1款；两端缺少8月6日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261104-01.json",
    "iconOverrideBundles": [f"assets/market-icons-20261104-{i:02d}.json" for i in range(2, 8)],
    "rankingSources": {"googlePlay":"data/games-20261104.json","ios":"data/ios-games-20261104.json"},
    "previousRankingSources": {"googlePlay":"data/games-20261103.json","ios":"data/ios-games-20261103.json"},
    "rankingDynamics": {
        "googlePlay": {"label":"Google Play · Android","sourceTime":f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取","anchors":"榜单锚点：#1 Whiteout Survival · #25 Age of Origins · #60 Doomsday: Last Survivors","products":google_products},
        "ios": {"label":"App Store · iPhone/iOS","sourceTime":f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）","anchors":"榜单锚点：#1 Kingshot · #25 Top Force: Commander · #60 DC: Dark Legion™","products":ios_products},
    },
    "marketNews": news, "closing": closing, "globalStrategyRevenue": global_revenue,
    "status": {
        "googlePlay":{"top60":60,"newRelease90d":google_new,"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-06"},
        "ios":{"top60":60,"newRelease90d":ios_new,"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-06"},
    },
    "sources": [
        {"label":"Google Play美国区策略畅销榜直连","url":google_history["sourceUrl"],"capturedAt":google_history["sourceCapturedAt"]},
        {"label":"Apple官方美国区iPhone策略畅销RSS","url":ios_history["sourceUrl"],"updated":ios_history["sourceUpdated"],"sourceDateBeijing":ios_history["dataDate"]},
        {"label":"Sensor Tower全球收入榜中的策略产品","url":global_revenue["sourceUrl"],"period":global_revenue["period"],"estimateAsOf":global_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown":"reports/2026-11-04.md","json":"data/market-brief-20261104.json"},
}


def markdown(value):
    lines = [f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "", "## 数据源与口径", "",
             f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
             f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
             f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}", f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
             "- 对比基准：各自上一份最终有效快照为2026-11-03；升降为相邻有效快照变化，不等于收入增减。",
             f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-08-06精确同口径TOP60基准，较老产品暂不判断飙升。", "", "## 1. 双榜当日异动产品", ""]
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


save("data/market-brief-20261104.json", brief)
(ROOT / "reports/2026-11-04.md").write_text(markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date":DATE,"title":brief["title"],"summary":brief["summary"],"markdown":brief["downloads"]["markdown"],"json":brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = sorted([entry] + [x for x in manifest["reports"] if x["date"] != DATE], key=lambda x: x["date"], reverse=True)
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(google_products)+len(ios_products)} cards and {len(news)} news items")
