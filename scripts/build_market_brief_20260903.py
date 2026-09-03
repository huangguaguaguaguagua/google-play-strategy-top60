#!/usr/bin/env python3
"""Generate the Beijing 2026-09-03 market brief and archive entry."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-03"
STAMP = "20260903"


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


google_history = load("data/history/google-play/2026-09-03.json")
ios_history = load("data/history/ios/2026-09-03.json")
global_revenue = load("data/sensortower-global-revenue-top10-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))

google_products = [
    product("Arknights", "com.YoStarEN.Arknights", "googlePlay", "entry", "回榜 · #60", "8月20日最后一次在项目Google快照位于#48，之后持续榜外，本期压线回到#60；iOS当前未进入TOP60。官方8月曾开放故事集活动，但没有与9月3日回榜直接对应的已核验节点，因此只按成熟产品榜尾回补记录。"),
    product("Kiss of War: Dead Blood", "com.tap4fun.kissofwar.googleplay", "googlePlay", "exit", "掉榜 · 上期#59", "近三次Google快照由#58、#56回落到#59后本期掉榜，iOS也未进入TOP60。连续滑向榜尾后退出比单日噪声更值得警惕，但仍不足以判断长期收入下行。"),
    product("MARVEL SNAP", "com.nvsgames.snap", "googlePlay", "up", "+6 · #31", "Google连续第二个工作日上升6位，已由9月1日#43升至#31；iOS也由#35经#22升至#18。AXIS: Inversion赛季、季票和9月活动已于8月31日公布，双端连续上行提高了信号质量，但仍需赛季首周验证中枢。"),
    product("Age of Empires Mobile", "com.proximabeta.aoemobile", "googlePlay", "up", "+4 · #47", "Google由#51回升至#47，iOS同步由#39回升7位至#32，部分收复昨日跌幅。8月31日开始的Hero Reset仍在进行，节点与双端回补重合；当前只能确认活动窗口内付费位置恢复。"),
]

ios_products = [
    product("Last Fortress: Underground", "1540557475", "ios", "entry", "回榜 · #58", "本期以#58进入项目iOS TOP60；对应Google商品当前未进入同口径榜单。产品2021年上线，属于成熟产品回榜而非近90天新品；8月26日版本说明只有常规改进与修复，暂无证据确认具体回榜原因。"),
    product("Kingdom Clash：Medieval Defense", "1611722542", "ios", "exit", "掉榜 · 上期#56", "9月1日以#47回榜，随后降至#56并在本期退出，Google仍无对应TOP60排名。两次连续回落表明该轮回榜尚未形成稳定位置，先归为榜尾风险兑现。"),
    product("Watcher of Realms - US", "6741674823", "ios", "down", "−14 · #51", "由#37跌至#51，是本期iOS最大跌幅，并重新进入榜尾风险区；Google策略TOP60没有对应商品排名。未找到与9月2日完全对应的官方重大节点，单日降幅仍需下一次快照确认。"),
    product("Top War: Battle Game", "1479198816", "ios", "up", "+11 · #36", "iOS由#47升至#36，Google同时位于#29、变化不大。双端均在中段说明产品基本盘仍在，但今日的主要增量来自iPhone侧；没有可确认活动依据，暂按单端回补信号。"),
    product("Fire Emblem Heroes", "1181774280", "ios", "down", "−11 · #47", "由#36降至#47，9月1日以#31回榜后的高位已连续回吐；Google策略榜无对应排名。短期形态更像成熟角色产品的付费峰值消退，原因仍需结合卡池周期验证。"),
    product("Forge Master – Idle RPG", "6746636289", "ios", "up", "+10 · #35", "由#45升至#35，Google也位于#48。产品在8月27日曾上冲iOS #22后回落，本次再次反弹，显示波动仍大；尚不能认定建立新的稳定区间。"),
    product("Evo Defense", "6755173751", "ios", "up", "+9 · #43", "由#52回升至#43，Google仍无对应TOP60。产品仍处上线早期，本次上行是值得继续验证的单端信号，但缺少公开活动证据，不能直接归因为新增买量或版本。"),
    product("Age of Empires Mobile", "6476261995", "ios", "up", "+7 · #32", "iOS由#39回升至#32，Google也由#51升至#47；Hero Reset活动窗口与双端同步回补重合。由于两端仅收复昨日部分跌幅，暂不把它写成长期反转。"),
    product("The Tower - Idle Tower Defense", "1575590830", "ios", "down", "−7 · #40", "昨日由#59跃升至#33后，本期回吐7位至#40；Google策略榜没有对应排名。仍明显高于9月1日位置，但单日峰值已经降温，需观察能否守住TOP40附近。"),
    product("Overgeared Hero: Merge RPG", "6755585789", "ios", "down", "−6 · #60", "iOS降至最后一名，Google则位于#39，跨端差距扩大到21位。iPhone侧已进入直接掉榜风险，Android仍有中段承接；下一次快照可判断是否只是平台付费节奏差异。"),
]

news = [
    {"category": "IP联动", "date": "2026-09-01", "title": "Clash of Clans开启WWE“Search for Cena”整月活动", "summary": "官方列出9月1—30日限定WWE英雄皮肤与场景、John Cena挑战、临时兵种、部落冲刺和多段资源/装备活动。", "impact": "Clash of Clans当前iOS #2、Google #7，双端高位与活动首周重合；限定外观、部落玩法和战斗事件的贡献仍需拆分。", "source": "Supercell / Clash of Clans官方", "url": "https://supercell.com/en/games/clashofclans/blog/news/wwe-search-for-cena-steps-into-the-ring/"},
    {"category": "新赛季", "date": "2026-08-31", "title": "MARVEL SNAP发布AXIS: Inversion赛季", "summary": "新赛季加入季票角色、两处新地点、21日登录日历、Draft、Team Clash和多段9月活动。", "impact": "产品Google连续两日+6至#31，iOS继续升至#18；这是当前最清晰的双端活动窗口信号之一，赛季首周持续性比单日峰值更重要。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/new-season-axis-inversion/"},
    {"category": "皮肤与会员", "date": "2026-09-01", "title": "Mobile Legends美国版上线9月StarLight", "summary": "北美官方账号确认Hanzo“Fangs of Slaughter”专属皮肤与StarLight会员权益开放。", "impact": "美国iOS版当前保持#13，昨日跃升后的高位尚未回吐；需继续区分皮肤首周付费与长期排名变化。", "source": "Mobile Legends: Bang Bang北美官方", "url": "https://www.facebook.com/MobileLegendsNorthAmerica/posts/september-starlight-is-officially-available-for-only-300-diamonds-you-can-get-th/1079137584518950/"},
    {"category": "活动复盘", "date": "2026-08-31", "title": "Age of Empires Mobile的Hero Reset进入活动中段", "summary": "官方Hero Reset活动从8月31日开始并持续7天，允许部分服务器重置英雄等级、技能与天赋并返还材料。", "impact": "产品本期Google +4、iOS +7，双端同步收复昨日跌幅；只有活动结束后仍守住区间，才能判断是否形成更稳定的付费中枢。", "source": "Age of Empires Mobile官方", "url": "https://www.facebook.com/aoemobile/"},
    {"category": "长线回榜", "date": "2026-08-26", "title": "Last Fortress常规版本后回到iOS策略TOP60", "summary": "Apple商品页显示8月26日更新仅标注常规改进与修复；产品本期以#58进入iOS榜。", "impact": "缺少重大版本或活动证据时，应把它视为成熟产品的榜尾回补，不将单日进入误写成内容驱动增长。", "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id1540557475"},
    {"category": "IP联动", "date": "2026-08-28", "title": "State of Survival推进《如龙8》联动", "summary": "FunPlus公布春日一番、桐生一马和真岛吾朗英雄，以及联盟Boss、节奏挑战、感染摩托和排行榜活动。", "impact": "产品当前Google #42、iOS仍未进榜，暂未出现双端同步抬升；完整活动周期比首日排名更能验证联动贡献。", "source": "FunPlus官方", "url": "https://funplus.com/state-of-survival-x-like-a-dragon-infinite-wealth-crossover-event/"},
    {"category": "版本运营", "date": "2026-08-25", "title": "GFL2的Chiral Redundancy版本继续维持Android高位", "summary": "官方公告列出OTs-14、Nemesis: Gnosis、限时剧情和Tile Transformation等内容。", "impact": "产品当前Google保持#13，iOS仍在榜外；版本后的Android承接持续，而iPhone侧暂无同步信号。", "source": "GIRLS' FRONTLINE 2官方", "url": "https://gf2exilium.sunborngame.com/NewsInfo?id=393&typeId=3"},
    {"category": "报道 / 软启动", "date": "2026-08-31", "title": "报道：腾讯Level Infinite测试Crownstone Survival", "summary": "Mobilegamer.biz援引AppMagic称该生存新游拟在菲律宾、法国、印尼、土耳其和美国Google Play软启动；具体范围仍可能变化。", "impact": "腾讯继续测试生存经营赛道，若美国测试开放，可对照Last War、Kingshot等产品的轻玩法入口与4X承接。", "source": "Mobilegamer.biz（报道）", "url": "https://mobilegamer.biz/the-soft-launch-games-you-need-to-know-about/"},
    {"category": "报道 / 新品测试", "date": "2026-08-31", "title": "报道：Century Games准备Frozen Manor: Merge Mystery早期测试", "summary": "报道援引AppMagic称，Whiteout Survival厂商Century Games出现新的Android合成产品页面，目前尚未记录Google Play下载。", "impact": "若测试推进，将检验点点互动是否把冰雪题材从4X生存延伸到合成经营；当前尚处无下载早期阶段。", "source": "Mobilegamer.biz（报道）", "url": "https://mobilegamer.biz/the-soft-launch-games-you-need-to-know-about/"},
    {"category": "报道 / 塔防测试", "date": "2026-08-31", "title": "报道：Small Giant在菲律宾软启动Defend the Castle", "summary": "报道援引AppMagic称，Zynga旗下Small Giant在菲律宾Google Play测试一款卡牌收集塔防产品。", "impact": "卡牌收集与塔防融合继续成为策略新品测试方向，可与Kingshot、Raid Rush等不同深度的塔防获量和长期养成结构对照。", "source": "Mobilegamer.biz（报道）", "url": "https://mobilegamer.biz/the-soft-launch-games-you-need-to-know-about/"},
]

closing = [
    {"type": "判断", "title": "两端换榜均收敛为一进一出，但iOS中后段波动仍大", "detail": "Google只有Arknights回榜、Kiss of War掉榜；iOS只有Last Fortress进入、Kingdom Clash退出。不过iOS同时出现Watcher of Realms -14、Top War +11、Fire Emblem -11和Forge Master +10，榜面稳定度仍低于Google。"},
    {"type": "判断", "title": "MARVEL SNAP的赛季信号已从单日异动延伸为双端连续上行", "detail": "Google两天累计由#43升至#31，iOS由#35升至#18；官方AXIS: Inversion季票、登录日历和多段活动提供同期节点。当前可以确认连续上行，仍不能把全部变化拆解为单一内容贡献。"},
    {"type": "判断", "title": "全球月榜与美国日榜共同显示头部策略产品的强承接", "detail": "Sensor Tower 7月全球收入榜中Whiteout Survival第4、Kingshot第8；当前两款分别位于Google #2/#1和iOS #4/#3。月度全球表现与美国双端高位相互印证，但统计周期和地域不同，不做金额换算。"},
    {"type": "关注", "title": "截至9月4日：验证Arknights与Last Fortress的首个留榜结果", "detail": "两款都只在各自新进入商店位于#58—60；若下一快照仍在榜并脱离最后三名，才提高回榜信号权重，否则继续按榜尾换防处理。"},
    {"type": "关注", "title": "9月4—7日：跟踪MARVEL SNAP与Age of Empires活动窗口", "detail": "检查MARVEL SNAP能否保持iOS TOP20、Google TOP35，以及Age of Empires能否守住iOS TOP35、Google TOP50；满足条件再判断赛季/重置活动形成短期中枢。"},
    {"type": "关注", "title": "Sensor Tower下一期发布时：核对策略产品全球位次是否换挡", "detail": "工作日只检查官方月榜一次；待8月全球收入榜正式发布后，重点核对Kingshot、Whiteout Survival及其他策略产品的完整TOP10位次与官方升降方向，不提前推算。"},
]

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "MARVEL SNAP双端连续上行；两端换榜收敛但iOS中段仍高波动",
    "summary": "与9月2日相比，两端均只有一进一出：Google Play的Arknights回榜#60、Kiss of War掉榜；iOS的Last Fortress回榜#58、Kingdom Clash掉榜。MARVEL SNAP继续双端上升，Age of Empires也同步回补；iOS中段则同时出现多组9—14位涨跌。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": "data/games-20260903.json", "ios": "data/ios-games-20260903.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260902.json", "ios": "data/ios-games-20260902.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Duck Survival · #60 Arknights", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}", "anchors": "榜单锚点：#1 Pokémon GO · #25 Puzzles & Survival · #60 Overgeared Hero", "products": ios_products},
    },
    "marketNews": news,
    "closing": closing,
    "globalRevenueTop10": global_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": 6, "surge90d": 0, "baselineAvailable": False},
        "ios": {"top60": 60, "newRelease90d": 2, "surge90d": 0, "baselineAvailable": False},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球手游月收入TOP10", "url": global_revenue["sourceUrl"], "period": global_revenue["period"], "estimateAsOf": global_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-03.md", "json": "data/market-brief-20260903.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        "- Google锚点：#1 Kingshot · #25 Duck Survival · #60 Arknights",
        "- iOS锚点：#1 Pokémon GO · #25 Puzzles & Survival · #60 Overgeared Hero",
        "- 对比基准：各自上一份有效快照为2026-09-02。",
        "- 近90天状态：Google新上榜6款、iOS新上榜2款；两端均缺少2026-06-05精确同口径TOP60基准，较老产品暂不判断飙升。", "",
        "## 1. 双榜当日异动产品", "",
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
    revenue = value["globalRevenueTop10"]
    lines += [
        "## 4. Sensor Tower 全球手游月收入 TOP10", "",
        f"- 数据期：{revenue['periodLabel']}｜官方页面：{revenue['publicationLabel']}｜估算截至：{revenue['estimateAsOf']}",
        f"- 口径：{revenue['scope']['region']}｜{revenue['scope']['stores']}｜{revenue['scope']['exclusions']}",
        f"- 市场总览：全球手游消费者支出约${revenue['marketSummary']['globalConsumerSpendingUsd'] / 1_000_000_000:g}B，环比+{revenue['marketSummary']['monthOverMonthPercent']:g}%",
        f"- 原始来源：[{revenue['source']}]({revenue['sourceUrl']})", "",
        "| 排名 | 游戏 | 发行商 | 较上期 |", "|---:|---|---|---|",
    ]
    for item in revenue["rankings"]:
        lines.append(f"| {item['rank']} | {item['gameName']} | {item['publisher']} | {item['movementLabel']} |")
    lines += ["", "### 本期官方解读", ""]
    lines += [f"- {item}" for item in revenue["officialHighlights"]]
    lines += ["", revenue["methodologyNote"], "", "## 下载与来源", "", f"- JSON：`{value['downloads']['json']}`", "- Google Play直连源：https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US", "- Apple官方RSS：https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json", ""]
    return "\n".join(lines)


save("data/market-brief-20260903.json", brief)
(ROOT / "reports/2026-09-03.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(google_products) + len(ios_products)} product cards and {len(news)} news items")
