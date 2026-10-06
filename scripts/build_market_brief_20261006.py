#!/usr/bin/env python3
"""Generate the Beijing 2026-10-06 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, CURRENT, PREVIOUS = "2026-10-06", "20261006", "20261006", "20261005"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261006.json"), "prior": load("data/games-20261005.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261006.json"), "prior": load("data/ios-games-20261005.json"), "id": "appId"},
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


google_history = load("data/history/google-play/2026-10-06.json")
ios_history = load("data/history/ios/2026-10-06.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Forge of Empires", "entry", "回到Google #53。成熟城建产品的美国区商品页最近一次可见更新为8月27日，未发现与今天回榜同日的重大节点；先按榜尾回补处理。"),
    card("googlePlay", "Kingdom Guard", "entry", "回到Google #57，同时iOS上升7位至#34，是今天最清晰的双端共同改善信号；但Android仍处后四名，且Fruit Market已于9月27日结束，不能据此确认活动因果。"),
    card("googlePlay", "GIRLS' FRONTLINE 2", "entry", "回到Google #59，iOS同口径未进入TOP60；当前没有核验到与本次回榜同日的重大官方节点，仍属高掉榜风险。"),
    card("googlePlay", "Aliens vs Zombies", "entry", "回到Google #60且恰处末位；产品近期多次在榜尾与榜外切换，本次只记录为待验证回补，不外推长期趋势。"),
    card("googlePlay", "Game of Thrones: Conquest", "exit", "从Google上期#52掉榜，iOS却回到#50；Dragonseeds仍是近期版本背景，但今天呈现平台分化，而不是双端共同改善。"),
    card("googlePlay", "The Ants", "exit", "从Google上期#54掉榜，iOS同口径未进入TOP60；前一快照的Gamera活动期可见度没有延续为连续留榜。"),
    card("googlePlay", "Sea War", "exit", "从Google上期#56掉榜，iOS也从#58退出，是今天最清晰的双端共同走弱信号；仍只说明本期低于截线，不能直接断言长期下行。"),
    card("googlePlay", "Last Shelter: Survival", "exit", "从Google上期#60掉榜；iOS回榜的是另一应用Last Shelter: War Z，两个产品ID与版本线不同，不把它们合并为同一跨端信号。"),
    card("googlePlay", "The Grand Mafia", "up", "Google上升5位至#25，为本端唯一达到5位的上涨；iOS未进入TOP60，当前改善仅见于Android端。"),
]


ios_products = [
    card("ios", "Warpath", "entry", "回到iOS #48。9月Age of Artisans版本扩充等级、科技、材料、联盟联赛和征服奖励，但本次仍只是后13名回补。"),
    card("ios", "Game of Thrones: Conquest", "entry", "回到iOS #50，Google却从#52掉榜；Dragonseeds版本提供可核验内容背景，但两端方向相反。"),
    card("ios", "Kingdom Clash", "entry", "回到iOS #51。8月版本加入Clan Boss、Revenge并发限制与聊天互动，距本次回榜已有一段时间，不能作为直接原因。"),
    card("ios", "Boom Beach", "entry", "回到iOS #57。Apple官方10月5日版本说明加入Blitz关卡、奖励与排行榜，发布时间与回榜相邻；因仍处后四名，只按更新窗口内的待验证信号处理。"),
    card("ios", "Last Shelter: War Z", "entry", "回到iOS #58。9月版本新增Milestone of Glory、世界宝箱探索与兑换码功能；Google同名版本位于#39，但iPhone端仍贴近截线。"),
    card("ios", "Top Heroes", "entry", "回到iOS #60且恰处末位，Google为#43。Cloudsea Odyssey赛季升级仍是近期内容背景，但本次回榜的持续性尚未建立。"),
    card("ios", "League of Legends: Wild Rift", "exit", "从iOS上期#52掉榜，Google策略榜仍未收录；该产品属于MOBA分类边界，本次只记录分类榜退出。"),
    card("ios", "Hearthstone", "exit", "从iOS上期#55掉榜；卡牌长线产品的后段留榜未延续，未发现足以解释本次退出的同日重大节点。"),
    card("ios", "Draft Showdown", "exit", "从iOS上期#56掉榜，Google同口径也未进入TOP60；9月新增单位后的榜尾回补未形成连续留榜。"),
    card("ios", "Sea War", "exit", "从iOS上期#58掉榜，Google也从#56退出；这是双端共同触及截线的事实，但一个快照不足以判断长期运营转折。"),
    card("ios", "The Tower", "exit", "从iOS上期#59掉榜；v29大版本后的短暂回榜再次中断，当前仍表现为榜尾高频轮换。"),
    card("ios", "Yu-Gi-Oh", "exit", "从iOS上期#60掉榜；前一快照恰处末位，本次退出符合最高掉榜风险，未发现同日重大官方转折。"),
    card("ios", "Forge Master", "up", "iOS上升15位至#32，为本端最大上涨；Google维持#48。最近可核验的大版本仍是9月Fairies与Clan Tech Race，不能把今天的跃升直接归因于旧版本。"),
    card("ios", "Warhammer 40,000", "down", "iOS下跌14位至#56，Google小升至#40。Ûthar活动已于10月4日开始、Terminus生存活动排期10月10日，内容窗口未阻止iPhone端落入后五名。"),
    card("ios", "The Battle Cats", "up", "iOS上升11位至#28。10月5日15.6.1修复问题，15.6版本加入战斗震动、形态、天赋、地图与奖励；时间相邻但尚不能证明因果。"),
    card("ios", "Lords Mobile", "down", "iOS下跌9位至#59，Google为#26，跨端差扩大到33位；Transformers联动仍在版本窗口，但iPhone端已进入倒数第二。"),
    card("ios", "Supremacy", "down", "iOS下跌9位至#45；9月平衡更新仍是最近节点，前一快照的大幅上涨没有延续，说明单日峰值需要降级解读。"),
    card("ios", "Puzzles & Survival", "up", "iOS上升7位至#13，Google为#11；双端都进入前15，是成熟末日三消SLG的共同高位信号，但今天只有iOS显著移动。"),
    card("ios", "Kingdom Guard", "up", "iOS上升7位至#34，同时Google回榜#57；两端同向但Android仍靠近截线，至少需要下一有效快照确认持续性。"),
    card("ios", "Overgeared Hero", "up", "iOS上升7位至#46，Google维持#35；当前仍是中后段改善，未发现可确认的同日重大版本转折。"),
    card("ios", "X-Clash", "up", "iOS上升6位至#17，Google同口径未收录；产品回到前20，但单端单日变化不足以判断新的增长阶段。"),
    card("ios", "Tiles Survive", "up", "iOS上升5位至#24，Google升2位至#21；两端同处前25，是温和共同改善，但幅度不足以视为重大转折。"),
    card("ios", "Guns of Glory", "up", "iOS上升5位至#49，Google为#30；iPhone端刚回到前50，仍需观察能否脱离后段。"),
]


news = [
    {
        "category": "全球收入月榜", "date": "2026-10-01",
        "title": "Sensor Tower 9月全球收入TOP10的核心策略子集为3款",
        "summary": "官方完整图表显示Whiteout Survival全球总榜#6、Last War: Survival #7、Kingshot #9；全球App Store与Google Play消费者支出约61.3亿美元，排除第三方Android商店。",
        "impact": "Last War新进入全球TOP10，Whiteout与Kingshot较上月分别下降3位、2位；这些是总榜名次变化，不是单品收入同比。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
    {
        "category": "海岛策略 / 版本", "date": "2026-10-05",
        "title": "Boom Beach更新Blitz玩法后回到iOS榜尾",
        "summary": "Apple官方63.211版本说明加入Blitz递增难度关卡、奖励和新排行榜，并继续修复问题与改善体验。",
        "impact": "产品本期回到iOS #57，更新时间与回榜相邻，但后四名位置仍不足以确认版本承接。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id672150402",
    },
    {
        "category": "塔防 / 版本", "date": "2026-10-05",
        "title": "The Battle Cats 15.6.1更新后iOS上升11位",
        "summary": "官方15.6.1修复问题；15.6加入战斗震动、新形态与天赋、地图难度、Rank奖励和CatCombo。",
        "impact": "产品升至iOS #28，内容与名次变化同处近期窗口；仍需下一快照确认是否只是短期峰值。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id850057092",
    },
    {
        "category": "战术RPG / 活动", "date": "2026-10-04",
        "title": "Tacticus进入Ûthar与Terminus活动窗口但跌至iOS #56",
        "summary": "Apple官方版本说明列出10月4日Ûthar传奇活动，并排期10月10日Terminus生存活动。",
        "impact": "明确内容节点并未阻止本期iOS下跌14位；活动与榜位不能机械建立因果，需观察10月10日前后。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1599937506",
    },
    {
        "category": "末日4X / 版本", "date": "2026-09-24",
        "title": "Last Shelter: War Z以荣耀里程碑版本回到iOS #58",
        "summary": "官方26.0904.001版本加入Milestone of Glory、世界宝箱探索与兑换码功能。",
        "impact": "版本内容明确，但本期仅回到倒数第三；下一快照能否留榜比一次回补更重要。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6760406772",
    },
    {
        "category": "IP 4X / 平台分化", "date": "2026-09-21",
        "title": "Game of Thrones: Conquest的Dragonseeds窗口出现双端分化",
        "summary": "官方版本加入Alys Rivers、Hugh Hammer、Dragonseed装备与新的龙装备。",
        "impact": "本期iOS回到#50而Google从#52掉榜，说明同一内容窗口下的平台付费可见度并不同步。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1035712810",
    },
    {
        "category": "城建塔防 / 活动复核", "date": "2026-09-27",
        "title": "Kingdom Guard双端改善，但Fruit Market已结束",
        "summary": "官方1.0.593版本记录Fruit Market开放至9月27日，并修复酒馆英雄与弹窗显示问题。",
        "impact": "本期iOS +7至#34、Google回榜#57；活动已结束，不能把今天的共同改善直接写成活动拉动。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1570095804",
    },
    {
        "category": "放置经营 / 版本复核", "date": "2026-09-02",
        "title": "Forge Master在Fairies版本后一个月跃升至iOS #32",
        "summary": "官方2.9.0版本加入Fairies、Clan Tech Race淘汰制、新皮肤、头像和任务自动开始。",
        "impact": "今天+15是本端最大上涨，但版本已过去一个月，不能用旧版本直接解释单日名次。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6746636289",
    },
    {
        "category": "英雄4X / 赛季", "date": "2026-09-28",
        "title": "Top Heroes升级Cloudsea Odyssey后回到iOS #60",
        "summary": "官方1.123.5版本调整Cloudsea Odyssey，加入免体力World Boss、Legendary Puffel保底、Legendary Battlefield与邮件收藏。",
        "impact": "Google位于#43、iOS仅回到末位；赛季内容在两端的榜位承接明显不同。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6450953550",
    },
    {
        "category": "部落策略 / 月度活动", "date": "2026-10-01",
        "title": "Clash of Clans继续运行Cosmic Curse活动月",
        "summary": "Supercell官方确认10月1日至31日上线Portal Panic、Totem Thrower、Cosmic Curse奖章活动与Clan War League等内容。",
        "impact": "本期Google #7、iOS #8，双端前10位置稳定；活动仍是高位运营背景，不把单日小幅变化当成收入结论。",
        "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/news/cosmic-curse-portal-panic-teleports-in/",
    },
]


closing = [
    {
        "type": "判断", "title": "Google主体稳定，iOS榜尾轮换明显扩大",
        "detail": "Google四进四出，56款共同产品中49款变动不超过2位，中位绝对变动1位且前10全部保留；iOS六进六出，54款共同产品仅29款变动不超过2位，中位绝对变动2位，波动集中在中后段。",
    },
    {
        "type": "判断", "title": "Sea War共同掉榜，Kingdom Guard共同改善",
        "detail": "Sea War从Google #56和iOS #58同时退出；Kingdom Guard则回到Google #57并在iOS +7至#34。两者都是双端信号，但只有一个相邻快照，分别按截线风险和待验证改善处理。",
    },
    {
        "type": "判断", "title": "内容节点与榜位并非单向对应",
        "detail": "Boom Beach在Blitz版本旁回榜、The Battle Cats在15.6.1后上涨；Tacticus却在Ûthar活动窗口跌14位。外部节点只能作为背景，不能代替榜位连续性验证。",
    },
    {
        "type": "关注", "title": "下一有效快照：复核Google四款回榜的留存",
        "detail": "Forge of Empires #53、Kingdom Guard #57、GFL2 #59、Aliens #60全部处后八名；若无法继续留榜，应维持榜尾回补判断。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：检验iOS六款回榜产品",
        "detail": "Warpath、Game of Thrones、Kingdom Clash、Boom Beach、Last Shelter与Top Heroes均位于#48—#60；至少连续两次留榜并有产品进入前45，才说明本轮换榜形成承接。",
    },
    {
        "type": "关注", "title": "10月10日前后：核对Tacticus活动承接",
        "detail": "Terminus活动开启后若Tacticus从iOS #56回到前45，可将今天视为活动前回吐；若继续处后五名或掉榜，则内容窗口尚未形成榜位承接。",
    },
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Kingdom Guard双端改善，Sea War双端掉榜，iOS榜尾六进六出",
    "summary": "较10月5日前一有效快照，Google Play四进四出：Forge of Empires #53、Kingdom Guard #57、GFL2 #59、Aliens vs Zombies #60回榜，Game of Thrones: Conquest、The Ants、Sea War、Last Shelter: Survival掉榜；The Grand Mafia +5至#25。iOS六进六出：Warpath #48、Game of Thrones #50、Kingdom Clash #51、Boom Beach #57、Last Shelter #58、Top Heroes #60回榜，Wild Rift、Hearthstone、Draft Showdown、Sea War、The Tower、Yu-Gi-Oh掉榜；Forge Master +15、Tacticus -14、The Battle Cats +11。近90天新品为Google 2款、iOS 2款，较老产品因缺少7月8日精确基准不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261006.json",
    "rankingSources": {"googlePlay": "data/games-20261006.json", "ios": "data/ios-games-20261006.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261005.json", "ios": "data/ios-games-20261005.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 The Grand Mafia · #60 Aliens vs Zombies: Invasion",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Kingshot · #25 Rise of Kingdoms · #60 Top Heroes: Kingdom Saga",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-08"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-08"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-06.md", "json": "data/market-brief-20261006.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-05；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-08精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261006.json", brief)
(ROOT / "reports/2026-10-06.md").write_text(build_markdown(brief), encoding="utf-8")
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
