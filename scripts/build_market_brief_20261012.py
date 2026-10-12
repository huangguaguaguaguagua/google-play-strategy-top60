#!/usr/bin/env python3
"""Generate the Beijing 2026-10-12 market brief, local icons and archive entry."""

from datetime import datetime
from zoneinfo import ZoneInfo

import build_market_brief_20261007 as base


DATE, STAMP = "2026-10-12", "20261012"
base.DATE = DATE
base.STAMP = STAMP
base.datasets = {
    "googlePlay": {
        "now": base.load("data/games-20261012.json"),
        "prior": base.load("data/games-20261009.json"),
        "id": "packageName",
    },
    "ios": {
        "now": base.load("data/ios-games-20261012.json"),
        "prior": base.load("data/ios-games-20261009.json"),
        "id": "appId",
    },
}
datasets = base.datasets
card = base.card


google_products = [
    card("googlePlay", "Vikings: War of Clans", "entry", "回到Google #52，iOS当前未进入TOP60；成熟4X产品重新落在后九名，尚未发现与本次回榜同日的可确认重大节点。"),
    card("googlePlay", "Sea of Conquest", "entry", "回到Google #56，iOS当前未进入TOP60；产品仍处后五名，先按榜尾回补记录，不能由单日位置推断联动或版本拉动。"),
    card("googlePlay", "Sea War", "entry", "回到Google #59，iOS当前未进入TOP60；位于倒数第二，未发现足以解释本次变化的同日重大内容，首先属于掉榜线附近轮换。"),
    card("googlePlay", "Kingdom Guard", "exit", "从Google上期#55掉榜，iOS当前也未进入TOP60；前一期已处后六名，本次更接近榜尾风险兑现，不能据此断言长期衰退。"),
    card("googlePlay", "Last Fortress", "exit", "从Google上期#57掉榜，iOS当前未进入TOP60；上期位于后四名，本次退出延续截线风险，未发现可确认的同日重大转折。"),
    card("googlePlay", "League of Legends: Wild Rift", "exit", "从Google上期#58掉榜，iOS也未进入TOP60；该产品属于MOBA分类边界，本次只记录美国策略分类榜中的退出，不扩展为核心策略品类判断。"),
    card("googlePlay", "Auto Drill", "up", "Google上升9位至#51，为本端最大上涨；产品6月24日上架且仍处首发验证，但一次周末后改善不足以确认稳定承接。"),
    card("googlePlay", "Warhammer 40,000", "up", "Google上升6位至#38，iOS同时上升26位至#32；10月10日Terminus与Battle Pass是可核验背景，两端同向改善仍需下一快照确认。"),
    card("googlePlay", "Lords Mobile", "down", "Google下跌11位至#43，iOS则回榜#52；Transformers联动仍在商品页展示，但跨端一降一回，不支持写成统一活动拉动。"),
    card("googlePlay", "Frost & Flame", "down", "Google下跌8位至#42，iOS当前未进入TOP60；单端中段回落缺少可确认的同日产品节点，先按待验证波动处理。"),
    card("googlePlay", "Raid Rush", "down", "Google下跌8位至#60且恰处末位，iOS为#38；同产品跨端相差22位，下一有效快照面临最高直接掉榜风险。"),
]


ios_products = [
    card("ios", "Watcher of Realms", "entry", "回到iOS #30，Google当前未进入TOP60；9月22日新阵营Grey Blades、Guild Boss与Guild War赛季是最近内容背景，但相隔近三周，今天仍按待验证回榜处理。"),
    card("ios", "Lords Mobile", "entry", "回到iOS #52，而Google下跌11位至#43；Transformers联动仍可核验，但两端方向不同且iPhone端处后九名。"),
    card("ios", "Bloons TD 6", "entry", "首次进入项目iOS #54。10月6日57.0加入Sniper Paragon与社区地图Ship Capture，时间相邻但榜位仍在后七名，需要连续快照验证。", first=True),
    card("ios", "Star Trek Fleet Command", "entry", "回到iOS #56，Google为#22；10月8日Update 95加入Haven与新舰船，内容窗口明确，但34位跨端差异和后五名位置仍提示iPhone端风险。"),
    card("ios", "Aliens vs Zombies", "entry", "首次进入项目iOS #59，Google为#57。10月6日装备2.0已上线，万圣节活动分别排期10月19日与26日，尚未开始的活动不能解释今天榜位。", first=True),
    card("ios", "Yu-Gi-Oh", "exit", "从iOS上期#40掉榜，Google当前未进入TOP60；中后段位置未延续到本期，未发现可确认的同日重大转折。"),
    card("ios", "DC: Dark Legion", "exit", "从iOS上期#46掉榜，Google当前未进入TOP60；上期回榜没有连续承接，Nemesis Takedown只能作为较早版本背景。"),
    card("ios", "Last Shelter: War Z", "exit", "从iOS上期#54掉榜，同产品体系Google版位于#53；上期已处后七名，本次体现iPhone端榜尾风险兑现。"),
    card("ios", "Rise of Castles", "exit", "从iOS上期#59掉榜，Google同产品体系为#24；前一期倒数第二的风险兑现，双端位置继续明显分化。"),
    card("ios", "Pokémon Champions", "exit", "从iOS上期#60掉榜，Google当前未进入TOP60；上期末位直接退出，10月7日维护版本没有形成第二个有效快照留榜。"),
    card("ios", "Warhammer 40,000", "up", "iOS上升26位至#32，为本端最大上涨；Google同步+6至#38。10月10日Terminus与Battle Pass提供活动背景，但仍需观察活动后的连续位置。"),
    card("ios", "Mobile Legends", "up", "iOS上升18位至#14，进入前15；9月16日十周年英雄重做与S42赛季是最近公开节点，但与本期相隔近一个月，不能据此确认因果。"),
    card("ios", "PUBG MOBILE", "up", "iOS上升15位至#10并进入前10；V4.6吸血鬼主题模式是当前版本背景，本期只记录为一次明显改善，仍需下一快照验证。"),
    card("ios", "Last Day on Earth", "up", "iOS上升15位至#41；10月8日版本只简化授权与进度恢复，没有新增核心商业化内容，本次反弹先记为待验证信号。"),
    card("ios", "Game of Thrones: Conquest", "down", "iOS下跌28位至#49，为本端最大下跌，Google却上升3位至#39；Dragonseeds仍是最近版本背景，但跨端方向相反。"),
    card("ios", "Dragon Traveler", "down", "iOS下跌13位至#47；9月Golden Night与Lilith版本已相隔一个月，本次更适合描述为前期高位回吐，而非新增事件因果。"),
    card("ios", "Summoners War", "down", "iOS下跌12位至#45；9月30日平衡与制作体验更新、10月10日赛事窗口只能作背景，单次回落不代表长期趋势。"),
    card("ios", "Fire Emblem Heroes", "down", "iOS下跌12位至#48。10月6日新增七名英雄武器精炼与限时战斗手册，但榜位方向说明版本存在不等于短期名次必然上涨。"),
    card("ios", "Game of Thrones: Dragonfire", "down", "iOS下跌9位至#20，而Google上升5位至#25；10月7日龙相关更新与本期相邻，但两端相反方向不支持统一归因。"),
]


news = [
    {
        "category": "全球收入月榜", "date": "2026-10-01",
        "title": "Sensor Tower 9月全球收入TOP10的核心策略子集仍为3款",
        "summary": "官方完整图表显示Whiteout Survival全球总榜#6、Last War: Survival #7、Kingshot #9；截至10月12日本次单次检查未见更新月份。",
        "impact": "Last War为新进全球TOP10，Whiteout与Kingshot较8月分别下降3位、2位；全球总榜名次变化不等于单品收入同比。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
    {
        "category": "星际4X / 大版本", "date": "2026-10-08",
        "title": "Star Trek Fleet Command以Update 95回到iOS后段",
        "summary": "Apple官方M95.4加入Ops 61+行星基地Haven、U.S.S. Kelcie Mae、Independent Archives中的Stella、Battle Pass与Territory Capture更新。",
        "impact": "产品回到iOS #56而Google为#22；内容更新明确，但34位跨端差异和榜尾位置表明iPhone端承接仍弱。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1427744264",
    },
    {
        "category": "战术RPG / 活动", "date": "2026-10-08",
        "title": "Tacticus在Terminus活动窗口双端同步改善",
        "summary": "Apple官方1.43.127加入Lost and the Damned阵营，并列出10月10日Terminus生存活动与Forcas Battle Pass。",
        "impact": "本期iOS +26至#32、Google +6至#38；活动窗口与上涨相邻，但至少需要下一个有效快照确认承接。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1599937506",
    },
    {
        "category": "IP 4X / 版本", "date": "2026-10-07",
        "title": "Game of Thrones: Dragonfire更新后双端方向分化",
        "summary": "Apple官方26.9.57505继续突出养龙、家族争夺与Westeros世界；版本于10月7日更新。",
        "impact": "产品本期iOS −9至#20、Google +5至#25；更新相邻但方向相反，不能写成统一版本拉动。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1642607669",
    },
    {
        "category": "塔防 / 长线运营", "date": "2026-10-06",
        "title": "Bloons TD 6发布57.0并首次进入项目iOS榜",
        "summary": "Apple官方57.0加入Sniper Paragon S.P.I.D.E.R. Monkey、社区竞赛地图Ship Capture，以及平衡和体验调整。",
        "impact": "产品首次进入项目榜但仅位于#54；新内容能否把产品带离后十名，需未来1—2个有效快照验证。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1118115766",
    },
    {
        "category": "轻度塔防 / 活动预告", "date": "2026-10-06",
        "title": "Aliens vs Zombies重做装备并预告万圣节双活动",
        "summary": "Apple官方1.22b加入配方制作、一键合成、槽位升级、Cosmic稀有度与Equipment Workshop；Boss Hunt排期10月19日，Halloween Night排期10月26日。",
        "impact": "产品首次进入项目iOS #59、Google #57；活动尚未开始，今天只能把装备重做作为背景，不能提前归因。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6740232087",
    },
    {
        "category": "战棋RPG / 版本", "date": "2026-10-06",
        "title": "Fire Emblem Heroes新增武器精炼但本期回落",
        "summary": "Apple官方10.10.0为包括Emblem Hero Ike在内的七名英雄加入可精炼武器技能，并更新Divine Codes: Ephemera 10限时战斗手册。",
        "impact": "产品本期iOS −12至#48；版本存在不等于畅销名次单向上涨，后续仍需看活动与核心用户承接。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1181774280",
    },
    {
        "category": "塔防RPG / 新阵营", "date": "2026-09-22",
        "title": "Watcher of Realms携Grey Blades与Guild Boss回到iOS #30",
        "summary": "Apple官方1.6.38加入Grey Blades新阵营、Fallen Covenant Guild Boss、新Guild War赛季与Doomripper兵种。",
        "impact": "本期是五款iOS进入产品中位置最高者；因版本已相隔近三周，需避免把回榜直接归因于该内容。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6741674823",
    },
    {
        "category": "MOBA / 十周年赛季", "date": "2026-09-16",
        "title": "Mobile Legends十周年版本后升至iOS #14",
        "summary": "Apple官方2.2.16重做Masha与Bruno，并启动S42赛季及赛季皮肤奖励。",
        "impact": "产品本期+18进入前15，但该产品属于MOBA分类边界；只记录其在Apple策略分类榜的异动，不纳入核心策略收入子集。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6741568655",
    },
    {
        "category": "IP 4X / 联动", "date": "2026-09-01",
        "title": "Lords Mobile在Transformers联动第二阶段出现跨端分化",
        "summary": "Apple官方2.201继续Transformers Raceway、Cybertron Battlefield与Bumblebee奖励内容。",
        "impact": "本期iOS回榜#52，Google却−11至#43；联动可作运营背景，但不能解释平台间相反变化。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1071976327",
    },
]

for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google周末后仍以稳定为主，截线完成三款轮换",
        "detail": "Google三进三出，57款共同产品中37款变动不超过2位、中位绝对变动2位，前10全部留存；Vikings #52、Sea of Conquest #56与Sea War #59进入，三款退出产品上期均处#55以后。",
    },
    {
        "type": "判断", "title": "iOS换榜与位移同步放大，活动背景不能覆盖平台差异",
        "detail": "iOS五进五出，55款共同产品中仅25款变动不超过2位、中位绝对变动3位，前10留存9款；Tacticus +26与GoT Conquest −28构成双向大幅波动。",
    },
    {
        "type": "判断", "title": "同产品跨端既有共振也有明显分化",
        "detail": "Tacticus两端同步改善至Google #38、iOS #32；Star Trek位于Google #22、iOS #56，GoT Conquest位于Google #39、iOS #49且方向相反，Dragonfire也呈Google +5、iOS −9。单日异动仍是待验证信号。",
    },
    {
        "type": "关注", "title": "下一有效快照：复核Google三款进入产品与末位Raid Rush",
        "detail": "Vikings #52、Sea of Conquest #56、Sea War #59均在后九名，Raid Rush已跌至#60；若进入产品立即退出或末位产品掉榜，应继续按截线轮换而非结构性增长处理。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：检验iOS五款进入产品",
        "detail": "Watcher #30之外，Lords Mobile #52、Bloons #54、Star Trek #56与Aliens #59都在后九名；至少连续两次留榜并有产品进入前45，才说明本轮回补形成承接。",
    },
    {
        "type": "关注", "title": "10月19日至26日：单独核对Aliens万圣节窗口",
        "detail": "先记录10月19日Boss Hunt与10月26日Halloween Night开始前的双端基线；只有活动后连续改善，才可进一步评估内容承接，不能用未来活动解释当前#57/#59。",
    },
]


google_history = base.load("data/history/google-play/2026-10-12.json")
ios_history = base.load("data/history/ios/2026-10-12.json")
global_strategy_revenue = base.load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
all_products = google_products + ios_products
icons = base.build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Google截线三进三出，iOS双向放大，Tacticus双端共振",
    "summary": "较10月9日前一有效快照，Google Play三进三出：Vikings #52、Sea of Conquest #56、Sea War #59回榜，Kingdom Guard、Last Fortress、Wild Rift掉榜；Auto Drill +9、Tacticus +6，Lords Mobile −11。iOS五进五出：Watcher #30、Lords Mobile #52、Bloons TD 6 #54、Star Trek #56、Aliens vs Zombies #59进入，Yu-Gi-Oh、DC、Last Shelter War Z、Rise of Castles、Pokémon Champions掉榜；Tacticus +26、Mobile Legends +18、PUBG +15、GoT Conquest −28。近90天新品为Google 2款、iOS 3款；两端缺少7月14日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261012.json",
    "rankingSources": {"googlePlay": "data/games-20261012.json", "ios": "data/ios-games-20261012.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261009.json", "ios": "data/ios-games-20261009.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Game of Thrones: Dragonfire · #60 Raid Rush: Tower Defense TD",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Kingshot · #25 Rise of Kingdoms · #60 Plants on Fire",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-14"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-14"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-12.md", "json": "data/market-brief-20261012.json"},
}

base.google_history = google_history
base.ios_history = ios_history
base.global_strategy_revenue = global_strategy_revenue
base.google_new = google_new
base.ios_new = ios_new
base.save("data/market-brief-20261012.json", brief)
markdown = base.build_markdown(brief)
markdown = markdown.replace(
    "各自上一份最终有效快照为2026-10-06",
    "各自上一份最终有效快照为2026-10-09",
).replace(
    "两端均缺少2026-07-09精确同口径TOP60基准",
    "两端均缺少2026-07-14精确同口径TOP60基准",
)
(base.ROOT / "reports/2026-10-12.md").write_text(markdown, encoding="utf-8")
manifest = base.load("reports/manifest.json")
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
base.save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
