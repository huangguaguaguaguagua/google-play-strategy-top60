#!/usr/bin/env python3
"""Generate the Beijing 2026-09-10 market brief and archive entry."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-10"
STAMP = "20260910"


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


google_history = load("data/history/google-play/2026-09-10.json")
ios_history = load("data/history/ios/2026-09-10.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    product("Lordrush", "com.s01.global", "googlePlay", "entry", "回榜 · #17", "昨日从Google #23直接掉榜后，今天回到#17；iOS同期位于#22。两端均进入前25且都属于近90天新品，是今日最强的共同高位信号，但一天回补仍不足以确认持续收入增长。"),
    product("Titan Rush", "com.ratinghope.gplay", "googlePlay", "entry", "回榜 · #53", "9月9日刚掉榜，今天回到Google #53；iOS仍未进入TOP60。当前位置仍在后十名，先按成熟产品的单端榜尾回补观察。"),
    product("Draft Showdown", "com.QuestLab.DraftWar", "googlePlay", "entry", "回榜 · #60", "Google回到末位#60，iOS同期上升5位至#52。两端同时改善，但两个位置都在榜尾风险区，现阶段只能记为待验证信号。"),
    product("Sea of Conquest: Pirate War", "com.seaofconquest.global", "googlePlay", "exit", "掉榜 · 上期#55", "Google从#55退出，iOS同口径榜外。该作此前在榜尾往返，本次只确认末段位置再次失守，不能据此判断产品整体收入转弱。"),
    product("Supremacy: World War 3", "com.doradogames.conflictnations.worldwar3", "googlePlay", "exit", "掉榜 · 上期#56", "Google从#56掉榜，而iOS当前#43。iPhone端仍在中后段，说明本次是Android单端退出，不构成双端共同下滑证据。"),
    product("Ant Legion: For The Swarm", "com.global.antgame", "googlePlay", "exit", "掉榜 · 上期#60", "昨日刚回到Google末位，今天立即退出；iOS无对应TOP60排名。榜尾回补仅维持一个快照，短期风险已经兑现。"),
    product("MARVEL SNAP: Hero Strategy CCG", "com.nvsgames.snap", "googlePlay", "down", "−15 · #49", "Google下降15位至#49，而iOS反向上升5位至#44。两端名次最终接近、方向却完全相反，AXIS赛季当前更像平台付费节奏差异，不能写成整体下滑。"),
    product("Frost & Flame: King of Avalon", "com.funplus.kingofavalon", "googlePlay", "down", "−8 · #43", "十周年整月活动期间，Google由#35降至#43，iOS仍未进榜。周年节点没有转化为今日榜位上涨，但单日回落也不足以否定活动效果。"),
    product("Top War: Battle Game", "com.topwar.gp", "googlePlay", "down", "−7 · #33", "Google下降7位至#33，iOS反而上升2位至#39。两端仍处相近区间，今天主要体现Android回吐，而非双端同步转弱。"),
    product("Top Lords", "com.gamespark.topking.gp", "googlePlay", "up", "+5 · #39", "Google升5位至#39，iOS小降1位至#30。Android版仍属近90天新品，两个商店均留在前40，但方向不同，暂不把Google改善外推为共同趋势。"),
    product("Game of Thrones: Conquest ™", "com.wb.goog.got.conquest", "googlePlay", "up", "+4 · #37", "Google升4位至#37，iOS下降3位至#33。两个商店位置接近且方向相反，属于成熟IP产品的单日平台波动。"),
    product("Infinity Kingdom", "com.gtarcade.ioe.global", "googlePlay", "down", "−4 · #40", "Google降4位至#40，iOS同时降6位至#50，是今日较少见的双端同向回落。两端仍在榜内，需连续快照才能判断是否从短期噪声转为持续走弱。"),
]


ios_products = [
    product("Pokémon Champions", "6741503079", "ios", "entry", "首次进入 · #19", "6月17日移动端上线后首次进入本项目iOS策略TOP60，直接来到#19；Google同口径榜外。上架仍在90天窗口，标记为近三个月新上榜。9月9日1.2.0只确认问题修复，不能直接作为进榜原因。"),
    product("Last Fortress: Underground", "1540557475", "ios", "entry", "回榜 · #48", "iOS回到#48，Google同期处#59。成熟城建生存产品重新形成双端在榜，但两个位置都在后段，当前更接近榜尾回补而非明确复苏。"),
    product("F1® Clash - Official 2026 Game", "1434561536", "ios", "entry", "首次进入 · #56", "2019年上线的成熟赛车经营产品首次进入项目iOS策略TOP60。9月1日Update 60加入Madring及未来活动内容，9月9日版本仅修复优化；当前#56仍需结合现实赛历继续验证。"),
    product("Galaxy Defense: Fortress TD", "6740189002", "ios", "entry", "回榜 · #60", "iOS回到末位#60，Google同期位于#55。两端都在最后六名，当前只能确认双端榜尾承接，下一快照再次掉榜的风险很高。"),
    product("Vikings: War of Clans PvP", "966810173", "ios", "exit", "掉榜 · 上期#51", "昨日回到iOS #51后今天再次退出，Google同口径榜外。成熟SLG的单端回榜只维持一个快照，尚未形成稳定付费位置。"),
    product("Kingdom Guard:Tower Defense TD", "1570095804", "ios", "exit", "掉榜 · 上期#55", "iOS从#55掉榜，而Google仍在#50。两个商店都靠近榜尾，本次是iPhone风险兑现，不代表Android同时退出。"),
    product("League of Legends: Wild Rift", "1480616990", "ios", "exit", "掉榜 · 上期#58", "iOS从#58退出，但Google策略榜仍在#41。由于MOBA仅因Apple策略标签进入本榜，本次应按平台分类榜波动理解，不能外推全球产品收入。"),
    product("Top Heroes: Kingdom Saga", "6450953550", "ios", "exit", "掉榜 · 上期#60", "昨日处iOS末位，今天退出；Google同期仍在#47。iPhone榜尾风险兑现，但Android仍在榜，属于跨端分化。"),
    product("Lands of Jail", "6738469826", "ios", "down", "−13 · #58", "iOS下降13位至#58，Google同期位于#30。两端差距扩大到28位，iPhone已进入直接掉榜风险区，Android仍保持中段。"),
    product("Warline: Sniper Strike", "6742809194", "ios", "down", "−10 · #57", "iOS下降10位至#57，而Google升1位至#28。iOS版仍在90天新品窗口，但今天跨端差距扩大，需确认iPhone端是否只是短时付费回吐。"),
    product("Dragon Traveler", "6751086804", "ios", "up", "+8 · #42", "iOS升8位至#42，Google策略榜外。产品仍处中后段且只有单端证据，先记录为短期改善，不推断活动或买量原因。"),
    product("Lords Mobile x Transformers", "1071976327", "ios", "up", "+8 · #46", "iOS升8位至#46，Google同期降2位至#25。iPhone端脱离后十名，但Android仍明显更强；联动标题本身不足以解释今日变化。"),
    product("War and Order", "1071744151", "ios", "up", "+7 · #29", "iOS升7位至#29，Google当前同为#29，双端名次完全收敛。成熟SLG出现共同中段位置，但本次上涨来自iOS单端，仍需看能否连续守住前30。"),
    product("Raid Rush: Tower Defense TD", "1662335371", "ios", "down", "−7 · #41", "iOS降7位至#41，Google同期降3位至#56。两端同向回落且Android已靠近榜尾，是值得继续验证的共同转弱信号，但一天排名不能换算收入下降。"),
    product("Age of Empires Mobile", "6476261995", "ios", "down", "−7 · #49", "iOS降7位至#49，Google同时降3位至#51。两端都落到后段，方向一致；若下一快照继续下降，才可升级为连续回落信号。"),
]


news = [
    {"category": "新品 / 竞技生态", "date": "2026-09-06", "title": "Pokémon Champions移动端进入竞技生态观察期", "summary": "The Verge报道该作跨平台用户已形成规模，但区域级及以上官方赛事仍要求使用Switch；移动端目前主要扩展日常对战入口。", "impact": "该作今天首次进入iOS策略榜#19。高IP认知与竞技生态可能共同支撑，但赛事硬件限制意味着移动端榜位仍需单独验证。", "source": "The Verge", "url": "https://www.theverge.com/games/990691/competitive-pokemon-champions-mobile-tournament-accessibility"},
    {"category": "全球月榜", "date": "2026-09-04（官方发布）", "title": "Sensor Tower发布8月全球手游收入TOP10", "summary": "全球手游消费者支出约65.7亿美元、环比下降1%；Honor of Kings居首，Whiteout Survival第3、Kingshot第7。", "impact": "两款核心策略产品均较7月上升1位，并继续位于今日美国双端头部；官方未公开单品收入同比，页面不从名次补算百分比。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"},
    {"category": "新赛季", "date": "2026-09-07", "title": "Clash Royale开启Minion Academy赛季", "summary": "官方公布Minion Giant新卡、Ice Wizard英雄、Album Event、2v2 League和Royale Shuffle等9月内容。", "impact": "Clash Royale今日Google #10、iOS #6，继续保持双端前十；节点与高位重合，但持续收入仍需首周后数据验证。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/new-season-minion-academy/"},
    {"category": "周年运营", "date": "2026-09-04", "title": "King of Avalon开启十周年整月活动", "summary": "9月4日至30日活动加入可收集Merlin、八个传奇地点、七件遗物、拼图、英雄与周年奖励。", "impact": "该作今日Google降8位至#43、iOS榜外；周年内容仍在进行，但单日排名没有形成双端抬升。", "source": "FunPlus官方", "url": "https://funplus.com/king-of-avalon-celebrates-10th-anniversary/"},
    {"category": "版本 / 现实赛历", "date": "2026-09-01", "title": "F1 Clash Update 60加入Madring与后续活动内容", "summary": "Hutch官方说明Update 60新增Madring赛道、未来活动内容及多项修复；产品继续围绕真实F1赛历经营。", "impact": "F1 Clash今天首次进入项目iOS策略榜#56，但9月9日小版本只写修复优化，进榜原因仍需结合赛道活动和后续留榜验证。", "source": "Hutch Games官方", "url": "https://www.hutch.io/our-games/f1-clash/patch-notes/"},
    {"category": "版本 / 榜外观察", "date": "2026-09-07", "title": "Forge of Empires发布1.343国际服版本", "summary": "版本调整Historical Allies与Stellar Age提示并修复多项移动端稳定性问题；全服计划9月9日更新。", "impact": "该作9月9日从Google掉榜，今天仍未回归；更新后首个快照尚未显示榜位承接，继续作为版本—排名对照。", "source": "InnoGames官方", "url": "https://support.innogames.com/kb/ForgeOfEmpires/en_DK/6975/Update-to-version-1343"},
    {"category": "区域趋势", "date": "2026-09（官方发布月）", "title": "Sensor Tower：日本4X策略收入同比增长9.4%", "summary": "日本近12个月手游IAP超100亿美元；报告称4X Strategy领跑细分收入并增长9.4%，Last War是主要支撑产品。", "impact": "成熟高付费市场仍能支撑4X增长，但这是日本区域口径，不能替代美国双榜或全球单品收入。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/state-of-japan-gaming-2026"},
    {"category": "版本更新", "date": "2026-08-30", "title": "Clash of Clans更新TH18宠物与Supercharge等级", "summary": "官方更新增加Diggy等级、Builder's Hut与Monolith强化，并调整回流、新手与部落战联赛体验。", "impact": "Clash of Clans今日Google #8、iOS #7，持续位于双端头部；版本效果仍应结合多日位置而非单一快照。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/release-notes/august-update-3/"},
    {"category": "新赛季 / 跨端分化", "date": "2026-08-31", "title": "MARVEL SNAP运营AXIS: Inversion赛季", "summary": "赛季包含新角色、地点、登录日历、Draft、Team Clash及网页商店季票奖励。", "impact": "今天Google下降15位至#49、iOS反升5位至#44；同一赛季下的跨端反向说明不能用单端日榜概括活动收入。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/new-season-axis-inversion/"},
    {"category": "长线运营", "date": "2026-08-28", "title": "Boom Beach公布9月活动日历", "summary": "9月安排Speed Serum、兵种Mania、Mega Crab、Leader Deployment与月底Warships Season 92。", "impact": "Boom Beach仍未进两端策略TOP60；密集活动不等同于当日榜面回升，可继续作为活动—排名转化对照。", "source": "Supercell官方", "url": "https://supercell.com/en/games/boombeach/blog/blog/this-september-on-boom-beach-2/"},
]


closing = [
    {"type": "判断", "title": "Google主要是前一日掉榜产品回补，iOS出现真正的新产品高位进入", "detail": "Google三款进入均为历史榜内产品回榜，其中Titan Rush与Draft Showdown仍在后八名；iOS的Pokémon Champions则首次进入即到#19，F1 Clash也首次进入项目榜。两端换榜质量不能只按进出数量判断。"},
    {"type": "判断", "title": "新品信号从单端数量转向可持续位置验证", "detail": "Google新品仍为5款，但Warline因窗口滚动不再属于90天新品，由回榜#17的Lordrush补位；iOS新品增至3款。Lordrush双端前25和Pokémon Champions iOS前20，比单纯新增计数更值得观察。"},
    {"type": "判断", "title": "月度收入头部稳定，日榜中段仍存在明显跨端噪声", "detail": "Sensor Tower 8月策略子集Whiteout Survival与Kingshot仍对应今日美国双端头部；与此同时MARVEL SNAP在Google−15、iOS+5，说明单日平台波动不能替代全球月度收入判断。"},
    {"type": "关注", "title": "9月11日：验证Lordrush与Pokémon Champions的高位持续性", "detail": "Lordrush若继续保持双端前25、Pokémon Champions若守住iOS前30，可把今天从单日回补升级为连续高位信号；任一快速回落则按短时付费峰值归档。"},
    {"type": "关注", "title": "9月11日：复核五款榜尾进入产品", "detail": "Google的Titan Rush与Draft Showdown，以及iOS的F1 Clash、Galaxy Defense和Last Fortress均在#48以后；重点看至少两款能否脱离后十名，而不只是继续轮换。"},
    {"type": "关注", "title": "截至9月14日：拆分版本、赛事与跨端排名", "detail": "结合Pokémon竞技规则、F1 Madring、Clash Royale赛季与King of Avalon周年节点，只有连续榜位与双端共振出现时才升级判断；否则继续标记为待验证，不换算单品收入。"},
]


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Lordrush双端重回前25，Pokémon Champions首进iOS #19",
    "summary": "与9月9日快照相比，Google Play由Lordrush、Titan Rush和Draft Showdown进入/回榜，Sea of Conquest、Supremacy与Ant Legion掉榜；iOS由Pokémon Champions、Last Fortress、F1 Clash和Galaxy Defense进入/回榜，Vikings、Kingdom Guard、Wild Rift与Top Heroes掉榜。Lordrush双端前25与Pokémon Champions首进#19是今日最值得连续验证的信号。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": "data/games-20260910.json", "ios": "data/ios-games-20260910.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260909.json", "ios": "data/ios-games-20260909.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Lords Mobile x Transformers · #60 Draft Showdown", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}", "anchors": "榜单锚点：#1 Pokémon GO · #25 Tiles Survive! · #60 Galaxy Defense: Fortress TD", "products": ios_products},
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": 5, "surge90d": 0, "baselineAvailable": False},
        "ios": {"top60": 60, "newRelease90d": 3, "surge90d": 0, "baselineAvailable": False},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-10.md", "json": "data/market-brief-20260910.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        "- Google锚点：#1 Kingshot · #25 Lords Mobile x Transformers · #60 Draft Showdown",
        "- iOS锚点：#1 Pokémon GO · #25 Tiles Survive! · #60 Galaxy Defense: Fortress TD",
        "- 对比基准：各自上一份有效快照为2026-09-09；所有升降均为相邻工作日变化。",
        "- 近90天状态：Google新上榜5款、iOS新上榜3款；两端均缺少2026-06-12精确同口径TOP60基准，较老产品暂不判断飙升。", "",
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


save("data/market-brief-20260910.json", brief)
(ROOT / "reports/2026-09-10.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(google_products) + len(ios_products)} product cards and {len(news)} news items")
