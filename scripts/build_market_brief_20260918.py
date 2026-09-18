#!/usr/bin/env python3
"""Generate the Beijing 2026-09-18 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-18"
STAMP = "20260918"
CURRENT = "20260918"
PREVIOUS = "20260917"


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


google_history = load("data/history/google-play/2026-09-18.json")
ios_history = load("data/history/ios/2026-09-18.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Limbus Company", "entry", "回到Google #43，同时首次进入项目iOS榜#16。Apple 1.114.0于9月17日明确上线Season 8、新Identity和新章节；版本与双端进入时间相邻，但现阶段只记为待验证信号。"),
    card("googlePlay", "Arknights", "entry", "首次进入项目Google策略TOP60，位列#57；iOS却从上期#58掉榜。两端反向触及榜尾，且Google最近一次版本仍是8月13日，未发现可确认的当日运营原因。", first=True),
    card("googlePlay", "Aliens vs Zombies", "entry", "首次进入项目Google榜#60。2024年上架的单机塔防产品当前商品页突出Boss挑战与Fire Crossbow Tower，位置仍在掉榜线，先按单日榜尾信号处理。", first=True),
    card("googlePlay", "Vikings: War of Clans", "exit", "上期Google #57后掉榜，iOS同口径未收录；成熟4X从后五名退出只能确认边界波动，未发现可确认的重大转折。"),
    card("googlePlay", "Age of Spirits", "exit", "美国区9月16日上架、上期首次进入#59后今天掉榜；按本店released日期仍是近90天新品，但首发榜尾承接尚未成立。"),
    card("googlePlay", "Sea War", "exit", "上期Google #60后掉榜，iOS则从榜外回到#45；同产品跨端方向完全相反，更像商店节奏差异，不能合并判断为整体走强或走弱。"),
    card("googlePlay", "GIRLS' FRONTLINE 2", "up", "Google大涨21位至#28，为Android最大升幅；iOS也由榜外回到#31。双端共同改善值得跟踪，但当前商店版本仍为8月26日Chiral Redundancy活动，未发现9月18日新节点。"),
    card("googlePlay", "Star Trek Fleet Command", "up", "Google升6位至#17，iOS同时回榜#48。Apple M95于9月17日加入Ops 61+ Haven基地、U.S.S. Kelcie May和领地更新，时间相邻但仍需连续名次确认。"),
    card("googlePlay", "Infinity Kingdom", "up", "Google升5位至#19，iOS则下滑3位至#27；两端仍在前半区但方向分化，今天没有可核验的共同活动依据。"),
    card("googlePlay", "Top Heroes", "down", "Google下滑5位至#26，iOS也下滑3位至#49。两端同向回落但幅度有限，先视为单日调整而非长期衰退。"),
    card("googlePlay", "League of Legends: Wild Rift", "down", "Google下滑5位至#51并进入榜尾区，iOS仍在榜外；近期7.2e平衡补丁仅是背景，没有证据将回落直接归因于版本。"),
    card("googlePlay", "Rise of Kingdoms", "down", "Google下滑4位至#22，iOS同产品升1位至#33；成熟4X继续保持双端在榜，方向差异不足以支持统一趋势判断。"),
]


ios_products = [
    card("ios", "Limbus Company", "entry", "首次进入项目iOS榜即到#16，Google也回到#43。9月17日Season 8、新Identity和新章节是可核验节点；高位双端进入仍需下一快照判断持续性。", first=True),
    card("ios", "GIRLS' FRONTLINE 2", "entry", "回到iOS #31，Google同步大涨21位至#28。两端名次接近并共同改善，是今天最清晰的跨端信号之一，但现有公开版本仍停留在8月26日。"),
    card("ios", "Sea War", "entry", "回到iOS #45，Google却从上期#60掉榜；两端反向变化说明不能用单一商店榜位概括整体表现。"),
    card("ios", "Star Trek Fleet Command", "entry", "回到iOS #48，Google同时升6位至#17。9月17日M95加入Haven基地、U.S.S. Kelcie May和Territory Capture更新，时间相邻但不等于已确认增收。"),
    card("ios", "Warline", "entry", "回到iOS #54，Google仍在#31。Apple本店7月22日上架，继续按近90天新品计算；9月16日1.3.0开启八服Eye of the Storm，仍处版本承接验证。"),
    card("ios", "Mafia City", "entry", "首次进入项目iOS榜#59，Google同产品#48。9月17日1.8.519新增Beers without Borders活动与Dionysus Garden装饰，节点相邻但榜尾回归尚未稳定。", first=True),
    card("ios", "DC: Dark Legion", "exit", "上期iOS #47后掉榜；9月9日Forge Breach联盟玩法没有形成连续留榜，当前只记录为成熟产品边界回落。"),
    card("ios", "SimCity BuildIt", "exit", "上期回榜#49后今天退出；9月17日Kuala Lumpur赛季与土地扩建已上线，但同日榜位未能守住TOP60，不能据此评价活动整体表现。"),
    card("ios", "Draft Showdown", "exit", "上期iOS #53后掉榜，Google仍在#58；同产品转为仅Android榜尾在榜，下一快照需观察Google是否继续承压。"),
    card("ios", "Lords Mobile x Transformers", "exit", "上期iOS #57后掉榜，Google仍在#30；Transformers联动第二阶段仍在商品页展示，但今天呈现明显跨端分化。"),
    card("ios", "Arknights", "exit", "上期首次进入iOS #58后掉榜，Google反而首次进入#57；两端反向交换榜尾位置，尚无公开节点可解释。"),
    card("ios", "Kingdom Guard", "exit", "上期iOS #60后掉榜，Google仍在#55；9月14—21日Alliance Expedition活动正在进行，但当前iPhone端仍表现为榜尾风险。"),
    card("ios", "Dragon Traveler", "up", "iOS升10位至#38，为今日最大存量涨幅；Google策略榜未收录，仍处上线初期的单端高波动阶段。"),
    card("ios", "Watcher of Realms", "up", "iOS升9位至#46，刚离开后五名但仍靠近榜尾；Google没有同口径排名，先按单端短时改善处理。"),
    card("ios", "Game of Thrones: Dragonfire", "up", "iOS升7位至#11，Google则下滑2位至#24；双端仍在前半区但方向不同，暂无共同活动证据支撑统一判断。"),
    card("ios", "Top Force", "up", "iOS升7位至#30，Google维持#32；两端名次接近且都在中段，是相对稳健的跨端位置，但单日升幅仍需复核。"),
    card("ios", "The Tower", "down", "iOS下滑15位至#56，为今天最大跌幅并进入掉榜区；此前已出现大幅往返，当前更像高波动而非可确认的长期转向。"),
    card("ios", "Age of Empires Mobile", "down", "iOS下滑14位至#50，Google仅下滑1位至#41；付费位置回落主要集中在iPhone端，跨端仍有9位差。"),
    card("ios", "Hearthstone", "down", "iOS下滑11位至#41，回吐9月17日版本窗口附近的部分涨幅；36.6更新仍可核验，但单日反向变化说明峰值承接尚不稳定。"),
    card("ios", "Supremacy: World War 3", "down", "iOS下滑8位至#52，Google也小跌至#59；两端同向靠近榜尾，是今天需要优先复核的共同风险信号。"),
]


news = [
    {"category": "赛季 / 剧情", "date": "2026-09-17", "title": "Limbus Company 1.114.0上线Season 8与新章节", "summary": "Apple官方版本说明列出Season 8、新Identity、新章节以及问题修复；产品仍以技能连锁、Clash、Identity与E.G.O为核心。", "impact": "Limbus今天进入iOS #16并回到Google #43，是最强双端共振之一；节点与榜位相邻，但尚不能拆分其收入贡献。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/limbus-company/id6444112366"},
    {"category": "版本 / 高阶基地", "date": "2026-09-17", "title": "Star Trek Fleet Command M95加入Haven基地", "summary": "Apple官方版本说明显示Ops 61+玩家可建设并自定义Haven，另加入U.S.S. Kelcie May、Stella Archives、Battle Pass与Territory Capture更新。", "impact": "产品今天iOS回榜#48、Google升6位至#17；双端改善需用下一快照判断是否获得持续承接。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/star-trek-fleet-command/id1427744264"},
    {"category": "长线活动 / 经营", "date": "2026-09-17", "title": "Mafia City推出Beers without Borders活动", "summary": "1.8.519新增同名活动、Dionysus Garden地盘装饰与社交装饰套装，并优化Inventory、Island Edit和联盟招募机制。", "impact": "产品首次进入项目iOS榜#59、Google #48；活动与回榜同日，但目前仍是榜尾待验证信号。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/mafia-city-war-of-underworld/id1235569398"},
    {"category": "城市经营 / 赛季", "date": "2026-09-17", "title": "SimCity BuildIt开启Kuala Lumpur赛季", "summary": "Apple官方版本说明列出Batu Temple Stairs、Skyline Harmony Hub、新土地扩建以及限时建筑和赛季奖励。", "impact": "产品上期回榜#49后今天掉榜，说明版本上线并未在当前快照形成连续TOP60留存；不能据此评价整个赛季。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/simcity-buildit/id913292932"},
    {"category": "赛季 / 周年", "date": "2026-09-16", "title": "Mobile Legends美国版上线十周年内容与S42赛季", "summary": "Apple官方版本说明列出Masha、Bruno重做及十周年内容；S42赛季同步开启并提供赛季皮肤与头像框。", "impact": "产品在昨日大涨后今天回落6位至iOS #20；仍在前20，但单日反向说明周年峰值承接需要继续复核。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/mobile-legends-bang-bang-us/id6741568655"},
    {"category": "新品 / 跨服战", "date": "2026-09-16", "title": "Warline 1.3.0开启八服Eye of the Storm", "summary": "Apple版本说明列出八服Conquest、Pulse Resist、Stormbreaker争夺、三件Signature Armaments、Insignia奖励与车队外观。", "impact": "Warline今天回到iOS #54、Google #31；Apple本店7月22日上架，仍属近90天新品与版本承接观察对象。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/warline-sniper-strike/id6742809194"},
    {"category": "卡牌 / 版本", "date": "2026-09-15", "title": "Hearthstone 36.6加入扩展预览卡与战棋异变", "summary": "Apple官方版本说明提供Reign of the Black Empire预览卡、构筑模式平衡调整与Battlegrounds Aberrations。", "impact": "产品今天iOS回落11位至#41，显示版本窗口后的排名仍有波动；不能把昨日升幅等同于长期增收。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/hearthstone/id625257520"},
    {"category": "联盟活动 / 塔防", "date": "2026-09-13", "title": "Kingdom Guard开启Alliance Expedition", "summary": "Apple版本说明将联盟远征活动窗口标为9月14日至21日。", "impact": "产品今天从iOS #60掉榜、Google仍在#55；活动并未阻止当前iPhone端离榜，需在窗口结束前复核。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/kingdom-guard-tower-defense-td/id1570095804"},
    {"category": "IP活动 / 长线运营", "date": "2026-09-09", "title": "Clash of Clans推出WWE Equipment Blast活动", "summary": "Supercell公布9月9日至22日的勋章活动，玩家通过多人战斗获取Tag Tickets、Champ Medals、临时兵种与装备奖励。", "impact": "CoC仍位于双端头部；活动可作为头部稳定度背景，但不能由当前名次拆算其单独收入贡献。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/news/equipment-blast-medal-event/"},
    {"category": "全球收入月榜", "date": "2026-09-04", "title": "Sensor Tower公布8月全球手游收入TOP10", "summary": "全球App Store与Google Play手游消费者支出估算约65.7亿美元，Whiteout Survival全球总榜#3、Kingshot #7。", "impact": "两款核心策略产品较7月各升1位；官方未公开单品收入同比，不能由名次换算收入百分比。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"},
]


closing = [
    {"type": "判断", "title": "iOS换位和波动都明显高于Google", "detail": "Google三进三出，57款共同在榜产品中49款日变动不超过2位、中位绝对变动1位；iOS六进六出，54款共同在榜产品中只有25款不超过2位、中位绝对变动3位。榜首两端未变，但iPhone中后段轮换显著加快。"},
    {"type": "判断", "title": "Limbus、GFL2与Star Trek构成三组双端改善", "detail": "Limbus iOS #16且Google #43，GFL2 iOS回榜#31且Google +21至#28，Star Trek iOS回榜#48且Google +6至#17；其中Limbus和Star Trek都有9月17日官方版本节点，但单日共振仍不能写成长期趋势。"},
    {"type": "判断", "title": "新品状态收缩，榜尾更多由成熟产品轮换", "detail": "Google近90天新品4款、iOS 2款；Age of Spirits上架两日即从Google掉榜，Warline则在iOS回榜。Arknights、Mafia City和Aliens vs Zombies等本次进入者均非90天新品，显示今日换位主要来自成熟产品。"},
    {"type": "关注", "title": "下一工作日：验证三组双端改善", "detail": "Limbus需同时守住iOS前20与Google前50，GFL2需双端保持前35，Star Trek需保持Google前20且iOS不再掉榜；否则仅归档为版本窗口附近的单日信号。"},
    {"type": "关注", "title": "下一工作日：复核榜尾首录与反向换位", "detail": "观察Google端Arknights #57、Aliens #60能否留榜，以及Arknights、Sea War在两端的反向换位是否收敛；若继续一端进一端出，不合并为产品整体趋势。"},
    {"type": "关注", "title": "截至9月21—22日：核对活动窗口承接", "detail": "Kingdom Guard联盟远征截至9月21日、Clash of Clans WWE活动截至9月22日；同时跟踪Warline Eye of the Storm、Mafia City Beers without Borders和Mobile Legends S42能否形成连续名次。"},
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Limbus双端共振，GFL2与Star Trek同步改善；iOS换位加快",
    "summary": "较9月17日最终有效快照，Google Play三进三出：Limbus回榜#43，Arknights与Aliens vs Zombies首次进入项目记录；Vikings、Age of Spirits、Sea War掉榜。iOS六进六出：Limbus首次进入#16，GFL2、Sea War、Star Trek、Warline回榜，Mafia City首次进入；DC: Dark Legion、SimCity、Draft Showdown、Lords Mobile、Arknights与Kingdom Guard掉榜。GFL2在Google +21、Star Trek +6且两者同时iOS回榜；iOS存量最大涨跌为Dragon Traveler +10与The Tower -15。近90天新品Google 4款、iOS 2款；两端缺少6月20日精确基准，较老产品不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": f"data/games-{CURRENT}.json", "ios": f"data/ios-games-{CURRENT}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREVIOUS}.json", "ios": f"data/ios-games-{PREVIOUS}.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 The Grand Mafia · #60 Aliens vs Zombies: Invasion", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）", "anchors": "榜单锚点：#1 Pokémon GO · #25 Magic: The Gathering Arena · #60 Rise of Castles: Fire and War", "products": ios_products},
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-20"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-20"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-18.md", "json": "data/market-brief-20260918.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-09-17；升降为相邻自然日变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-06-20精确同口径TOP60基准，较老产品暂不判断飙升。", "",
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


save("data/market-brief-20260918.json", brief)
(ROOT / "reports/2026-09-18.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
