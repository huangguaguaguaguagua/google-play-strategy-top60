#!/usr/bin/env python3
"""Generate the Beijing 2026-09-11 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-11"
STAMP = "20260911"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


def product(game_name, product_id, store, tone, label, analysis):
    return {
        "gameName": game_name,
        "productId": product_id,
        "iconKey": f"{store}:{product_id}",
        "tone": tone,
        "changeLabel": label,
        "analysis": analysis,
    }


def asset_icons(manifest_path):
    result = {}
    for filename in load(manifest_path)["files"]:
        result.update(load(f"assets/{filename}"))
    return result


def build_market_icons(products):
    current = {
        "googlePlay": load("data/games-20260911.json"),
        "ios": load("data/ios-games-20260911.json"),
    }
    previous = {
        "googlePlay": load("data/games-20260910.json"),
        "ios": load("data/ios-games-20260910.json"),
    }
    id_fields = {"googlePlay": "packageName", "ios": "appId"}
    local_assets = {
        "googlePlay": asset_icons("assets/manifest.json"),
        "ios": asset_icons("assets/ios-manifest.json"),
    }
    bundle = {}
    for item in products:
        store = item["iconKey"].split(":", 1)[0]
        product_id = item["productId"]
        field = id_fields[store]
        games = current[store] + previous[store]
        game = next((row for row in games if str(row[field]) == str(product_id)), None)
        if not game:
            raise RuntimeError(f"No game record for market icon: {item['iconKey']}")
        icon = local_assets[store].get(f"{game['assetRank']}_icon")
        if not icon or not icon.startswith("data:image/"):
            raise RuntimeError(f"No local icon for market card: {item['iconKey']}")
        bundle[item["iconKey"]] = icon
    if len(bundle) != len(products):
        raise RuntimeError("Duplicate market-card product keys")
    save(f"assets/market-icons-{STAMP}.json", bundle, compact=True)
    return bundle


google_history = load("data/history/google-play/2026-09-11.json")
ios_history = load("data/history/ios/2026-09-11.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    product("Draft Showdown", "com.QuestLab.DraftWar", "googlePlay", "up", "+3 · #57", "Google从#60升至#57，但仍处后四名；iOS同期反向下降2位至#54。双端都在榜尾区且方向相反，暂只视为末段排序变化。"),
    product("Galaxy Defense: Fortress TD", "com.cyberjoy.galaxydefense", "googlePlay", "up", "+2 · #53", "Google升2位至#53，iOS却从#60掉榜。Android仍在后八名，今天体现的是跨端分化，而不是双端共同改善。"),
    product("Titan Rush", "com.ratinghope.gplay", "googlePlay", "down", "−2 · #55", "Google由#53降至#55，iOS仍未进入TOP60。该作刚在前一日回榜，目前继续停留在高风险榜尾，尚未形成稳定位置。"),
    product("Lordrush", "com.s01.global", "googlePlay", "down", "−1 · #18", "Google小降至#18，iOS维持#22；两端继续守住前25且都属于近90天新品。相比单日升降，连续双端高位是当前更有价值的信号。"),
    product("Last Fortress: Underground", "com.more.lastfortress.gp", "googlePlay", "down", "−1 · #60", "Google降至末位#60，iOS同时下降3位至#51。两端同向走弱且Android已压线，下一个工作日存在直接掉榜风险。"),
]


ios_products = [
    product("Watcher of Realms - US", "6741674823", "ios", "entry", "回榜 · #20", "离榜两个快照后直接回到iOS #20，是今天质量最高的回榜；Google同口径榜外。高位回归可能是单日付费峰值，需到下个工作日确认能否守住前30。"),
    product("League of Legends: Wild Rift", "1480616990", "ios", "entry", "回榜 · #26", "离榜一个快照后回到iOS #26，Google同期升1位至#40。两端重新同时在榜，但MOBA只是因商店分类标签进入策略榜，不能据此代表核心SLG市场扩大。"),
    product("Top Heroes: Kingdom Saga", "6450953550", "ios", "entry", "回榜 · #43", "离榜一个快照后回到iOS #43，Google同期位于#47。双端位置接近且均在中后段，今天首先确认榜内承接恢复，尚不能判断持续改善。"),
    product("Coop TD: Together", "6503702666", "ios", "entry", "首次进入 · #55", "2024年上线的合作塔防首次进入项目iOS榜，当前#55；Google同口径榜外。Android在9月10日更新Clara、Deep Sea与Demon Legion内容，但平台和日期不同，不能直接认定为iOS进榜原因。"),
    product("DC: Dark Legion™", "6479020757", "ios", "entry", "回榜 · #58", "自8月27日后再次进入iOS榜，仍为#58；Google同口径榜外。长时间离榜后的末段回归更接近单日脉冲，下一快照掉榜风险高。"),
    product("Age of Empires Mobile", "6476261995", "ios", "exit", "掉榜 · 上期#49", "iOS从#49掉榜，Google同期仍在#51。两端都处后段，今天先确认iPhone端退出；若Google也跌出，才构成双端共同转弱。"),
    product("Rise of Castles: Fire and War", "1411917616", "ios", "exit", "掉榜 · 上期#55", "iOS从#55掉榜，而Google版本仍位于#19。跨端相差至少42位，表明该成熟SLG当前美国Android承接明显强于iPhone。"),
    product("F1® Clash - Official 2026 Game", "1434561536", "ios", "exit", "掉榜 · 上期#56", "首次进入项目榜仅维持一个快照便退出，Google同口径榜外。9月赛道内容尚未形成可确认的持续榜位承接，本次按短时赛事/付费信号归档。"),
    product("Warline: Sniper Strike", "6742809194", "ios", "exit", "掉榜 · 上期#57", "iOS从#57退出，Google同期仍在#28。产品退出后iOS近90天新品数由3款降至2款，当前商业化位置明显偏向Android。"),
    product("Galaxy Defense: Fortress TD", "6740189002", "ios", "exit", "掉榜 · 上期#60", "昨日回到末位后立即退出，Google则升2位至#53。iOS榜尾回补只维持一个快照，Android也尚未脱离后十名。"),
    product("Dragon Traveler", "6751086804", "ios", "up", "+19 · #23", "iOS由#42升至#23，是今天最大涨幅；Google同口径榜外。单端一天跃升不能直接归因于活动或买量，先观察能否连续留在前30。"),
    product("PUBG MOBILE", "1330123889", "ios", "up", "+11 · #9", "iOS升11位进入前十；该作因Apple策略标签进入本榜，核心仍是战术射击。今天的高位反映产品付费变化，不应被写成SLG品类增长。"),
    product("Pokémon Champions", "6741503079", "ios", "down", "−14 · #33", "首次进榜次日由#19回落至#33，仍属于近90天新品且保持中段；Google同口径榜外。首日高位已有回吐，但尚未跌回榜尾。"),
    product("Warhammer 40,000: Tacticus ™", "1599937506", "ios", "down", "−14 · #59", "iOS由#45降至#59，Google同期位于#34。iPhone端已进入直接掉榜风险区，跨端差距扩大至25位。"),
    product("Sea War: Uboat Raid", "6447612873", "ios", "down", "−11 · #42", "iOS下降11位至#42，Google同期降1位至#59。两端同向回落，且Android已接近榜尾，是今天较清晰但仍待连续验证的共同风险信号。"),
    product("War and Order", "1071744151", "ios", "down", "−10 · #39", "iOS从#29回落至#39，Google维持#29。前一日的双端同名次没有延续，当前重新出现Android领先10位的分化。"),
]


news = [
    {"category": "版本 / 新进榜", "date": "2026-09-10", "title": "Coop TD更新Clara、Deep Sea与Demon Legion内容", "summary": "Google Play官方商品页显示9月10日更新，加入Clara Liberation、Deep Sea难度、Demon Legion城墙防守与新赛季皮肤奖励。", "impact": "该作今天首次进入iOS策略榜#55；Android更新与iOS榜位时间相邻，但跨平台差异意味着只能把它视为待验证线索。", "source": "Google Play官方商品页", "url": "https://play.google.com/store/apps/details?id=com.percent.aos.cooptd&hl=en_US&gl=US"},
    {"category": "全球月榜", "date": "2026-09-04（官方发布）", "title": "Sensor Tower发布8月全球手游收入TOP10", "summary": "全球手游消费者支出约65.7亿美元、环比下降1%；Honor of Kings居首，Whiteout Survival第3、Kingshot第7。", "impact": "两款核心策略产品较7月各升1位，并继续位于今日美国双端头部；官方未公开单品收入同比，页面不从名次补算百分比。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"},
    {"category": "新品 / 竞技生态", "date": "2026-09-06", "title": "Pokémon Champions移动端进入竞技生态观察期", "summary": "The Verge报道该作已支持跨平台对战，但区域级及以上官方赛事仍要求使用Switch；移动端目前主要扩展日常竞技入口。", "impact": "该作首进iOS #19后今天回落至#33，仍在新品窗口；赛事入口与移动端收入承接需分开观察。", "source": "The Verge", "url": "https://www.theverge.com/games/990691/competitive-pokemon-champions-mobile-tournament-accessibility"},
    {"category": "新赛季", "date": "2026-09-07", "title": "Clash Royale开启Minion Academy赛季", "summary": "官方公布Minion Giant新卡、Ice Wizard英雄、Album Event、2v2 League和Royale Shuffle等9月内容。", "impact": "Clash Royale今日Google #10、iOS #7，继续保持双端前十；节点与高位重合，但持续收入仍需首周后位置验证。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/new-season-minion-academy/"},
    {"category": "周年运营", "date": "2026-09-04", "title": "King of Avalon开启十周年整月活动", "summary": "9月4日至30日活动加入可收集Merlin、八个传奇地点、七件遗物、拼图、英雄与周年奖励。", "impact": "该作今日Google #44、iOS榜外；周年内容仍在进行，但当前没有形成双端同步高位。", "source": "FunPlus官方", "url": "https://funplus.com/king-of-avalon-celebrates-10th-anniversary/"},
    {"category": "区域趋势", "date": "2026-09（官方发布月）", "title": "Sensor Tower：日本4X策略收入同比增长9.4%", "summary": "日本近12个月手游IAP超100亿美元；报告称4X Strategy领跑细分收入并增长9.4%，Last War是主要支撑产品。", "impact": "成熟高付费市场仍能支撑4X增长，但这是日本区域口径，不能替代美国双榜或全球单品收入。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/state-of-japan-gaming-2026"},
    {"category": "版本 / 现实赛历", "date": "2026-09-01", "title": "F1 Clash Update 60加入Madring与后续活动内容", "summary": "Hutch官方说明Update 60新增Madring赛道、未来活动内容及多项修复，继续围绕真实F1赛历运营。", "impact": "F1 Clash昨天首次进入项目iOS榜、今天即退出；版本暂未形成可确认的持续榜位承接。", "source": "Hutch Games官方", "url": "https://www.hutch.io/our-games/f1-clash/patch-notes/"},
    {"category": "版本 / 榜外观察", "date": "2026-09-07", "title": "Forge of Empires发布1.343国际服版本", "summary": "版本调整Historical Allies与Stellar Age提示并修复多项移动端稳定性问题，计划9月9日全服更新。", "impact": "该作仍未回到Google TOP60；版本上线后尚未显示榜位承接，可继续作为版本—排名对照。", "source": "InnoGames官方", "url": "https://support.innogames.com/kb/ForgeOfEmpires/en_DK/6975/Update-to-version-1343"},
    {"category": "新赛季 / 双端", "date": "2026-08-31", "title": "MARVEL SNAP运营AXIS: Inversion赛季", "summary": "赛季包含新角色、地点、登录日历、Draft、Team Clash及网页商店季票奖励。", "impact": "今天Google #49、iOS #49，两个商店名次收敛且较昨日分别下降3位和5位；单日同向回落仍不能直接换算收入跌幅。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/new-season-axis-inversion/"},
    {"category": "版本更新", "date": "2026-08-30", "title": "Clash of Clans更新TH18宠物与Supercharge等级", "summary": "官方更新增加Diggy等级、Builder's Hut与Monolith强化，并调整回流、新手与部落战联赛体验。", "impact": "Clash of Clans今日Google #8、iOS #6，持续位于双端头部；版本效果仍应结合多日位置而非单一快照。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/release-notes/august-update-3/"},
]


closing = [
    {"type": "判断", "title": "Google成员稳定，iOS换榜集中释放", "detail": "Google连续两个快照保持同一批60款，最大位移仅3位；iOS同时出现5进5出，并包含Watcher of Realms #20与Wild Rift #26的中高位回榜。今天的主要市场波动来自iPhone端。"},
    {"type": "判断", "title": "iOS回榜质量提升，但新品数量反而下降", "detail": "Watcher of Realms和Wild Rift回到前30，Coop TD首次进入；与此同时Warline从#57掉榜，使iOS近90天新品由3款降至2款。进入数量增加不等于新品供给增强。"},
    {"type": "判断", "title": "全球月度收入头部稳定，日榜跨端分化仍强", "detail": "Sensor Tower 8月策略子集仍是Whiteout Survival #3与Kingshot #7；美国日榜中Rise of Castles、Warline、Galaxy Defense和Tacticus均出现明显跨端差异，不能用单平台名次替代全球收入判断。"},
    {"type": "关注", "title": "9月14日：验证三款iOS回榜与Coop TD首进", "detail": "Watcher of Realms若守住前30、Wild Rift与Top Heroes继续在榜、Coop TD脱离后十名，才把今天升级为持续信号；DC Dark Legion若仍停在#58附近则保持榜尾风险判断。"},
    {"type": "关注", "title": "9月14日：检查Pokémon Champions与Tacticus回落是否延续", "detail": "Pokémon Champions需确认能否守住中段，Tacticus需避免从#59掉榜；Dragon Traveler和PUBG的上涨也须至少维持一个工作日，才能排除单日峰值。"},
    {"type": "关注", "title": "截至9月16日：核对双端分化是否收敛", "detail": "重点跟踪Rise of Castles、Warline、Galaxy Defense、Sea War和Last Fortress；只有同向连续变化或版本证据出现时才升级结论，不把榜位变化换算为收入百分比。"},
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Google成员零换榜，Watcher of Realms回到iOS #20",
    "summary": "与9月10日快照相比，Google Play完整60款成员不变、最大位移仅3位；iOS由Watcher of Realms、Wild Rift、Top Heroes、Coop TD和DC Dark Legion进入/回榜，Age of Empires、Rise of Castles、F1 Clash、Warline和Galaxy Defense掉榜。Dragon Traveler +19、PUBG +11，Pokémon Champions与Tacticus均下降14位，iPhone端是今日波动中心。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": "data/games-20260911.json", "ios": "data/ios-games-20260911.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260910.json", "ios": "data/ios-games-20260910.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Lords Mobile x Transformers · #60 Last Fortress: Underground", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}", "anchors": "榜单锚点：#1 Kingshot · #25 Tiles Survive! · #60 Lands of Jail", "products": ios_products},
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": 5, "surge90d": 0, "baselineAvailable": False},
        "ios": {"top60": 60, "newRelease90d": 2, "surge90d": 0, "baselineAvailable": False},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-11.md", "json": "data/market-brief-20260911.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        "- Google锚点：#1 Kingshot · #25 Lords Mobile x Transformers · #60 Last Fortress: Underground",
        "- iOS锚点：#1 Kingshot · #25 Tiles Survive! · #60 Lands of Jail",
        "- 对比基准：各自上一份有效快照为2026-09-10；所有升降均为相邻工作日变化。",
        "- 近90天状态：Google新上榜5款、iOS新上榜2款；两端均缺少2026-06-13精确同口径TOP60基准，较老产品暂不判断飙升。", "",
        "## 1. 双榜当日异动产品", "",
    ]
    for store in ("googlePlay", "ios"):
        section = value["rankingDynamics"][store]
        lines += [f"### {section['label']}", "", f"{section['sourceTime']}。", ""]
        for item in section["products"]:
            lines += [f"#### {item['gameName']}｜{item['changeLabel']}", "", item["analysis"], ""]
    lines += ["## 2. 策略手游市场热点", "", value["newsMethod"], ""]
    for index, item in enumerate(value["marketNews"], 1):
        lines += [f"### {index}. [{item['title']}]({item['url']})", "", f"- 类别：{item['category']}｜发布日期：{item['date']}｜来源：{item['source']}", f"- 事实摘要：{item['summary']}", f"- 市场含义：{item['impact']}", ""]
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
        "| 全球总榜 | 游戏 | 发行商 | 策略类型 | 较上月榜位 | 单品收入同比 |", "|---:|---|---|---|---|---|",
    ]
    for item in revenue["rankings"]:
        lines.append(f"| {item['rank']} | {item['gameName']} | {item['publisher']} | {item['strategyGenre']} | {item['movementLabel']} | {item['yoyRevenueLabel']} |")
    lines += ["", "### 策略产品与同比口径", ""]
    lines += [f"- {item}" for item in revenue["officialHighlights"]]
    lines += ["", revenue["methodologyNote"], "", "## 下载与来源", "", f"- JSON：`{value['downloads']['json']}`", f"- Sensor Tower上月对照：{revenue['previousPeriodSourceUrl']}", f"- Sensor Tower同比对照：{revenue['yearOverYearSourceUrl']}", "- Google Play直连源：https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US", "- Apple官方RSS：https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json", ""]
    return "\n".join(lines)


save("data/market-brief-20260911.json", brief)
(ROOT / "reports/2026-09-11.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
