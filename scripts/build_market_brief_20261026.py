#!/usr/bin/env python3
"""Generate the Beijing 2026-10-26 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-26", "20261026"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261026.json"), "prior": load("data/games-20261023.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261026.json"), "prior": load("data/ios-games-20261023.json"), "id": "appId"},
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


def find_game(store, prefix, include_prior=True):
    data, ident = datasets[store], datasets[store]["id"]
    pool = data["now"] + (data["prior"] if include_prior else [])
    found = [row for row in pool if row["gameName"].startswith(prefix)]
    ids = {str(row[ident]) for row in found}
    if len(ids) != 1:
        raise RuntimeError(f"Ambiguous product {store}:{prefix}: {ids}")
    product_id = ids.pop()
    return next(row for row in pool if str(row[ident]) == product_id)


def current_rank(store, prefix):
    return find_game(store, prefix, include_prior=False)["rank"]


def card(store, prefix, tone, analysis, first_time_ids=None):
    data, ident = datasets[store], datasets[store]["id"]
    row = find_game(store, prefix)
    product_id = str(row[ident])
    current = next((item for item in data["now"] if str(item[ident]) == product_id), None)
    previous = next((item for item in data["prior"] if str(item[ident]) == product_id), None)
    if tone == "entry" and current and not previous:
        first = product_id in (first_time_ids or set())
        label = f"{'首次收录' if first else '回榜'} · #{current['rank']}"
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


google_products = [
    card("googlePlay", "Vikings", "entry", "回到Google #56，iOS未入榜。北欧联盟4X再次进入后十名，但没有与今天同步的重大官方节点，先按周末后的榜尾回补处理。"),
    card("googlePlay", "Ant Legion", "entry", "回到Google #58，iOS未入榜。蚁巢题材与联盟4X仍是既有结构；当前只有一次末位回补，尚不能确认稳定承接。"),
    card("googlePlay", "Limbus Company", "entry", "回到Google #59，iOS未入榜。核心用户盘与角色内容可维持脉冲，但未找到与本次回榜同步的重大官方节点。"),
    card("googlePlay", "Game of Thrones: Conquest", "exit", "上期#57后Google掉榜，但iOS回到#35。10月15日2026_10更新与九周年仍在窗口，跨端分化不支持直接归因为活动。"),
    card("googlePlay", "Last Shelter: Survival", "exit", "上期Google #58后掉榜，iOS同名产品由#51微降至#52。这个2017—2018年上线的长期运营产品出现Android榜尾回落，但跨端不支持写成双端同步走弱。"),
    card("googlePlay", "Sea of Conquest", "exit", "上期回榜#60后再次掉榜，iOS未入榜。连续两个有效快照的末位进出更像榜尾轮换，不写成长线转弱。"),
    card("googlePlay", "Infinity Kingdom", "up", "Google上升8位至#28，iOS反向下跌2位至#26。最近可确认的v2.9.9节点已较早，无法解释周末后跨端分化；先按单期信号记录。"),
    card("googlePlay", "MARVEL SNAP", "up", "Google上升6位至#48，iOS反向下跌3位至#51。两端都在后段，未发现同步重大节点，当前只能视作平台节奏分化。"),
    card("googlePlay", "Age of Origins", "up", "Google上升5位至#24，iOS小跌1位至#19。成熟末日4X在两端仍处前中段，但没有可确认的当日活动证据，不能据此判断结构性增长。"),
    card("googlePlay", "Call of Dragons", "down", "Google下跌9位至#54，iOS未入榜。由#45退到后十名，暂记为留榜风险；未发现与今天同步的重大官方节点。"),
    card("googlePlay", "Arknights", "down", "Google下跌6位至#14，iOS位于#42。Episode 17仍在开放窗口，但两端都未延续上期方向，版本不等于榜位必然抬升。"),
    card("googlePlay", "Frost & Flame", "down", "Google下跌5位至#37，iOS未入榜。长期4X产品由中段回落，未对应到可确认的当天节点。"),
    card("googlePlay", "League of Legends", "down", "Google下跌5位至#53，iOS回榜#53。两端同位但路径不同，尚不能把iOS回榜解读为产品整体同步改善。"),
]


ios_products = [
    card("ios", "Game of Thrones: Conquest", "entry", "回到iOS #35，Google掉榜。九周年2026_10更新仍在窗口，但跨端反向说明应继续观察平台付费节奏，而非直接写成活动拉升。"),
    card("ios", "DC: Dark Legion", "entry", "回到iOS #41，Google未入榜。DC角色与地下基地经营回到中后段，尚无连续留榜证据。"),
    card("ios", "Star Trek Fleet Command", "entry", "回到iOS #50，Google当前#21。10月22日联盟锦标赛调整与10月23日万圣活动时间相邻，但iPhone端仍在后十名。"),
    card("ios", "League of Legends", "entry", "回到iOS #53，Google同产品#53。双端当前同位，但Google是下跌、iOS是回榜，不能视作一致上行。"),
    card("ios", "Last Day on Earth", "entry", "回到iOS #57，Google策略榜未入榜。本次仅是iPhone端榜尾回补，尚无跨端同步信号。"),
    card("ios", "Age of Spirits", "entry", "项目历史首次收录于iOS #58，Google#57。Apple Lookup上架日为9月15日，因此iOS独立归类为近90天新品；双端均在榜尾，仍处首发验证。", {"6805006706"}),
    card("ios", "Boom Beach", "entry", "回到iOS #59，Google未入榜。成熟基地攻防产品再次压线入榜，未形成连续后十名留位。"),
    card("ios", "Aliens vs Zombies", "entry", "回到iOS #60，Google#47。双端都在后段，iPhone端仅为末位回补，尚无稳定性证据。"),
    card("ios", "Coop TD", "exit", "上期回榜#36后本期掉榜，Google未入榜。一次中段回补未形成周末后的连续留位。"),
    card("ios", "Last Shelter: War Z", "exit", "上期回榜#50后本期掉榜，Google仍在#35。产品仍处首发验证，当前是iPhone端留榜风险而非双端同步走弱。"),
    card("ios", "Cell Survivor", "exit", "上期升至#52后本期掉榜，Google未入榜。2026年新作的后十名改善未能延续，继续按首发验证处理。"),
    card("ios", "Fire Emblem", "exit", "上期#53后掉榜。10.10.0武器精炼仍是近期内容背景，但没有形成连续后十名留位。"),
    card("ios", "Evo Defense", "exit", "上期#56后掉榜，Google未入榜。塔防产品的末位回补未延续，不推演长期走势。"),
    card("ios", "Sea War", "exit", "上期#57后掉榜，Google跌至#60。两端同时走弱但都处榜尾，仅可视作短期风险信号。"),
    card("ios", "Rise of Castles", "exit", "上期#58后掉榜，Google未入榜。成熟城建4X未形成连续榜尾留位。"),
    card("ios", "Infinite Borders", "exit", "上期首次收录#60后即掉榜。周年与例行更新没有形成连续留位，当前仍按一次末位信号归档。"),
    card("ios", "Mobile Legends", "up", "iOS上升18位至#17。10周年版本仍是当前内容背景，但其核心为MOBA，不能据商店策略标签把它纳入核心SLG趋势。"),
    card("ios", "PUBG MOBILE", "up", "iOS上升18位至#4。产品核心是战术竞技而非核心策略，本次只作为Apple策略榜边界产品的大幅波动记录。"),
    card("ios", "RAID", "up", "iOS上升9位至#32。10月20日11.85.5加入CvC目标、Faction Wars调整和英雄平衡，时间相邻但仍需后续快照确认。"),
    card("ios", "Dragon Traveler", "down", "iOS下跌21位至#49。10月21日1.9.0仍有新角色与活动，但上期跃升未保持，说明版本窗口内波动很大。"),
    card("ios", "Game of Thrones: Dragonfire", "down", "iOS下跌12位至#23，Google反向升至#33。Kalspire内容仍在近期窗口，跨端反向需继续验证。"),
    card("ios", "X-Clash", "down", "iOS下跌10位至#31，Google未入榜。仍在中段但单期回撤明显，未找到同步重大官方节点。"),
    card("ios", "Forge Master", "down", "iOS下跌10位至#37，Google当前#51。双端都处中后段，暂按周末后的单期回落记录。"),
    card("ios", "Star Wars", "down", "iOS下跌9位至#18。成熟角色收集盘仍在前20，单期回落不足以确认长线转弱。"),
    card("ios", "Hearthstone", "down", "iOS下跌9位至#34。Reign of the Black Empire已上线，本次继续回落，需要区分资料片首发峰值与稳定承接。"),
    card("ios", "Lords Mobile", "down", "iOS下跌9位至#48，Google#31。Heroic Saga于10月21日上线，但iPhone端未表现为持续上行。"),
]


news = [
    {
        "category": "原始部落4X / 新品", "date": "2026-10-19",
        "title": "Age of Spirits iOS 1.1.1更新，双端进入美国策略榜尾",
        "summary": "Apple美国区商品页显示产品9月15日上架、10月19日更新1.1.1；核心由篝火部落建设、居民分工、英雄远征和联盟世界地图构成。",
        "impact": f"产品本期首次进入项目iOS榜#{current_rank('ios', 'Age of Spirits')}，Google同期#{current_rank('googlePlay', 'Age of Spirits')}；两端均为近90天新品的榜尾信号。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/age-of-spirits/id6805006706",
    },
    {
        "category": "科幻4X / 联盟运营", "date": "2026-10-22",
        "title": "Star Trek Fleet Command调整联盟锦标赛并开启万圣活动",
        "summary": "官方确认10月23日联盟锦标赛回归并调整任务，11月将加入两日Rally；Division 12同时安排Trick or Treat、万圣Battle Pass与阶段奖励。",
        "impact": f"产品本期iOS回榜#{current_rank('ios', 'Star Trek')}、Google#{current_rank('googlePlay', 'Star Trek')}；活动与回榜相邻，但平台差距仍大。",
        "source": "Star Trek Fleet Command官方", "url": "https://startrekfleetcommand.com/news/alliance-tournaments-updates-october-2026/",
    },
    {
        "category": "IP 4X / 九周年", "date": "2026-10-15",
        "title": "Game of Thrones: Conquest 2026_10扩充研究树与操作优化",
        "summary": "官方九周年更新加入研究扩展、援军排序、配方收藏、书签分类、Dragon Lore计数及多项界面和性能修复。",
        "impact": f"产品本期iOS回榜#{current_rank('ios', 'Game of Thrones: Conquest')}、Google掉榜；跨端反向不支持把更新直接写成榜位拉升。",
        "source": "Game of Thrones: Conquest官方", "url": "https://www.gotconquest.com/news/2026/10/15/release-notes-2026_10/",
    },
    {
        "category": "卡牌策略 / 资料片", "date": "2026-10-23",
        "title": "Hearthstone 37.0更新上线Reign of the Black Empire",
        "summary": "Apple版本记录与Blizzard说明显示资料片加入Old Gods、Assemble关键词、新竞技场赛季和更新后的Journal。",
        "impact": f"产品本期iOS下跌至#{current_rank('ios', 'Hearthstone')}；需要继续区分资料片首发峰值回落和中期承接。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "4X / 英雄成长", "date": "2026-10-21",
        "title": "Lords Mobile 2.208上线Heroic Saga与Battle Spirit",
        "summary": "Apple官方版本记录确认Rank 8满装备英雄可觉醒Battle Spirit，并通过Heroic Saga任务获得Armament与强化资源。",
        "impact": f"产品本期iOS跌至#{current_rank('ios', 'Lords Mobile')}、Google#{current_rank('googlePlay', 'Lords Mobile')}；版本没有对应为双端同步上行。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/lords-mobile-kingdom-wars/id1071976327",
    },
    {
        "category": "角色策略RPG / 系统调整", "date": "2026-10-20",
        "title": "RAID 11.85.5调整CvC、Faction Wars与英雄平衡",
        "summary": "Apple版本记录列出Relic Craft & Upgrade锦标赛目标、Faction Wars Hard数值调整、Doom Tower展示扩充及英雄平衡。",
        "impact": f"产品本期iOS上升9位至#{current_rank('ios', 'RAID')}；时间相邻但单期升幅仍需后续留位确认。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/raid-shadow-legends/id1371565796",
    },
    {
        "category": "卡牌策略 / IP联动", "date": "2026-10-20",
        "title": "Magic: The Gathering Arena预热Star Trek联动",
        "summary": "Apple版本记录以Explore the Final Frontier为主题，开始预热Magic与Star Trek的跨IP内容。",
        "impact": f"产品当前iOS#{current_rank('ios', 'Magic')}；大型IP联动提供后续付费观察窗口，但本期仅上升5位，不写成已确认爆发。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/magic-the-gathering-arena/id1496227521",
    },
    {
        "category": "角色策略RPG / 首发运营", "date": "2026-10-21",
        "title": "Dragon Traveler 1.9.0加入Arachne与跨宇宙活动",
        "summary": "Apple版本记录加入SSR+ Arachne、限定召唤、Star Level奖励、新皮肤和登录奖励。",
        "impact": f"产品本期iOS反而下跌21位至#{current_rank('ios', 'Dragon Traveler')}，说明版本窗口不等于榜位持续上行。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/dragon-traveler/id6751086804",
    },
    {
        "category": "塔防RPG / 主线大版本", "date": "2026-10-21",
        "title": "Arknights Episode 17开放Extreme Mode",
        "summary": "官方Episode 17公告将Extreme Mode开放时间定在10月21日，章节活动、限定干员与兑换商店仍处开放期。",
        "impact": f"产品本期Google降至#{current_rank('googlePlay', 'Arknights')}、iOS#{current_rank('ios', 'Arknights')}；版本期内两端均未延续上期走势。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4814",
    },
    {
        "category": "全球市场 / 收入榜", "date": "2026-10",
        "title": "Sensor Tower最新官方全球收入榜仍为2026年9月",
        "summary": "官方9月全球手游收入TOP10的核心策略子集仍为Whiteout Survival #6、Last War #7与Kingshot #9；口径覆盖App Store和Google Play并排除第三方Android商店。",
        "impact": "本工作日的一次官方博客检查未发现更新一期完整图表，因此保留9月真实统计期；全球月榜不替代美国单区日榜。",
        "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google周末后仍较稳定，波动主要集中在中后段",
        "detail": "Google三进三出，57款共同产品中44款位移不超过2名；最大上行是Infinity Kingdom +8，最大下行是Call of Dragons −9，前三名没有变化。",
    },
    {
        "type": "判断", "title": "iOS八进八出且大幅重排，榜尾轮换与中段位移并存",
        "detail": "iOS仅52款共同产品，23款位移不超过2名；Mobile Legends与PUBG各+18，Dragon Traveler −21，八款入榜中只有GoT Conquest进入前40。",
    },
    {
        "type": "判断", "title": "新品信号集中在Age of Spirits，成熟盘仍主导收入榜面",
        "detail": "近90天新品为Google 2款、iOS 1款；Age of Spirits首次实现双端同时留榜但均在#57—58，尚处首发验证，其余主要变化仍来自成熟长线产品。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证八款iOS入榜产品的留榜率",
        "detail": "重点看GoT Conquest、Star Trek与Age of Spirits能否连续留榜；Boom Beach、Aliens vs Zombies若仍停在#59—60附近，继续按榜尾轮换处理。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：复核Age of Spirits的双端首发承接",
        "detail": "只有当Google与iOS同时脱离后十名，才进一步判断暗黑原始部落获量层是否有效承接城建、英雄远征和联盟4X。",
    },
    {
        "type": "关注", "title": "至10月30日：观察资料片和联盟活动能否形成连续付费",
        "detail": "关注Hearthstone能否止住资料片后的连续回落、Star Trek能否由联盟锦标赛与万圣活动脱离iOS后十名，以及Lords Mobile能否恢复双端接近。",
    },
]


google_history = load("data/history/google-play/2026-10-26.json")
ios_history = load("data/history/ios/2026-10-26.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Google三进三出保持稳定，iOS八进八出；Age of Spirits首次双端留榜",
    "summary": "较10月23日前一有效快照，Google Play三进三出，57款共同产品中44款位移不超过2名；Infinity Kingdom +8、Call of Dragons −9。iOS八进八出，Mobile Legends与PUBG各+18、Dragon Traveler −21。Age of Spirits首次进入项目iOS榜#58并与Google #57同时留榜。近90天新品为Google 2款、iOS 1款；两端缺少7月28日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261026.json",
    "rankingSources": {"googlePlay": "data/games-20261026.json", "ios": "data/ios-games-20261026.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261023.json", "ios": "data/ios-games-20261023.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Warline: Sniper Strike · #60 Sea War: Uboat Raid",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Top Force: Commander · #60 Aliens vs Zombies: Invasion",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-28"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-28"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-26.md", "json": "data/market-brief-20261026.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-23；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-28精确同口径TOP60基准，较老产品暂不判断飙升。",
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
        f"- 市场总览：全球手游消费者支出约${revenue['marketSummary']['globalConsumerSpendingUsd'] / 1_000_000_000:g}B，环比{revenue['marketSummary']['monthOverMonthPercent']:g}%，全市场同比（约）{revenue['marketSummary']['yearOverYearPercentApprox']:g}%",
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


save("data/market-brief-20261026.json", brief)
(ROOT / "reports/2026-10-26.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {
    "date": DATE,
    "title": brief["title"],
    "summary": brief["summary"],
    "markdown": brief["downloads"]["markdown"],
    "json": brief["downloads"]["json"],
}
manifest["updated"] = DATE
manifest["reports"] = sorted(
    [entry] + [item for item in manifest["reports"] if item["date"] != DATE],
    key=lambda item: item["date"], reverse=True,
)
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
