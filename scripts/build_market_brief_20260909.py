#!/usr/bin/env python3
"""Generate the Beijing 2026-09-09 market brief and archive entry."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-09"
STAMP = "20260909"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, value):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def product(game_name, product_id, store, tone, label, analysis):
    return {
        "gameName": game_name,
        "productId": product_id,
        "iconKey": f"{store}:{product_id}",
        "tone": tone,
        "changeLabel": label,
        "analysis": analysis,
    }


google_history = load("data/history/google-play/2026-09-09.json")
ios_history = load("data/history/ios/2026-09-09.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    product("Sea War: Uboat Raid", "com.bw.ud.googleplay", "googlePlay", "entry", "进入 · #58", "Google首次进入今日TOP60且位于#58，iOS同时大升16位至#35。两端同向改善比单端压线更值得关注，但公开资料尚不能确认由具体活动或投放触发，先记为待验证信号。"),
    product("Last Fortress: Underground", "com.more.lastfortress.gp", "googlePlay", "entry", "回榜 · #59", "9月8日刚掉榜，今天即回到Google #59；iOS仍未进TOP60。成熟城建生存产品的快速回补尚未脱离榜尾，不能据此判断为持续复苏。"),
    product("Ant Legion: For The Swarm", "com.global.antgame", "googlePlay", "entry", "回榜 · #60", "成熟蚁群SLG回到Google #60，iOS没有对应TOP60排名。当前只确认榜尾回补，没有公开版本节点足以解释原因，下一快照仍有直接掉榜风险。"),
    product("Lordrush", "com.s01.global", "googlePlay", "exit", "掉榜 · 上期#23", "Google从上期#23直接掉出TOP60，而iOS同期仍在#23。该作7月上架、仍属iOS近90天新品；本次出现显著跨端分化，需先排查Google侧短时榜单或付费波动，不能写成产品整体转弱。"),
    product("Titan Rush", "com.ratinghope.gplay", "googlePlay", "exit", "掉榜 · 上期#56", "上期位于Google #56，今天退出；iOS没有对应TOP60名次。此前已处榜尾风险区，本次掉榜符合短期位置压力，但仍不足以证明长期收入下行。"),
    product("Forge of Empires: Build a City", "com.innogames.foeandroid", "googlePlay", "exit", "掉榜 · 上期#58", "从9月7日#53、9月8日#58继续掉出Google TOP60，iOS仍未进榜。1.343全服更新计划在今天落地，现阶段只能确认更新前后的榜尾承接偏弱，后续需等待新快照。"),
    product("The Grand Mafia", "com.yottagames.gameofmafia", "googlePlay", "up", "+8 · #25", "Google升8位进入#25，成为今日Android最大涨幅；iOS未进同口径TOP60。没有可核验的同步活动依据，按单端付费位置抬升观察，而非直接归因为版本或买量。"),
    product("Top War: Battle Game", "com.topwar.gp", "googlePlay", "up", "+6 · #26", "Google升6位至#26，iOS维持#41。两个商店都在榜，但本次改善集中于Android，跨端仍相差15位，需看Google能否连续保持前30。"),
    product("Top Lords", "com.gamespark.topking.gp", "googlePlay", "up", "+6 · #44", "Google升6位至#44，iOS小降1位至#29。Android版6月25日上架，仍属近90天新品；两端方向不同，今天只能视为Google侧短期改善。"),
    product("Supremacy: World War 3", "com.doradogames.conflictnations.worldwar3", "googlePlay", "up", "+4 · #56", "昨日以#60回榜后升至Google #56，但iOS同期降6位至#40。Android暂时脱离末位、仍处后五名；双端反向使活动峰值解释不充分。"),
    product("Age of Empires Mobile", "com.proximabeta.aoemobile", "googlePlay", "down", "−4 · #48", "Google降4位至#48，iOS反而升3位至#42。两个商店位置接近但方向相反，属于单日跨端噪声，暂不判断版本运营成效。"),
]


ios_products = [
    product("Fire Emblem Heroes", "1181774280", "ios", "entry", "回榜 · #21", "9月8日刚从#60掉榜，今天回到iOS #21，幅度显著；Google未进策略TOP60。成熟IP产品的单日高位回补更像活动或付费峰值信号，但缺少同步官方节点，原因待验证。"),
    product("Vikings: War of Clans PvP", "966810173", "ios", "entry", "回榜 · #51", "iOS回到#51，Google当前榜外。产品仍位于后十名，属于成熟SLG单端回补；若下一快照不能上移，仍面临再次掉榜风险。"),
    product("Lords Mobile x Transformers", "1071976327", "ios", "entry", "回榜 · #54", "iOS回到#54，Google当前#23，跨端相差31位。成熟长线产品的Android付费位置明显更强；iOS回榜尚未摆脱榜尾风险，不能仅凭联动标题推断本次变化原因。"),
    product("Draft Showdown", "6743368869", "ios", "entry", "回榜 · #57", "iOS回到#57，Google当前未进TOP60。作为2026年2月上架产品已不属于90天新品，今天只记录单端榜尾回补，后续需验证能否连续留榜。"),
    product("Rise of Castles: Fire and War", "1411917616", "ios", "entry", "回榜 · #59", "iOS回到#59，Google同产品以Rise of Castles: Ice and Fire位列#21。Apple显示9月7日更新，但说明仅包含优化和修复；跨端差距清晰，不能把回榜直接归因于版本。"),
    product("Watcher of Realms - US", "6741674823", "ios", "exit", "掉榜 · 上期#44", "从上期iOS #44退出，Google没有对应策略TOP60名次。单日掉榜只说明当前iPhone策略榜位置跌出前60，不能外推到产品全球收入或整体用户规模。"),
    product("Yu-Gi-Oh! Master Duel", "1554247785", "ios", "exit", "掉榜 · 上期#54", "上期已降至#54，今天退出iOS策略TOP60；Google同口径榜外。产品具有卡牌与IP活动驱动特征，但没有证据把这次掉榜归为长期衰退。"),
    product("Star Trek Fleet Command", "1427744264", "ios", "exit", "掉榜 · 上期#56", "iOS从#56掉榜，而Google仍在#18，跨端差距进一步扩大。Android端保持中上段，因此本次更接近iPhone单端回落，不代表双端共同转弱。"),
    product("Overgeared Hero: Merge RPG", "6755585789", "ios", "exit", "掉榜 · 上期#59", "昨日刚回到iOS #59，今天即退出；Google同期升1位至#37。iOS榜尾回补仅维持一个快照，Google表现相对稳定，跨端分化继续。"),
    product("Guns of Glory: Lost Island", "1274354704", "ios", "exit", "掉榜 · 上期#60", "从iOS末位退出，Google同期仍在#30。成熟SLG的Android位置明显强于iPhone；本次是可预期的榜尾风险兑现，不足以说明全平台收入下降。"),
    product("Sea War: Uboat Raid", "6447612873", "ios", "up", "+16 · #35", "iOS升16位至#35，Google同时进入#58，是今日少数双端同向改善产品。由于Android仍在榜尾且无可确认活动证据，需要连续两至三个快照才能升级为持续信号。"),
    product("Summoners War", "852912420", "ios", "up", "+16 · #39", "iOS从#55升至#39，脱离掉榜风险区；Google未进策略TOP60。成熟RPG/策略混合产品出现单端回补，但公开信息不足以解释本次幅度。"),
    product("Star Wars™: Galaxy of Heroes", "921022358", "ios", "up", "+10 · #13", "iOS升10位至#13，Google同口径榜外。成熟IP产品回到前15，但这是单端日榜位置变化，尚不能推断收入同比或长期趋势。"),
    product("Last Shelter: Survival", "1342290011", "ios", "down", "−18 · #56", "昨日升21位至#38后，今天回落18位至#56；Google同期升4位至#43。iOS基本回吐前一日峰值并重回风险区，Android却改善，说明昨日双端共振未持续。"),
    product("Kingdom Guard:Tower Defense TD", "1570095804", "ios", "down", "−16 · #55", "iOS由#39降至#55，Google则升2位至#50。两端都在后段且方向相反，iOS已接近掉榜，当前不能把单日变化归因于版本或买量。"),
    product("The Battle Cats", "850057092", "ios", "down", "−11 · #43", "iOS降11位至#43，Google策略榜外。产品仍处中后段，单日回落幅度较大但未到榜尾；下一快照能否止跌比原因推测更重要。"),
    product("MARVEL SNAP - Hero Card Game", "1592081003", "ios", "down", "−9 · #49", "iOS降9位至#49，而Google维持#34。AXIS: Inversion赛季期间两端没有同步上行，今天iPhone端回落更明显，但榜位不能直接等同于活动收入。"),
    product("Rise of Kingdoms", "1354260888", "ios", "up", "+7 · #20", "iOS升7位至#20，Google当前#19，双端名次收敛。成熟4X产品在两个商店均位于前20附近，但需要后续快照确认是否为稳定抬升而非日内付费波动。"),
]


news = [
    {"category": "全球月榜", "date": "2026-09-04（估算截至）", "title": "Sensor Tower发布8月全球手游收入TOP10", "summary": "全球手游消费者支出约65.7亿美元、环比下降1%；Honor of Kings居首，Whiteout Survival第3、Kingshot第7。", "impact": "两款核心策略产品均较7月上升1位，并继续处于今日美国双端头部；官方未公开单品收入同比，页面不从名次补算百分比。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"},
    {"category": "新赛季", "date": "2026-09-07", "title": "Clash Royale开启Minion Academy赛季", "summary": "官方公布Minion Giant新卡、Ice Wizard英雄、Album Event、2v2 League和Royale Shuffle等9月内容。", "impact": "Clash Royale今日Google再升2位至#11、iOS维持#5；节点与双端高位重合，但持续收入仍需首周数据验证。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/new-season-minion-academy/"},
    {"category": "版本 / 掉榜", "date": "2026-09-07", "title": "Forge of Empires发布1.343国际服版本", "summary": "版本调整Historical Allies与Stellar Age提示并修复多项移动端稳定性问题；全服计划9月9日更新。", "impact": "该作今日从Google #58掉榜；全服更新与掉榜同日，不能先验判断版本承接，需看后续是否回榜。", "source": "InnoGames官方", "url": "https://support.innogames.com/kb/ForgeOfEmpires/en_DK/6975/Update-to-version-1343"},
    {"category": "长线运营", "date": "2026-08-28", "title": "Boom Beach公布9月活动日历", "summary": "9月安排Speed Serum、兵种Mania、Mega Crab、Leader Deployment与月底Warships Season 92。", "impact": "Boom Beach当前未进两端策略TOP60；密集长线活动并未等同于当日榜面回升，适合作为活动—排名转化对照。", "source": "Supercell官方", "url": "https://supercell.com/en/games/boombeach/blog/blog/this-september-on-boom-beach-2/"},
    {"category": "周年运营", "date": "2026-09-04", "title": "King of Avalon开启十周年整月活动", "summary": "9月4日至30日活动加入可收集Merlin、八个传奇地点、七件遗物、拼图、英雄与周年奖励。", "impact": "该作今日Google #35、iOS未进榜；周年活动在Android仍有承接，但暂未形成双端共同抬升。", "source": "FunPlus官方", "url": "https://funplus.com/king-of-avalon-celebrates-10th-anniversary/"},
    {"category": "区域趋势", "date": "2026-09（官方发布月）", "title": "Sensor Tower：日本4X策略收入同比增长9.4%", "summary": "日本近12个月手游IAP超100亿美元；报告称4X Strategy领跑细分收入并增长9.4%，Last War是主要支撑产品。", "impact": "这说明成熟高付费市场仍能支撑4X增长，但属于日本市场口径，不能替代美国双榜或全球单品收入。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/state-of-japan-gaming-2026"},
    {"category": "版本更新", "date": "2026-08-30", "title": "Clash of Clans更新TH18宠物与Supercharge等级", "summary": "官方更新增加Diggy等级、Builder's Hut与Monolith强化，并调整回流、新手与部落战联赛体验。", "impact": "Clash of Clans今日Google #7、iOS #9，持续位于双端头部；版本效果仍应结合多日位置而非单一快照。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/release-notes/august-update-3/"},
    {"category": "新赛季", "date": "2026-08-31", "title": "MARVEL SNAP运营AXIS: Inversion赛季", "summary": "赛季包含新角色、地点、登录日历、Draft、Team Clash与多段活动，并提供网页商店季票奖励。", "impact": "今日Google #34、iOS降至#49，双端方向并未共振；赛季节点不能单独解释日榜变化。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/new-season-axis-inversion/"},
    {"category": "版本运营", "date": "2026-08-26", "title": "GFL2的Chiral Redundancy版本进入承接观察期", "summary": "官方加入限时剧情、Frontier platoon玩法、Tile Transformation系统及角色卡池。", "impact": "GFL2今日Google维持#51、iOS榜外；版本后高位已回吐，但榜位不能单独证明收入或用户流失。", "source": "GIRLS' FRONTLINE 2官方", "url": "https://gf2exilium.sunborngame.com/NewsInfo?id=393&typeId=3"},
    {"category": "IP联动", "date": "2026-08-25", "title": "State of Survival推进《如龙8》联动", "summary": "8月28日起加入联盟Boss、节奏挑战、感染摩托、角色和排行榜内容。", "impact": "State of Survival今日Google #45、iOS未进榜，联动目前没有形成双端共同高位。", "source": "FunPlus官方", "url": "https://funplus.com/state-of-survival-x-like-a-dragon-infinite-wealth-crossover-event/"},
]


closing = [
    {"type": "判断", "title": "两端换榜同时扩大，但波动重心不同", "detail": "Google为3进3出且变动集中于榜尾，iOS为5进5出并出现Fire Emblem直接回到#21；iOS榜内还出现两组±16位以上变化。今天不能只用进出数量描述市场稳定度。"},
    {"type": "判断", "title": "Sea War是今日最清晰的双端共同改善信号", "detail": "Sea War进入Google #58并在iOS上升16位至#35；相对地，Last Shelter昨日双端改善后今天出现iOS回吐18位、Google升4位。双端同向需要连续性，单日共振仍不能直接写成长期收入增长。"},
    {"type": "判断", "title": "月度全球收入头部与美国日榜头部仍保持一致", "detail": "Sensor Tower 8月全球收入TOP10中的策略子集Whiteout Survival与Kingshot，今天分别位于Google #3/#1、iOS #3/#2；但官方未公开单品同比，日榜名次也不能换算收入百分比。"},
    {"type": "关注", "title": "9月10日：复核Google三款榜尾回榜产品", "detail": "Sea War、Last Fortress和Ant Legion分别位于#58—#60；至少一款脱离后五名并连续留榜，才说明本次换榜不只是末位轮换。"},
    {"type": "关注", "title": "9月10—11日：验证iOS大幅回补与回吐", "detail": "观察Fire Emblem能否守住前30、Sea War与Summoners War能否留在前40，以及Last Shelter和Kingdom Guard是否从#55—#56反弹；否则分别按短峰或榜尾风险归档。"},
    {"type": "关注", "title": "截至9月14日：拆分版本节点与真实榜位承接", "detail": "Forge of Empires 1.343若在全服更新后回到Google TOP60，Clash Royale若继续守住Google前15和iOS前10，才为两个公开节点提供后续榜面证据；仍不等同于单品收入同比。"},
]


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Google三进三出、iOS五进五出；Sea War双端共同改善",
    "summary": "与9月8日快照相比，Google Play由Sea War、Last Fortress和Ant Legion进入/回榜，Lordrush、Titan Rush与Forge of Empires掉榜；iOS有Fire Emblem、Vikings、Lords Mobile、Draft Showdown及Rise of Castles进入/回榜，另有5款掉榜。Sea War同时进入Google并在iOS上升16位，是今日最值得连续验证的共同信号。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": "data/games-20260909.json", "ios": "data/ios-games-20260909.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260908.json", "ios": "data/ios-games-20260908.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 The Grand Mafia · #60 Ant Legion: For The Swarm", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}", "anchors": "榜单锚点：#1 Pokémon GO · #25 Police Chief · #60 Top Heroes: Kingdom Saga", "products": ios_products},
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": 5, "surge90d": 0, "baselineAvailable": False},
        "ios": {"top60": 60, "newRelease90d": 2, "surge90d": 0, "baselineAvailable": False},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-09.md", "json": "data/market-brief-20260909.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        "- Google锚点：#1 Kingshot · #25 The Grand Mafia · #60 Ant Legion: For The Swarm",
        "- iOS锚点：#1 Pokémon GO · #25 Police Chief · #60 Top Heroes: Kingdom Saga",
        "- 对比基准：各自上一份有效快照为2026-09-08；所有升降均为相邻工作日变化。",
        "- 近90天状态：Google新上榜5款、iOS新上榜2款；两端均缺少2026-06-11精确同口径TOP60基准，较老产品暂不判断飙升。", "",
        "## 1. 双榜当日异动产品", "",
    ]
    for store in ("googlePlay", "ios"):
        section = value["rankingDynamics"][store]
        lines += [f"### {section['label']}", "", f"{section['sourceTime']}。", ""]
        for item in section["products"]:
            lines += [f"#### {item['gameName']}｜{item['changeLabel']}", "", item["analysis"], ""]
    lines += ["## 2. 策略手游市场热点", "", value["newsMethod"], ""]
    for index, item in enumerate(value["marketNews"], 1):
        lines += [f"### {index}. [{item['title']}]({item['url']})", "", f"- 类别：{item['category']}｜发布日期：{item['date']}｜来源：{item['source']}", f"- 事实摘要：{item['summary']}", f"- 市场含义：{item['impact']}", ""]
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
        "| 全球总榜 | 游戏 | 发行商 | 策略类型 | 较上月榜位 | 单品收入同比 |", "|---:|---|---|---|---|---|",
    ]
    for item in revenue["rankings"]:
        lines.append(f"| {item['rank']} | {item['gameName']} | {item['publisher']} | {item['strategyGenre']} | {item['movementLabel']} | {item['yoyRevenueLabel']} |")
    lines += ["", "### 策略产品与同比口径", ""]
    lines += [f"- {item}" for item in revenue["officialHighlights"]]
    lines += ["", revenue["methodologyNote"], "", "## 下载与来源", "", f"- JSON：`{value['downloads']['json']}`", f"- Sensor Tower上月对照：{revenue['previousPeriodSourceUrl']}", f"- Sensor Tower同比对照：{revenue['yearOverYearSourceUrl']}", "- Google Play直连源：https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US", "- Apple官方RSS：https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json", ""]
    return "\n".join(lines)


save("data/market-brief-20260909.json", brief)
(ROOT / "reports/2026-09-09.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(google_products) + len(ios_products)} product cards and {len(news)} news items")
