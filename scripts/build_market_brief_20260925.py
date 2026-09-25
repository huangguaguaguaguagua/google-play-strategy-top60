#!/usr/bin/env python3
"""Generate the Beijing 2026-09-25 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, CURRENT, PREVIOUS = "2026-09-25", "20260925", "20260925", "20260924"


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
    return {
        "gameName": game_name,
        "productId": product_id,
        "iconKey": f"{store}:{product_id}",
        "tone": tone,
        "changeLabel": label,
        "analysis": analysis,
    }


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


google_history = load("data/history/google-play/2026-09-25.json")
ios_history = load("data/history/ios/2026-09-25.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Age of Spirits", "entry", "9月16日美国区上架并曾短暂进入#59，本次回到Google #60；按本店released日期仍归类为近90天新品。当前只确认首发版本与榜尾回归，没有新版本节点可解释当天变化。"),
    card("googlePlay", "Ant Legion", "exit", "从上期Google #58掉出TOP60，iOS同口径未收录。成熟4X产品此前一直贴近榜尾，本次只能确认边界风险兑现，不能外推为整体收入下滑。"),
    card("googlePlay", "Overgeared Hero", "up", "Google升5位至#33，iOS也升8位至#50，是今天较清晰的双端共同改善信号。9月16日联动仍在运营窗口，但iPhone仍处后十名，需要连续快照验证。"),
    card("googlePlay", "Age of Empires Mobile", "up", "Google升5位至#51，iOS却跌6位至#41。两端方向相反，当前属于平台分化，不能用Android改善代表整体回升。"),
    card("googlePlay", "Call of Dragons", "up", "Google升4位至#43、iOS升3位至#53，呈现温和双端改善；Full Moon Festivities仍提供节庆活动背景，但iOS继续靠近掉榜区。"),
    card("googlePlay", "GIRLS' FRONTLINE 2", "down", "Google跌17位至#34，为本端最大跌幅；iOS策略榜当前未收录。没有找到与当天回落直接对应的官方节点，先按单日待验证信号处理。"),
    card("googlePlay", "Limbus Company", "down", "Google跌11位至#54，但iOS在1.115.0更新后回榜#44。相反方向显示新章节、Identity与E.G.O更新的榜位承接暂时集中在iPhone端。"),
    card("googlePlay", "Top Heroes", "down", "Google跌4位至#37，iOS则从上期#59掉榜。两端共同减弱且iPhone先触发掉榜，但单日结果仍不足以判断赛季内容的长期效果。"),
    card("googlePlay", "DC: Dark Legion", "down", "Google跌4位至#59，iOS从上期#60掉榜。Nemesis Takedown活动没有在相邻快照中把产品带离榜尾，下一次Google快照存在掉榜风险。"),
]


ios_products = [
    card("ios", "Kingdom Rush 6", "entry", "9月24日正式上架后，首个完整榜单日直接进入iOS #26。产品以Linirea前传、15座塔、双英雄与离线单机回归经典塔防；上线不足两天，仍处首发验证。", first=True),
    card("ios", "Limbus Company", "entry", "在1.115.0加入新Identity、E.G.O与章节后回到iOS #44；Google却跌11位至#54。版本节点与回榜相邻，但跨端方向分化，不能写成确定因果。"),
    card("ios", "Galaxy Defense", "entry", "回到iOS #47。Season: Expedition测试期已开启，Kronos Exploration于9月24日上线；活动与回榜同期，但当前仍在后段。"),
    card("ios", "Warpath", "entry", "回到iOS #56，Google同口径未收录。14.4版本扩展Age of Artisans、Toy Joy Night及联盟赛，但回榜位于后五名，仍是榜尾待验证信号。"),
    card("ios", "Kiss of War", "exit", "从上期iOS #47掉榜，Google同口径未收录。前一日回榜没有形成连续承接，且未发现可确认的当天重大内容节点。"),
    card("ios", "Hearthstone", "exit", "从上期iOS #57掉榜。Reign of the Black Empire预热与卡牌调整尚未在相邻策略分类榜快照中形成留榜；该产品属于卡牌分类边界。"),
    card("ios", "Top Heroes", "exit", "从上期iOS #59掉榜，Google同步跌4位至#37。Cloudsea Odyssey与Legendary Battlefield上线后的榜位承接继续减弱，但仍需更多快照判断是否为短期回吐。"),
    card("ios", "DC: Dark Legion", "exit", "从上期iOS #60掉榜，Google也跌4位至#59。Nemesis Takedown仍在活动窗口，但两端都没有脱离榜尾风险区。"),
    card("ios", "Dragon Traveler", "up", "iOS升14位至#35，Google同口径未收录。Golden Night Reverie与SSR+ Lilith活动仍提供运营背景，但当前只记录单端改善。"),
    card("ios", "Summoners War", "up", "iOS升14位至#36，Google策略榜未收录。9.3.2加入Siege Battle策略信息与符文、神器体验优化；单日上涨仍需后续快照确认。"),
    card("ios", "Game of Thrones: Conquest", "up", "iOS升12位至#39，而Google跌3位至#56。Dragonseed装备与新英雄版本没有形成双端同向变化，暂按iPhone单端改善处理。"),
    card("ios", "Lands of Jail", "up", "iOS升10位至#31，Google也升2位至#25。双端方向一致但幅度主要来自iPhone；Qixi活动已非当日新节点，不能据此直接解释涨幅。"),
    card("ios", "Overgeared Hero", "up", "iOS升8位至#50、Google升5位至#33。两端同步改善与现有联动窗口重合，但iOS仍贴近后十名，暂不升级为持续趋势。"),
    card("ios", "League of Legends: Wild Rift", "down", "iOS跌20位至#59，为全榜最大跌幅；Google维持#46。Patch 7.3仍在版本窗口，但今天呈现明显平台分化，且该产品属于MOBA分类边界。"),
    card("ios", "Top War", "down", "iOS跌12位至#54，Google同口径未收录。产品重新进入后七名，暂未发现与单日回落直接对应的官方重大节点。"),
    card("ios", "RAID: Shadow Legends", "down", "iOS跌9位至#45，Google策略榜未收录。作为RPG分类边界产品，本次回落不代表核心4X或SLG同步转弱。"),
    card("ios", "The Battle Cats", "down", "iOS跌8位至#60，连续回吐后触及掉榜线。15.6.0新增形态、地图与震动功能，但内容更新尚未形成稳定榜位承接。"),
    card("ios", "Age of Empires Mobile", "down", "iOS跌6位至#41，Google却升5位至#51。两个商店方向相反，需分平台观察，不能合并成统一趋势。"),
]


news = [
    {
        "category": "新品 / 经典塔防",
        "date": "2026-09-24",
        "title": "Kingdom Rush 6: Genesis全球上架并进入iOS #26",
        "summary": "Apple官方商品页确认产品于9月24日上架，以Linirea前传、15座塔、12名英雄、9种法术、18个战役关卡和离线模式回归经典塔防。",
        "impact": "首个完整榜单日进入iOS策略畅销#26，是今天最重要的新品信号；上线时间短，仍需验证首发IP热度能否转为连续留榜。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6759664029",
    },
    {
        "category": "策略RPG / 新章节",
        "date": "2026-09-24",
        "title": "Limbus Company 1.115.0加入新Identity、E.G.O与章节",
        "summary": "Apple官方版本说明列出新Identity、新E.G.O、新章节以及缺陷与体验修复。",
        "impact": "产品回到iOS #44，但Google跌11位至#54；内容节点存在，榜位承接却出现跨端分化。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6444112366",
    },
    {
        "category": "塔防 / 公会赛季",
        "date": "2026-09-22",
        "title": "Galaxy Defense开启Season: Expedition与Kronos Exploration",
        "summary": "1.0.1版本加入60级公会参与的Season: Expedition测试期，并于9月24日开启Kronos Exploration活动。",
        "impact": "产品回到iOS #47；活动与回榜时间相邻，但当前仍在后段，需要连续快照确认。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6740189002",
    },
    {
        "category": "军事SLG / 长线版本",
        "date": "2026-09-09",
        "title": "Warpath 14.4扩展Age of Artisans与联盟赛事",
        "summary": "14.4加入Age of Artisans等级、科技与材料，推出Toy Joy Night，并调整Army League、Conquest、Brave's Path及单位平衡。",
        "impact": "产品本期回到iOS #56；版本内容较完整，但当前仍是榜尾回归，不能据此判断长期抬升。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1529067679",
    },
    {
        "category": "IP SLG / 龙裔更新",
        "date": "2026-09-21",
        "title": "Game of Thrones: Conquest推进Dragonseed版本",
        "summary": "26.9.830115加入Alys Rivers、Hugh Hammer、Dragonseed装备和Ever-Ready Warrior Saddle龙具。",
        "impact": "iOS升12位至#39、Google跌3位至#56；内容更新没有形成双端同步改善。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1035712810",
    },
    {
        "category": "奇幻RPG / 节庆活动",
        "date": "2026-09-09",
        "title": "Dragon Traveler开启Golden Night Reverie",
        "summary": "1.8.0版本加入Festival Cavalcade Gullveig、SSR+ Lilith、Chronicle of the Immortal Isles以及多款节庆皮肤与登录奖励。",
        "impact": "产品iOS升14位至#35；活动提供背景，但Google策略榜未收录，当前仍是单端信号。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6751086804",
    },
    {
        "category": "长线运营 / 公会策略",
        "date": "2026-09-11",
        "title": "Summoners War 9.3.2补充Siege Battle策略信息",
        "summary": "版本加入Siege Battle Strategy Info，并改善符文、神器与其他操作体验。",
        "impact": "产品iOS升14位至#36；作为成熟RPG，今天的变化只代表Apple策略分类内改善。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id852912420",
    },
    {
        "category": "MOBA / 跨端分化",
        "date": "2026-09-22",
        "title": "Wild Rift Patch 7.3后iOS跌至榜尾",
        "summary": "Patch 7.3加入Hwei、Sylas、Rek'Sai、3v3v3v3模式、SMASH社区内容和音乐主题皮肤。",
        "impact": "iOS跌20位至#59而Google维持#46；版本窗口内仍出现平台分化，且产品不属于核心策略收入子集。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1480616990",
    },
    {
        "category": "新品 / 部落4X",
        "date": "2026-09-16",
        "title": "Age of Spirits首发后再次回到Google榜尾",
        "summary": "Google Play商品页以篝火建部落、萨满编队、世界地图和联盟4X为核心；首发版本加入七种语言、11级兵种与萨满伤势机制。",
        "impact": "产品回到Google #60并继续计入近90天新品；两次出现都在榜尾，首发承接仍未稳定。",
        "source": "Google Play官方商品页",
        "url": "https://play.google.com/store/apps/details?id=leyi.ageofspirits&hl=en_US&gl=US",
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
        "title": "Google维持高稳定度，iOS波动明显扩大",
        "detail": "Google仅一进一出，59款共同产品中48款变动不超过2位，中位绝对变动1位且前10全部保留；iOS四进四出，56款共同产品仅25款变动不超过2位，中位绝对变动3位。",
    },
    {
        "type": "判断",
        "title": "Kingdom Rush 6提供强首发信号，其他回榜仍集中在中后段",
        "detail": "Kingdom Rush 6上架后直接进入iOS #26；Limbus、Galaxy Defense与Warpath分别回到#44、#47和#56。外部版本资料能确认新章节、公会赛季和长线版本，但只有新品进入前30。",
    },
    {
        "type": "判断",
        "title": "跨端方向继续分化，只有少数产品同步改善",
        "detail": "Overgeared在Google +5、iOS +8，Call of Dragons两端温和上升；Limbus、Age of Empires、Sea War和Game of Thrones: Conquest均出现反向变化，不能把单店涨跌外推到整体市场。",
    },
    {
        "type": "关注",
        "title": "未来1—2个有效快照：验证Kingdom Rush 6首发承接",
        "detail": "若Kingdom Rush 6继续守住iOS前35，可记为首发高位承接；若快速跌出前45，则更接近系列IP首发峰值。",
    },
    {
        "type": "关注",
        "title": "下一有效快照：检验Limbus与Galaxy Defense的活动延续性",
        "detail": "Limbus需让iOS保持前50并让Google脱离后十名；Galaxy Defense需守住iOS前50，才说明新章节或Season: Expedition不只是单次回榜。",
    },
    {
        "type": "关注",
        "title": "下一有效快照：观察双端同步产品与榜尾风险",
        "detail": "Overgeared若Google保持前35且iOS继续升入前50，才升级为连续改善；Wild Rift、DC与The Battle Cats已触及iOS或Google后两名，继续下移即可能掉榜。",
    },
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Kingdom Rush 6首日进入iOS #26，Google稳盘而iOS四进四出",
    "summary": "较9月24日最终有效快照，Google Play一进一出：Age of Spirits回榜#60，Ant Legion掉榜；Overgeared与Age of Empires各升5位，GFL2跌17位、Limbus跌11位。iOS四进四出：Kingdom Rush 6首次进入#26，Limbus、Galaxy Defense、Warpath回榜，Kiss of War、Hearthstone、Top Heroes、DC掉榜；Dragon Traveler与Summoners War各+14，Wild Rift -20。近90天新品Google 3款、iOS 3款；两端缺少6月27日精确基准，较老产品不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": f"data/games-{CURRENT}.json", "ios": f"data/ios-games-{CURRENT}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREVIOUS}.json", "ios": f"data/ios-games-{PREVIOUS}.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Lands of Jail · #60 Age of Spirits",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Forge Master – Idle RPG · #60 The Battle Cats",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-27"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-27"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-25.md", "json": "data/market-brief-20260925.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-09-24；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-06-27精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20260925.json", brief)
(ROOT / "reports/2026-09-25.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {
    "date": DATE,
    "title": brief["title"],
    "summary": brief["summary"],
    "markdown": brief["downloads"]["markdown"],
    "json": brief["downloads"]["json"],
}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
