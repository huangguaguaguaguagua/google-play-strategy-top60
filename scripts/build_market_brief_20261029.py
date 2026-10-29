#!/usr/bin/env python3
"""Generate the Beijing 2026-10-29 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-29", "20261029"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261029.json"), "prior": load("data/games-20261028.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261029.json"), "prior": load("data/ios-games-20261028.json"), "id": "appId"},
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
    card("googlePlay", "Sea War", "entry", "回到Google #57；iOS同名产品本期未入榜。潜艇编队与海上基地只在Android榜尾回补，需下一快照确认留位。"),
    card("googlePlay", "Raid Rush", "entry", "回到Google #59，iOS同产品升至#39。塔防路径与英雄技能出现跨端同日改善，但Android仍压线入榜，当前只算待验证信号。"),
    card("googlePlay", "Vikings: War of Clans", "exit", "上期Google #58后掉榜，iOS未入榜。成熟维京4X未连续守住后十名，继续按榜尾轮换处理。"),
    card("googlePlay", "Call of Dragons", "exit", "上期Google #59后掉榜，iOS未入榜。奇幻自由行军与联盟围猎再次落出末段，不据单日掉榜判断长线退潮。"),
    card("googlePlay", "Stormshot", "up", "Google上升4位至#38，iOS未入榜。弹道谜题获量层与海岛4X盘出现单期回升，未发现可确认的同步重大节点。"),
    card("googlePlay", "Narco Empire", "up", "Google上升4位至#26。产品仍按7月31日Google released归类为近90天新品，本期改善不外推为成熟期趋势。"),
    card("googlePlay", "Duck Survival", "down", "Google下跌6位至#52，iOS未入榜。武装鸭子与昼建夜守已进入后十名，当前是榜尾风险信号。"),
    card("googlePlay", "Frost & Flame", "down", "Google下跌3位至#42，iOS未入榜。成熟城堡4X回到中后段，没有证据把变化归因于单一活动。"),
]


ios_products = [
    card("ios", "Last Shelter: Survival", "entry", "回到iOS #46，Google同名产品为#51。两端分别保留商店记录；本期只确认成熟末日SLG回到iPhone中后段。"),
    card("ios", "Age of Spirits", "entry", "回到iOS #59，Google同产品升至#54。9月上架的近90天新品再次双端同榜，但iPhone仍在掉榜线附近。"),
    card("ios", "Avatar: Realms Collide", "entry", "项目历史首次收录于iOS #60。Apple显示2025年上架；10月SvS预赛仍在窗口，但末位入榜只作待验证信号。", {"6479603752"}),
    card("ios", "Boom Beach", "exit", "上期iOS #51后掉榜，Google未入榜。10月Blitz之后的回落延续到榜外，仍需更多快照区分活动峰值与常态。"),
    card("ios", "Kingdom Clash", "exit", "上期iOS #52后掉榜，Google未入榜。中世纪塔防与英雄养成未连续守住后十名，按榜尾轮换处理。"),
    card("ios", "West Game", "exit", "上期首次项目收录于iOS #58后即掉榜。西部城镇与联盟SLG未形成连续留位，不把短暂回补写成长线复苏。"),
    card("ios", "Summoners War", "up", "iOS上升14位至#41。成熟魔灵盘由后十名回到中后段，9.3.6版本仍是近期背景，但单日跃升不等于收入增长。"),
    card("ios", "Forge Master", "up", "iOS上升9位至#26，Google同产品为#50。iPhone端明显领先Android，需下一快照验证是否只是平台活动节奏。"),
    card("ios", "Arknights", "up", "iOS上升7位至#32，Google为#24。Episode 17限时窗口刚结束，本次只记录活动后单期改善。"),
    card("ios", "Raid Rush", "up", "iOS上升6位至#39，Google同日回榜#59。双端同向改善但Android仍在榜尾，尚不足以确认共同驱动。"),
    card("ios", "Plants on Fire", "down", "iOS下跌10位至#42。8月上架的近90天新品仍在中后段，本期回吐不改变新品分类。"),
    card("ios", "Last Shelter: War Z", "down", "iOS下跌9位至#57。2026年6月上架的地下庇护所产品接近掉榜线，需验证首发期承接。"),
    card("ios", "The Tower", "down", "iOS下跌9位至#50。永久研究、卡牌和锦标赛构成成熟盘，本次只记为中后段回落。"),
    card("ios", "Game of Thrones: Conquest", "down", "iOS下跌8位至#35，Google为#42。九周年2026_10仍在近期窗口，但双端没有同步抬升。"),
    card("ios", "Lands of Jail", "down", "iOS下跌8位至#38，Google为#29。前一日双端同步上行未在iPhone端延续，活动峰值判断仍待验证。"),
]


news = [
    {
        "category": "IP 4X / 跨服运营", "date": "2026-10-28",
        "title": "Avatar: Realms Collide在SvS预赛窗口更新1.8.1034",
        "summary": "Apple Lookup记录10月28日更新；官方版本资料显示Glowworm's Ruse预赛持续至10月30日，并加入World Migration、Accessory装备位及城防规则调整。",
        "impact": f"产品首次进入项目iOS榜#{current_rank('ios', 'Avatar: Realms Collide')}；活动与末位入榜时间相邻，但没有证据证明其单独造成榜位变化。",
        "source": "Apple App Store与Tilting Point官方", "url": "https://apps.apple.com/us/app/avatar-realms-collide/id6479603752",
    },
    {
        "category": "冰雪城建 / 节日运营", "date": "2026-10-27",
        "title": "Whiteout Survival万圣活动正式开启",
        "summary": "活动资料列出10月27日至11月2日的Halloween Party、Pumpkin Invasion、Nightmare Pumpkin King与阶段奖励，Kasia's Wish House于10月28日开启；来源为跟踪官方游戏内公告的社区资料。",
        "impact": f"产品当前Google#{current_rank('googlePlay', 'Whiteout')}、iOS#{current_rank('ios', 'Whiteout')}，仍居双端榜首；活动与名次时间相邻，但不写成唯一原因。",
        "source": "Whiteout Survival Wiki（社区转录）", "url": "https://www.whiteoutsurvival.wiki/sneak-peek/102514638en/",
    },
    {
        "category": "IP 4X / 九周年", "date": "2026-10-15",
        "title": "Game of Thrones: Conquest 2026_10扩充研究树与操作优化",
        "summary": "官方九周年更新加入研究扩展、援军排序、配方收藏、书签分类、Dragon Lore计数及多项界面和性能修复。",
        "impact": f"产品当前Google#{current_rank('googlePlay', 'Game of Thrones: Conquest')}、iOS#{current_rank('ios', 'Game of Thrones: Conquest')}，本期iPhone端回落；更新窗口不能替代平台榜面。",
        "source": "Game of Thrones: Conquest官方", "url": "https://www.gotconquest.com/news/2026/10/15/release-notes-2026_10/",
    },
    {
        "category": "科幻4X / 联盟运营", "date": "2026-10-22",
        "title": "Star Trek Fleet Command调整联盟锦标赛并公布11月Rally",
        "summary": "官方确认Alliance Tournaments于10月23日回归并调整任务；11月9日至11日将测试两日Rally，以较短周期复用任务和个人奖励。",
        "impact": "产品iOS仍未入榜、Google继续留榜；联盟运营节点没有对应为双端同步改善，需分平台观察。",
        "source": "Star Trek Fleet Command官方", "url": "https://startrekfleetcommand.com/news/alliance-tournaments-updates-october-2026/",
    },
    {
        "category": "卡牌策略 / 资料片", "date": "2026-10-12",
        "title": "Hearthstone 37.0与Reign of the Black Empire资料片落地",
        "summary": "Blizzard官方37.0说明确认10月20日开放135张卡的Reign of the Black Empire，引入Assemble关键词并刷新Rewards Track。",
        "impact": f"产品本期iOS#{current_rank('ios', 'Hearthstone')}；观察资料片首发峰值后能否在未来1—2个快照稳定承接。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "塔防RPG / 主线大版本", "date": "2026-10-09",
        "title": "Arknights Episode 17进入Extreme Mode收尾窗口",
        "summary": "官方Episode 17公告将Extreme Mode开放时间定为10月21日，并说明限时较低解锁门槛与Factory scrip掉落于10月28日结束。",
        "impact": f"产品当前Google#{current_rank('googlePlay', 'Arknights')}、iOS#{current_rank('ios', 'Arknights')}；活动后iOS单日上升7位仍需连续快照验证。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4814",
    },
    {
        "category": "实时PvP / 新品", "date": "2026-10-15",
        "title": "Plants on Fire 2.0.2870加入Pirate Captain与Ace Plan",
        "summary": "Apple版本资料显示该更新加入新传奇卡Pirate Captain、新植物和四种变体、Ace Plan活动与Auto Chess相关内容。",
        "impact": f"产品本期下跌10位至iOS#{current_rank('ios', 'Plants on Fire')}，仍按8月26日releaseDate归类为近90天新品；版本后承接需继续验证。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/plants-on-fire/id6776076449",
    },
    {
        "category": "海战SLG / 回归运营", "date": "2026-10-21",
        "title": "Sea War 1.175.0加入精英招募角色与回归福利",
        "summary": "Apple版本记录列出两名精英招募角色与回归指挥官福利，继续围绕舰长、潜艇编队和海上基地运营。",
        "impact": f"iOS本期未入榜，Google同名产品回到#{current_rank('googlePlay', 'Sea War')}；版本节点没有形成跨端同步。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/sea-war-uboat-raid/id6447612873",
    },
    {
        "category": "基地攻防 / 竞技活动", "date": "2026-09-15",
        "title": "Boom Beach Blitz活动后的榜位回吐进入观察期",
        "summary": "Supercell官方9月更新介绍Blitz竞争型Leader活动，10月2日开启，以Leader构筑和挑战扩展成熟基地攻防循环。",
        "impact": "产品本期从iOS掉榜、Google未入榜；需观察活动后是否回补，不能由相邻两次回落直接判断长线衰退。",
        "source": "Supercell官方", "url": "https://supercell.com/en/games/boombeach/blog/blog/september-update-blitz/",
    },
    {
        "category": "全球市场 / 收入榜", "date": "2026-10-01",
        "title": "Sensor Tower最新完整全球收入榜仍为2026年9月",
        "summary": "官方9月全球手游收入TOP10的核心策略子集仍为Whiteout Survival #6、Last War #7与Kingshot #9；口径覆盖App Store和Google Play并排除第三方Android商店。",
        "impact": "本工作日仅检查一次官方博客，未发现更新一期完整图表，因此保留9月真实统计期；全球月榜不替代美国单区日榜。",
        "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Whiteout Survival双端升至榜首，Google主体仍稳定",
        "detail": "Whiteout Survival在Google和iOS均由#2升至#1；Kingshot在Google退至#2、iOS退至#3。Google两进两出，58款共同产品中52款位移不超过2名，波动仍集中在榜尾。",
    },
    {
        "type": "判断", "title": "iOS中后段波动明显高于Google，跨端同步只见于少数产品",
        "detail": "iOS三进三出，57款共同产品中35款位移不超过2名；Summoners War +14至#41、Plants on Fire −10至#42。Raid Rush则Google回榜#59、iOS +6至#39，仍只是单日同步信号。",
    },
    {
        "type": "判断", "title": "近90天新品集中于少数产品，精确90天飙升仍不判定",
        "detail": "Google新品为Top Force #15、Age of Spirits #54、Last Human #58；iOS新品为Plants on Fire #42、Age of Spirits #59。两端缺少2026-07-31精确同口径完整基准，因此较老产品内部pending、页面按常规展示。",
    },
    {
        "type": "关注", "title": "下一有效快照：核验五款进入/回榜产品的留位",
        "detail": "观察Google的Sea War #57、Raid Rush #59，以及iOS的Last Shelter: Survival #46、Age of Spirits #59、Avatar #60；若快速退出，继续按榜尾轮换或首发验证记录。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：复核iOS大幅升降与榜尾风险",
        "detail": "重点看Summoners War +14、Forge Master +9能否保持，以及Plants on Fire −10、Last Shelter: War Z −9、The Tower −9是否继续下探；单日异动不直接解释为收入趋势。",
    },
    {
        "type": "关注", "title": "至10月30日及11月2日：分开核验Avatar与Whiteout活动窗口",
        "detail": "Avatar的Glowworm's Ruse预赛至10月30日、Whiteout万圣活动至11月2日；分别观察Avatar能否离开#60与Whiteout能否双端守住#1，活动时间只作验证条件，不作确定因果。",
    },
]
google_history = load("data/history/google-play/2026-10-29.json")
ios_history = load("data/history/ios/2026-10-29.json")
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
    "title": "Whiteout Survival双端升至榜首；Google两进两出，iOS三进三出",
    "summary": "较10月28日前一有效快照，Google Play两进两出，58款共同产品中52款位移不超过2名；Sea War与Raid Rush在#57/#59回榜，Duck Survival −6至#52。iOS三进三出，Summoners War +14、Forge Master +9，Plants on Fire −10；Avatar: Realms Collide首次项目收录于#60。Google近90天新品3款、iOS 2款；两端缺少7月31日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261029.json",
    "rankingSources": {"googlePlay": "data/games-20261029.json", "ios": "data/ios-games-20261029.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261028.json", "ios": "data/ios-games-20261028.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Warline: Sniper Strike · #60 Supremacy: World War 3",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Castle Busters · #60 Avatar: Realms Collide",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-31"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-31"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-29.md", "json": "data/market-brief-20261029.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-28；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-31精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261029.json", brief)
(ROOT / "reports/2026-10-29.md").write_text(build_markdown(brief), encoding="utf-8")
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
