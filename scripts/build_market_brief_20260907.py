#!/usr/bin/env python3
"""Generate the Beijing 2026-09-07 market brief and archive entry."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-07"
STAMP = "20260907"


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


google_history = load("data/history/google-play/2026-09-07.json")
ios_history = load("data/history/ios/2026-09-07.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    product("Forge of Empires: Build a City", "com.innogames.foeandroid", "googlePlay", "entry", "进入 · #53", "项目首次记录该作进入Google TOP60。Android版2015年上线、属于成熟长线产品；官方1.343国际服更新与本次进榜同日，但移动更新可能延后，现阶段只记时间重合，不能确认由版本驱动。"),
    product("Last Fortress: Underground", "com.more.lastfortress.gp", "googlePlay", "entry", "回榜 · #60", "自8月19日#58后再次进入项目Google快照，本期压线#60；iOS则由上期#56掉榜，形成Android回榜、iOS退出的跨端错位，稳定性仍弱。"),
    product("Sea War: Uboat Raid", "com.bw.ud.googleplay", "googlePlay", "exit", "掉榜 · 上期#53", "9月4日仍处#53，本期跌出Google TOP60；iOS同时由#50降至#53但仍在榜。单端掉榜说明Android侧短期承接转弱，不代表全产品收入同步下行。"),
    product("Arknights", "com.YoStarEN.Arknights", "googlePlay", "exit", "掉榜 · 上期#60", "上期以#60回榜，本期再次退出Google策略TOP60；iOS当前也未进入同口径榜。一次压线回榜未形成连续留榜，按榜尾短峰处理。"),
    product("GIRLS' FRONTLINE 2: EXILIUM", "com.Sunborn.SnqxExilium.Glo", "googlePlay", "down", "−17 · #41", "较9月4日由#24降至#41，iOS仍在榜外；8月末Chiral Redundancy版本带来的Android高位承接继续回吐，但周末累计跌幅不能直接解释为单日变化或版本失效。"),
    product("Duck Survival", "com.mrtgd2us.google", "googlePlay", "down", "−13 · #40", "较上一份有效快照从#27回落至#40，iOS无对应TOP60排名。产品仍处Google中段而非榜尾，缺少可核验活动节点，先观察是否继续滑向后十名。"),
    product("Titan Rush", "com.ratinghope.gplay", "googlePlay", "down", "−9 · #54", "由#45降至#54，进入最后七名风险区；iOS没有对应TOP60排名。当前无公开节点可解释跌幅，下一快照若再降将接近掉榜。"),
    product("Guns of Glory: Lost Island", "com.diandian.gog", "googlePlay", "up", "+7 · #30", "Google由#37升至#30，同时iOS回榜#58。两端方向一致但强度差异很大；Google已进入中段，iOS仍压线，需连续快照确认是否与同期活动有关。"),
    product("Lords Mobile x Transformers", "com.igg.android.lordsmobile", "googlePlay", "up", "+6 · #25", "Google由#31升至#25，但iOS从上期#51掉榜，跨端明显分化。联动后缀仍在店铺名中，却不能仅凭名称把Android上涨归因于联动付费。"),
    product("Lands of Jail", "com.justgame.jails", "googlePlay", "down", "−6 · #31", "Google从#25降至#31，iOS同步从#47降至#57；这是少数双端共同下行产品。两端仍在榜，但iOS已进入榜尾风险区。"),
]


ios_products = [
    product("The Battle Cats", "850057092", "ios", "entry", "回榜 · #26", "8月31日最后一次在榜为#53，本期回到#26，属于成熟产品从榜尾回到中段；Google当前无对应TOP60排名，缺少活动证据，先按iOS单端回补信号处理。"),
    product("Watcher of Realms - US", "6741674823", "ios", "entry", "回榜 · #35", "9月4日刚从#51掉榜，本期直接回到#35；Google无对应排名。回榜幅度较强，但此前波动反复，仍需验证能否连续守住TOP40。"),
    product("Star Trek Fleet Command", "1427744264", "ios", "entry", "回榜 · #52", "8月31日最后在榜#57，本期回到#52；Google当前#17，跨端差距达到35位。iOS仍处后段，产品收入承接主要体现在Android侧。"),
    product("Warline: Sniper Strike", "6742809194", "ios", "entry", "回榜 · #56", "8月24日曾位于#58，本期回到#56；按iOS 7月22日上架日期仍属于近90天新品。Google当前位于#29，主要由Android侧承接，iOS仍有榜尾风险。"),
    product("Guns of Glory: Lost Island", "1274354704", "ios", "entry", "回榜 · #58", "9月4日从#59掉榜后本期回到#58；Google同期升7位至#30。iOS反复压线，双端共同在榜但商业化强度仍由Google主导。"),
    product("Lords Mobile x Transformers", "1071976327", "ios", "exit", "掉榜 · 上期#51", "iOS由#51掉榜，而Google升6位至#25，成为今日最明显的跨端反向案例之一。不能用Android上行替代iPhone侧真实掉榜。"),
    product("Last Fortress: Underground", "1540557475", "ios", "exit", "掉榜 · 上期#56", "iOS由#56退出，同时Google以#60回榜；两个商店都处边缘位置，跨端错位更像成熟产品的短期付费脉冲，而非稳定上行。"),
    product("Top Heroes: Kingdom Saga", "6450953550", "ios", "exit", "掉榜 · 上期#57", "上期已处#57，本期跌出iOS TOP60；Google仍在#43但较9月4日下降2位。iOS榜尾风险兑现，Android也没有同步改善。"),
    product("Last Light: Wasteland", "6754545818", "ios", "exit", "掉榜 · 上期#58", "上期回榜#58后本期再次退出，Google也无对应排名。短暂回榜未能脱离最后三名，当前仍属于上线首年的单端榜尾信号。"),
    product("Draft Showdown", "6743368869", "ios", "exit", "掉榜 · 上期#60", "9月4日压线回榜后再次掉出iOS TOP60，Google也未在榜。两次只触及#60且都未留住，榜尾脆弱性得到连续快照确认。"),
    product("Warhammer 40,000: Tacticus", "1599937506", "ios", "up", "+19 · #29", "iOS由#48升至#29，是本期主要上涨；Google同期升2位至#27，双端重新靠拢到相近区间。尚无与本次周末涨幅直接对应的官方节点，先记为待验证信号。"),
    product("Dragon Traveler", "6751086804", "ios", "down", "−14 · #45", "9月4日刚从#52升至#31，本期回落到#45，前一轮高位明显回吐；Google仍无对应TOP60排名。若下一快照继续下滑，将重新接近榜尾。"),
    product("Kingdom Guard: Tower Defense", "1570095804", "ios", "up", "+14 · #38", "iOS由#52升至#38，但Google由#47降至#52，形成明确跨端分化。iPhone侧回补强，Android侧却进入榜尾风险区，不能合并为统一收入趋势。"),
    product("Forge Master – Idle RPG", "6746636289", "ios", "down", "−14 · #49", "iOS由#35降至#49，Google没有对应TOP60排名。产品从中段退到后段，周末累计跌幅较大，但当前缺少可核验的活动结束节点。"),
    product("War and Order", "1071744151", "ios", "up", "+11 · #28", "iOS由#39升至#28，Google也由#30升至#26，是本期最清晰的双端同步上行之一。三天累计信号尚不能外推长期趋势，下一工作日是否守住双端TOP30更关键。"),
    product("MARVEL SNAP", "1592081003", "ios", "down", "−11 · #36", "iOS由#25降至#36，而Google小升至#33，AXIS赛季后的双端走势转为分化。iOS回吐明显，Google维持中段，需避免把一个商店的跌幅扩展为全产品判断。"),
    product("Yu-Gi-Oh! Master Duel", "1554247785", "ios", "down", "−22 · #46", "9月4日借回榜来到#24，本期回落到#46，WCS同期高位没有继续维持。产品仍在榜，但三天后大幅回吐使短期赛事/付费峰值解释更可信。"),
    product("Summoners War", "852912420", "ios", "down", "−11 · #44", "iOS由#33降至#44，Google没有对应策略TOP60排名。成熟RPG仍处中后段，不到掉榜边缘；缺少同日官方节点时只记录位置回落。"),
    product("Lands of Jail", "6738469826", "ios", "down", "−10 · #57", "iOS由#47降至#57，Google同步由#25降至#31。两端共同下行，其中iOS已进入最后四名；下一快照将检验是否继续掉榜。"),
]


news = [
    {"category": "全球月榜", "date": "2026-09-04（估算截至）", "title": "Sensor Tower发布8月全球手游收入TOP10", "summary": "全球手游消费者支出约65.7亿美元、环比下降1%；Honor of Kings居首，Whiteout Survival第3、Kingshot第7。", "impact": "两款核心策略产品均较7月上升1位，并在今日美国双端保持TOP3；但官方仍未公开单品收入同比，不能从榜位换算百分比。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"},
    {"category": "新赛季", "date": "2026-09-07", "title": "Clash Royale开启Minion Academy赛季", "summary": "官方公布Minion Giant新卡、Ice Wizard英雄、Album Event、2v2 League和Royale Shuffle等9月内容。", "impact": "Clash Royale今日Google #18、iOS #11，双端均较9月4日上升；需用赛季首周观察通行证与新卡承接，不能只看首日。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/new-season-minion-academy/"},
    {"category": "版本 / 回榜", "date": "2026-09-07", "title": "Forge of Empires发布1.343国际服版本", "summary": "版本调整Historical Allies与Stellar Age提示并修复多项移动端稳定性问题；全服计划9月9日更新。", "impact": "该作今日首次进入项目Google榜#53；官方同时提醒移动端商店发布可能延后，因此当前只能记录时间重合。", "source": "InnoGames官方", "url": "https://support.innogames.com/kb/ForgeOfEmpires/en_DK/6975/Update-to-version-1343"},
    {"category": "周年运营", "date": "2026-09-04", "title": "King of Avalon开启十周年整月活动", "summary": "9月4日至30日活动加入可收集Merlin、八个传奇地点、七件遗物、拼图、英雄与周年奖励。", "impact": "King of Avalon今日Google升3位至#36、iOS未进榜；活动初期出现Android回补，但尚无双端同步验证。", "source": "FunPlus官方", "url": "https://funplus.com/king-of-avalon-celebrates-10th-anniversary/"},
    {"category": "区域趋势", "date": "2026-09（官方发布月）", "title": "Sensor Tower：日本4X策略收入同比增长9.4%", "summary": "日本近12个月手游IAP超100亿美元；报告称4X Strategy领跑细分收入并增长9.4%，Last War是主要支撑产品。", "impact": "这表明成熟高付费市场仍能支撑4X增长，但报告是日本市场口径，不能直接替代美国双榜或全球单品收入。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/state-of-japan-gaming-2026"},
    {"category": "版本更新", "date": "2026-08-30", "title": "Clash of Clans更新TH18宠物与Supercharge等级", "summary": "官方8月更新增加Diggy等级、Builder's Hut与Monolith强化，并调整回流、新手与部落战联赛体验。", "impact": "Clash of Clans今日Google #6、iOS #8，仍稳居双端头部；版本影响应结合数个工作日，而非单一排名。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/release-notes/august-update-3/"},
    {"category": "新赛季", "date": "2026-08-31", "title": "MARVEL SNAP继续运营AXIS: Inversion赛季", "summary": "赛季包含新角色、地点、登录日历、Draft、Team Clash与多段活动，并提供网页商店季票奖励。", "impact": "今日Google #33、iOS #36，iPhone侧较9月4日回落11位；赛季首周的双端承接已出现分化。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/new-season-axis-inversion/"},
    {"category": "长线赛季", "date": "2026-08-28", "title": "Clash Royale将Merge Tactics第11赛季延长至三个月", "summary": "Season 11从9月1日持续至12月1日，不再月度重置，并扩展Starsteel Road及统治者奖励。", "impact": "更长周期与主赛季新内容叠加，提供观察战术副玩法能否改善留存和付费节奏的窗口。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/merge-tactics-season-11/"},
    {"category": "版本运营", "date": "2026-08-26", "title": "GFL2的Chiral Redundancy版本进入承接观察期", "summary": "官方加入限时剧情、Frontier platoon玩法、Tile Transformation系统及角色卡池。", "impact": "GFL2今日Google由#24降至#41、iOS榜外；版本后高位继续回吐，但三天累计变化不能归结为单一原因。", "source": "GIRLS' FRONTLINE 2官方", "url": "https://gf2exilium.sunborngame.com/NewsInfo?id=393&typeId=3"},
    {"category": "IP联动", "date": "2026-08-25", "title": "State of Survival推进《如龙8》联动", "summary": "8月28日起加入联盟Boss、节奏挑战、感染摩托、角色和排行榜内容。", "impact": "State of Survival今日Google #44、iOS未进榜，仍未形成双端共同抬升；应继续观察完整联动周期。", "source": "FunPlus官方", "url": "https://funplus.com/state-of-survival-x-like-a-dragon-infinite-wealth-crossover-event/"},
]


closing = [
    {"type": "判断", "title": "周末后三天累计波动主要集中在iOS中后段", "detail": "Google为2进2出，iOS为5进5出；iOS还出现Yu-Gi-Oh! −22、Tacticus +19，以及Dragon Traveler与Forge Master均−14。由于这是9月4日至7日累计变化，不把幅度解释为单日冲击。"},
    {"type": "判断", "title": "War and Order与Tacticus形成双端同向信号", "detail": "War and Order在Google +4至#26、iOS +11至#28；Tacticus在Google +2至#27、iOS +19至#29。两款都收敛到双端TOP30，但三天累计信号仍不足以断言长期趋势。"},
    {"type": "判断", "title": "Sensor Tower新月榜中两款核心策略产品均上升1位", "detail": "Whiteout Survival位列8月全球收入总榜#3、Kingshot #7；今日美国榜对应为Google #3/#1、iOS #3/#2。月度全球数据与美国日榜都处头部，但官方未公开单品同比，页面不补算。"},
    {"type": "关注", "title": "9月8—9日：验证Forge of Empires回榜与1.343全服更新", "detail": "若Google能从#53脱离榜尾并在9月9日全服更新后持续留榜，才提高版本承接判断；若迅速退出，仍按成熟产品短期回补记录。"},
    {"type": "关注", "title": "9月8日下一快照：核对五款iOS回榜产品留存", "detail": "The Battle Cats #26与Watcher #35信号强于位于#52、#56、#58的Star Trek、Warline和Guns of Glory；后三款若不能脱离榜尾，继续按短期回补处理。"},
    {"type": "关注", "title": "9月8—10日：检验双端共振与分化能否延续", "detail": "观察War and Order能否双端守住TOP30，同时看GFL2是否跌出Google TOP45、Lands of Jail是否在iOS掉榜，以及MARVEL SNAP能否恢复双端同向。"},
]


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "周末后Google两进两出、iOS五进五出；War and Order与Tacticus双端靠拢",
    "summary": "与9月4日上一份有效快照相比，Google Play有Forge of Empires与Last Fortress: Underground进入/回榜，Sea War与Arknights掉榜；iOS有5款回榜、5款掉榜。War and Order升至Google #26/iOS #28，Tacticus升至#27/#29；Lords Mobile、Kingdom Guard与MARVEL SNAP则呈跨端分化。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": "data/games-20260907.json", "ios": "data/ios-games-20260907.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260904.json", "ios": "data/ios-games-20260904.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Lords Mobile x Transformers · #60 Last Fortress: Underground", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}", "anchors": "榜单锚点：#1 Pokémon GO · #25 Mobile Legends: Bang Bang.US · #60 Fire Emblem Heroes", "products": ios_products},
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": 6, "surge90d": 0, "baselineAvailable": False},
        "ios": {"top60": 60, "newRelease90d": 2, "surge90d": 0, "baselineAvailable": False},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-07.md", "json": "data/market-brief-20260907.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        "- Google锚点：#1 Kingshot · #25 Lords Mobile x Transformers · #60 Last Fortress: Underground",
        "- iOS锚点：#1 Pokémon GO · #25 Mobile Legends: Bang Bang.US · #60 Fire Emblem Heroes",
        "- 对比基准：各自上一份有效快照为2026-09-04；升降是跨周末三天累计变化，不写成单日变化。",
        "- 近90天状态：Google新上榜6款、iOS新上榜2款；两端均缺少2026-06-09精确同口径TOP60基准，较老产品暂不判断飙升。", "",
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


save("data/market-brief-20260907.json", brief)
(ROOT / "reports/2026-09-07.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(google_products) + len(ios_products)} product cards and {len(news)} news items")
