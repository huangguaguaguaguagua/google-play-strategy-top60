#!/usr/bin/env python3
"""Generate the Beijing 2026-09-04 market brief and archive entry."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-04"
STAMP = "20260904"


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


google_history = load("data/history/google-play/2026-09-04.json")
ios_history = load("data/history/ios/2026-09-04.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))

google_products = [
    product("Foundation: Galactic Frontier", "com.games.foundation", "googlePlay", "up", "+3 · #20", "Google连续从#26、#23升至#20，iOS也同步上升3位至#34，形成温和的双端共振。公开信息没有与9月4日精确对应的重大活动，因此先记录为连续榜位信号，不把原因归到特定内容。"),
    product("GIRLS' FRONTLINE 2: EXILIUM", "com.Sunborn.SnqxExilium.Glo", "googlePlay", "down", "−11 · #24", "8月28日双端共同进入后，产品一直由Android侧承接，本期Google由#13回落至#24，iOS已不在TOP60。8月25日版本内容仍在运营期，但单日下跌不能直接等同于版本失效；下一快照决定是否只是高位回吐。"),
    product("Top Lords", "com.gamespark.topking.gp", "googlePlay", "up", "+5 · #52", "Google由#57升至#52、暂离最后五名，iOS当前#32且变化较小。该产品仍属近90天新品，Android侧只是从榜尾回补，尚不足以确认形成稳定上行区间。"),
    product("Doomsday: The Seven Deadly Sins", "com.igg.android.doomsdaylastsurvivors", "googlePlay", "down", "−5 · #51", "Google由#46降至#51并进入榜尾风险区，iOS没有对应TOP60排名。当前没有与本次下跌直接对应的官方节点，先按单日付费位置回落处理。"),
    product("Kingdom Guard: Tower Defense", "com.tap4fun.odin.kingdomguard", "googlePlay", "up", "+4 · #47", "Google由#51回升至#47，但iOS同时由#49降至#52，出现轻度跨端分化。两端都仍在后段，Android单日回补不能代表整体收入趋势反转。"),
    product("MARVEL SNAP", "com.nvsgames.snap", "googlePlay", "down", "−3 · #34", "Google由#31降至#34，iOS也由#18回落7位至#25，结束了此前两天的同步快速上行。AXIS: Inversion赛季仍在首周，本期更像活动峰值后的首次回吐；需要继续判断能否守住Google TOP35与iOS TOP25。"),
]

ios_products = [
    product("Yu-Gi-Oh! Master Duel", "1554247785", "ios", "entry", "回榜 · #24", "8月21日最后一次在项目iOS快照位于#35，本期直接回到#24；Google策略TOP60没有对应排名。WCS 2026于9月1日公布冠军，时间与回榜接近，但仅凭日榜不能认定赛事就是收入抬升原因。"),
    product("Cell Survivor - Shoot Defense", "6746465127", "ios", "entry", "回榜 · #45", "8月26日最后一次在榜为#53，本期回到#45，仍是iOS单端信号，Google未进入TOP60。产品当前处中后段而非压线位置，但没有公开活动依据，先观察能否连续留榜。"),
    product("Last Shelter: Survival", "1342290011", "ios", "entry", "回榜 · #59", "8月27日曾以#60短暂回榜，本期再次出现在#59；Google同名老产品没有进入当前TOP60。成熟SLG连续以末两名回补，说明仍有付费脉冲，但榜尾稳定性很低。"),
    product("Draft Showdown", "6743368869", "ios", "entry", "回榜 · #60", "8月24日最后一次在榜同样位于#60，本期再次压线回归；Google当前也未进入TOP60。反复只触及最后一名，应视为边缘回榜信号，而不是稳定收入增长。"),
    product("Watcher of Realms - US", "6741674823", "ios", "exit", "掉榜 · 上期#51", "昨日从#37跌至#51，本期继续掉出TOP60，Google也无对应排名。连续两次向下使短期风险得到确认，但仍不能据此推断产品的长期或全球收入趋势。"),
    product("Galaxy Defense: Fortress TD", "6740189002", "ios", "exit", "掉榜 · 上期#55", "9月2日以#57回榜、昨日升至#55，本期再次退出；Google没有对应TOP60排名。短暂两日回榜未能摆脱榜尾，当前应按脆弱回补处理。"),
    product("Guns of Glory: Lost Island", "1274354704", "ios", "exit", "掉榜 · 上期#59", "9月2日回榜#58、昨日降至#59后本期掉榜，Google同口径榜也未收录。两日榜尾停留后退出，尚未形成可持续的周年或活动信号。"),
    product("Overgeared Hero: Merge RPG", "6755585789", "ios", "exit", "掉榜 · 上期#60", "昨日降至#60后本期退出，而Google仍在#40，跨端差异转为Android单端承接。iOS榜尾风险兑现，但不能把一个商店的掉榜扩大解释为全产品收入下行。"),
    product("Dragon Traveler", "6751086804", "ios", "up", "+21 · #31", "iOS由#52跃升至#31，是今日最大涨幅；产品在8月下旬曾位于#30—40区间，此次更像从榜尾回到此前区间。Google策略TOP60没有对应排名，且缺少可确认活动节点，仍属单端待验证信号。"),
    product("The Tower - Idle Tower Defense", "1575590830", "ios", "down", "−15 · #55", "9月2日由#59升至#33，随后降至#40，本期再降15位至#55，首日峰值已大幅回吐。Google没有对应TOP60排名，下一快照若继续下滑将重新面临掉榜风险。"),
    product("RAID: Shadow Legends", "1371565796", "ios", "down", "−8 · #29", "iOS由#21降至#29，Google策略TOP60未收录。产品仍处TOP30而非榜尾，本次更适合解释为成熟RPG付费位置波动，不应把单日跌幅当作长期衰退。"),
    product("MARVEL SNAP", "1592081003", "ios", "down", "−7 · #25", "iOS由#18回落至#25，Google同步小降至#34；此前赛季首两日的双端上行出现首次共同修正。若接下来仍守住当前区间，可视为活动后中枢抬高；继续回落则更接近短期峰值。"),
    product("Game of Thrones: Dragonfire", "1642607669", "ios", "up", "+6 · #11", "iOS由#17升至#11，Google保持#22附近，仍是两端同时在榜的近90天新品。今日增量集中在iPhone侧，缺少同日官方重大节点，因此先观察能否进入并守住TOP10。"),
]

news = [
    {"category": "赛事 / 回榜", "date": "2026-09-01", "title": "Yu-Gi-Oh! WCS 2026公布Master Duel冠军", "summary": "Konami公告确认东京总决赛结束，Called By Army获得Master Duel三人赛冠军，并保留赛事直播回放。", "impact": "Master Duel今日回到美国iOS策略畅销榜#24；赛事与回榜时间重合，但需要后续留榜与卡包/活动节点共同验证，不能直接做因果判断。", "source": "Konami新闻稿", "url": "https://www.mynewsdesk.com/uk/swipe-right/pressreleases/introducing-the-kings-of-games-yu-gi-oh-world-championship-2026-crowns-champions-in-tokyo-3463917"},
    {"category": "IP联动", "date": "2026-09-01", "title": "Clash of Clans开启WWE Search for Cena整月活动", "summary": "官方列出9月限定WWE英雄皮肤与场景、John Cena挑战、临时兵种、部落冲刺和多段资源/装备活动。", "impact": "Clash of Clans当前Google #7、iOS #6，双端仍处高位；本期iOS小幅回落，需用活动首周而非单日排名评估承接。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/news/wwe-search-for-cena-steps-into-the-ring/"},
    {"category": "新赛季", "date": "2026-08-31", "title": "MARVEL SNAP进入AXIS: Inversion赛季首周", "summary": "新赛季加入季票角色、两处新地点、21日登录日历、Draft、Team Clash及多段9月活动。", "impact": "产品此前双端连涨后今日Google -3、iOS -7；这是一轮峰值后的首次共同回吐，接下来两次快照可检验新中枢。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/new-season-axis-inversion/"},
    {"category": "品类趋势", "date": "2026-08", "title": "Sensor Tower：Q2策略仍是全球收入最高游戏品类", "summary": "Sensor Tower披露Q2策略游戏IAP收入约44亿美元；益智类增长17%至逾40亿美元，正在接近策略品类。", "impact": "策略仍保持收入规模领先，但益智快速靠近，进一步解释了策略产品持续采用解谜、塔防和轻玩法获量入口的竞争压力。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/q2-2026-digital-market-index-report"},
    {"category": "社区运营", "date": "2026-09-01", "title": "Kingshot上线Observation Test社区活动", "summary": "Century Games发布水桶观察题互动，并引导玩家参与社区评论及官方商店。", "impact": "Kingshot当前Google #1、iOS #2，且位列Sensor Tower 7月全球收入总榜#8；该活动规模有限，只能视为高频社区运营的一环。", "source": "Century Games官方", "url": "https://www.centurygames.com/kingshot-observation-test/"},
    {"category": "社区运营", "date": "2026-09-01", "title": "Whiteout Survival发布Fix The Equation互动", "summary": "Century Games同步上线解题型社区活动，通过评论与游戏ID发放奖励。", "impact": "Whiteout当前Google #2、iOS #4，并位列Sensor Tower 7月全球收入总榜#4；小型互动不能解释收入，但显示头部产品仍维持连续社区触达。", "source": "Century Games官方", "url": "https://www.centurygames.com/whiteout-survival-fix-the-equation/"},
    {"category": "长线赛季", "date": "2026-08-28", "title": "Clash Royale Merge Tactics第11赛季改为三个月周期", "summary": "官方宣布Season 11从9月1日持续至12月1日，不再月度重置，并加入3个新兵种、Rider特性和17个兵种重做。", "impact": "Clash Royale当前Google #19、iOS #15；更长赛季有利于观察战术副玩法对长期参与和付费节奏的影响。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/merge-tactics-season-11/"},
    {"category": "IP联动", "date": "2026-08-25", "title": "State of Survival推进《如龙8》联动", "summary": "FunPlus公布春日一番、桐生一马和真岛吾朗英雄，以及联盟Boss、节奏挑战、感染摩托和排行榜活动。", "impact": "产品当前Google #43、iOS仍未进榜，尚未出现双端同步抬升；应继续观察完整活动周期。", "source": "FunPlus官方", "url": "https://funplus.com/state-of-survival-x-like-a-dragon-infinite-wealth-crossover-event/"},
    {"category": "版本运营", "date": "2026-08-25", "title": "GFL2的Chiral Redundancy版本进入后续观察期", "summary": "官方公告列出OTs-14、Nemesis: Gnosis、限时剧情与Tile Transformation等内容。", "impact": "产品今日Google -11至#24、iOS榜外；Android仍在前半榜，但版本后的高位承接出现明显回吐。", "source": "GIRLS' FRONTLINE 2官方", "url": "https://gf2exilium.sunborngame.com/NewsInfo?id=393&typeId=3"},
    {"category": "报道 / 软启动", "date": "2026-08-31", "title": "大厂策略与生存新品继续密集软启动", "summary": "Mobilegamer.biz汇总Supercell、腾讯、Century Games与Zynga等测试产品，报道中的地区和范围均可能继续变化。", "impact": "Crownstone Survival、Frozen Manor等测试显示生存经营、合成与塔防仍是大厂探索方向；需等待美国商店实际开放和下载数据验证。", "source": "Mobilegamer.biz（报道）", "url": "https://mobilegamer.biz/the-soft-launch-games-you-need-to-know-about/"},
]

closing = [
    {"type": "判断", "title": "Google成分稳定，iOS则出现四进四出和大幅中段换位", "detail": "Google没有产品进出，仅GFL2出现两位数下跌；iOS有4款回榜、4款掉榜，并同时出现Dragon Traveler +21与The Tower -15。今天最明确的是平台波动差异，而不是整个策略市场共同转向。"},
    {"type": "判断", "title": "MARVEL SNAP的赛季首轮峰值开始回吐", "detail": "Google由#31降至#34、iOS由#18降至#25，结束此前连续双端上行。官方赛季节点仍在，只有后续守住当前区间，才能说明活动抬高了短期中枢。"},
    {"type": "判断", "title": "全球月榜策略子集仍由Whiteout与Kingshot代表，且美国双端保持头部", "detail": "Sensor Tower 7月全球收入总榜中Whiteout Survival #4、Kingshot #8；今天两款分别位于Google #2/#1和iOS #4/#2。月度全球数据与美国日榜方向一致，但周期和地域不同，不据此推算单品收入同比。"},
    {"type": "关注", "title": "9月7日下一快照：核对iOS四款回榜产品的留榜质量", "detail": "Yu-Gi-Oh!当前#24，信号强于位于#45、#59、#60的Cell Survivor、Last Shelter与Draft Showdown；若后三款不能脱离榜尾，继续按短期回补记录。"},
    {"type": "关注", "title": "9月7—8日：验证GFL2与MARVEL SNAP是否继续回吐", "detail": "若GFL2继续跌出Google TOP30，或MARVEL SNAP跌出Google TOP35且iOS TOP25，应降低当前版本/赛季的短期承接判断；反之视为峰值后的区间整理。"},
    {"type": "关注", "title": "Sensor Tower发布8月榜时：只更新官方策略命中项", "detail": "继续在工作日检查一次官方月榜；新一期发布后核对完整全球收入TOP10、前期位次及策略定义，未公开的单品同比仍显示为未公开，不从名次推算百分比。"},
]

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Google零换榜保持稳定；iOS四进四出，MARVEL SNAP首轮回吐",
    "summary": "与9月3日相比，Google Play完整60款没有进出，最大变化是GFL2下跌11位；iOS出现Yu-Gi-Oh!、Cell Survivor、Last Shelter与Draft Showdown回榜，Watcher of Realms、Galaxy Defense、Guns of Glory与Overgeared Hero掉榜。Dragon Traveler上升21位、The Tower下降15位，iOS中后段波动继续显著高于Google。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": "data/games-20260904.json", "ios": "data/ios-games-20260904.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260903.json", "ios": "data/ios-games-20260903.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Lands of Jail · #60 Arknights", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}", "anchors": "榜单锚点：#1 Pokémon GO · #25 MARVEL SNAP · #60 Draft Showdown", "products": ios_products},
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
    "downloads": {"markdown": "reports/2026-09-04.md", "json": "data/market-brief-20260904.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        "- Google锚点：#1 Kingshot · #25 Lands of Jail · #60 Arknights",
        "- iOS锚点：#1 Pokémon GO · #25 MARVEL SNAP · #60 Draft Showdown",
        "- 对比基准：各自上一份有效快照为2026-09-03。",
        "- 近90天状态：Google新上榜6款、iOS新上榜2款；两端均缺少2026-06-06精确同口径TOP60基准，较老产品暂不判断飙升。", "",
        "## 1. 双榜当日异动产品", "",
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
        f"- 市场总览：全球手游消费者支出约${revenue['marketSummary']['globalConsumerSpendingUsd'] / 1_000_000_000:g}B，环比+{revenue['marketSummary']['monthOverMonthPercent']:g}%，全市场同比约{revenue['marketSummary']['yearOverYearPercentApprox']:g}%",
        f"- 原始来源：[{revenue['source']}]({revenue['sourceUrl']})", "",
        "| 全球总榜 | 游戏 | 发行商 | 策略类型 | 较上月榜位 | 单品收入同比 |", "|---:|---|---|---|---|---|",
    ]
    for item in revenue["rankings"]:
        lines.append(f"| {item['rank']} | {item['gameName']} | {item['publisher']} | {item['strategyGenre']} | {item['movementLabel']} | {item['yoyRevenueLabel']} |")
    lines += ["", "### 策略产品与同比口径", ""]
    lines += [f"- {item}" for item in revenue["officialHighlights"]]
    lines += [
        "", revenue["methodologyNote"], "", "## 下载与来源", "",
        f"- JSON：`{value['downloads']['json']}`",
        f"- Sensor Tower上月对照：{revenue['previousPeriodSourceUrl']}",
        f"- Sensor Tower同比对照：{revenue['yearOverYearSourceUrl']}",
        "- Google Play直连源：https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US",
        "- Apple官方RSS：https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json", "",
    ]
    return "\n".join(lines)


save("data/market-brief-20260904.json", brief)
(ROOT / "reports/2026-09-04.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(google_products) + len(ios_products)} product cards and {len(news)} news items")
