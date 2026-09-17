#!/usr/bin/env python3
"""Generate the Beijing 2026-09-17 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-17"
STAMP = "20260917"
CURRENT = "20260917"
PREVIOUS = "20260916"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {
        "now": load(f"data/games-{CURRENT}.json"),
        "prior": load(f"data/games-{PREVIOUS}.json"),
        "id": "packageName",
    },
    "ios": {
        "now": load(f"data/ios-games-{CURRENT}.json"),
        "prior": load(f"data/ios-games-{PREVIOUS}.json"),
        "id": "appId",
    },
}


def product(game_name, product_id, store, tone, label, analysis):
    return {
        "gameName": game_name,
        "productId": product_id,
        "iconKey": f"{store}:{product_id}",
        "tone": tone,
        "changeLabel": label,
        "analysis": analysis,
    }


def card(store, prefix, tone, analysis, first=False):
    data = datasets[store]
    ident = data["id"]
    found = [row for row in data["now"] + data["prior"] if row["gameName"].startswith(prefix)]
    ids = {str(row[ident]) for row in found}
    if len(ids) != 1:
        raise RuntimeError(f"Ambiguous market card {store}:{prefix}: {ids}")
    product_id = ids.pop()
    current = next((row for row in data["now"] if str(row[ident]) == product_id), None)
    previous = next((row for row in data["prior"] if str(row[ident]) == product_id), None)
    if tone == "entry" and current and not previous:
        label = f"{'首次进入' if first else '回榜'} · #{current['rank']}"
    elif tone == "exit" and previous and not current:
        label = f"掉榜 · 上期#{previous['rank']}"
    elif tone in ("up", "down") and current and previous:
        change = previous["rank"] - current["rank"]
        if (change > 0) != (tone == "up"):
            raise RuntimeError(f"Incorrect direction {store}:{prefix}: {change}")
        label = f"{'+' if change > 0 else '−'}{abs(change)} · #{current['rank']}"
    else:
        raise RuntimeError(f"Incorrect membership for {store}:{prefix}:{tone}")
    return product((current or previous)["gameName"], product_id, store, tone, label, analysis)


def asset_icons(manifest_path):
    result = {}
    for filename in load(manifest_path)["files"]:
        result.update(load(f"assets/{filename}"))
    return result


def build_market_icons(products):
    local_assets = {
        "googlePlay": asset_icons("assets/manifest.json"),
        "ios": asset_icons("assets/ios-manifest.json"),
    }
    bundle = {}
    for item in products:
        store = item["iconKey"].split(":", 1)[0]
        product_id = item["productId"]
        data = datasets[store]
        game = next(
            (row for row in data["now"] + data["prior"] if str(row[data["id"]]) == str(product_id)),
            None,
        )
        if not game:
            raise RuntimeError(f"No game record for market icon: {item['iconKey']}")
        asset_rank = int(game["assetRank"])
        icon = local_assets[store].get(f"{asset_rank}_icon") or local_assets[store].get(f"{asset_rank:02d}_icon")
        if not icon or not icon.startswith("data:image/"):
            raise RuntimeError(f"No local icon for market card: {item['iconKey']}")
        bundle[item["iconKey"]] = icon
    if len(bundle) != len(products):
        raise RuntimeError("Duplicate market-card product keys")
    save(f"assets/market-icons-{STAMP}.json", bundle, compact=True)
    return bundle


google_history = load("data/history/google-play/2026-09-17.json")
ios_history = load("data/history/ios/2026-09-17.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Supremacy: World War 3", "entry", "9月8日、12日和今天三次在Google榜尾回归，本次为#58；iOS同时下滑6位至#47。连续进出说明Android端仍处边界波动，不能写成稳定回暖。"),
    card("googlePlay", "Age of Spirits", "entry", "Google Play美国区9月16日上架，次日首次进入本项目榜单#59，按本店released日期归类为近三个月新上榜。首发版本同步扩展七种语言、11级兵种和萨满伤势机制，仍处首发验证。", first=True),
    card("googlePlay", "Pokémon Champions", "exit", "上期Google #55后掉榜，iOS当前也不在策略TOP60；9月8日启用的新竞技规则未带来连续榜尾留存，仍不能据此判断产品整体收入趋势。"),
    card("googlePlay", "Game of Thrones: Conquest", "exit", "上期已降至Google #59，今天掉榜；iOS也下滑5位至#43。两端方向一致，但Google离榜仍只是一日边界信号。"),
    card("googlePlay", "Infinity Kingdom", "up", "Google升4位至#24，iOS小幅回落至#23；两端名次几乎重合并共同位于前半区，不过今天没有匹配幅度的官方活动证据。"),
    card("googlePlay", "Raid Rush", "up", "Google升3位至#50，iOS则大涨17位至#22；这是今日少数两端同向信号，但幅度明显集中在iPhone端，仍需下一快照确认。"),
    card("googlePlay", "League of Legends: Wild Rift", "down", "Google下滑5位至#45，iOS继续在榜外；7.2e平衡补丁是近期节点，但没有证据把名次变化直接归因于版本。"),
    card("googlePlay", "Last Shelter: Survival", "down", "Google下滑3位至#52，iOS仍在榜外；成熟产品重新靠近榜尾，当前未发现可确认的重大转折。"),
    card("googlePlay", "Sea War", "down", "Google下滑2位至#60，iOS也位于#60；同产品在两个商店同时压线，是今天最明确的共同掉榜风险，但仍需后续快照验证。"),
]


ios_products = [
    card("ios", "DC: Dark Legion", "entry", "回到iOS #46。9月9日版本加入Forge Breach联盟占点玩法，并有Beast Boy相关活动；节点与回榜相邻，但不足以确认因果。"),
    card("ios", "SimCity BuildIt", "entry", "回到iOS #49，Google策略榜未收录同产品；当前仅能确认成熟城建产品的单端回榜，未发现可确认的重大运营转折。"),
    card("ios", "MARVEL SNAP", "exit", "上期iOS #51后掉榜，Google反而小升至#55。9月15日57.x重做角色精通奖励并预告Draft回归，今天呈现跨端分化。"),
    card("ios", "Fire Emblem Heroes", "exit", "上期iOS #57后退出TOP60，Google没有同产品排名；处于典型榜尾风险位，暂不将单日离榜解释为长期衰退。"),
    card("ios", "Mobile Legends", "up", "由#49大涨35位至iOS #14，为今日最大升幅。9月16日版本上线十周年内容并开启S42赛季，时间相邻但仍需连续快照确认承接。"),
    card("ios", "Hearthstone", "up", "由#53升23位至#30。9月15日36.6更新提供新扩展预览卡、平衡调整与战棋Aberrations，是可核验节点；单日涨幅不等于长期趋势。"),
    card("ios", "Raid Rush", "up", "由#39升17位至#22，Google也升3位至#50；两端共同改善，但28位跨端差仍显示付费节奏集中在iPhone端。"),
    card("ios", "Pokémon GO", "up", "由#4升3位重回iOS榜首，Google策略榜无同产品；头部变化只代表当前快照，需要观察能否连续保持前三。"),
    card("ios", "The Tower", "down", "由#30跌11位至#41，回吐昨日19位涨幅的一部分；这种连续大幅反向波动更像短时峰值，尚不能确认稳定上行。"),
    card("ios", "Watcher of Realms", "down", "由#47跌11位至#58，直接进入掉榜区；Google没有同口径排名，先按iPhone端榜尾风险处理。"),
    card("ios", "Rise of Kingdoms", "down", "由#28跌8位至#36，Google对应《万国觉醒》仍在#5；成熟4X出现明显跨端差，不能用iOS单日回落概括产品整体。"),
    card("ios", "Dragon Traveler", "down", "由#40跌8位至#48，仍在上线初期的高波动阶段；Google策略榜未收录，暂按单端待验证信号。"),
    card("ios", "Warline", "down", "由#52跌7位至#59，仍按Apple本店7月22日上架日期归类为近三个月新上榜；Google #29，跨端相差30位且iOS已接近掉榜线。"),
    card("ios", "Game of Thrones: Conquest", "down", "iOS下滑5位至#43，Google则从#59掉榜；两端共同走弱但幅度不同，下一快照将检验是否只是短时回落。"),
]


news = [
    {"category": "新品 / 首发", "date": "2026-09-16", "title": "Age of Spirits美国区上架并扩展七种语言", "summary": "Google Play商品页显示产品以部落城建、萨满编队、世界地图与联盟4X为核心；首发更新加入七种语言、11级兵种和萨满伤势机制。", "impact": "该作今天首次进入Google策略畅销榜#59并按本店released日期计入近90天新品；后续留榜是首发验证重点。", "source": "Google Play官方商品页", "url": "https://play.google.com/store/apps/details?id=leyi.ageofspirits&hl=en_US&gl=US"},
    {"category": "赛季 / 周年", "date": "2026-09-16", "title": "Mobile Legends美国版上线十周年内容与S42赛季", "summary": "Apple官方版本说明列出Masha、Bruno重做及十周年内容；S42赛季于9月16日服务器时间开启，并提供赛季皮肤与头像框。", "impact": "产品今天iOS跃升35位至#14；版本与榜位时间相邻，但仍需后续快照验证持续性。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/mobile-legends-bang-bang-us/id6741568655"},
    {"category": "卡牌 / 版本", "date": "2026-09-15", "title": "Hearthstone 36.6加入新扩展预览卡与战棋异变", "summary": "Apple官方版本说明显示更新提供Reign of the Black Empire预览卡、构筑模式平衡调整与Battlegrounds Aberrations。", "impact": "产品今天iOS升23位至#30；更新是可核验运营节点，但不能把单日名次换算成版本收入贡献。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/hearthstone/id625257520"},
    {"category": "联盟玩法 / 版本", "date": "2026-09-09", "title": "DC: Dark Legion加入Forge Breach联盟占点玩法", "summary": "Apple版本说明显示联盟成员需要占领建筑、使用协议克制并摧毁核心；同期商品页也展示Beast Boy相关内容。", "impact": "产品今天回到iOS #46；活动节点提供解释线索，但单次回榜不足以确认增收。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/dc-dark-legion/id6479020757"},
    {"category": "版本 / 成长系统", "date": "2026-09-15", "title": "MARVEL SNAP 57.x重做角色精通奖励轨道", "summary": "官方更新加入Wild Boosters、Split Reroll Coins、额外Custom Card槽位与Level 27奖励，并预告Draft于9月28日回归。", "impact": "该作今天从iOS掉榜而Google升至#55，体现跨端分化；新系统应作为后续回流观察点。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/patch-notes-september-15-2026/"},
    {"category": "IP活动 / 长线运营", "date": "2026-09-09", "title": "Clash of Clans推出WWE Equipment Blast活动", "summary": "Supercell公布9月9日至22日的勋章活动，玩家通过多人战斗获取Tag Tickets、Champ Medals、临时兵种与装备奖励。", "impact": "CoC继续位于双端头部；活动可用于观察头部稳定性，但不能拆算其单独收入贡献。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/news/equipment-blast-medal-event/"},
    {"category": "版本 / 跨端", "date": "2026-09-09", "title": "Wild Rift 7.2e调整Vi、Swain及多件装备", "summary": "Riot削弱Vi、Swain，并增强Janna、Nautilus、Malphite等英雄，同时修改多件装备。", "impact": "该作今天Google降至#45且iOS仍在榜外；补丁只是背景，尚无官方材料证明与名次存在因果。", "source": "Riot Games官方", "url": "https://wildrift.leagueoflegends.com/en-us/news/game-updates/wild-rift-patch-notes-72e/"},
    {"category": "赛季 / 平衡", "date": "2026-09-08", "title": "Clash Royale九月平衡覆盖Hero Balloon与Freeze", "summary": "Supercell调整Hero Balloon、Freeze、Fireball及多张进化卡，并重做Hero Mega Minion等单位。", "impact": "Clash Royale仍处双端头部；平衡更新用于解释竞技环境变化，不应由排名换算收入。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/september-balance-changes-2026/"},
    {"category": "新品 / 联盟赛事", "date": "2026-09-10", "title": "Last Shelter: War Z开启四周制联盟决斗锦标赛", "summary": "Apple官方版本说明显示26.0902.001新增Alliance Duel Tournament，并以相近联盟实力进行四周匹配。", "impact": "该作今天Google #43、iOS榜外；同一运营节点没有形成双端同步信号。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/last-shelter-war-z/id6760406772"},
    {"category": "全球收入月榜", "date": "2026-09-04", "title": "Sensor Tower公布8月全球手游收入TOP10", "summary": "全球App Store与Google Play手游消费者支出估算约65.7亿美元，Whiteout Survival全球总榜#3、Kingshot #7。", "impact": "两款核心策略产品较7月各升1位；官方未公开单品收入同比，不能由名次换算收入百分比。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"},
]


closing = [
    {"type": "判断", "title": "iOS波动显著高于Google，榜首也再次易位", "detail": "两个商店均为两进两出，但58款共同在榜产品中，Google有49款日变动不超过2位、中位绝对变动1位；iOS只有33款不超过2位、中位绝对变动2位，并由Pokémon GO重回榜首。"},
    {"type": "判断", "title": "今日最强信号集中在iPhone版本节点", "detail": "Mobile Legends +35、Hearthstone +23与Raid Rush +17主导iOS波动；前两款恰逢可核验版本节点，Raid Rush也两端同升，但都只能视为待验证信号。"},
    {"type": "判断", "title": "新品进入榜尾，成熟产品跨端风险并存", "detail": "Age of Spirits美国区上架次日首次进入Google #59；Sea War双端同为#60，Game of Thrones: Conquest则Google掉榜且iOS下滑。新品首发与成熟产品边界风险同时出现。"},
    {"type": "关注", "title": "9月18—21日：验证Age of Spirits首发承接", "detail": "若Age of Spirits连续留榜并脱离后五名，再把它从首日进入升级为短期承接信号；若快速掉榜，则归档为首发榜尾脉冲。"},
    {"type": "关注", "title": "下一工作日：复核三组iOS大涨是否回吐", "detail": "Mobile Legends需保持前20、Hearthstone保持前40、Raid Rush保持前30；任何一款大幅反向回落都应继续按活动/版本附近的单日波动处理。"},
    {"type": "关注", "title": "截至9月22日：跟踪共同榜尾与活动窗口", "detail": "重点看Sea War能否守住任一商店、Supremacy是否再次退出Google，并在Clash of Clans WWE活动结束前复核头部稳定度。"},
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Age of Spirits首发入榜；iOS三款大涨、Pokémon GO重回榜首",
    "summary": "较9月16日有效快照，Google Play两进两出：Supremacy回榜#58、Age of Spirits首次进入#59，Pokémon Champions与Game of Thrones: Conquest掉榜；iOS同样两进两出，DC: Dark Legion与SimCity回榜，MARVEL SNAP与Fire Emblem掉榜。Mobile Legends +35、Hearthstone +23、Raid Rush +17主导iOS波动，Pokémon GO重回榜首。近90天新品Google 5款、iOS 2款；两端缺少6月19日精确基准，较老产品不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": f"data/games-{CURRENT}.json", "ios": f"data/ios-games-{CURRENT}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREVIOUS}.json", "ios": f"data/ios-games-{PREVIOUS}.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Lands of Jail · #60 Sea War: Uboat Raid", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）", "anchors": "榜单锚点：#1 Pokémon GO · #25 Magic: The Gathering Arena · #60 Sea War: Uboat Raid", "products": ios_products},
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-19"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-19"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-17.md", "json": "data/market-brief-20260917.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份有效快照为2026-09-16；升降为相邻工作日变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-06-19精确同口径TOP60基准，较老产品暂不判断飙升。", "",
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


save("data/market-brief-20260917.json", brief)
(ROOT / "reports/2026-09-17.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
