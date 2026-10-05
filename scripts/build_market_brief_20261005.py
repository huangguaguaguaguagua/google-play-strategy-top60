#!/usr/bin/env python3
"""Generate the Beijing 2026-10-05 market brief, local icons and archive entry."""

from datetime import datetime
from zoneinfo import ZoneInfo

import build_market_brief_20261002 as prior


p = prior.p
p.DATE, p.STAMP, p.CURRENT, p.PREVIOUS = "2026-10-05", "20261005", "20261005", "20261002"
p.datasets = {
    "googlePlay": {"now": p.load("data/games-20261005.json"), "prior": p.load("data/games-20261002.json"), "id": "packageName"},
    "ios": {"now": p.load("data/ios-games-20261005.json"), "prior": p.load("data/ios-games-20261002.json"), "id": "appId"},
}
p.google_history = p.load("data/history/google-play/2026-10-05.json")
p.ios_history = p.load("data/history/ios/2026-10-05.json")
p.global_strategy_revenue = p.load("data/sensortower-global-strategy-revenue-latest.json")
p.captured = datetime.fromisoformat(p.google_history["sourceCapturedAt"])
p.source_date = datetime.fromisoformat(p.ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    p.card("googlePlay", "Last Beacon", "entry", "首次进入项目Google榜#51。官方2.5.5版本仅披露服务器性能与稳定性优化，未发现足以解释入榜的重大内容节点；海洋末日生存4X先按首次入榜待验证信号处理。", first=True),
    p.card("googlePlay", "MARVEL SNAP", "entry", "回到Google #53，iOS同口径未进入TOP60；近期未核验到与本次回榜同日的重大官方节点，按卡牌产品的中后段回补记录。"),
    p.card("googlePlay", "Last Fortress", "entry", "回到Google #55，iOS仍在榜但处后段；成熟末日城建产品尚未脱离高掉榜风险，本次回榜不外推为长期改善。"),
    p.card("googlePlay", "Sea of Conquest", "entry", "回到Google #59，恰处倒数第二；iOS同口径未收录，海盗4X的末位回补需至少再留榜一个有效快照才能升级判断。"),
    p.card("googlePlay", "Kiss of War", "exit", "从Google上期#43掉榜，iOS同口径亦未进入TOP60；单次退出只说明本期低于截线，未发现可确认的重大生命周期转折。"),
    p.card("googlePlay", "Draft Showdown", "exit", "从Google上期#52掉榜；近期反复在后十名与榜外之间切换，当前仍是留榜不稳而非可确认的长期下行。"),
    p.card("googlePlay", "Ant Legion", "exit", "从Google上期#59掉榜，榜尾回补未延续；与The Ants升至#54形成同题材不同步，不能据此判断蚂蚁题材整体趋势。"),
    p.card("googlePlay", "Aliens vs Zombies", "exit", "从Google上期#60掉榜；前一有效快照恰处末位，本次退出符合榜尾高风险，但没有证据支持更强的运营归因。"),
    p.card("googlePlay", "The Grand Mafia", "up", "Google上升8位至#30，为本端最大上涨；iOS未进TOP60，先按Android端单日改善信号记录。"),
    p.card("googlePlay", "Frost & Flame", "up", "Google上升7位至#33；成熟4X回到中段，但没有可核验同日重大版本，不能把单日名次变化直接归因于活动。"),
    p.card("googlePlay", "Stormshot", "up", "Google上升7位至#37，由后15名回到中后段；iOS未收录，留榜改善仍局限于Android端。"),
    p.card("googlePlay", "Raid Rush", "up", "Google上升6位至#45；塔防产品仍在后16名，当前更接近风险缓解而非新的高位阶段。"),
    p.card("googlePlay", "Sea War", "down", "Google下跌20位至#56，iOS也下跌8位至#58，是本期最清晰的双端共同走弱信号；两端均贴近截线，但仍只按一个有效快照判断。"),
    p.card("googlePlay", "Duck Survival", "down", "Google下跌8位至#43；iOS未进入TOP60，当前由中段落入后18名，下一快照需核对是否继续回吐。"),
    p.card("googlePlay", "Rise of Castles", "down", "Google下跌7位至#22，仍稳居前25；iOS同口径未收录，单日回落尚未构成留榜风险。"),
    p.card("googlePlay", "Top War", "down", "Google下跌6位至#36，而iOS上升10位至#34，两端最终名次接近但方向完全相反，属于平台间短期分化。"),
]


ios_products = [
    p.card("ios", "Kingdom Guard", "entry", "回到iOS #41，Google为#57；9月下旬Fruit Market已结束，当前没有证据证明其驱动本次回榜，且两端仍都在中后段。"),
    p.card("ios", "Guns of Glory", "entry", "回到iOS #54，Google同口径未收录；9月23日版本仅披露界面与体验优化，不能据此解释本次榜尾回补。"),
    p.card("ios", "The Tower", "entry", "回到iOS #59。v29新增全局预设、Mythic锦标赛联赛、Vault重做和新卡牌/模组内容，但产品恰处倒数第二，仍按大版本后的榜尾待验证信号处理。"),
    p.card("ios", "Yu-Gi-Oh", "entry", "回到iOS #60且恰处末位；当前官方版本节点早于本次快照，未发现足以解释单日回榜的新增内容，掉榜风险最高。"),
    p.card("ios", "SD Gundam", "exit", "从iOS上期#27掉榜，跌幅跨越33位以上；前一版本只披露图标与标题画面更新，未发现能解释剧烈波动的重大系统节点。"),
    p.card("ios", "Limbus", "exit", "从iOS上期#32掉榜，Google反而升4位至#49；10月1日内容更新后的双端共同回榜没有延续为iPhone留榜，出现明显平台分化。"),
    p.card("ios", "Game of Thrones: Conquest", "exit", "从iOS上期#37掉榜，Google升2位至#52；成熟IP 4X本期由iPhone端退出而Android仍留在后段。"),
    p.card("ios", "Plants on Fire", "exit", "从iOS上期#60掉榜；产品上期仍属近90天新品且恰处末位，本次退出说明海盗赛季后的首发承接尚未形成连续留榜。"),
    p.card("ios", "Warhammer 40,000", "up", "iOS上升17位至#42。官方已排期10月4日Ûthar传奇活动与10月10日Terminus生存活动，时间上构成内容背景，但尚不能证明活动直接造成名次变化。"),
    p.card("ios", "Supremacy", "up", "iOS上升17位至#36；9月25日版本集中于坦克歼击车学说、动员平衡、无障碍与缺陷修复，当前先记为维护窗口内的单日改善。"),
    p.card("ios", "War and Order", "up", "iOS上升13位至#32，Google为#30且小幅上升；两端名次接近，是本期较清晰的共同在榜信号，但iOS大幅波动仍需复核。"),
    p.card("ios", "Warline", "up", "iOS上升11位至#40且仍属近90天新品；1.3版本的八服Eye of the Storm与新军备是近期内容背景，下一快照将检验首发期承接。"),
    p.card("ios", "Top War", "up", "iOS上升10位至#34，Google却下跌6位至#36；两端最终名次只差2位，但相反方向显示单日平台结构不同。"),
    p.card("ios", "Magic", "up", "iOS上升9位至#11，Reality Fracture版本仍在窗口内；从上期#20回到前12是明确反弹，但尚需下一快照区分版本峰值与稳定承接。"),
    p.card("ios", "Fire Emblem", "down", "iOS下跌18位至#51，为本端最大回落；9月版本围绕Fortune's Weave预热，当前已落入后十名，下一快照掉榜风险显著。"),
    p.card("ios", "Forge Master", "down", "iOS下跌13位至#47；9月版本新增Fairies、Clan Tech Race淘汰制与外观，当前回落到后14名但仍未到末位。"),
    p.card("ios", "Mobile Legends", "down", "iOS下跌11位至#24，Google策略榜未收录；产品属于MOBA分类边界，仍在前25，不把单日回落外推为长期趋势。"),
    p.card("ios", "Summoners War", "down", "iOS下跌9位至#35；成熟长线RPG由前30回到中段，未发现可确认的同日重大转折。"),
    p.card("ios", "Dragon Traveler", "down", "iOS下跌8位至#46，回吐上期跳升的一部分；当前已进入后15名，需核对是否继续向榜尾移动。"),
    p.card("ios", "Sea War", "down", "iOS下跌8位至#58，Google更大幅下跌20位至#56；双端同时贴近截线，是下一有效快照最需要验证的共同风险。"),
]


news = [
    {
        "category": "全球收入月榜", "date": "2026-10-01",
        "title": "Sensor Tower发布9月全球手游收入TOP10，策略子集增至3款",
        "summary": "官方完整图表显示Whiteout Survival全球总榜#6、Last War: Survival #7、Kingshot #9；全球App Store与Google Play消费者支出约61亿美元，排除第三方Android商店。",
        "impact": "Last War新进入全球TOP10，Whiteout与Kingshot较上月分别下降3位、2位；这些是总榜名次变化，不是单品收入同比。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
    {
        "category": "海洋生存4X / 新进榜", "date": "2026-09-30",
        "title": "Last Beacon首次进入项目Google榜，最新版本仅做稳定性优化",
        "summary": "Apple官方2.5.5版本说明只披露服务器性能与稳定性优化；Google商品页以灯塔庇护所、舰队探索、联盟和海上要塞为核心。",
        "impact": "产品本期首次进入Google #51，但缺少同日重大内容证据，应按首次入榜信号而非版本驱动结论处理。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6761043541",
    },
    {
        "category": "末日4X / 全球收入", "date": "2026-10-01",
        "title": "Last War首次进入Sensor Tower全球收入TOP10第7",
        "summary": "Sensor Tower 9月官方图表把Last War: Survival列为全球手游收入总榜#7，上月未进入TOP10；官方未披露单品同比百分比。",
        "impact": "其全球收入位置与美国双端持续前列共同说明长线规模，但不能由名次推算收入增幅。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
    {
        "category": "战术RPG / 活动", "date": "2026-10-04",
        "title": "Tacticus开启Ûthar传奇活动并预告Terminus生存活动",
        "summary": "Apple官方版本说明列出10月4日Ûthar传奇活动与10月10日Terminus生存活动，同时保留9月战斗通行证等内容。",
        "impact": "产品本期iOS +17至#42，活动提供可核验背景，但目前仍是中后段单日跃升。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1599937506",
    },
    {
        "category": "塔防长线 / 大版本", "date": "2026-09-25",
        "title": "The Tower v29大版本后回到iOS #59",
        "summary": "官方v29加入全局预设、Preset Lab、Mythic锦标赛联赛、Vault重做、新Harmony升级以及卡牌和模组内容。",
        "impact": "内容规模明确，但回榜仅处倒数第二；是否形成稳定承接要看下一有效快照。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1575590830",
    },
    {
        "category": "现代战争策略 / 平衡更新", "date": "2026-09-25",
        "title": "Supremacy更新学说与动员平衡后iOS升17位",
        "summary": "官方0.242版本调整Tank Destroyer学说、动员平衡、无障碍选项，并修复飞机、导弹、情报员和界面问题。",
        "impact": "产品本期升至iOS #36；维护更新与排名同处近期窗口，但仍不能确认直接因果。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1510997559",
    },
    {
        "category": "新品SLG / 跨服战", "date": "2026-09-16",
        "title": "Warline以八服Eye of the Storm承接首发期",
        "summary": "官方1.3版本加入八服Conquest、Stormbreaker目标、三件Signature Armaments、新徽章与联盟系统优化。",
        "impact": "产品仍属90天新品，本期iOS +11至#40；需继续观察能否稳定进入前40。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6742809194",
    },
    {
        "category": "卡牌 / 版本", "date": "2026-09-29",
        "title": "Magic Arena在Reality Fracture窗口回升至iOS #11",
        "summary": "官方2026.63.10版本推出Reality Fracture，并以每包成对回响卡和扭曲的熟悉策略为主要内容。",
        "impact": "本期+9接近前10；下一快照将区分新版本峰值与稳定付费承接。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1496227521",
    },
    {
        "category": "部落策略 / 月度活动", "date": "2026-10-01",
        "title": "Clash of Clans进入Cosmic Curse活动月",
        "summary": "Supercell官方确认10月1日至31日上线Portal Panic、Totem Thrower、Cosmic Curse奖章活动与Clan War League等内容。",
        "impact": "本期iOS由#1回落至#7、Google仍处前10；一个快照不能判断活动月的最终承接。",
        "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/news/cosmic-curse-portal-panic-teleports-in/",
    },
    {
        "category": "末日城建4X / 版本维护", "date": "2026-09-23",
        "title": "Last War版本优化任务展示并进入全球收入总榜#7",
        "summary": "Apple官方1.0.364版本优化Secret Mobile Squad补充任务的文字标识；Sensor Tower同期确认其9月全球收入总榜位置。",
        "impact": "版本本身属于体验优化，全球榜位不能归因于该改动；两项事实应分开理解。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6448786147",
    },
]


closing = [
    {
        "type": "判断", "title": "Google稳定、iOS中后段显著换位",
        "detail": "两端均四进四出；Google 56款共同产品中40款变动不超过2位，中位绝对变动2位，iOS仅21款不超过2位、中位绝对变动3位。Google前10保留9款，iOS前10全部保留，波动仍主要集中在中后段。",
    },
    {
        "type": "判断", "title": "Sea War是最清晰的双端共同风险",
        "detail": "Sea War在Google下跌20位至#56、iOS下跌8位至#58，两端同时进入后五名。Top War则相反：Google -6至#36、iOS +10至#34，最终名次相近但方向分化。",
    },
    {
        "type": "判断", "title": "全球策略头部由两款增至三款，但不是品类前三",
        "detail": "Sensor Tower 9月全球收入TOP10的策略子集为Whiteout #6、Last War #7、Kingshot #9；Last War新进入，另外两款总榜名次回落。单品同比均未公开，不从名次推算收入。",
    },
    {
        "type": "关注", "title": "下一有效快照：检验Last Beacon与三款Google回榜产品",
        "detail": "Last Beacon #51首次进入，MARVEL SNAP #53、Last Fortress #55、Sea of Conquest #59回榜；若不能连续留榜，应维持首次/榜尾回补判断。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：复核Sea War双端截线风险",
        "detail": "若Google与iOS任一端掉榜，说明本期共同回落已触及截线；若双端同时反弹至前50，再把今天视为短期波动。",
    },
    {
        "type": "关注", "title": "10月10日前后：核对Tacticus与The Tower活动承接",
        "detail": "Tacticus需在Terminus活动开启后继续留在iOS前45，The Tower需脱离后五名，才可把当前大幅上涨/回榜升级为连续内容承接。",
    },
]


all_products = google_products + ios_products
icons = p.build_market_icons(all_products)
p.google_new = sum(game["comparison90d"]["status"] == "new" for game in p.datasets["googlePlay"]["now"])
p.ios_new = sum(game["comparison90d"]["status"] == "new" for game in p.datasets["ios"]["now"])


brief = {
    "date": p.DATE,
    "timezone": "Asia/Shanghai",
    "title": "Last Beacon首次入榜，Sea War双端承压，Sensor Tower 9月策略子集增至3款",
    "summary": "较10月2日前一有效快照，Google Play四进四出：Last Beacon #51首次进入，MARVEL SNAP #53、Last Fortress #55、Sea of Conquest #59回榜，Kiss of War、Draft Showdown、Ant Legion、Aliens vs Zombies掉榜；The Grand Mafia +8至#30，King of Avalon与Stormshot均+7，Sea War -20至#56。iOS四进四出：Kingdom Guard #41、Guns of Glory #54、The Tower #59、Yu-Gi-Oh #60回榜，SD Gundam、Limbus、Game of Thrones: Conquest、Plants on Fire掉榜；Tacticus与Supremacy均+17，Fire Emblem -18。近90天新品为Google 2款、iOS 2款，较老产品因缺少7月7日精确基准不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261005.json",
    "rankingSources": {"googlePlay": "data/games-20261005.json", "ios": "data/ios-games-20261005.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261002.json", "ios": "data/ios-games-20261002.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {p.captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Game of Thrones: Dragonfire · #60 Last Shelter: Survival",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {p.source_date:%Y-%m-%d}（源更新：{p.ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Pokémon GO · #25 Top Force: Commander · #60 Yu-Gi-Oh! Master Duel",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": p.global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": p.google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-07"},
        "ios": {"top60": 60, "newRelease90d": p.ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-07"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": p.google_history["sourceUrl"], "capturedAt": p.google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": p.ios_history["sourceUrl"], "updated": p.ios_history["sourceUpdated"], "sourceDateBeijing": p.ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": p.global_strategy_revenue["sourceUrl"], "period": p.global_strategy_revenue["period"], "estimateAsOf": p.global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-05.md", "json": "data/market-brief-20261005.json"},
}


p.save("data/market-brief-20261005.json", brief)
markdown = p.build_markdown(brief).replace(
    "各自上一份最终有效快照为2026-09-28",
    "各自上一份最终有效快照为2026-10-02",
).replace(
    "两端均缺少2026-07-01精确同口径TOP60基准",
    "两端均缺少2026-07-07精确同口径TOP60基准",
)
(p.ROOT / "reports/2026-10-05.md").write_text(markdown, encoding="utf-8")
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
