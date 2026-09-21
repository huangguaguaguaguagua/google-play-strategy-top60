#!/usr/bin/env python3
"""Generate the Beijing 2026-09-21 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, CURRENT, PREVIOUS = "2026-09-21", "20260921", "20260921", "20260918"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load(f"data/games-{CURRENT}.json"), "prior": load(f"data/games-{PREVIOUS}.json"), "id": "packageName"},
    "ios": {"now": load(f"data/ios-games-{CURRENT}.json"), "prior": load(f"data/ios-games-{PREVIOUS}.json"), "id": "appId"},
}


def product(game_name, product_id, store, tone, label, analysis):
    return {"gameName": game_name, "productId": product_id, "iconKey": f"{store}:{product_id}", "tone": tone, "changeLabel": label, "analysis": analysis}


def card(store, prefix, tone, analysis, first=False):
    data, ident = datasets[store], datasets[store]["id"]
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
    local = {"googlePlay": asset_icons("assets/manifest.json"), "ios": asset_icons("assets/ios-manifest.json")}
    bundle = {}
    for item in products:
        store, product_id = item["iconKey"].split(":", 1)
        data = datasets[store]
        game = next((row for row in data["now"] + data["prior"] if str(row[data["id"]]) == product_id), None)
        if not game:
            raise RuntimeError(f"No game record for {item['iconKey']}")
        rank = int(game["assetRank"])
        icon = local[store].get(f"{rank}_icon") or local[store].get(f"{rank:02d}_icon")
        if not icon or not icon.startswith("data:image/"):
            raise RuntimeError(f"No local icon for {item['iconKey']}")
        bundle[item["iconKey"]] = icon
    if len(bundle) != len(products):
        raise RuntimeError("Duplicate market-card product keys")
    save(f"assets/market-icons-{STAMP}.json", bundle, compact=True)
    return bundle


google_history = load("data/history/google-play/2026-09-21.json")
ios_history = load("data/history/ios/2026-09-21.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Last Fortress", "entry", "回到Google #47；iOS今天未进榜。成熟城建生存产品重新越过榜尾线，但没有与本次回榜直接对应的公开版本节点，先按单端待验证信号处理。"),
    card("googlePlay", "Game of Thrones: Conquest", "entry", "回到Google #49，iOS同口径未收录。Apple 9月14日版本仍在推进House of the Dragon第三季相关活动，但当前只能确认Android榜尾回归，不能把活动写成确定原因。"),
    card("googlePlay", "DC: Dark Legion", "entry", "首次进入项目Google榜#51，iOS也回榜#55。9月18日官方版本加入Echoes of the Batcave弹珠主题活动；双端同步进入与节点相邻，但仍需下一快照验证持续性。", first=True),
    card("googlePlay", "Doomsday:The Seven Deadly Sins", "entry", "回到Google #59，仍在掉榜线附近；iOS未进入。没有发现可确认的当天重大转折，暂按联动产品的榜尾回归信号记录。"),
    card("googlePlay", "League of Legends: Wild Rift", "exit", "上期Google #51后掉榜，iOS策略榜也未收录；成熟MOBA在Google策略分类边界退出，不能据此推断整体收入下滑。"),
    card("googlePlay", "Draft Showdown", "exit", "上期Google #58后掉榜，iOS也不在榜；连续位于榜尾后退出，当前可确认的是边界承接不足，尚无公开节点可解释。"),
    card("googlePlay", "Supremacy: World War 3", "exit", "上期Google #59后掉榜，iOS同样未在榜；成熟战争策略失去双端TOP60位置，下一次回榜前不把单次退出外推为长期衰退。"),
    card("googlePlay", "Aliens vs Zombies", "exit", "上期首次进入Google #60后退出；单机塔防的Boss活动附近只形成一次榜尾记录，尚未建立连续留榜。"),
    card("googlePlay", "GIRLS' FRONTLINE 2", "up", "Google升12位至#16，成为Android最大涨幅；iOS却从上期#31掉榜。两端方向相反，当前更像平台付费节奏分化而非统一增长。"),
    card("googlePlay", "Limbus Company", "up", "Google升10位至#33，iOS则从上期#16掉榜。Season 8节点仍是背景，但两端反向幅度较大，不能继续沿用上期的“双端共振”判断。"),
    card("googlePlay", "Raid Rush", "up", "Google升6位至#43，iOS却跌6位至#34。塔防产品在两端交换强弱，今天没有共同版本依据支持整体走强。"),
    card("googlePlay", "Top Force", "up", "Google升5位至#27，iOS当前未入榜；7月31日美国区上架，仍按近90天新品计算，当前是Android单端中段改善。"),
    card("googlePlay", "Age of Empires Mobile", "down", "Google跌14位至#55，iOS也跌10位至#60；两端同步进入危险区，是今天最明确的共同回落信号，但单日排名不能直接等同收入长期下降。"),
    card("googlePlay", "Lords Mobile", "down", "Google跌7位至#37，但iOS回榜#53。Transformers联动仍在商品页展示，跨端一降一进说明活动承接并不一致。"),
    card("googlePlay", "Age of Origins", "down", "Google跌6位至#26，仍在前30；iOS未进榜。当前只是Android单日回调，未发现可确认的重大运营转折。"),
    card("googlePlay", "Top Heroes", "down", "Google跌6位至#32，iOS也跌10位至#59。两端同向回落且iPhone接近掉榜线，需优先复核是否只是周末后支付节奏回落。"),
]


ios_products = [
    card("ios", "Fire Emblem Heroes", "entry", "回到iOS #51，Google策略榜未收录。任天堂长线角色策略RPG再次越过榜尾线，但没有与今天直接对应的公开版本证据，先按成熟产品回榜处理。"),
    card("ios", "Lords Mobile", "entry", "回到iOS #53，Google则跌7位至#37。Transformers联动背景相同但两端方向不同，不能合并判断为整体增长。"),
    card("ios", "DC: Dark Legion", "entry", "回到iOS #55，并首次进入Google #51。9月18日Echoes of the Batcave弹珠主题活动与双端进入时间相邻，是可继续验证的活动窗口信号。"),
    card("ios", "Guns of Glory", "entry", "回到iOS #56，Google未入榜；位置仍在后五名，当前更接近成熟SLG的单端榜尾回归而非趋势反转。"),
    card("ios", "Last Day on Earth", "entry", "回到iOS #57；9月16日版本重做Crooked Creek Farm并加入金币复活，但榜位仍处危险区，版本承接尚未稳定。"),
    card("ios", "Limbus Company", "exit", "上期iOS #16后掉榜，Google反而升10位至#33。Season 8后的付费峰值没有在iPhone端延续，双端共振已转为平台分化。"),
    card("ios", "GIRLS' FRONTLINE 2", "exit", "上期iOS #31后掉榜，Google同时升12位至#16；与Limbus相似，今天的改善集中在Android端。"),
    card("ios", "Cell Survivor", "exit", "上期iOS #53后掉榜，Google策略榜未收录；新品/小体量产品在榜尾未形成连续承接，暂无证据判断具体原因。"),
    card("ios", "Mafia City", "exit", "上期iOS #59后掉榜，Google仍在#48。Beers without Borders更新未在iPhone端形成连续留榜，但Android仍守住中后段。"),
    card("ios", "Rise of Castles", "exit", "上期iOS #60后掉榜，Google未入榜；成熟4X从边界退出，今天没有可核验的新节点。"),
    card("ios", "The Battle Cats", "up", "iOS大涨35位至#22，为今日双榜最大升幅。9月14日15.6.0加入震动反馈、新True/Ultra Forms与关卡内容；版本时间相邻，但幅度仍需下一快照复核。"),
    card("ios", "Puzzles & Survival", "up", "iOS升11位至#15，Google也在#9且小涨1位。9月12日版本加入Azure Planet外观与圣地外观升级，是双端头部稳定中的可核验运营背景。"),
    card("ios", "Watcher of Realms", "up", "iOS升9位至#37，Google未进策略榜；离开榜尾但仍属单端波动，尚无公开节点支持长期判断。"),
    card("ios", "Warhammer 40,000: Tacticus", "up", "iOS升9位至#46，Google却跌5位至#40。两端名次接近但方向相反，今天没有共同活动依据。"),
    card("ios", "Warline", "up", "iOS升7位至#47，Google持平#31。Apple本店7月22日上架，继续按近90天新品计算；Eye of the Storm八服战仍在承接观察期。"),
    card("ios", "Age of Empires Mobile", "down", "iOS跌10位至#60，Google也跌14位至#55；两端同步触及掉榜区，是下一工作日最需要复核的共同风险。"),
    card("ios", "Top Heroes", "down", "iOS跌10位至#59，Google也跌6位至#32；双端同向回落，但只有iPhone已逼近掉榜线。"),
    card("ios", "Star Wars", "down", "iOS跌9位至#23；9月15日版本仅披露后台优化与性能改进，没有证据把排名回落归因于版本。"),
    card("ios", "Game of Thrones: Dragonfire", "down", "iOS跌7位至#18，Google同产品#14且小涨1位；双端仍在前20，但方向分化，不构成共同转弱。"),
]


news = [
    {"category": "活动 / 双端回榜", "date": "2026-09-18", "title": "DC: Dark Legion上线Echoes of the Batcave主题活动", "summary": "Apple官方2.2.25版本说明显示，蝙蝠洞操作界面改为复古弹珠机，并加入Drop Target Drills、Bat-Coins与活动商店。", "impact": "产品今天首次进入Google #51并回到iOS #55；活动与双端进入时间相邻，但仍需连续快照确认承接。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/dc-dark-legion/id6479020757"},
    {"category": "经营 / 跨州迁移", "date": "2026-09-20", "title": "Police Chief加入Interstate Reassignment与Oktoberfest", "summary": "0.1.47开放州际重新分配，为部分州提供Reassignment Orders，并上线Oktoberfest和三名英雄专属武器。", "impact": "iOS升7位至#25，而Google跌4位至#22；版本节点明确，但两端方向不同，需观察迁移玩法是否形成持续付费。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/police-chief/id6757350661"},
    {"category": "塔防 / 版本", "date": "2026-09-14", "title": "The Battle Cats 15.6.0扩充形态、天赋与关卡", "summary": "官方版本说明加入战斗震动反馈、新True/Ultra Forms、Talents、Legend Map难度、Rank奖励与CatCombos。", "impact": "产品今天在iOS大涨35位至#22，是最强单端异动；仍需排除版本窗口的一次性峰值。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/the-battle-cats/id850057092"},
    {"category": "SLG / 外观系统", "date": "2026-09-12", "title": "Puzzles & Survival开放圣地外观升级", "summary": "4.0.240加入Azure Planet外观、圣地外观升级，以及Pet Gallery额外属性与激活奖励。", "impact": "产品iOS升11位至#15、Google #9；双端都在头部，但不能由名次拆分外观系统的单独收入贡献。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/puzzles-survival/id1517980891"},
    {"category": "4X / 自动攻城", "date": "2026-09-17", "title": "Top Lords加入Scheduled Auto-Siege", "summary": "1.0.38增加预约自动攻城、战前阵容快速升级与批量祝贺功能。", "impact": "Google升5位至#29，iOS回落3位至#27；两端仍在中段但方向分化。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/top-lords/id6767834940"},
    {"category": "城建生存 / 宠物", "date": "2026-09-17", "title": "Tiles Survive推出完整Pet System", "summary": "2.6.100加入宠物蛋、孵化养成、外观互动、全英雄属性加成与队伍支援。", "impact": "今天Google #24、iOS #28但两端均回落；新品类系统尚未在当前快照体现共同上升。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/tiles-survive/id6738109752"},
    {"category": "太空SLG / 赛季测试", "date": "2026-09-16", "title": "Foundation测试S2 The Usurper与Combat Lab", "summary": "1.1.153在部分服务器测试S2，预告Shared Moonlight特别行动，并加入Combat Lab地面战斗活动。", "impact": "Google升5位至#28、iOS小升至#33；双端同在中段，是可继续验证的版本承接信号。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/foundation-galactic-frontier/id6737595599"},
    {"category": "新品 / 跨服战", "date": "2026-09-16", "title": "Warline 1.3.0推进Eye of the Storm八服战", "summary": "版本加入Pulse Resist、Stormbreaker争夺、三件Signature Armaments、Insignia奖励与Conquest Trucks。", "impact": "iOS升7位至#47、Google持平#31；本店7月22日上架，仍处近90天新品的版本验证期。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/warline-sniper-strike/id6742809194"},
    {"category": "卡牌策略 / 新卡", "date": "2026-09-14", "title": "Clash Royale加入Minion Giant与新Hero", "summary": "16.402.12的Back to Battle更新加入Minion Giant胜利条件、新Hero及赛季内容。", "impact": "产品iOS #8、Google #13，双端头部稳定；更新可解释内容节奏，但不用于推算单卡收入。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/clash-royale/id1053012308"},
    {"category": "全球收入月榜", "date": "2026-09-04", "title": "Sensor Tower最新官方月榜仍为2026年8月", "summary": "全球App Store与Google Play手游消费者支出估算约65.7亿美元；Whiteout Survival全球总榜#3、Kingshot #7，均较7月升1位。", "impact": "两款命中核心策略口径；官方未披露单品收入同比，不能由榜位变化换算收入增幅。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"},
]


closing = [
    {"type": "判断", "title": "周末后iOS中后段轮换仍强于Google", "detail": "Google四进四出，56款共同产品中28款变动不超过2位，中位绝对变动2.5位；iOS五进五出，55款共同产品中22款不超过2位，中位绝对变动3位。两端前10均全部留存，但中后段换位明显。"},
    {"type": "判断", "title": "DC形成双端活动窗口信号，Limbus与GFL2转为Android单端改善", "detail": "DC首次进入Google #51并回到iOS #55，紧邻9月18日Batcave活动；与此同时Limbus和GFL2分别升至Google #33与#16，却从iOS掉榜，说明上期双端共振没有延续。"},
    {"type": "判断", "title": "Age of Empires与Top Heroes出现共同回落", "detail": "Age of Empires分别跌至Google #55、iOS #60，Top Heroes跌至Google #32、iOS #59；两组都呈双端同向，但目前只有一次周末后快照，不能直接定义长期衰退。近90天新品仍为Google 4款、iOS 2款。"},
    {"type": "关注", "title": "下一工作日：验证DC与Battle Cats的活动承接", "detail": "DC需双端继续留榜并至少一端离开后五名；The Battle Cats需维持iOS前30。若快速回落，只归档为活动/版本窗口的一次性峰值。"},
    {"type": "关注", "title": "下一工作日：复核两组共同榜尾风险", "detail": "重点看Age of Empires能否避免任一端掉榜、Top Heroes能否让iOS脱离后两名；同时观察Lords Mobile的一降一进是否收敛。"},
    {"type": "关注", "title": "未来2个有效快照：检验新品与中段版本信号", "detail": "Warline需保持iOS TOP50和Google TOP35；Foundation需双端继续在前35；Top Force需守住Google前30。满足两次连续条件后再讨论版本承接，而非用单日名次下结论。"},
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(g["comparison90d"]["status"] == "new" for g in datasets["googlePlay"]["now"])
ios_new = sum(g["comparison90d"]["status"] == "new" for g in datasets["ios"]["now"])

brief = {
    "date": DATE, "timezone": "Asia/Shanghai",
    "title": "DC双端进入，Battle Cats跃升；Limbus与GFL2转为Android单端改善",
    "summary": "较9月18日最终有效快照，Google Play四进四出：Last Fortress、Game of Thrones: Conquest和Doomsday回榜，DC: Dark Legion首次进入#51；Wild Rift、Draft Showdown、Supremacy和Aliens vs Zombies掉榜。iOS五进五出：Fire Emblem Heroes、Lords Mobile、DC、Guns of Glory与Last Day on Earth回榜；Limbus、GFL2、Cell Survivor、Mafia City与Rise of Castles掉榜。Google最大涨跌为GFL2 +12和Age of Empires -14；iOS为The Battle Cats +35和Age of Empires/Top Heroes各-10。近90天新品Google 4款、iOS 2款；两端缺少6月23日精确基准，较老产品不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": f"data/games-{CURRENT}.json", "ios": f"data/ios-games-{CURRENT}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREVIOUS}.json", "ios": f"data/ios-games-{PREVIOUS}.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Lands of Jail · #60 MARVEL SNAP: Hero Strategy CCG", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）", "anchors": "榜单锚点：#1 Kingshot · #25 Police Chief · #60 Age of Empires Mobile", "products": ios_products},
    },
    "marketNews": news, "closing": closing, "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-23"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-23"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-21.md", "json": "data/market-brief-20260921.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-09-18；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-06-23精确同口径TOP60基准，较老产品暂不判断飙升。", "",
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
    lines += ["", "### 策略产品与同比口径", ""] + [f"- {item}" for item in revenue["officialHighlights"]]
    lines += ["", revenue["methodologyNote"], "", "## 下载与来源", "", f"- JSON：`{value['downloads']['json']}`", f"- Sensor Tower上月对照：{revenue['previousPeriodSourceUrl']}", f"- Sensor Tower同比对照：{revenue['yearOverYearSourceUrl']}", "- Google Play直连源：https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US", "- Apple官方RSS：https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json", ""]
    return "\n".join(lines)


save("data/market-brief-20260921.json", brief)
(ROOT / "reports/2026-09-21.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
