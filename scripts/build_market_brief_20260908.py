#!/usr/bin/env python3
"""Generate the Beijing 2026-09-08 market brief and archive entry."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-08"
STAMP = "20260908"


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


google_history = load("data/history/google-play/2026-09-08.json")
ios_history = load("data/history/ios/2026-09-08.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    product("Supremacy: World War 3", "com.doradogames.conflictnations.worldwar3", "googlePlay", "entry", "进入 · #60", "项目首次记录该作进入Google TOP60，iOS同期升3位至#34。Android版2020年上线，属于成熟实时大战略；双端同向但Google仍压线，且没有可确认的近期活动证据，先记为待验证回补信号。"),
    product("Last Fortress: Underground", "com.more.lastfortress.gp", "googlePlay", "exit", "掉榜 · 上期#60", "上期刚以#60回榜，本期即退出；iOS也未进入当前TOP60。两端都没有形成连续留榜，榜尾短期付费脉冲的解释强于稳定回升。"),
    product("GIRLS' FRONTLINE 2: EXILIUM", "com.Sunborn.SnqxExilium.Glo", "googlePlay", "down", "−10 · #51", "继9月4日至7日从#24降至#41后，今天继续回落到#51，iOS仍在榜外。Chiral Redundancy版本后的高位承接继续消退，但仅凭榜位不能判定活动收入或用户规模同步下滑。"),
    product("Narco Empire", "com.spark.sp.gp", "googlePlay", "up", "+6 · #26", "Android由#32升至#26，重新接近前25；iOS未进同口径TOP60。该作7月14日上架，仍属近90天新品，本次上行是新品中最明显的Android信号，但需要连续两至三个快照确认。"),
    product("Clash Royale", "com.supercell.clashroyale", "googlePlay", "up", "+5 · #13", "Google升至#13，iOS同步升6位至#5。Minion Academy新赛季于9月7日开启，与双端上涨时间重合；可作为活动承接信号，但首日不足以确认持续收入提升。"),
    product("Stormshot: Isle of Adventure", "com.sivona.stormshot.e", "googlePlay", "up", "+5 · #40", "Google由#45升至#40，iOS没有对应TOP60排名。产品仍处中后段，当前缺少与这次上行对应的公开版本或活动节点，按单端待验证信号记录。"),
    product("Forge of Empires: Build a City", "com.innogames.foeandroid", "googlePlay", "down", "−5 · #58", "昨日首次进入项目榜#53，今天退到#58，已进入最后三名风险区；iOS仍未进榜。1.343版本计划9月9日全服更新，目前尚未形成稳定回榜证据。"),
    product("Game of Thrones: Conquest", "com.wb.goog.got.conquest", "googlePlay", "up", "+4 · #45", "Google升至#45，iOS同时大升27位至#24，是今天最强的双端同向产品之一。没有公开节点足以解释幅度，尤其iOS单日跳升先按付费峰值或回补信号观察。"),
]


ios_products = [
    product("Top Heroes: Kingdom Saga", "6450953550", "ios", "entry", "回榜 · #57", "昨日从#57掉榜，今天回到相同位置；Google维持#43。iOS仍处最后四名，属于快速回榜但未脱离风险区的成熟产品信号。"),
    product("Overgeared Hero: Merge RPG", "6755585789", "ios", "entry", "回榜 · #59", "iOS回到#59，Google同期维持#38。双端都在榜但iPhone端仍压线；缺少公开活动证据，不能把回榜直接归因于版本或买量。"),
    product("The Tower - Idle Tower Defense", "1575590830", "ios", "exit", "掉榜 · 上期#53", "昨日回榜后位于#53，今天再次退出；Google没有对应TOP60排名。单端回榜只维持一个快照，继续按榜尾短峰处理。"),
    product("Fire Emblem Heroes", "1181774280", "ios", "exit", "掉榜 · 上期#60", "昨日压线回榜#60，今天即退出；Google未进入策略TOP60。成熟IP产品的单日回补未能延续，不能据此判断长期运营转弱。"),
    product("Game of Thrones: Conquest", "1035712810", "ios", "up", "+27 · #24", "iOS由#51升至#24，Google也升4位至#45。双端方向一致但iPhone幅度远大于Android，现阶段只确认当日付费位置抬升，原因仍待活动或促销证据。"),
    product("Last Shelter: Survival", "1342290011", "ios", "up", "+21 · #38", "iOS由#59升至#38，Google同步升3位至#47。两个商店共同改善使信号强于单端跳升，但仍需确认能否连续留在中段。"),
    product("Forge Master – Idle RPG", "6746636289", "ios", "up", "+20 · #29", "iOS由#49升至#29，Google也升3位至#48。产品重新进入iOS前30且双端同向，当前没有可核验活动节点，先标记为待验证付费回补。"),
    product("Warhammer 40,000: Tacticus", "1599937506", "ios", "down", "−14 · #43", "iOS由#29回落至#43，而Google仅降2位至#29，跨端位置重新拉开。昨日两端靠拢没有延续，说明iPhone侧短期峰值回吐更明显。"),
    product("Summoners War", "852912420", "ios", "down", "−11 · #55", "iOS由#44降至#55，进入最后六名风险区；Google没有对应策略TOP60排名。成熟产品仍在榜，但下一快照若继续下滑将接近掉榜。"),
    product("Top Force: Commander", "6761893238", "ios", "up", "+8 · #31", "iOS升至#31，Google同产品维持#35，双端名次收敛到相近区间。iOS版6月8日上架，已早于本期90天窗口，因此不再标记近三个月新品。"),
    product("Clash Royale", "1053012308", "ios", "up", "+6 · #5", "iOS升至#5，Google同步升5位至#13。Minion Academy新赛季与上涨同日出现，双端共振清晰，但仍需用本周后续快照检验新卡、英雄与通行证带来的持续性。"),
]


news = [
    {"category": "全球月榜", "date": "2026-09-04（估算截至）", "title": "Sensor Tower发布8月全球手游收入TOP10", "summary": "全球手游消费者支出约65.7亿美元、环比下降1%；Honor of Kings居首，Whiteout Survival第3、Kingshot第7。", "impact": "两款核心策略产品均较7月上升1位，并继续处于今日美国双端头部；官方未公开单品收入同比，页面不从名次补算百分比。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"},
    {"category": "新赛季", "date": "2026-09-07", "title": "Clash Royale开启Minion Academy赛季", "summary": "官方公布Minion Giant新卡、Ice Wizard英雄、Album Event、2v2 League和Royale Shuffle等9月内容。", "impact": "Clash Royale今日Google +5至#13、iOS +6至#5；新赛季与双端抬升时间重合，但需要首周连续数据验证。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/new-season-minion-academy/"},
    {"category": "版本 / 榜尾", "date": "2026-09-07", "title": "Forge of Empires发布1.343国际服版本", "summary": "版本调整Historical Allies与Stellar Age提示并修复多项移动端稳定性问题；全服计划9月9日更新。", "impact": "该作今日Google由#53降至#58；版本尚未形成稳定承接，9月9日全服更新后需继续观察。", "source": "InnoGames官方", "url": "https://support.innogames.com/kb/ForgeOfEmpires/en_DK/6975/Update-to-version-1343"},
    {"category": "周年运营", "date": "2026-09-04", "title": "King of Avalon开启十周年整月活动", "summary": "9月4日至30日活动加入可收集Merlin、八个传奇地点、七件遗物、拼图、英雄与周年奖励。", "impact": "King of Avalon今日Google #34、iOS未进榜；Android仍有承接，但没有双端共同抬升。", "source": "FunPlus官方", "url": "https://funplus.com/king-of-avalon-celebrates-10th-anniversary/"},
    {"category": "区域趋势", "date": "2026-09（官方发布月）", "title": "Sensor Tower：日本4X策略收入同比增长9.4%", "summary": "日本近12个月手游IAP超100亿美元；报告称4X Strategy领跑细分收入并增长9.4%，Last War是主要支撑产品。", "impact": "这说明成熟高付费市场仍能支撑4X增长，但属于日本市场口径，不能替代美国双榜或全球单品收入。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/state-of-japan-gaming-2026"},
    {"category": "版本更新", "date": "2026-08-30", "title": "Clash of Clans更新TH18宠物与Supercharge等级", "summary": "官方更新增加Diggy等级、Builder's Hut与Monolith强化，并调整回流、新手与部落战联赛体验。", "impact": "Clash of Clans今日Google #6、iOS #9，仍稳居双端头部；版本效果需结合多日位置而非单一快照。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/release-notes/august-update-3/"},
    {"category": "新赛季", "date": "2026-08-31", "title": "MARVEL SNAP运营AXIS: Inversion赛季", "summary": "赛季包含新角色、地点、登录日历、Draft、Team Clash与多段活动，并提供网页商店季票奖励。", "impact": "今日Google #35、iOS #40，双端均处中段；赛季后位置尚未出现持续共振。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/new-season-axis-inversion/"},
    {"category": "平衡调整", "date": "2026-09-02", "title": "Clash Royale发布9月平衡调整", "summary": "官方下调Furnace Evolution热生成速度和Spirit Empress生命值，并调整多张卡牌数值。", "impact": "平衡调整与9月7日新赛季叠加，今日双端上涨需要在赛季首周拆分观察，不能只归因于单一卡牌。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/september-balance-changes/"},
    {"category": "版本运营", "date": "2026-08-26", "title": "GFL2的Chiral Redundancy版本进入承接观察期", "summary": "官方加入限时剧情、Frontier platoon玩法、Tile Transformation系统及角色卡池。", "impact": "GFL2今日Google再降10位至#51、iOS榜外；版本后高位继续回吐，但榜位不能单独证明收入或用户流失。", "source": "GIRLS' FRONTLINE 2官方", "url": "https://gf2exilium.sunborngame.com/NewsInfo?id=393&typeId=3"},
    {"category": "IP联动", "date": "2026-08-25", "title": "State of Survival推进《如龙8》联动", "summary": "8月28日起加入联盟Boss、节奏挑战、感染摩托、角色和排行榜内容。", "impact": "State of Survival今日Google #44、iOS未进榜，联动仍未形成双端共同抬升。", "source": "FunPlus官方", "url": "https://funplus.com/state-of-survival-x-like-a-dragon-infinite-wealth-crossover-event/"},
]


closing = [
    {"type": "判断", "title": "Google换榜很少，iOS换榜同样有限但中段位移更剧烈", "detail": "Google仅1进1出、最大跌幅10位；iOS为2进2出，却出现Game of Thrones +27、Last Shelter +21、Forge Master +20。换榜数量与榜内付费位移不是同一件事，今天的主要波动来自iOS存量产品。"},
    {"type": "判断", "title": "三款老产品形成双端同向上行，但仍缺少原因证据", "detail": "Game of Thrones、Last Shelter和Forge Master分别在iOS大幅上升，同时Google也上涨3—4位。双端共振提高信号可信度，但没有公开活动节点时只能确认榜位共同改善，不能直接写成长期趋势。"},
    {"type": "判断", "title": "Clash Royale的赛季节点与双端上升重合", "detail": "Minion Academy于9月7日开启，今日Clash Royale升至Google #13和iOS #5；相较之下，全球收入月榜中的Whiteout Survival与Kingshot仍维持美国双端头部。日榜活动响应与月度全球收入地位需要分开理解。"},
    {"type": "关注", "title": "9月9日：验证Supremacy与Forge of Empires的榜尾去留", "detail": "Supremacy若能从Google #60上移且iOS继续守住#34附近，才强化双端回补判断；Forge of Empires若在1.343全服更新后仍处#58或掉榜，则当前版本承接有限。"},
    {"type": "关注", "title": "9月9—10日：复核iOS三组20位以上跳升", "detail": "Game of Thrones、Last Shelter和Forge Master至少连续两个工作日保持在当前区间，才从单日峰值升级为持续信号；若快速回落，则按短期付费脉冲归档。"},
    {"type": "关注", "title": "截至9月11日：检验Minion Academy首周承接", "detail": "观察Clash Royale能否维持iOS TOP10并让Google守住TOP15，同时跟踪GFL2是否跌出Google后十名；两个节点分别代表新赛季承接与前期版本热度回吐。"},
]


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Google仅一进一出；iOS换榜有限但三款老产品出现20位以上跳升",
    "summary": "与9月7日快照相比，Google Play由Supremacy: World War 3进入#60、Last Fortress掉榜；iOS由Top Heroes和Overgeared Hero回榜，The Tower和Fire Emblem Heroes掉榜。Game of Thrones、Last Shelter与Forge Master在iOS分别上升27、21和20位，并在Google同步小幅上行；Clash Royale在Minion Academy开启后双端上涨。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": "data/games-20260908.json", "ios": "data/ios-games-20260908.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260907.json", "ios": "data/ios-games-20260907.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Foundation: Galactic Frontier · #60 Supremacy: World War 3", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}", "anchors": "榜单锚点：#1 Pokémon GO · #25 Magic: The Gathering Arena · #60 Guns of Glory", "products": ios_products},
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
    "downloads": {"markdown": "reports/2026-09-08.md", "json": "data/market-brief-20260908.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        "- Google锚点：#1 Kingshot · #25 Foundation: Galactic Frontier · #60 Supremacy: World War 3",
        "- iOS锚点：#1 Pokémon GO · #25 Magic: The Gathering Arena · #60 Guns of Glory",
        "- 对比基准：各自上一份有效快照为2026-09-07；所有升降均为相邻工作日变化。",
        "- 近90天状态：Google新上榜6款、iOS新上榜2款；两端均缺少2026-06-10精确同口径TOP60基准，较老产品暂不判断飙升。", "",
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


save("data/market-brief-20260908.json", brief)
(ROOT / "reports/2026-09-08.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(google_products) + len(ios_products)} product cards and {len(news)} news items")
