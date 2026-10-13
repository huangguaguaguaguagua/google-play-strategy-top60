#!/usr/bin/env python3
"""Generate the Beijing 2026-10-13 market brief, local icons and archive entry."""

from datetime import datetime
from zoneinfo import ZoneInfo

import build_market_brief_20261007 as base


DATE, STAMP = "2026-10-13", "20261013"
base.DATE = DATE
base.STAMP = STAMP
base.datasets = {
    "googlePlay": {
        "now": base.load("data/games-20261013.json"),
        "prior": base.load("data/games-20261012.json"),
        "id": "packageName",
    },
    "ios": {
        "now": base.load("data/ios-games-20261013.json"),
        "prior": base.load("data/ios-games-20261012.json"),
        "id": "appId",
    },
}
datasets = base.datasets
card = base.card


google_products = [
    card("googlePlay", "Top Heroes", "up", "Google上升4位至#44，为本端最大上涨；iOS同日回榜#44。10月12日iOS版本调整Lord Runes、Castle Gifting与Romance in Bloom界面，但单日同位仅是待验证共振。"),
    card("googlePlay", "Aliens vs Zombies", "up", "Google上升3位至#54，iOS却从上期#59掉榜；10月6日装备2.0可作背景，10月19日Boss Hunt尚未开始，不能用未来活动解释今天的跨端分化。"),
    card("googlePlay", "Lords Mobile", "up", "Google上升3位至#40，iOS则下跌6位至#58；Transformers联动仍在商品页展示，但两端方向相反，不支持统一活动拉动判断。"),
    card("googlePlay", "Clash Royale", "down", "Google下跌3位至#13，为本端并列最大下跌；仍处前15且iOS为#9，未发现与本次温和回落同日的可确认重大转折。"),
]


ios_products = [
    card("ios", "Top Heroes", "entry", "回到iOS #44，同时Google +4至#44。10月12日版本优化Lord Runes、Castle Gifting与Romance in Bloom界面，但首次同位仍需下一有效快照验证。"),
    card("ios", "Kingdom Guard", "entry", "回到iOS #45，Google当前未进入TOP60；9月Fruit Market活动已经结束，未发现与今天同日的可确认重大节点，本次先按中后段回补记录。"),
    card("ios", "Guns of Glory", "entry", "回到iOS #55，Google为#30；10月5日版本只披露界面显示与体验优化，25位跨端差异和后六名位置仍提示iPhone端掉榜风险。"),
    card("ios", "Last Shelter: War Z", "entry", "回到iOS #57；Google榜内的Last Shelter: Survival为另一应用与产品ID，不合并为同一跨端信号。当前回榜仅处后四名。"),
    card("ios", "The Tower", "entry", "回到iOS #59。10月6日v29加入全局预设、Mythic赛事联赛、重做Vault与Harmony Tree，但本次仅位于倒数第二，版本承接仍待验证。"),
    card("ios", "Kingdom Clash", "entry", "回到iOS #60且恰处末位，Google当前未进入TOP60；成熟塔防产品仍在截线附近轮换，未发现可确认的同日重大转折。"),
    card("ios", "Bloons TD 6", "exit", "从iOS上期#54掉榜。10月6日57.0的Sniper Paragon与社区地图未形成第二个有效快照留榜，不能由一次进出榜判断长线版本效果。"),
    card("ios", "Star Trek Fleet Command", "exit", "从iOS上期#56掉榜，Google仍为#21；10月8日Update 95后的榜尾回补未延续，同产品跨端差距再次扩大。"),
    card("ios", "Evo Defense", "exit", "从iOS上期#57掉榜。产品此前已在榜尾反复进出，本次未发现足以确认原因的同日新节点，继续按截线轮换处理。"),
    card("ios", "Draft Showdown", "exit", "从iOS上期#58掉榜。10月5日1.17.1以问题修复与Discord入口为主，前一期后三名回补没有形成连续留榜。"),
    card("ios", "Aliens vs Zombies", "exit", "从iOS上期#59掉榜，而Google +3至#54；装备2.0是最近可核验节点，10月19日与26日活动尚未开始，今天体现为平台分化。"),
    card("ios", "Plants on Fire", "exit", "从iOS上期#60掉榜。该产品8月26日上架，掉榜前始终处于末位；Pirate Captain版本尚未形成连续畅销榜承接。"),
    card("ios", "Lands of Jail", "up", "iOS上升9位至#31，为本端最大上涨；Google同步+3至#24。两端同向但幅度不同，尚无同日重大产品节点可确认因果。"),
    card("ios", "Warline", "up", "iOS上升7位至#35，同时Google +1至#27；作为7月22日上架的近90天新品，本期改善仍需下一快照确认是否脱离首发波动。"),
    card("ios", "Warhammer 40,000", "down", "iOS下跌9位至#41，为本端并列最大下跌，Google仍为#38；10月10日Terminus与Battle Pass已开启，单日回落说明活动存在不等于榜位必然上涨。"),
    card("ios", "Summoners War", "down", "iOS下跌9位至#54，为本端并列最大下跌；9月30日技能平衡与制作体验更新只能作背景，当前已回到后七名风险区。"),
    card("ios", "Lords Mobile", "down", "iOS下跌6位至#58，Google却+3至#40；Transformers联动仍可核验，但18位跨端差异和相反方向不支持统一归因。"),
]


news = [
    {
        "category": "全球收入月榜", "date": "2026-10-01",
        "title": "Sensor Tower 9月全球收入TOP10的核心策略子集仍为3款",
        "summary": "官方完整图表显示Whiteout Survival全球总榜#6、Last War: Survival #7、Kingshot #9；本次单次检查未发现10月新一期。",
        "impact": "Last War为新进全球TOP10，Whiteout与Kingshot较8月分别下降3位、2位；全球总榜名次变化不等于单品收入同比。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
    {
        "category": "三消SLG / 万圣节版本", "date": "2026-10-12",
        "title": "Puzzles & Survival上线万圣节外观与限时Bomb Fusion",
        "summary": "Apple官方4.0.241加入万圣节主题外观、Gold M.Card、限时Match-3 Bomb Fusion，以及Sorting Reagent和Gem Master新关卡。",
        "impact": "产品当前Google #14、iOS #22；版本刚上线，未来1—2个有效快照可检验活动是否形成双端可见改善。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1517980891",
    },
    {
        "category": "4X / 赛季体验", "date": "2026-10-12",
        "title": "Top Heroes更新界面后双端同至#44",
        "summary": "Apple官方1.124.4优化Lord Runes、Castle Gifting及Romance in Bloom排名页，并调整Cloudsea Odyssey赛季遗迹放弃时间。",
        "impact": "产品本期iOS回榜#44、Google +4至#44；版本与榜位同日，但需要下一快照确认不是短暂同位。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6450953550",
    },
    {
        "category": "战术经营 / 赛季内容", "date": "2026-10-12",
        "title": "Mob Control加入Big Blob新机制与Base Builder赛季场景",
        "summary": "Apple官方3.23.4更新House of Champions展示，为Big Blob加入新玩法机制，并更新Base Builder赛季环境。",
        "impact": "产品位于iOS #27；轻度入口与基地经营的内容组合值得观察，但单次版本说明不能推断收入增幅。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1562817072",
    },
    {
        "category": "战术RPG / 活动", "date": "2026-10-08",
        "title": "Tacticus进入Terminus与Battle Pass活动窗口",
        "summary": "Apple官方1.43.127加入Lost and the Damned阵营，并列出10月10日Terminus生存活动、Forcas Battle Pass及后续活动排期。",
        "impact": "本期iOS −9至#41、Google #38；活动上线与单日回落并存，需要活动后的连续快照验证承接。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1599937506",
    },
    {
        "category": "塔防 / 大版本", "date": "2026-10-06",
        "title": "The Tower以v29大版本回到iOS末段",
        "summary": "Apple官方v29加入Global Presets、Preset Lab、Mythic赛事联赛、重做Vault及Harmony Tree升级。",
        "impact": "产品回榜但仅位于#59；新系统是否能把成熟产品带离掉榜线，要看未来1—2个有效快照。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1575590830",
    },
    {
        "category": "IP 4X / 版本", "date": "2026-10-07",
        "title": "Game of Thrones: Dragonfire更新后维持双端前25",
        "summary": "Apple官方26.9.57505继续突出养龙、家族争夺与Westeros世界，并引导至官方产品站了解版本内容。",
        "impact": "产品当前Google #25、iOS #24；位置接近但本期变动温和，尚不能把稳定性直接归因于该版本。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1642607669",
    },
    {
        "category": "现代战争 / 平衡", "date": "2026-10-08",
        "title": "Supremacy更新Doctrine、动员与无障碍体验",
        "summary": "Apple官方0.244调整Tank Destroyer doctrine、mobilization平衡和无障碍选项，并修复飞机、导弹、情报单位与界面问题。",
        "impact": "产品当前iOS #43；平衡更新可改善长线体验，但今天的榜位不足以确认商业化响应。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1510997559",
    },
    {
        "category": "战棋RPG / 版本", "date": "2026-10-06",
        "title": "Fire Emblem Heroes为七名英雄加入武器精炼",
        "summary": "Apple官方10.10.0为包括Emblem Hero Ike在内的七名英雄增加可精炼武器技能，并更新限时战斗手册。",
        "impact": "产品当前iOS #47且较前期回落5位；版本存在不代表畅销名次单向上涨。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1181774280",
    },
    {
        "category": "卡牌策略 / 新内容", "date": "2026-10-06",
        "title": "MTG Arena上线Reality Fracture主题内容",
        "summary": "Apple官方2026.63.20以Shatter the Looking Glass为主题，加入Reality Fracture及每包echoed pair的构筑选择。",
        "impact": "产品当前iOS #20；IP体量与新构筑环境值得持续观察，但未公开单品收入变化。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1496227521",
    },
]

for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google无进出榜且位移收窄，榜面明显稳定",
        "detail": "Google 60款全部留榜，51款位移不超过2名，中位绝对变动1名；Top Heroes +4为最大上涨，四款产品并列−3为最大下跌，整体仍属于小幅重排。",
    },
    {
        "type": "判断", "title": "iOS六进六出集中在中后段，榜尾承接仍弱",
        "detail": "iOS 54款共同产品中27款位移不超过2名，中位绝对变动2.5名；六款进入产品仅Top Heroes与Kingdom Guard进入前45，其余四款位于#55—#60。",
    },
    {
        "type": "判断", "title": "Top Heroes双端共振，Aliens与Lords跨端分化",
        "detail": "Top Heroes在Google +4并回到iOS，双端同为#44；Aliens升至Google #54却从iOS掉榜，Lords在Google +3至#40、iOS −6至#58。单日信号仍不能扩展为长期趋势。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证iOS六款进入产品的留榜率",
        "detail": "重点观察Guns of Glory #55、Last Shelter #57、The Tower #59与Kingdom Clash #60能否连续留榜；若多数立即退出，应继续按截线轮换处理。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：复核Top Heroes与Warline改善",
        "detail": "Top Heroes需要在双端至少保持前45；近90天新品Warline需在iOS #35、Google #27附近继续留榜，才可从首发波动转向持续承接判断。",
    },
    {
        "type": "关注", "title": "10月19日至26日：单独核对Aliens活动窗口",
        "detail": "以当前Google #54与iOS掉榜为活动前基线，分别在Boss Hunt和Halloween Night启动后观察双端位置；活动前不提前归因。",
    },
]


google_history = base.load("data/history/google-play/2026-10-13.json")
ios_history = base.load("data/history/ios/2026-10-13.json")
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
    "title": "Google全榜留存，iOS六进六出，Top Heroes双端同至#44",
    "summary": "较10月12日前一有效快照，Google Play无进入或掉榜，Top Heroes +4至#44，Aliens、Lords各+3，Clash Royale等四款各−3。iOS六进六出：Top Heroes #44、Kingdom Guard #45、Guns of Glory #55、Last Shelter #57、The Tower #59、Kingdom Clash #60进入，Bloons TD 6、Star Trek、Evo Defense、Draft Showdown、Aliens、Plants on Fire掉榜；Lands of Jail +9，Warline、Overgeared、Infinity Kingdom各+7，Tacticus与Summoners War各−9。近90天新品为Google 1款、iOS 2款；两端缺少7月15日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261013.json",
    "rankingSources": {"googlePlay": "data/games-20261013.json", "ios": "data/ios-games-20261013.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261012.json", "ios": "data/ios-games-20261012.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Game of Thrones: Dragonfire · #60 Call of Dragons",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Kingshot · #25 Star Wars: Galaxy of Heroes · #60 Kingdom Clash",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-15"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-15"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-13.md", "json": "data/market-brief-20261013.json"},
}

base.google_history = google_history
base.ios_history = ios_history
base.global_strategy_revenue = global_strategy_revenue
base.google_new = google_new
base.ios_new = ios_new
base.save("data/market-brief-20261013.json", brief)
markdown = base.build_markdown(brief)
markdown = markdown.replace(
    "各自上一份最终有效快照为2026-10-06",
    "各自上一份最终有效快照为2026-10-12",
).replace(
    "两端均缺少2026-07-09精确同口径TOP60基准",
    "两端均缺少2026-07-15精确同口径TOP60基准",
)
(base.ROOT / "reports/2026-10-13.md").write_text(markdown, encoding="utf-8")
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
