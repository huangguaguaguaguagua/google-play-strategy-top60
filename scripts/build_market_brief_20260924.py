#!/usr/bin/env python3
"""Generate the Beijing 2026-09-24 market brief, local icons and archive entry."""

from datetime import datetime
from zoneinfo import ZoneInfo

import build_market_brief_20260923 as base


DATE, STAMP, CURRENT, PREVIOUS = "2026-09-24", "20260924", "20260924", "20260923"
base.DATE, base.STAMP, base.CURRENT, base.PREVIOUS = DATE, STAMP, CURRENT, PREVIOUS
base.datasets = {
    "googlePlay": {
        "now": base.load(f"data/games-{CURRENT}.json"),
        "prior": base.load(f"data/games-{PREVIOUS}.json"),
        "id": "packageName",
    },
    "ios": {
        "now": base.load(f"data/ios-games-{CURRENT}.json"),
        "prior": base.load(f"data/ios-games-{PREVIOUS}.json"),
        "id": "appId",
    },
}
datasets = base.datasets


def card(store, prefix, tone, analysis, first=False):
    return base.card(store, prefix, tone, analysis, first)


google_history = base.load("data/history/google-play/2026-09-24.json")
ios_history = base.load("data/history/ios/2026-09-24.json")
global_strategy_revenue = base.load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Sea War", "entry", "回到Google #59，同时iOS升19位至#29，是今天最清晰的双端共同改善信号。Apple 9月22日版本仅披露界面与缺陷修复，缺少可确认的内容节点，先按待验证信号处理。"),
    card("googlePlay", "Vikings", "entry", "回到Google #60，iOS同口径未收录。产品属于成熟4X，本次紧贴掉榜线；未找到与当天回榜直接对应的官方重大节点。"),
    card("googlePlay", "Kingdom Guard", "exit", "昨日回到Google #60后今天掉榜，iOS也从#59掉榜。Fruit Market仍在9月22—27日窗口内，但双端均未形成连续留榜。"),
    card("googlePlay", "Arknights", "exit", "从上期Google #55掉出TOP60，iOS同口径未收录。单个快照只说明当前策略分类榜承接减弱，不能等同于产品整体收入下降。"),
    card("googlePlay", "League of Legends: Wild Rift", "up", "Google升5位至#46，iOS却跌7位至#39。Patch 7.3仍在上线窗口，但两个商店方向相反，属于平台分化而非双端同步增长。"),
    card("googlePlay", "Call of Dragons", "up", "Google升5位至#47，并首次进入iOS #56。Full Moon Festivities仍在运营窗口，但iOS位于后五名，需要连续快照确认承接。"),
    card("googlePlay", "Last Fortress", "up", "Google升3位至#40，iOS则从#56掉榜。Android改善没有在iPhone同步出现，暂按单端变化归档。"),
    card("googlePlay", "Limbus Company", "down", "Google跌11位至#43，为本端最大跌幅；iOS同口径未收录。没有可核验的新节点足以解释单日回落，需观察是否快速修复。"),
    card("googlePlay", "Raid Rush", "down", "Google跌4位至#50，iOS仅小幅变化并仍在榜。当前进入后十名，下一有效快照是榜尾风险观察点。"),
    card("googlePlay", "Mafia City", "down", "Google跌3位至#52，iOS同口径未收录。成熟产品滑入后十名，但单日变动不足以证明长期付费盘转弱。"),
    card("googlePlay", "Game of Thrones: Conquest", "down", "Google跌3位至#53，iOS小幅回升但仍在后段。Dragonseed版本没有形成明确双端同向抬升。"),
]


ios_products = [
    card("ios", "Honor of Kings", "entry", "首次进入iOS #40。Season 16《Flow As One》于9月23日开启，版本节点与入榜相邻；产品属于MOBA分类边界，不计入核心策略收入子集。", first=True),
    card("ios", "Kiss of War", "entry", "回到iOS #47，Google同口径未收录。Apple最新公开版本仍是8月14日的界面与缺陷修复，缺少可确认的新活动原因。"),
    card("ios", "Rise of Castles", "entry", "回到iOS #48，Google当前#20。9月14日版本只披露性能优化与缺陷修复，先记录为单端后段回归。"),
    card("ios", "Lucky Defense", "entry", "首次进入iOS #54。9月23日版本加入Emily、极限突破和中秋Kingdom Festival，节点与入榜同期，但当前仍在后七名。", first=True),
    card("ios", "Call of Dragons", "entry", "首次进入iOS #56，同时Google升5位至#47。Full Moon Festivities提供烟花兑换、占卜、军种转换等活动，双端改善仍需连续快照验证。", first=True),
    card("ios", "Coop TD", "exit", "昨日随中秋活动回到iOS #49，今天即掉榜。新活动尚未形成连续留榜，当前按一次性边界回归归档。"),
    card("ios", "Last Fortress", "exit", "从上期iOS #56掉榜，而Google升3位至#40。两个商店方向分化，不能将iOS掉榜外推为产品整体转弱。"),
    card("ios", "Star Trek Fleet Command", "exit", "从上期iOS #57掉榜，Google同口径未收录。成熟IP SLG仍处分类榜边缘，未发现当天可确认的重大转折。"),
    card("ios", "Kingdom Guard", "exit", "昨日回到iOS #59后今天掉榜，Google也同步掉榜。Fruit Market活动窗口仍在，但双端回归仅维持一个有效快照。"),
    card("ios", "Lords Mobile", "exit", "上期跌至iOS #60后掉榜，Google仍在#33。Transformers联动在Android保持中段可见度，但iPhone分类榜承接暂时中断。"),
    card("ios", "Sea War", "up", "iOS升19位至#29并进入前30，Google同步回榜#59。官方最新版本只写界面与缺陷修复，因此不臆测具体增长原因。"),
    card("ios", "Forge Master", "up", "iOS升7位至#26，Google当前未进入TOP60。产品回到前30，但暂无与今天涨幅直接对应的公开节点。"),
    card("ios", "MARVEL SNAP", "up", "iOS升6位至#45，Google策略榜未收录。作为卡牌产品，本次仅记录Apple Strategy分类内改善，不代表4X或SLG市场变化。"),
    card("ios", "The Battle Cats", "down", "iOS跌13位至#52，延续此前高位回吐。15.6.0新增震动、形态与地图内容，但近期榜位承接正在减弱。"),
    card("ios", "Last Day on Earth", "down", "iOS跌12位至#53，Google策略榜未收录。Crooked Creek Farm重做节点仍在，但今天重新进入后十名。"),
    card("ios", "Top Heroes", "down", "iOS跌12位至#59，Google基本稳定在#34。Cloudsea Odyssey和Legendary Battlefield上线后，iPhone端连续回吐至掉榜线。"),
    card("ios", "League of Legends: Wild Rift", "down", "iOS跌7位至#39，而Google升5位至#46。Patch 7.3没有形成双端同向榜位表现，需分平台观察。"),
    card("ios", "Overgeared Hero", "down", "iOS跌6位至#58，Google仍在#39。联动窗口内连续回落到后五名，下一快照存在掉榜风险。"),
]


news = [
    {
        "category": "MOBA / 新赛季",
        "date": "2026-09-22",
        "title": "Honor of Kings开启Season 16《Flow As One》",
        "summary": "Apple官方版本说明确认Season 16于9月23日开启，并带来Mai Shiranui限时皮肤回归及多名英雄机制、数值调整。",
        "impact": "产品首次进入iOS策略分类榜#40；它属于MOBA分类边界，不纳入核心策略收入子集。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1619254071",
    },
    {
        "category": "合作塔防 / 中秋活动",
        "date": "2026-09-23",
        "title": "Lucky Defense推出Emily与Kingdom Festival",
        "summary": "2.0.13版本加入守护者Emily、极限突破与限定皮肤，并开启中秋Kingdom Festival和最多四人参与的Lucky Game Paradise。",
        "impact": "产品首次进入iOS #54；版本与入榜同期，但当前仍在榜尾区域。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6482291732",
    },
    {
        "category": "海战SLG / 双端异动",
        "date": "2026-09-22",
        "title": "Sea War双端改善但官方版本仅披露修复",
        "summary": "Apple 1.174.0版本说明只列出界面显示与缺陷修复，没有披露新玩法、联动或赛季内容。",
        "impact": "产品iOS升19位至#29并回到Google #59；原因缺少官方内容证据，仍按待验证信号处理。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6447612873",
    },
    {
        "category": "奇幻4X / 节庆运营",
        "date": "2026-09-16",
        "title": "Call of Dragons推进Full Moon Festivities",
        "summary": "官方版本列出烟花兑换、限时礼包、House of Destiny占卜、军种转换、神器许愿及年度回顾等活动。",
        "impact": "产品首次进入iOS #56，同时Google升5位至#47；iPhone仍在后五名，需要观察活动后的留榜。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1605558677",
    },
    {
        "category": "MOBA / 跨端分化",
        "date": "2026-09-22",
        "title": "Wild Rift Patch 7.3后出现跨端反向变化",
        "summary": "Patch 7.3加入Hwei、Sylas、Rek'Sai、3v3v3v3模式、SMASH社区内容和音乐主题皮肤。",
        "impact": "Google升5位至#46、iOS跌7位至#39；相反方向说明单日版本效果不能跨平台直接外推。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1480616990",
    },
    {
        "category": "卡牌 / 新卡包",
        "date": "2026-09-22",
        "title": "Magic Arena上线Reality Fracture",
        "summary": "2026.63.0版本以Shatter the Looking Glass为主题，每包加入echoed pair并围绕扭曲的熟悉策略构筑套牌。",
        "impact": "产品本期位列iOS #25，是Apple策略分类中卡牌产品稳定占位的代表。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1496227521",
    },
    {
        "category": "SLG / 赛季承接",
        "date": "2026-09-21",
        "title": "Top Heroes赛季更新后继续回吐",
        "summary": "1.122.8开启Legendary Battlefield，并调整Cloudsea Odyssey世界Boss体力、Ranch保底与邮件收藏。",
        "impact": "产品今天iOS再跌12位至#59、Google维持#34，版本尚未在iPhone形成连续榜位承接。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6450953550",
    },
    {
        "category": "塔防 / 长线更新",
        "date": "2026-09-14",
        "title": "The Battle Cats 15.6.0扩充形态与地图内容",
        "summary": "版本加入战斗震动、新True/Ultra Forms、新Talents、Legend地图难度、Rank奖励与CatCombos。",
        "impact": "产品今天iOS跌13位至#52，近期高位正在连续回吐，需观察内容更新后的常态区间。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id850057092",
    },
    {
        "category": "末日SLG / 回榜",
        "date": "2026-09-14",
        "title": "Rise of Castles回榜但版本仅披露性能优化",
        "summary": "26.901.1版本说明只有性能优化与缺陷修复，没有公开新赛季、活动或商业化节点。",
        "impact": "产品回到iOS #48、Google列#20；当前只能确认单端回榜，不能臆测具体推动因素。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1411917616",
    },
    {
        "category": "全球收入月榜",
        "date": "2026-09-04",
        "title": "Sensor Tower最新官方月榜仍为2026年8月",
        "summary": "全球App Store与Google Play消费者支出估算约65.7亿美元；Whiteout Survival全球总榜#3、Kingshot #7。",
        "impact": "两款均较7月上升1位；官方未披露单品同比，不能把榜位变化换算为收入增幅。",
        "source": "Sensor Tower官方",
        "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026",
    },
]


closing = [
    {
        "type": "判断",
        "title": "Google仍以小幅换位为主，iOS继续保持高轮换",
        "detail": "Google两进两出，58款共同产品中51款变动不超过2位，中位绝对变动1位且前10全部保留；iOS五进五出，55款共同产品中33款变动不超过2位，中位绝对变动2位且前10更换1款。",
    },
    {
        "type": "判断",
        "title": "Sea War是今日最强双端共同信号，但原因仍未被官方内容解释",
        "detail": "Sea War在iOS升19位并回到Google，方向一致；然而最新版本只披露界面与缺陷修复。Call of Dragons也双端改善，但iOS仅#56，因此两款都需要连续快照。",
    },
    {
        "type": "判断",
        "title": "新赛季与节庆活动正在影响榜尾轮换，核心策略与分类边界需分开",
        "detail": "Honor of Kings随Season 16进入iOS，但它属于MOBA；Lucky Defense与Call of Dragons在活动窗口进入后段。与此同时Kingdom Guard和Coop TD的活动回榜只维持一天。",
    },
    {
        "type": "关注",
        "title": "下一有效快照：确认Sea War和Call of Dragons的双端持续性",
        "detail": "Sea War若iOS保持前35且Google继续留榜，才升级为连续改善；Call of Dragons需守住Google前50并让iOS离开后五名，否则只记为活动期边界进入。",
    },
    {
        "type": "关注",
        "title": "未来1—2个有效快照：检验新活动产品能否离开榜尾",
        "detail": "Lucky Defense需由#54升入前50；Honor of Kings需守住iOS前45。若快速掉榜，则分别按中秋活动与新赛季的短期峰值归档。",
    },
    {
        "type": "关注",
        "title": "下一有效快照：观察iOS连续回吐产品的掉榜风险",
        "detail": "Top Heroes已到#59、Overgeared到#58，任一继续下移都可能掉榜；The Battle Cats与Last Day on Earth需先稳定在前55，才能结束本轮回吐。",
    },
]


all_products = google_products + ios_products
icons = base.build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])
base.google_history, base.ios_history = google_history, ios_history
base.google_new, base.ios_new = google_new, ios_new

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Sea War双端同步改善，iOS五进五出延续高轮换",
    "summary": "较9月23日最终有效快照，Google Play两进两出：Sea War与Vikings回榜，Kingdom Guard与Arknights掉榜；Wild Rift和Call of Dragons各升5位，Limbus Company跌11位。iOS五进五出：Honor of Kings、Kiss of War、Rise of Castles、Lucky Defense与Call of Dragons进入/回榜，Coop TD、Last Fortress、Star Trek、Kingdom Guard与Lords Mobile掉榜；Sea War +19至#29，The Battle Cats -13、Last Day on Earth与Top Heroes各-12。近90天新品Google 2款、iOS 2款；两端缺少6月26日精确基准，较老产品不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": f"data/games-{CURRENT}.json", "ios": f"data/ios-games-{CURRENT}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREVIOUS}.json", "ios": f"data/ios-games-{PREVIOUS}.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Age of Origins · #60 Vikings: War of Clans PvP",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Magic: The Gathering Arena · #60 DC: Dark Legion",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-26"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-26"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-24.md", "json": "data/market-brief-20260924.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-09-23；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-06-26精确同口径TOP60基准，较老产品暂不判断飙升。",
        "", "## 1. 双榜当日异动产品", "",
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
        f"- 市场总览：全球手游消费者支出约${revenue['marketSummary']['globalConsumerSpendingUsd'] / 1_000_000_000:g}B，环比{revenue['marketSummary']['monthOverMonthPercent']:g}%，全市场同比约{revenue['marketSummary']['yearOverYearPercentApprox']:g}%",
        f"- 原始来源：[{revenue['source']}]({revenue['sourceUrl']})", "",
        "| 全球总榜 | 游戏 | 发行商 | 策略类型 | 较上月榜位 | 单品收入同比 |",
        "|---:|---|---|---|---|---|",
    ]
    for item in revenue["rankings"]:
        lines.append(f"| {item['rank']} | {item['gameName']} | {item['publisher']} | {item['strategyGenre']} | {item['movementLabel']} | {item['yoyRevenueLabel']} |")
    lines += ["", "### 策略产品与同比口径", ""] + [f"- {item}" for item in revenue["officialHighlights"]]
    lines += [
        "", revenue["methodologyNote"], "", "## 下载与来源", "",
        f"- JSON：`{value['downloads']['json']}`",
        f"- Sensor Tower上月对照：{revenue['previousPeriodSourceUrl']}",
        f"- Sensor Tower同比对照：{revenue['yearOverYearSourceUrl']}",
        "- Google Play直连源：https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US",
        "- Apple官方RSS：https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json", "",
    ]
    return "\n".join(lines)


base.save("data/market-brief-20260924.json", brief)
(base.ROOT / "reports/2026-09-24.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = base.load("reports/manifest.json")
entry = {
    "date": DATE,
    "title": brief["title"],
    "summary": brief["summary"],
    "markdown": brief["downloads"]["markdown"],
    "json": brief["downloads"]["json"],
}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
base.save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
