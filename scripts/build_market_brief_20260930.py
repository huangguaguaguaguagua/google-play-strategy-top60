#!/usr/bin/env python3
"""Generate the Beijing 2026-09-30 market brief, local icons and archive entry."""

from datetime import datetime
from zoneinfo import ZoneInfo

import build_market_brief_20260929 as prior


p = prior
p.DATE, p.STAMP, p.CURRENT, p.PREVIOUS = "2026-09-30", "20260930", "20260930", "20260929"
p.datasets = {
    "googlePlay": {"now": p.load("data/games-20260930.json"), "prior": p.load("data/games-20260929.json"), "id": "packageName"},
    "ios": {"now": p.load("data/ios-games-20260930.json"), "prior": p.load("data/ios-games-20260929.json"), "id": "appId"},
}
p.google_history = p.load("data/history/google-play/2026-09-30.json")
p.ios_history = p.load("data/history/ios/2026-09-30.json")
p.global_strategy_revenue = p.load("data/sensortower-global-strategy-revenue-latest.json")
p.captured = datetime.fromisoformat(p.google_history["sourceCapturedAt"])
p.source_date = datetime.fromisoformat(p.ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    p.card("googlePlay", "Sea of Conquest", "entry", "回到Google #58；iOS昨日掉榜后本期仍未回归。9月24日版本只确认联动接近结束，本次Android回补先按榜尾信号处理。"),
    p.card("googlePlay", "Galaxy Defense", "entry", "回到Google #59，iOS也回榜#60。Season: Expedition与Kronos Exploration仍在运营窗口，但双端均压在末两名，留榜稳定性很低。"),
    p.card("googlePlay", "Vikings", "exit", "从Google上期#58掉榜，iOS未进入TOP60；成熟4X的单端榜尾回补未能维持，未发现与退出同日对应的官方重大节点。"),
    p.card("googlePlay", "Warpath", "exit", "从Google上期#59掉榜，iOS也未进入TOP60；当前只能确认美国区策略分类榜可见度回落，不能据此外推整体收入。"),
    p.card("googlePlay", "League of Legends", "up", "Google升9位至#47，同时回到iOS #24，是今天最清晰的双端共同改善；但Wild Rift属于MOBA分类边界，应单独解读，不能代表核心SLG扩张。"),
    p.card("googlePlay", "Last Shelter: Survival", "down", "Google再跌3位至#60，iOS则回榜#56。两端都位于最后五名，平台同时可见并未消除次日掉榜风险。"),
]


ios_products = [
    p.card("ios", "League of Legends", "entry", "回到iOS #24，Google同步升9位至#47。Patch 7.3仍是近期内容背景，但MOBA只因Apple策略标签进入本榜，按分类边界信号处理。"),
    p.card("ios", "The Tower", "entry", "回到iOS #33，Google策略榜未收录。成熟放置塔防本次位置高于此前多次榜尾回补，但仍需下一有效快照确认是否脱离单日峰值。"),
    p.card("ios", "Plants on Fire", "entry", "8月26日上架后首次进入项目iOS #39；9月29日海盗赛季加入两种新植物与四种变体，版本节点明确，但当前仍处首发验证。", first=True),
    p.card("ios", "Last Shelter: Survival", "entry", "回到iOS #56，Google跌至#60。成熟丧尸SLG双端同时可见但都压在后五名，当前更接近高风险榜尾回补。"),
    p.card("ios", "Galaxy Defense", "entry", "回到iOS #60，Google也回榜#59。Season: Expedition测试期与Kronos Exploration提供内容背景，但双端末位附近尚未形成稳定承接。"),
    p.card("ios", "Rise of Castles", "exit", "从iOS上期#38掉榜，Google仍在#16；前一快照的中段回归没有延续，平台差距扩大到至少44位。"),
    p.card("ios", "Watcher of Realms", "exit", "从iOS上期#51掉榜，Google策略榜未收录；公会Boss与公会战赛季背景没有阻止榜尾退出，单次回落不能直接定义长期趋势。"),
    p.card("ios", "Kingdom Rush 6", "exit", "从iOS上期#54掉榜，Google反而升2位至#50；首发后首次退出iOS TOP60，系列IP的双端承接转为明显分化。"),
    p.card("ios", "Dragon Traveler", "exit", "从iOS上期#58掉榜，Google同口径未收录；此前主要处于后十名，本次按榜尾轮换记录，未发现可确认的同日重大节点。"),
    p.card("ios", "Guns of Glory", "exit", "从iOS上期#60掉榜，Google仍位于#31；iPhone端末位回补只维持一个有效快照，Android端继续保持中段。"),
    p.card("ios", "MARVEL SNAP", "up", "iOS升19位至#40，为本端最大上涨；Vampires vs Zombies赛季仍是近期内容背景，但Google策略榜未收录，先按单端待验证峰值处理。"),
    p.card("ios", "Magic: The Gathering Arena", "up", "iOS升9位至#9，9月29日Reality Fracture版本与榜位改善时间相邻；版本事实可确认，但不足以证明全部涨幅由更新驱动。"),
    p.card("ios", "Draft Showdown", "down", "iOS跌12位至#41，Google却升4位至#51；9月25日新单位版本后出现平台分化，前一日双端回榜没有转成同步上行。"),
    p.card("ios", "Supremacy", "down", "iOS跌12位至#55，Google未进入TOP60；0.242平衡更新后仍处高风险榜尾，版本效果需要更长窗口判断。"),
    p.card("ios", "Lands of Jail", "down", "iOS跌11位至#48，Google位于#22；两端差距扩大到26位，今天应记录为iPhone端单日回吐而非产品整体走弱。"),
]


news = [
    {
        "category": "新品 / 合并塔防",
        "date": "2026-09-29",
        "title": "Plants on Fire海盗赛季上线并首次进入iOS TOP60",
        "summary": "Apple官方2.0.2810版本说明确认Pirate Captain回归，新增Chuckleberry、Thornmelon、四种变体与Ace Plan活动。",
        "impact": "产品本期首次进入项目iOS #39；版本与入榜时间相邻，但上线不足两个月，仍按首发验证而非长期增长判断。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6776076449",
    },
    {
        "category": "卡牌 / 新版本",
        "date": "2026-09-29",
        "title": "Magic Arena推出Reality Fracture并升入iOS前十",
        "summary": "2026.63.10版本以Reality Fracture、每包成对回响卡与扭曲的熟悉策略为核心。",
        "impact": "本期iOS +9至#9；大版本与排名同日改善值得继续观察，但不能从单日排名反推收入增幅。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1496227521",
    },
    {
        "category": "双端改善 / MOBA边界",
        "date": "2026-09-22",
        "title": "Wild Rift借Patch 7.3保持内容窗口并双端改善",
        "summary": "Patch 7.3加入Hwei、Sylas、Rek'Sai与3v3v3v3模式，并延续音乐主题皮肤和ARAM强化。",
        "impact": "本期iOS回榜#24、Google +9至#47；信号明确但产品属于MOBA分类边界，不作为核心SLG扩张证据。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1480616990",
    },
    {
        "category": "双端回榜 / 塔防运营",
        "date": "2026-09-22",
        "title": "Galaxy Defense赛季与探索活动背景下双端压线回榜",
        "summary": "1.0.1版本开放Season: Expedition测试赛季，并于9月24日开启Kronos Exploration。",
        "impact": "本期Google #59、iOS #60；内容节点可确认，但双端末两名意味着下一快照仍有极高换榜风险。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6740189002",
    },
    {
        "category": "太空4X / 高等级基地",
        "date": "2026-09-29",
        "title": "Star Trek Fleet Command更新Haven与新舰船",
        "summary": "M95.2围绕Ops 61+ Haven行星基地、账号增益、U.S.S. Kelcie Mae、Battle Pass与领地争夺更新。",
        "impact": "产品Google #17、iOS升4位至#53；高等级内容继续服务成熟核心用户，但iOS仍未脱离榜尾区。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1427744264",
    },
    {
        "category": "联盟运营 / 机制调整",
        "date": "2026-09-29",
        "title": "Police Chief新增联盟训练观战与护盾规则调整",
        "summary": "0.1.68加入联盟训练观战，调整增援中立建筑时的护盾机制，并修复行军卡顿等问题。",
        "impact": "产品本期恰好双端均为#25；同位只说明当前横截面一致，仍需观察联盟功能是否带来连续变化。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6757350661",
    },
    {
        "category": "轻量对战 / 新单位",
        "date": "2026-09-25",
        "title": "Draft Showdown新单位版本后转为平台分化",
        "summary": "Apple官方1.17.0版本仅披露新单位、体验改进与缺陷修复。",
        "impact": "本期Google +4至#51、iOS -12至#41；双端方向相反，前一日共同回榜不宜升级为持续改善。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6743368869",
    },
    {
        "category": "现代战争 / 平衡更新",
        "date": "2026-09-25",
        "title": "Supremacy平衡更新后回落至iOS后六名",
        "summary": "0.242版本调整Tank Destroyer学说、动员平衡和无障碍选项，并修复飞机、导弹与情报系统问题。",
        "impact": "本期iOS -12至#55、Google未入榜；更新事实明确，但短期榜位没有显示稳定承接。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1510997559",
    },
    {
        "category": "太空4X / S2优化",
        "date": "2026-09-24",
        "title": "Foundation调整Shadowfront奖励与S2港口奖励",
        "summary": "1.1.154提高Commerce Guild与S2首次占领港口奖励，降低部分科技树解锁要求，并优化集结排序。",
        "impact": "产品本期Google #29、iOS #37；成熟期仍通过经济与赛季奖励优化承接联盟用户。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6737595599",
    },
    {
        "category": "全球收入月榜",
        "date": "2026-09-04",
        "title": "Sensor Tower最新官方月榜仍为2026年8月",
        "summary": "全球App Store与Google Play消费者支出估算约65.7亿美元；Whiteout Survival全球总榜#3、Kingshot #7。",
        "impact": "两款均较7月上升1位；官方未披露单品同比，不能把榜位变化换算成收入增幅。",
        "source": "Sensor Tower官方",
        "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026",
    },
]


closing = [
    {
        "type": "判断",
        "title": "Google继续低波动，iOS换榜与中段跳动显著",
        "detail": "Google两进两出，58款共同产品中46款变动不超过2位，中位绝对变动1位且前10全部保留；iOS五进五出，55款共同产品中仅29款变动不超过2位，中位绝对变动2位、前10保留9款。",
    },
    {
        "type": "判断",
        "title": "Wild Rift双端改善成立，但核心策略信号仍偏弱",
        "detail": "Wild Rift回到iOS #24并在Google升9位至#47，是今天最清晰的双端改善；Galaxy Defense也双端回榜，但仅位于Google #59与iOS #60。前者属MOBA边界，后者仍是榜尾换防。",
    },
    {
        "type": "判断",
        "title": "iOS内容节点带来多个单日信号，尚未形成共同方向",
        "detail": "Plants on Fire在海盗赛季首进#39、Magic Arena随Reality Fracture升至#9，MARVEL SNAP升19位；同时Draft和Supremacy各跌12位，说明版本窗口并不等于一致的榜位改善。",
    },
    {
        "type": "关注",
        "title": "未来1—2个有效快照：验证Plants on Fire首进承接",
        "detail": "若Plants on Fire在2.0海盗赛季后仍能守住iOS前45，可把首次#39升级为连续首发承接；若迅速跌至后十名或掉榜，只记录为版本峰值。",
    },
    {
        "type": "关注",
        "title": "下一有效快照：核对Galaxy Defense双端末位风险",
        "detail": "当前Google #59、iOS #60；任一端再次退出都说明赛季与探索活动尚未带来稳定TOP60承接，双端继续留榜才算有效改善。",
    },
    {
        "type": "关注",
        "title": "未来两日：观察Wild Rift与Magic Arena是否保持改善",
        "detail": "Wild Rift需让Google脱离后十名并维持iOS前30；Magic Arena需在Reality Fracture上线后继续守住iOS前15，才把今天的跳升视为连续信号。",
    },
]


all_products = google_products + ios_products
icons = p.build_market_icons(all_products)
p.google_new = sum(game["comparison90d"]["status"] == "new" for game in p.datasets["googlePlay"]["now"])
p.ios_new = sum(game["comparison90d"]["status"] == "new" for game in p.datasets["ios"]["now"])


brief = {
    "date": p.DATE,
    "timezone": "Asia/Shanghai",
    "title": "Wild Rift双端改善，Plants on Fire首进iOS，iOS换榜继续高于Google",
    "summary": "较9月29日最终有效快照，Google Play两进两出：Sea of Conquest、Galaxy Defense回榜，Vikings、Warpath掉榜；Wild Rift +9至#47，Last Shelter: Survival跌至#60。iOS五进五出：Wild Rift、The Tower、Last Shelter、Galaxy Defense回榜，Plants on Fire首次进入#39；另有5款掉榜，MARVEL SNAP +19、Magic Arena +9，Draft与Supremacy各-12。Google仍显著稳定于iOS；近90天新品两端各3款，较老产品因缺少7月2日精确基准不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20260930.json",
    "rankingSources": {"googlePlay": "data/games-20260930.json", "ios": "data/ios-games-20260930.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260929.json", "ios": "data/ios-games-20260929.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {p.captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Police Chief · #60 Last Shelter: Survival",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {p.source_date:%Y-%m-%d}（源更新：{p.ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Pokémon GO · #25 Police Chief · #60 Galaxy Defense: Fortress TD",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": p.global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": p.google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-02"},
        "ios": {"top60": 60, "newRelease90d": p.ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-02"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": p.google_history["sourceUrl"], "capturedAt": p.google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": p.ios_history["sourceUrl"], "updated": p.ios_history["sourceUpdated"], "sourceDateBeijing": p.ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": p.global_strategy_revenue["sourceUrl"], "period": p.global_strategy_revenue["period"], "estimateAsOf": p.global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-30.md", "json": "data/market-brief-20260930.json"},
}


p.save("data/market-brief-20260930.json", brief)
markdown = p.build_markdown(brief).replace(
    "各自上一份最终有效快照为2026-09-28",
    "各自上一份最终有效快照为2026-09-29",
).replace(
    "两端均缺少2026-07-01精确同口径TOP60基准",
    "两端均缺少2026-07-02精确同口径TOP60基准",
)
(p.ROOT / "reports/2026-09-30.md").write_text(markdown, encoding="utf-8")
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
