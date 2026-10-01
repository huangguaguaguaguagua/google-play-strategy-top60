#!/usr/bin/env python3
"""Generate the Beijing 2026-10-01 market brief, local icons and archive entry."""

from datetime import datetime
from zoneinfo import ZoneInfo

import build_market_brief_20260930 as prior


p = prior.p
p.DATE, p.STAMP, p.CURRENT, p.PREVIOUS = "2026-10-01", "20261001", "20261001", "20260930"
p.datasets = {
    "googlePlay": {"now": p.load("data/games-20261001.json"), "prior": p.load("data/games-20260930.json"), "id": "packageName"},
    "ios": {"now": p.load("data/ios-games-20261001.json"), "prior": p.load("data/ios-games-20260930.json"), "id": "appId"},
}
p.google_history = p.load("data/history/google-play/2026-10-01.json")
p.ios_history = p.load("data/history/ios/2026-10-01.json")
p.global_strategy_revenue = p.load("data/sensortower-global-strategy-revenue-latest.json")
p.captured = datetime.fromisoformat(p.google_history["sourceCapturedAt"])
p.source_date = datetime.fromisoformat(p.ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    p.card("googlePlay", "Age of Origins", "down", "Google回落5位至#25，iOS仅回落1位至#17；两端仍处中前段，本次更像Android端单日校正。未发现与10月1日同步的官方重大节点。"),
    p.card("googlePlay", "Sea War", "down", "Google回落3位至#37，iOS仅回落1位至#38，两端名次几乎重合；昨日Android回补没有延续为同步上涨，先按短期回吐记录。"),
    p.card("googlePlay", "Top Force", "up", "Google上升2位至#19，iOS上升1位至#27。双端同向但幅度有限，尚不足以定义新的增长阶段。"),
]


ios_products = [
    p.card("ios", "SD Gundam", "entry", "回到iOS #15，是本次回榜产品中位置最高的一款；9月30日2.6.2版本只更新应用图标与标题画面，因此本次跃入前20仍按待验证信号处理。"),
    p.card("ios", "Fire Emblem Heroes", "entry", "回到iOS #25；10.9版本围绕Fire Emblem: Fortune's Weave预热和七名英雄武器精炼，但版本已于9月8日上线，不能直接解释本次单日回榜。"),
    p.card("ios", "Summoners War", "entry", "回到iOS #29；9月30日9.3.4调整怪物技能平衡并改进魔法制作与其他体验，更新与回榜时间相邻，但因果仍需连续快照确认。"),
    p.card("ios", "War Machines", "entry", "首次进入项目保存的iOS榜#57。9月29日8.74.2只披露缺陷修复与性能改进，未发现可确认的重大运营节点；按成熟PvP榜尾信号处理。", first=True),
    p.card("ios", "Dragon Traveler", "entry", "回到iOS #58；最近可核验的大节点仍是9月9日Golden Night Reverie与SSR+ Lilith，当前已相隔三周，不能把本次回榜直接归因于该版本。"),
    p.card("ios", "Hearthstone", "entry", "回到iOS #59；36.6版本以Reign of the Black Empire预览卡、标准与酒馆平衡、Aberration随从类型为内容背景，但仍贴近掉榜线。"),
    p.card("ios", "Age of Empires", "exit", "从iOS上期#51掉榜，Google仍为#53；两端都处高风险尾部，iPhone端先退出不能外推为全平台长期走弱。"),
    p.card("ios", "Star Trek Fleet Command", "exit", "从iOS上期#53掉榜，Google仍稳在#17，跨端差扩大到至少44位；高等级Haven内容在Android端的承接明显更强。"),
    p.card("ios", "Last Shelter: Survival", "exit", "从iOS上期#56掉榜，Google升2位至#58。双端仍在榜尾轮换区，当前没有可确认的同日重大转折。"),
    p.card("ios", "Boom Beach", "exit", "从iOS上期#58掉榜，Google同口径也未收录；成熟塔防策略的末位回补只维持一个有效快照。"),
    p.card("ios", "Kingdom Guard", "exit", "从iOS上期#59掉榜，Google亦未进入TOP60；前一日回补未形成留榜，继续按榜尾波动而非长期下行处理。"),
    p.card("ios", "Galaxy Defense", "exit", "从iOS上期#60掉榜，Google仍为#60。Season: Expedition与Kronos Exploration没有让双端同时脱离末位风险。"),
    p.card("ios", "Raid Rush", "up", "iOS上升6位至#28，为本端最大上涨；Google仅升1位至#54，双端同向但平台强度差异明显。"),
    p.card("ios", "Supremacy", "up", "iOS上升4位至#51，0.242平衡更新仍是近期内容背景；尚未脱离后十名，当前只记为榜尾改善。"),
    p.card("ios", "The Tower", "down", "iOS下跌16位至#49，为本端最大回落；v29新增全局预设、Mythic联赛和Vault改版，但大版本后的前一日回榜未转成稳定高位。"),
    p.card("ios", "League of Legends", "down", "iOS下跌13位至#37，Google反而升1位至#46；Patch 7.3仍在内容窗口，但今天转为平台分化，且产品属于MOBA分类边界。"),
    p.card("ios", "Draft Showdown", "down", "iOS下跌13位至#54，Google为#51；9月25日新单位版本后两端都压到后十名，前期回榜尚未形成稳定承接。"),
    p.card("ios", "Plants on Fire", "down", "iOS下跌9位至#48；海盗赛季仍在，但首次#39后的次日回吐明显。产品仍属近90天新品，暂不把版本入口写成长期增长。"),
]


news = [
    {
        "category": "回榜 / 平衡更新", "date": "2026-09-30",
        "title": "Summoners War更新怪物技能平衡并回到iOS #29",
        "summary": "Apple官方9.3.4版本说明确认调整怪物技能平衡，并改进Magic Crafting与其他体验。",
        "impact": "更新与本次回榜时间相邻，是今天较强的待验证内容信号；仍不能从单日排名判断收入增幅。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id852912420",
    },
    {
        "category": "IP战术 / 回榜", "date": "2026-09-30",
        "title": "SD Gundam 2.6.2更新图标与标题画面后回到iOS前20",
        "summary": "官方版本说明只列应用图标和标题画面更新，没有披露新系统或大型活动。",
        "impact": "产品回到iOS #15，但缺少明确玩法节点，需优先核对下一快照是否维持前20。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6692615881",
    },
    {
        "category": "合并塔防 / 新品", "date": "2026-09-29",
        "title": "Plants on Fire海盗赛季次日回吐至iOS #48",
        "summary": "2.0.2810带回Pirate Captain，新增Chuckleberry、Thornmelon、四种变体与Ace Plan活动。",
        "impact": "产品仍在90天新品窗口，但首次#39后下跌9位；是否形成首发承接需继续观察。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6776076449",
    },
    {
        "category": "卡牌 / 新版本", "date": "2026-09-29",
        "title": "Magic Arena的Reality Fracture版本继续留在iOS前十",
        "summary": "2026.63.10版本以Reality Fracture、每包成对回响卡与扭曲的熟悉策略为核心。",
        "impact": "产品本期#10，仍保持版本上线后的前十可见度；连续性比单日涨幅更值得关注。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1496227521",
    },
    {
        "category": "放置塔防 / 大版本", "date": "2026-09-25",
        "title": "The Tower v29扩展预设与Mythic联赛后单日回落",
        "summary": "v29新增Global Presets、Preset Lab、Mythic赛事联赛、Vault改版、Harmony Tree与卡牌/模组内容。",
        "impact": "产品从#33跌至#49，说明大版本与回榜并未立即形成稳定高位；后续留榜比单日峰值更关键。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1575590830",
    },
    {
        "category": "卡牌 / 版本预览", "date": "2026-09-24",
        "title": "Hearthstone预热Reign of the Black Empire并回到榜尾",
        "summary": "36.6版本提供预览传奇卡与活动卡，调整标准与酒馆战棋平衡，并加入Aberration随从类型。",
        "impact": "本期回到iOS #59，内容入口明确但榜位仍高风险；需观察预览期能否转为连续留榜。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id625257520",
    },
    {
        "category": "IP战棋 / 长线运营", "date": "2026-09-08",
        "title": "Fire Emblem Heroes以Fortune's Weave预热回到iOS #25",
        "summary": "10.9版本开启Fire Emblem: Fortune's Weave发布前庆祝，并为Mythic Veyle等七名英雄加入武器精炼。",
        "impact": "产品本次回到中段，但版本已上线三周；回榜只能视作与IP窗口并存，不能确认直接因果。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1181774280",
    },
    {
        "category": "坦克PvP / 公司归属", "date": "2026-09-29",
        "title": "War Machines首次进入项目iOS榜，发行主体确认为Wildlife Studios",
        "summary": "Apple Lookup列Wildlife Studios, Inc.为seller；8.74.2版本仅说明缺陷修复与性能改进。",
        "impact": "首次记录于#57，但产品2016年即上架且无重大节点，按成熟期榜尾信号而非新品处理。",
        "source": "Wildlife Studios官方", "url": "https://wildlifestudios.com/",
    },
    {
        "category": "IP联动 / 长线4X", "date": "2026-09-01",
        "title": "Lords Mobile x Transformers第二阶段仍在双端运营",
        "summary": "2.201版本加入Transformers Raceway、Megatron领主皮肤、Cybertron Rest Stop及战场调整。",
        "impact": "本期Google #28、iOS跌至#55；联动仍提供内容背景，但双端付费强度分化显著。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1071976327",
    },
    {
        "category": "全球收入月榜", "date": "2026-09-04",
        "title": "Sensor Tower官方最新全球收入月榜仍为2026年8月",
        "summary": "全球App Store与Google Play消费者支出估算约65.7亿美元；策略子集为Whiteout Survival总榜#3、Kingshot #7。",
        "impact": "两款均较7月上升1位；官方未披露单品同比，继续禁止从榜位变化换算收入增幅。",
        "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026",
    },
]


closing = [
    {
        "type": "判断", "title": "Google全量留榜且极稳，iOS六进六出",
        "detail": "Google 60款全部留榜，58款变动不超过2位，中位绝对变动1位且前10全部保留；iOS六进六出，54款共同产品中32款变动不超过2位，中位绝对变动1.5位，换榜压力集中在中后段。",
    },
    {
        "type": "判断", "title": "iOS回榜与同日版本并存，但信号强度不同",
        "detail": "Summoners War的技能平衡更新与#29回榜同日，SD Gundam却只更新图标与标题画面仍回到#15；The Tower大版本后又下跌16位，说明内容节点只能作为背景，不能直接当作排名因果。",
    },
    {
        "type": "判断", "title": "跨端分化由Star Trek与榜尾产品进一步放大",
        "detail": "Star Trek在Google #17而iOS掉榜，差距至少44位；Galaxy Defense保留Google #60却退出iOS，Last Shelter则Google #58、iOS退出。双端共同在榜不应默认成同强度运营。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证Summoners War与SD Gundam回榜",
        "detail": "若两款继续留在iOS前35，可把今天的中前段回归升级为连续承接；若迅速退到后十名或掉榜，则只保留为单日峰值。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：核对三款榜尾回榜留存",
        "detail": "War Machines #57、Dragon Traveler #58、Hearthstone #59均处极高掉榜风险；至少连续两次留榜才说明这轮尾部回补具有延续性。",
    },
    {
        "type": "关注", "title": "未来两日：观察Plants on Fire与The Tower能否止跌",
        "detail": "Plants on Fire需守住iOS前50并避免首进后快速掉榜；The Tower需在v29后回到前40，才可把近期回榜视为大版本后的有效承接。",
    },
]


all_products = google_products + ios_products
icons = p.build_market_icons(all_products)
p.google_new = sum(game["comparison90d"]["status"] == "new" for game in p.datasets["googlePlay"]["now"])
p.ios_new = sum(game["comparison90d"]["status"] == "new" for game in p.datasets["ios"]["now"])


brief = {
    "date": p.DATE,
    "timezone": "Asia/Shanghai",
    "title": "Google全量稳定，iOS六进六出，Summoners War与SD Gundam回到中前段",
    "summary": "较9月30日最终有效快照，Google Play无进入或掉榜，60款全部留榜；Age of Origins -5至#25、Sea War -3至#37，58款变动不超过2位。iOS六进六出：SD Gundam #15、Fire Emblem #25、Summoners War #29回榜，War Machines首次进入项目榜#57，另有Dragon Traveler、Hearthstone回榜；Age of Empires、Star Trek、Last Shelter、Boom Beach、Kingdom Guard、Galaxy Defense掉榜。The Tower -16、Wild Rift与Draft各-13，Raid Rush +6。近90天新品两端各3款，较老产品因缺少7月3日精确基准不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261001.json",
    "rankingSources": {"googlePlay": "data/games-20261001.json", "ios": "data/ios-games-20261001.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260930.json", "ios": "data/ios-games-20260930.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {p.captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Age of Origins · #60 Galaxy Defense: Fortress TD",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {p.source_date:%Y-%m-%d}（源更新：{p.ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Pokémon GO · #25 Fire Emblem Heroes · #60 Kiss of War",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": p.global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": p.google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-03"},
        "ios": {"top60": 60, "newRelease90d": p.ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-03"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": p.google_history["sourceUrl"], "capturedAt": p.google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": p.ios_history["sourceUrl"], "updated": p.ios_history["sourceUpdated"], "sourceDateBeijing": p.ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": p.global_strategy_revenue["sourceUrl"], "period": p.global_strategy_revenue["period"], "estimateAsOf": p.global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-01.md", "json": "data/market-brief-20261001.json"},
}


p.save("data/market-brief-20261001.json", brief)
markdown = p.build_markdown(brief).replace(
    "各自上一份最终有效快照为2026-09-28",
    "各自上一份最终有效快照为2026-09-30",
).replace(
    "两端均缺少2026-07-01精确同口径TOP60基准",
    "两端均缺少2026-07-03精确同口径TOP60基准",
)
(p.ROOT / "reports/2026-10-01.md").write_text(markdown, encoding="utf-8")
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
