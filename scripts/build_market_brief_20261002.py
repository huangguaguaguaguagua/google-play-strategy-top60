#!/usr/bin/env python3
"""Generate the Beijing 2026-10-02 market brief, local icons and archive entry."""

from datetime import datetime
from zoneinfo import ZoneInfo

import build_market_brief_20261001 as prior


p = prior.p
p.DATE, p.STAMP, p.CURRENT, p.PREVIOUS = "2026-10-02", "20261002", "20261002", "20261001"
p.datasets = {
    "googlePlay": {"now": p.load("data/games-20261002.json"), "prior": p.load("data/games-20261001.json"), "id": "packageName"},
    "ios": {"now": p.load("data/ios-games-20261002.json"), "prior": p.load("data/ios-games-20261001.json"), "id": "appId"},
}
p.google_history = p.load("data/history/google-play/2026-10-02.json")
p.ios_history = p.load("data/history/ios/2026-10-02.json")
p.global_strategy_revenue = p.load("data/sensortower-global-strategy-revenue-latest.json")
p.captured = datetime.fromisoformat(p.google_history["sourceCapturedAt"])
p.source_date = datetime.fromisoformat(p.ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    p.card("googlePlay", "Limbus Company", "entry", "回到Google #53，并同步进入iOS #32。Apple 10月1日1.116.0版本加入新Identity、E.G.O与章节，两端同日回榜是今天最清晰的共同信号，但仍需连续快照确认。"),
    p.card("googlePlay", "The Ants: Underground Kingdom", "entry", "首次进入项目Google榜#57。9月28日商品页更新并展示The Ants × Gamera活动，时间与入榜相邻但不能据此确认因果；成熟4X仍处榜尾验证。", first=True),
    p.card("googlePlay", "Ant Legion: For The Swarm", "entry", "回到Google #59，仍贴近掉榜线；当前商品页未披露足以解释本次回榜的重大节点，按单日榜尾回补处理。"),
    p.card("googlePlay", "Aliens vs Zombies: Invasion", "entry", "回到Google #60，恰处末位；竖屏塔防入口没有可确认的同日重大更新，本次仅记为待验证回榜信号。"),
    p.card("googlePlay", "Kingdom Rush 6: Genesis TD", "exit", "从Google上期#50掉榜；产品仍属近90天新品，但首次进入后的留榜没有延续，不能把单次退出外推为长期表现。"),
    p.card("googlePlay", "GIRLS' FRONTLINE 2: EXILIUM", "exit", "从Google上期#57掉榜；iOS同口径也未进入TOP60，成熟二次元战棋本次未形成双端承接。"),
    p.card("googlePlay", "Sea of Conquest: Pirate War", "exit", "从Google上期#59掉榜，iOS同口径亦未收录；末位回补未延续，当前没有可确认的重大转折。"),
    p.card("googlePlay", "Galaxy Defense: Fortress TD", "exit", "从Google上期#60掉榜，iOS同口径也未进入TOP60；前一日末位留榜未形成后续承接。"),
    p.card("googlePlay", "Police Chief", "up", "Google上升6位至#18，为本端最大上涨；iOS为#29。两端都在榜但Android强11位，单日变化仍不足以确认新的增长阶段。"),
    p.card("googlePlay", "Clash of Clans", "up", "Google上升5位至#8，iOS同时升10位至#1。Supercell 10月1日开启Cosmic Curse活动，时间与双端走强重合，是明确内容背景而非已证明的排名因果。"),
    p.card("googlePlay", "Age of Origins", "up", "Google上升5位至#20，iOS仅升2位至#15；两端同向改善但幅度不同，先按Android端更强的单日信号记录。"),
    p.card("googlePlay", "Call of Dragons", "down", "Google下跌8位至#48，为本端最大回落；iOS未进入TOP60，当前已落入后十余名风险区。"),
    p.card("googlePlay", "Stormshot: Isle of Adventure", "down", "Google下跌6位至#44，iOS未进入TOP60；单日回落扩大了留榜风险，但没有可确认的重大运营转折。"),
]


ios_products = [
    p.card("ios", "Limbus Company", "entry", "进入iOS #32，并同步回到Google #53。10月1日1.116.0版本加入新Identity、E.G.O与章节，两端共同回榜值得追踪，但当前仅有一个快照。"),
    p.card("ios", "Age of Empires Mobile", "entry", "回到iOS #42，Google为#55；9月23日Stormlands与Mounted Hunt仍是近期内容背景，本次回榜尚未脱离中后段。"),
    p.card("ios", "Star Trek Fleet Command", "entry", "回到iOS #56，而Google稳居#17，跨端差达到39位。Update 95 Haven与新舰船内容时间相邻，但iPhone端仍处极高掉榜风险。"),
    p.card("ios", "The Tower - Idle Tower Defense", "exit", "从iOS上期#49掉榜，Google同口径未收录；v29大版本后的回榜没有维持，暂按单日尾部退出记录。"),
    p.card("ios", "War Machines：Battle Tank Games", "exit", "从iOS上期#57掉榜；首次进入项目榜只维持一个有效快照，成熟坦克PvP的榜尾回补尚未形成连续承接。"),
    p.card("ios", "Kiss of War", "exit", "从iOS上期#60掉榜，Google仍为#43；iPhone端退出而Android留在中后段，属于平台分化而非双端同步走弱。"),
    p.card("ios", "Dragon Traveler", "up", "iOS上升20位至#38，为本端最大上涨；最近可核验的大节点仍是9月9日Golden Night版本，当前不能把三周后的单日跳升直接归因于该内容。"),
    p.card("ios", "Mobile Legends: Bang Bang.US", "up", "iOS上升19位至#13，Google策略榜未收录。产品属于MOBA分类边界，9月中旬十周年与S42仍是内容背景，但今天只记为待验证峰值。"),
    p.card("ios", "Game of Thrones: Dragonfire", "up", "iOS上升10位至#12，Google反而下跌3位至#26；双端方向相反，说明IP 4X的当日付费强度明显偏向iPhone端。"),
    p.card("ios", "Clash of Clans", "up", "iOS上升10位登顶#1，Google也升5位至#8。Cosmic Curse于10月1日开启，是双端共同走强的可核验活动背景；是否维持高位需看下一快照。"),
    p.card("ios", "Lords Mobile x Transformers", "up", "iOS上升9位至#46，Google也升4位至#24。Transformers第二阶段仍在运营，但iPhone端尚未脱离后15名。"),
    p.card("ios", "SD Gundam G Generation ETERNAL", "down", "iOS下跌12位至#27；9月30日版本只更新图标与标题画面，前一日回到#15后出现明显回吐。"),
    p.card("ios", "League of Legends: Wild Rift", "down", "iOS下跌12位至#49，Google却升4位至#42；两端同处中后段但方向相反，且产品属于MOBA分类边界。"),
    p.card("ios", "Sea War: Uboat Raid", "down", "iOS下跌12位至#50，Google仅升1位至#36；双端差14位，iPhone端重新落入后十名风险区。"),
    p.card("ios", "Plants on Fire", "down", "iOS下跌12位至#60，仍属近90天新品且恰处末位。海盗赛季未阻止连续回吐，下一快照存在直接掉榜风险。"),
    p.card("ios", "Magic: The Gathering Arena", "down", "iOS下跌10位至#20；Reality Fracture版本仍是近期内容背景，但产品从前十回到#20，先按版本窗口内的单日回吐记录。"),
]


news = [
    {
        "category": "部落策略 / 节日活动", "date": "2026-10-01",
        "title": "Clash of Clans开启Cosmic Curse并冲至iOS榜首",
        "summary": "Supercell官方确认10月1日至31日上线Portal Panic、Totem Thrower、Cosmic Curse奖章活动与Clan War League等内容。",
        "impact": "本期iOS升至#1、Google升至#8，活动与双端走强同日发生；仍需后续快照确认持续性。",
        "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/news/cosmic-curse-portal-panic-teleports-in/",
    },
    {
        "category": "动物4X / IP活动", "date": "2026-09-28",
        "title": "The Ants × Gamera活动期首次进入项目Google榜",
        "summary": "Google美国区官方商品页展示写实蚁巢经营、联盟4X与当前The Ants × Gamera活动，并记录9月28日更新。",
        "impact": "产品首次进入项目榜#57，但成熟产品的单日入榜不能直接归因于联动，需核对下一有效快照。",
        "source": "Google Play官方商品页", "url": "https://play.google.com/store/apps/details?id=com.star.union.planetant&hl=en_US&gl=US",
    },
    {
        "category": "太空4X / 大版本", "date": "2026-10-01",
        "title": "Star Trek Fleet Command以Update 95回到iOS榜尾",
        "summary": "官方商品页披露Haven高等级内容、USS Kelcie Mae、Stella Archives、Battle Pass与Territory Capture调整。",
        "impact": "产品回到iOS #56，但Google为#17，39位跨端差说明内容承接仍明显偏Android端。",
        "source": "Google Play官方商品页", "url": "https://play.google.com/store/apps/details?id=com.scopely.startrek&hl=en_US&gl=US",
    },
    {
        "category": "战术RPG / 双端回榜", "date": "2026-10-01",
        "title": "Limbus Company更新新Identity、E.G.O与章节后双端回榜",
        "summary": "Apple官方1.116.0版本说明列出新Identity、新E.G.O、新章节与缺陷修复。",
        "impact": "本期iOS #32、Google #53，是今天少数双端共同进入信号；一次快照尚不能证明长线抬升。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6444112366",
    },
    {
        "category": "IP 4X / 版本更新", "date": "2026-09-30",
        "title": "Game of Thrones: Dragonfire更新后iOS升至#12",
        "summary": "Apple官方26.9.57184版本于9月30日更新；商品页继续突出巨龙收集、联盟与维斯特洛实时战争。",
        "impact": "iOS单日上升10位而Google下跌3位，当前更像平台分化，不能把版本更新直接写成收入因果。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1642607669",
    },
    {
        "category": "长线RPG / 平衡更新", "date": "2026-09-30",
        "title": "Summoners War技能平衡更新后继续留在iOS中段",
        "summary": "官方9.3.4版本调整怪物技能平衡，并改进Magic Crafting与其他体验。",
        "impact": "产品本期#26、较上期再升3位，连续留榜比前一日单次回榜更具观察价值。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id852912420",
    },
    {
        "category": "卡牌 / 新版本", "date": "2026-09-29",
        "title": "Magic Arena的Reality Fracture版本窗口出现单日回吐",
        "summary": "官方2026.63.10版本以Reality Fracture、成对回响卡与扭曲的熟悉策略为核心。",
        "impact": "产品由iOS #10跌至#20，仍留在前20；需区分版本初期峰值与稳定付费承接。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1496227521",
    },
    {
        "category": "合并塔防 / 新品", "date": "2026-09-29",
        "title": "Plants on Fire海盗赛季后继续回落至iOS #60",
        "summary": "2.0.2810带回Pirate Captain，新增Chuckleberry、Thornmelon、四种变体与Ace Plan活动。",
        "impact": "产品仍在90天新品窗口，但已落至末位；下一快照能否留榜将直接检验首发承接。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6776076449",
    },
    {
        "category": "IP战术 / 版本更新", "date": "2026-09-30",
        "title": "SD Gundam更新图标与标题画面后由#15回吐至#27",
        "summary": "官方2.6.2版本说明只列应用图标与标题画面更新，没有披露新系统或大型活动。",
        "impact": "缺少明确内容节点时，12位回落应保留为榜位事实，不推演长期运营方向。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6692615881",
    },
    {
        "category": "全球收入月榜", "date": "2026-09-04",
        "title": "Sensor Tower官方最新全球收入月榜仍为2026年8月",
        "summary": "截至10月2日官方博客仍以8月榜为最新一期；全球App Store与Google Play消费者支出估算约65.7亿美元。",
        "impact": "策略子集继续为Whiteout Survival总榜#3、Kingshot #7；官方未披露单品同比，禁止从名次变化推算收入增幅。",
        "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026",
    },
]


closing = [
    {
        "type": "判断", "title": "双端换榜增多，但波动结构不同",
        "detail": "Google四进四出、56款共同产品中41款变动不超过2位，中位绝对变动1位；iOS三进三出、57款共同产品仅30款变动不超过2位，中位绝对变动2位。两端前10均全部保留，波动主要在中后段。",
    },
    {
        "type": "判断", "title": "Limbus与Clash构成两类双端共同信号",
        "detail": "Limbus在新Identity、E.G.O与章节上线后同时进入Google #53和iOS #32；Clash在Cosmic Curse启动日升至Google #8、iOS #1。前者是回榜，后者是高位抬升，均只能先记为单日待验证信号。",
    },
    {
        "type": "判断", "title": "跨端差继续由IP长线产品放大",
        "detail": "Star Trek为Google #17、iOS #56，差39位；Dragonfire在iOS升至#12却在Google跌至#26；Wild Rift两端方向也相反。相同内容窗口不能等同于相同平台付费强度。",
    },
    {
        "type": "关注", "title": "下一有效快照：检验The Ants与三款Google榜尾回榜",
        "detail": "The Ants #57、Ant Legion #59、Aliens #60都处高掉榜风险；若至少连续两个快照留榜，再判断Gamera活动期与蚂蚁题材是否形成可持续回补。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：核对Clash与Limbus的双端持续性",
        "detail": "Clash需继续维持iOS前3、Google前10，Limbus需同时留在iOS前40与Google TOP60，才可把今天的共同信号升级为连续承接。",
    },
    {
        "type": "关注", "title": "下一快照：观察Plants与Star Trek的尾部风险",
        "detail": "Plants on Fire已跌至iOS #60且仍属90天新品，Star Trek回榜仅#56；一旦掉榜，将分别表明首发回吐和大版本回补未形成连续留榜。",
    },
]


all_products = google_products + ios_products
icons = p.build_market_icons(all_products)
p.google_new = sum(game["comparison90d"]["status"] == "new" for game in p.datasets["googlePlay"]["now"])
p.ios_new = sum(game["comparison90d"]["status"] == "new" for game in p.datasets["ios"]["now"])


brief = {
    "date": p.DATE,
    "timezone": "Asia/Shanghai",
    "title": "Limbus双端回榜，Clash of Clans冲至iOS榜首，Google四进四出",
    "summary": "较10月1日最终有效快照，Google Play四进四出：Limbus #53、The Ants #57、Ant Legion #59、Aliens vs Zombies #60进入/回榜，Kingdom Rush 6、GFL2、Sea of Conquest、Galaxy Defense掉榜；Police Chief +6至#18，Call of Dragons -8至#48。iOS三进三出：Limbus #32、Age of Empires #42、Star Trek #56回榜，The Tower、War Machines、Kiss of War掉榜；Clash of Clans +10登顶，Dragon Traveler +20、Mobile Legends +19，SD Gundam、Wild Rift、Sea War与Plants均-12。近90天新品为Google 2款、iOS 3款，较老产品因缺少7月4日精确基准不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261002.json",
    "rankingSources": {"googlePlay": "data/games-20261002.json", "ios": "data/ios-games-20261002.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261001.json", "ios": "data/ios-games-20261001.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {p.captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Lands of Jail · #60 Aliens vs Zombies: Invasion",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {p.source_date:%Y-%m-%d}（源更新：{p.ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Clash of Clans · #25 Top Force: Commander · #60 Plants on Fire",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": p.global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": p.google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-04"},
        "ios": {"top60": 60, "newRelease90d": p.ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-04"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": p.google_history["sourceUrl"], "capturedAt": p.google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": p.ios_history["sourceUrl"], "updated": p.ios_history["sourceUpdated"], "sourceDateBeijing": p.ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": p.global_strategy_revenue["sourceUrl"], "period": p.global_strategy_revenue["period"], "estimateAsOf": p.global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-02.md", "json": "data/market-brief-20261002.json"},
}


p.save("data/market-brief-20261002.json", brief)
markdown = p.build_markdown(brief).replace(
    "各自上一份最终有效快照为2026-09-28",
    "各自上一份最终有效快照为2026-10-01",
).replace(
    "两端均缺少2026-07-01精确同口径TOP60基准",
    "两端均缺少2026-07-04精确同口径TOP60基准",
)
(p.ROOT / "reports/2026-10-02.md").write_text(markdown, encoding="utf-8")
manifest = p.load("reports/manifest.json")
entry = {
    "date": p.DATE,
    "title": brief["title"],
    "summary": brief["summary"],
    "markdown": brief["downloads"]["markdown"],
    "json": brief["downloads"]["json"],
}
manifest["updated"] = p.DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != p.DATE]
p.save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
