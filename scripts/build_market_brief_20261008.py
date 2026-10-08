#!/usr/bin/env python3
"""Generate the Beijing 2026-10-08 market brief, local icons and archive entry."""

from datetime import datetime
from zoneinfo import ZoneInfo

import build_market_brief_20261007 as prior


DATE, STAMP = "2026-10-08", "20261008"
prior.DATE = DATE
prior.STAMP = STAMP
prior.datasets = {
    "googlePlay": {
        "now": prior.load("data/games-20261008.json"),
        "prior": prior.load("data/games-20261007.json"),
        "id": "packageName",
    },
    "ios": {
        "now": prior.load("data/ios-games-20261008.json"),
        "prior": prior.load("data/ios-games-20261007.json"),
        "id": "appId",
    },
}
datasets = prior.datasets
card = prior.card


google_products = [
    card("googlePlay", "MARVEL SNAP", "entry", "回到Google #40，iOS同时小升2位至#21；Vampires vs Zombies赛季仍是最近可核验内容背景，但Google昨日掉榜、今日回归首先说明榜位波动，暂不写成稳定反转。"),
    card("googlePlay", "Age of Empires", "exit", "从Google上期#58掉榜，iOS也下跌3位至#60；Stormlands与Mounted Hunt版本未阻止双端同时进入掉榜风险区。"),
    card("googlePlay", "Game of Thrones: Conquest", "up", "Google上升9位至#46，iOS同步上升14位至#25；继昨日双端改善后连续第二个快照向上，但Dragonseeds版本早于本轮变化，仍不能确认直接因果。"),
    card("googlePlay", "GIRLS' FRONTLINE 2", "up", "Google上升9位至#51，暂时脱离末位但仍在后十名；iOS未进入当前TOP60，本轮仅是Android端回补信号。"),
    card("googlePlay", "Limbus Company", "down", "Google下跌10位至#59，iOS仍未入榜；从中后段快速回落到倒数第二，下一快照面临直接掉榜风险。"),
    card("googlePlay", "Forge of Empires", "down", "Google下跌10位至#60且处于末位，iOS未进入TOP60；成熟城建产品本轮回补已退到截线，未发现可确认的同日重大节点。"),
]


ios_products = [
    card("ios", "Pokémon Champions", "entry", "回到iOS #42。10月7日1.2.2仅说明修复问题与改善体验，回榜时间相邻但缺少新增内容证据，先按维护版本附近的待验证信号处理。"),
    card("ios", "Rise of Castles", "entry", "回到iOS #45，对应Google同产品体系位于#25；9月26日版本仅披露性能优化与错误修复，本次主要体现跨端排名差距。"),
    card("ios", "Kingdom Clash", "entry", "回到iOS #50。最近公开的Clan Boss、复仇机制与聊天互动更新在8月，未发现能直接解释今日回榜的同日节点。"),
    card("ios", "Overgeared Hero", "entry", "回到iOS #55，Google稳定在#37；Erwen联动、225章与200层头像框是最近内容背景，但iPhone端仍处后六名。"),
    card("ios", "Guns of Glory", "exit", "从iOS上期#53掉榜，Google却上升3位至#26；10月5日版本只披露界面与体验优化，今天首先表现为跨端分化。"),
    card("ios", "Last Shelter: War Z", "exit", "从iOS上期#54掉榜，Google同产品上升2位至#36；Milestone of Glory与世界宝箱仍是最近版本节点，但未形成双端同步改善。"),
    card("ios", "Plants on Fire", "exit", "从iOS上期#56掉榜。产品8月26日上架，昨日仍以近90天新品压线回榜，今天未能连续留榜，首发验证继续承压。"),
    card("ios", "Last Day on Earth", "exit", "从iOS上期末位#60掉榜；10月5日授权与进度恢复简化没有带来第二个有效快照的留榜，昨日榜尾风险已兑现。"),
    card("ios", "Fire Emblem Heroes", "up", "iOS上升14位至#30。10月6日版本加入七名英雄武器精炼与限时战斗手册，时间相邻但仍需连续榜位确认活动承接。"),
    card("ios", "Game of Thrones: Conquest", "up", "iOS上升14位至#25，Google同步上升9位至#46；双端连续第二个快照改善，当前是最清晰的共同上行信号，但仍不把旧版本节点写成确定原因。"),
    card("ios", "Top War", "down", "iOS下跌11位至#47，Google也下跌2位至#38；两端同向回落但幅度不同，当前版本说明只有常规优化与修复。"),
    card("ios", "The Battle Cats", "down", "iOS下跌8位至#34。10月5日15.6.1以修复为主，15.6.0新增震动、形态、天赋与关卡；本次回吐仍属于单日波动。"),
    card("ios", "Kingdom Guard", "down", "iOS下跌7位至#58，Google也在#57；两端同时落入最后四名，9月水果市场活动已结束，榜尾风险高于昨日。"),
    card("ios", "Summoners War", "down", "iOS下跌7位至#54。9月30日怪物平衡与制作体验调整仍是最近版本节点，当前再次回到后七名。"),
]


news = [
    {
        "category": "全球收入月榜", "date": "2026-10-01",
        "title": "Sensor Tower 9月全球收入TOP10的核心策略子集仍为3款",
        "summary": "官方完整图表显示Whiteout Survival全球总榜#6、Last War: Survival #7、Kingshot #9；截至10月8日检查未见更新月份。",
        "impact": "Last War为新进全球TOP10，Whiteout与Kingshot较8月分别下降3位、2位；全球总榜名次变化不等于单品收入同比。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
    {
        "category": "竞技策略 / 维护", "date": "2026-10-07",
        "title": "Pokémon Champions发布1.2.2后回到iOS #42",
        "summary": "Apple官方版本说明仅披露问题修复与体验改善，没有新增玩法或大型活动说明。",
        "impact": "回榜与维护版本时间相邻，但缺少内容型转折；未来1—2个快照能否继续上移更有验证价值。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6741503079",
    },
    {
        "category": "战术RPG / 活动", "date": "2026-10-07",
        "title": "Tacticus更新并进入Terminus生存活动前窗口",
        "summary": "Google Play官方页显示10月7日更新，商品页仍明确Terminus生存活动于10月10日开始。",
        "impact": "产品当前Google #43、iOS #41；10月10日前后的连续变化可检验活动窗口，而非只看单日名次。",
        "source": "Google Play官方商品页", "url": "https://play.google.com/store/apps/details?id=com.snowprintstudios.tacticus&hl=en_US&gl=US",
    },
    {
        "category": "战棋RPG / 版本", "date": "2026-10-06",
        "title": "Fire Emblem Heroes新增武器精炼后升至iOS #30",
        "summary": "官方10.10.0版本为Emblem Hero Ike等七名英雄加入可精炼武器，并更新限时战斗手册。",
        "impact": "本期上涨14位，节点与榜位改善相邻；没有下一快照承接前，仍不能确认版本直接带动收入。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1181774280",
    },
    {
        "category": "IP SLG / 版本", "date": "2026-09-21",
        "title": "Game of Thrones: Conquest双端连续改善",
        "summary": "Apple官方版本加入Alys Rivers与Hugh Hammer两名英雄、Dragonseed装备和龙具；本期Google +9、iOS +14。",
        "impact": "双端连续第二个快照向上比单日回榜更强，但版本早于榜位变化，仍需避免把时间关联写成确定因果。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1035712810",
    },
    {
        "category": "卡牌 / 赛季", "date": "2026-09-15",
        "title": "MARVEL SNAP在Vampires vs Zombies赛季中回到Google",
        "summary": "官方版本列出Vampire Killmonger、Zombie Venom等新角色，以及Draft、Grand Arena与Deadpool Diner限时模式。",
        "impact": "产品回到Google #40且iOS升至#21，但昨日刚从Google掉榜，当前更适合判为跨端回补而非稳定增长。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1592081003",
    },
    {
        "category": "联动 / 合成RPG", "date": "2026-09-29",
        "title": "Overgeared Hero以Erwen联动回到iOS后段",
        "summary": "官方1.40.1版本加入Erwen联动、225章、200层头像框与战斗信息改善。",
        "impact": "Google稳定在#37、iOS回到#55，说明联动背景尚未形成双端同幅度表现。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6755585789",
    },
    {
        "category": "长线塔防 / 版本", "date": "2026-10-05",
        "title": "The Battle Cats 15.6系列扩充形态与关卡后回吐8位",
        "summary": "15.6.0加入战斗震动、新True/Ultra Forms、天赋、地图与奖励，15.6.1主要为修复。",
        "impact": "产品仍在iOS #34，但本期下跌8位；内容扩充不能单独替代连续畅销榜验证。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id850057092",
    },
    {
        "category": "火器SLG / 维护", "date": "2026-10-05",
        "title": "Guns of Glory出现Google上升、iOS掉榜的跨端分化",
        "summary": "官方14.2.0版本仅说明界面显示与体验优化，没有披露大型内容节点。",
        "impact": "Google升至#26而iOS从#53掉榜；单端改善不应扩展为统一产品趋势。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1274354704",
    },
    {
        "category": "末日SLG / 长线运营", "date": "2026-09-24",
        "title": "Last Shelter: War Z新增荣耀里程碑后呈跨端反向变化",
        "summary": "官方版本加入Milestone of Glory、世界宝箱、兑换码，并优化跨服动态与联盟体验。",
        "impact": "Google升至#36而iOS掉榜；内容规模较明确，但当前没有双端同步榜位证据。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6760406772",
    },
]

for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google维持低换位，iOS仍由中后段轮换主导",
        "detail": "Google一进一出，59款共同产品中50款变动不超过2位、中位绝对变动1位，前10全部留存；iOS四进四出，56款共同产品中37款变动不超过2位、中位绝对变动2位，前10留存9款。",
    },
    {
        "type": "判断", "title": "Game of Thrones连续双端改善，MARVEL SNAP回补但仍波动",
        "detail": "Game of Thrones连续第二个快照双端向上，本期Google #46、iOS #25；MARVEL SNAP昨日Google掉榜、今日回到#40，iOS升至#21。前者信号更连续，但两者都缺少可确认的同日收入因果。",
    },
    {
        "type": "判断", "title": "榜尾风险在两端同步显现",
        "detail": "Age of Empires从Google掉榜并跌至iOS #60；Kingdom Guard位于Google #57、iOS #58；Limbus与Forge分别跌至Google #59和#60。当前更像榜尾换防，而非品类结构变化。",
    },
    {
        "type": "关注", "title": "下一有效快照：复核Google回榜与末位产品",
        "detail": "观察MARVEL SNAP #40能否连续留榜，以及Limbus #59、Forge #60是否掉榜；若MARVEL再次退出，应维持高波动判断。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：检验iOS四款回榜产品",
        "detail": "Pokémon Champions #42、Rise of Castles #45、Kingdom Clash #50、Overgeared #55均位于中后段；至少连续两次留榜并有产品进入前40，才说明本轮回补形成承接。",
    },
    {
        "type": "关注", "title": "10月10日前后：核对Tacticus Terminus活动窗口",
        "detail": "Tacticus当前Google #43、iOS #41，Terminus生存活动排期10月10日；若两端同步进入前35并连续保持，才支持活动承接判断。",
    },
]


google_history = prior.load("data/history/google-play/2026-10-08.json")
ios_history = prior.load("data/history/ios/2026-10-08.json")
global_strategy_revenue = prior.load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
all_products = google_products + ios_products
icons = prior.build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Game of Thrones连续双端改善，MARVEL SNAP回补，iOS四进四出",
    "summary": "较10月7日前一有效快照，Google Play一进一出：MARVEL SNAP回榜#40，Age of Empires掉榜；Game of Thrones与GFL2各+9，Limbus与Forge各−10。iOS四进四出：Pokémon Champions #42、Rise of Castles #45、Kingdom Clash #50、Overgeared Hero #55回榜，Guns of Glory、Last Shelter: War Z、Plants on Fire、Last Day on Earth掉榜；Fire Emblem与Game of Thrones各+14，Top War −11。近90天新品为Google 2款、iOS 2款，较老产品因缺少7月10日精确基准不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261008.json",
    "rankingSources": {"googlePlay": "data/games-20261008.json", "ios": "data/ios-games-20261008.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261007.json", "ios": "data/ios-games-20261007.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Rise of Castles: Ice and Fire · #60 Forge of Empires: Build a City",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Kingshot · #25 Game of Thrones: Conquest · #60 Age of Empires Mobile",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-10"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-10"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-08.md", "json": "data/market-brief-20261008.json"},
}

prior.google_history = google_history
prior.ios_history = ios_history
prior.global_strategy_revenue = global_strategy_revenue
prior.google_new = google_new
prior.ios_new = ios_new
prior.save("data/market-brief-20261008.json", brief)
markdown = prior.build_markdown(brief).replace("2026-10-06", "2026-10-07").replace("2026-07-09", "2026-07-10")
(prior.ROOT / "reports/2026-10-08.md").write_text(markdown, encoding="utf-8")
manifest = prior.load("reports/manifest.json")
entry = {
    "date": DATE,
    "title": brief["title"],
    "summary": brief["summary"],
    "markdown": brief["downloads"]["markdown"],
    "json": brief["downloads"]["json"],
}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
prior.save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
