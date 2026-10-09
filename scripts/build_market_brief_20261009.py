#!/usr/bin/env python3
"""Generate the Beijing 2026-10-09 market brief, local icons and archive entry."""

from datetime import datetime
from zoneinfo import ZoneInfo

import build_market_brief_20261007 as base


DATE, STAMP = "2026-10-09", "20261009"
base.DATE = DATE
base.STAMP = STAMP
base.datasets = {
    "googlePlay": {
        "now": base.load("data/games-20261009.json"),
        "prior": base.load("data/games-20261008.json"),
        "id": "packageName",
    },
    "ios": {
        "now": base.load("data/ios-games-20261009.json"),
        "prior": base.load("data/ios-games-20261008.json"),
        "id": "appId",
    },
}
datasets = base.datasets
card = base.card


google_products = [
    card("googlePlay", "Ant Legion", "entry", "回到Google #59，iOS当前未进入TOP60；成熟蚁群4X产品位于倒数第二，先按榜尾回补记录，不能由单日回榜推断活动拉动。"),
    card("googlePlay", "Auto Drill", "entry", "首次进入项目Google #60。产品6月24日上架，已早于7月11日的90天窗口；10月2日仅披露修复与性能改善，本次末位入榜仍处首发验证。", first=True),
    card("googlePlay", "Limbus Company", "exit", "从Google上期#59掉榜，iOS当前也未进入TOP60；昨日已处倒数第二，本次属于榜尾风险兑现，未发现可确认的同日重大转折。"),
    card("googlePlay", "Forge of Empires", "exit", "从Google上期#60掉榜，iOS未进入TOP60；成熟城建产品昨日处末位，本次退出更符合榜尾轮换，不能据此判断长线经营结构变化。"),
    card("googlePlay", "Last Fortress", "down", "Google下跌7位至#57，iOS未进入当前TOP60；产品重新落入最后四名，下一有效快照的留榜比单日跌幅更能说明风险。"),
    card("googlePlay", "GIRLS' FRONTLINE 2", "up", "Google上升6位至#45，iOS未进入当前TOP60；本次只见Android端中后段改善，尚无跨端或连续快照证据。"),
    card("googlePlay", "Game of Thrones: Conquest", "up", "Google上升4位至#42，iOS同步上升4位至#21；两端同向但幅度有限，仍需下一快照确认是否形成连续承接。"),
]


ios_products = [
    card("ios", "DC: Dark Legion", "entry", "回到iOS #46，Google当前未进入TOP60。9月22日Nemesis Takedown是最近可核验内容背景，但回榜仍在后十五名，先按待验证信号处理。"),
    card("ios", "Plants on Fire", "entry", "回到iOS #51。产品8月26日上架，仍属于近90天新品；Pirate Captain与Ace Plan版本提供近期背景，但首发验证仍位于榜尾区。"),
    card("ios", "Last Shelter: War Z", "entry", "回到iOS #54，同名Google产品位于#36；两端相差18位，Milestone of Glory与世界宝箱是近期节点，但不能据此确认回榜原因。"),
    card("ios", "Cell Survivor", "entry", "回到iOS #55，Google当前未进入TOP60；9月30日4.0版本只笼统说明更多任务，缺少足以确认收入转折的公开细节。"),
    card("ios", "Last Day on Earth", "entry", "回到iOS #56。10月8日版本简化授权与进度恢复，时间相邻但并非新增商业化内容；后五名位置仍有直接掉榜风险。"),
    card("ios", "Kingdom Clash", "exit", "从iOS上期#50掉榜，Google当前未进入TOP60；成熟塔防产品继续在榜尾与榜外切换，未发现可确认的同日重大转折。"),
    card("ios", "Sea of Conquest", "exit", "从iOS上期#56掉榜，Google当前也未进入TOP60；上期已属后五名，本次退出延续榜尾轮换，不写成联动或版本的确定结果。"),
    card("ios", "Galaxy Defense", "exit", "从iOS上期#57掉榜；Season: Expedition仍在公开测试窗口，但没有形成第二个有效快照留榜，当前活动承接信号不足。"),
    card("ios", "Kingdom Guard", "exit", "从iOS上期#58掉榜，Google仍在#55；同一产品出现Android留榜、iPhone退出的分化，不能合并为统一走弱。"),
    card("ios", "Age of Empires", "exit", "从iOS上期#60掉榜，Google当前也未进入TOP60；昨日末位风险兑现，Stormlands与Mounted Hunt版本没有提供双端留榜证据。"),
    card("ios", "Summoners War", "up", "iOS上升21位至#33，为本端最大上涨；9月30日平衡与制作体验更新、10月10日SWC窗口可作背景，但单日名次不能证明活动因果。"),
    card("ios", "Pokémon Champions", "down", "iOS下跌18位至#60且恰处末位；10月7日1.2.2仅披露修复与体验改善，下一快照面临最高掉榜风险。"),
    card("ios", "Dragon Traveler", "up", "iOS上升17位至#34。9月9日Golden Night与Lilith版本是最近内容节点，但相隔一个月，今天先记为待验证峰值。"),
    card("ios", "Warhammer 40,000", "down", "iOS下跌17位至#58，Google为#44；10月8日更新与10月10日Terminus活动窗口临近，但当前首先表现为iPhone端大幅回落。"),
    card("ios", "Rise of Castles", "down", "iOS下跌14位至#59，Google同产品体系位于#25；两端相差34位，9月26日版本仅披露优化与修复。"),
    card("ios", "Game of Thrones: Dragonfire", "up", "iOS上升11位至#11，Google却下跌3位至#30；10月7日龙相关更新与排名相邻，但两端方向相反，不能写成统一版本拉动。"),
    card("ios", "Evo Defense", "down", "iOS下跌10位至#53。Everbloom与Style Switch是最近公开节点，但本期已经回到后八名，先按单日回吐处理。"),
]


news = [
    {
        "category": "全球收入月榜", "date": "2026-10-01",
        "title": "Sensor Tower 9月全球收入TOP10的核心策略子集仍为3款",
        "summary": "官方完整图表显示Whiteout Survival全球总榜#6、Last War: Survival #7、Kingshot #9；截至10月9日本次单次检查未见更新月份。",
        "impact": "Last War为新进全球TOP10，Whiteout与Kingshot较8月分别下降3位、2位；全球总榜名次变化不等于单品收入同比。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
    {
        "category": "新品 / 放置策略", "date": "2026-10-02",
        "title": "Auto Drill首次进入项目Google榜但仍处#60",
        "summary": "Google Play美国区显示产品6月24日上架，入口为自动或摇杆驾驶飞船击穿方块行星，10月2日更新仅披露修复与性能改善。",
        "impact": "本期首次进入项目榜且位于末位；上架早于90天窗口，不能归为近三个月新品，也不能把维护版本写成入榜原因。",
        "source": "Google Play官方商品页", "url": "https://play.google.com/store/apps/details?id=com.lavalabs.autodrill&hl=en_US&gl=US",
    },
    {
        "category": "IP 4X / 版本", "date": "2026-10-07",
        "title": "Game of Thrones: Dragonfire更新后iOS升至#11",
        "summary": "Apple官方版本于10月7日更新并继续强化龙相关内容；产品本期iOS +11，Google却−3至#30。",
        "impact": "IP节点与iPhone端上涨相邻，但跨端方向相反；应继续核对而非归因为统一版本拉动。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1642607669",
    },
    {
        "category": "长线RPG / 赛事", "date": "2026-09-30",
        "title": "Summoners War在10月10日赛事窗口前升至iOS #33",
        "summary": "Apple官方9.3.4版本调整怪物技能平衡与制作体验；官方入口同时列出10月10日SWC 2026 Americas Cup排期。",
        "impact": "本期+21为最大上涨；赛事前后能否连续留在前40，才有助于判断内容与核心用户支撑。",
        "source": "Summoners War官方入口", "url": "https://linktr.ee/summonerswarapp",
    },
    {
        "category": "战术RPG / 活动", "date": "2026-10-08",
        "title": "Tacticus更新并进入10月10日Terminus活动前窗口",
        "summary": "Apple官方1.43.127版本列出Lost and Damned，并排期10月10日Terminus生存活动与Battle Pass。",
        "impact": "iOS本期−17至#58、Google位于#44；活动开始后的双端变化将比当前单日下跌更有验证价值。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1599937506",
    },
    {
        "category": "卡牌 / 赛季", "date": "2026-10-02",
        "title": "MARVEL SNAP进入Vampires vs Zombies赛季后双端仍在榜",
        "summary": "官方游戏更新页发布Vampires vs Zombies新赛季，并在10月1日披露平衡调整。",
        "impact": "本期产品位于Google #40、iOS #28且iOS −7；赛季存在不等于名次必然上涨，仍应观察连续承接。",
        "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/category/game-updates/",
    },
    {
        "category": "竞技策略 / 维护", "date": "2026-10-07",
        "title": "Pokémon Champions维护版本后跌至iOS末位",
        "summary": "Apple官方1.2.2只披露问题修复与体验改善，没有新增大型玩法或活动说明。",
        "impact": "产品本期−18至#60；下一有效快照能否留榜是最直接的风险验证。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6741503079",
    },
    {
        "category": "新品 / 卡牌塔防", "date": "2026-09-29",
        "title": "Plants on Fire携Pirate Captain版本回到iOS #51",
        "summary": "官方2.0.2810版本让Pirate Captain回归，加入新Minion、Variant与Ace Plan活动。",
        "impact": "产品8月26日上架，仍按近90天新品展示；回榜位置位于后十名，首发验证尚未脱离截线。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6776076449",
    },
    {
        "category": "末日生存 / 账户体验", "date": "2026-10-08",
        "title": "Last Day on Earth简化授权与恢复流程后回到iOS",
        "summary": "Apple官方1.52.99版本简化授权和进度恢复，没有披露新增核心系统。",
        "impact": "产品回到#56但仍处后五名；体验修复与回榜时间相邻，不足以证明商业化拉动。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1241932094",
    },
    {
        "category": "IP SLG / 版本", "date": "2026-09-22",
        "title": "DC: Dark Legion以Nemesis Takedown内容回到iOS #46",
        "summary": "Apple官方2.2.26版本加入Nemesis Takedown相关内容，是本次回榜前最近可核验版本节点。",
        "impact": "产品仍在后十五名且Google未入榜；当前更像单端回补，需要连续快照验证。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6479020757",
    },
]

for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google主体稳定，但截线一次更换两款",
        "detail": "Google两进两出，58款共同产品中49款变动不超过2位、中位绝对变动1位，前10全部留存；Ant Legion与Auto Drill进入#59—#60，Limbus与Forge掉榜。",
    },
    {
        "type": "判断", "title": "iOS中后段双向波动显著高于Google",
        "detail": "iOS五进五出，55款共同产品中29款变动不超过2位、中位绝对变动2位，前10留存9款；Summoners +21、Dragon Traveler +17，与Pokémon −18、Tacticus −17同时出现。",
    },
    {
        "type": "判断", "title": "跨端表现继续分化，版本节点不能代替榜位验证",
        "detail": "Dragonfire位于iOS #11、Google #30且本期方向相反；Rise of Castles位于Google #25、iOS #59；Tacticus位于Google #44、iOS #58。已知版本或活动只作背景，不写成单日收入因果。",
    },
    {
        "type": "关注", "title": "下一有效快照：复核Google末四名",
        "detail": "观察Last Fortress #57、Wild Rift #58、Ant Legion #59与Auto Drill #60；若Auto Drill或Ant Legion立即退出，应维持榜尾回补/首发验证判断。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：检验iOS五款回榜产品",
        "detail": "DC #46、Plants #51、Last Shelter #54、Cell Survivor #55、Last Day on Earth #56均在后十五名；至少连续两次留榜并有产品进入前45，才说明本轮回补形成承接。",
    },
    {
        "type": "关注", "title": "10月10日前后：核对赛事与活动窗口",
        "detail": "Summoners当前#33、Tacticus当前#58；分别观察SWC Americas Cup与Terminus活动开始后是否出现连续而非一次性变化，并同时核对Google端Tacticus #44。",
    },
]


google_history = base.load("data/history/google-play/2026-10-09.json")
ios_history = base.load("data/history/ios/2026-10-09.json")
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
    "title": "Google截线换防，iOS五进五出，Summoners与Pokémon反向波动",
    "summary": "较10月8日前一有效快照，Google Play两进两出：Ant Legion回榜#59、Auto Drill首次进入项目榜#60，Limbus Company与Forge of Empires掉榜；Last Fortress −7至#57，GFL2 +6至#45。iOS五进五出：DC: Dark Legion #46、Plants on Fire #51、Last Shelter: War Z #54、Cell Survivor #55、Last Day on Earth #56回榜，Kingdom Clash、Sea of Conquest、Galaxy Defense、Kingdom Guard、Age of Empires掉榜；Summoners +21、Pokémon −18、Tacticus −17、Dragon Traveler +17。近90天新品为Google 2款、iOS 3款，较老产品因缺少7月11日精确基准不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261009.json",
    "rankingSources": {"googlePlay": "data/games-20261009.json", "ios": "data/ios-games-20261009.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261008.json", "ios": "data/ios-games-20261008.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Rise of Castles: Ice and Fire · #60 Auto Drill: Galaxy",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Kingshot · #25 PUBG MOBILE · #60 Pokémon Champions",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-11"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-11"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-09.md", "json": "data/market-brief-20261009.json"},
}

base.google_history = google_history
base.ios_history = ios_history
base.global_strategy_revenue = global_strategy_revenue
base.google_new = google_new
base.ios_new = ios_new
base.save("data/market-brief-20261009.json", brief)
markdown = base.build_markdown(brief).replace("2026-10-06", "2026-10-08").replace("2026-07-09", "2026-07-11")
(base.ROOT / "reports/2026-10-09.md").write_text(markdown, encoding="utf-8")
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
