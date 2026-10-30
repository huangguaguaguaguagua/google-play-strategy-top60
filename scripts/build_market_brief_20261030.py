#!/usr/bin/env python3
"""Generate the Beijing 2026-10-30 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-30", "20261030"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261030.json"), "prior": load("data/games-20261029.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261030.json"), "prior": load("data/ios-games-20261029.json"), "id": "appId"},
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
        icon = game.get("iconData") or local[store].get(f"{rank}_icon") or local[store].get(f"{rank:02d}_icon")
        if not icon or not icon.startswith("data:image/"):
            raise RuntimeError(f"No local icon for {item['iconKey']}")
        bundle[item["iconKey"]] = icon
    if len(bundle) != len(products):
        raise RuntimeError("Duplicate market-card product keys")
    save(f"assets/market-icons-{STAMP}.json", bundle, compact=True)
    return bundle


google_products = [
    card("googlePlay", "Kiss of War", "entry", "回到Google #54，iOS同产品上升10位至#39。军事SLG出现双端同日改善，但Android仍处后十名，当前只作待验证信号。"),
    card("googlePlay", "West Game", "entry", "项目首次收录于Google #56；iOS本期未入榜。Google商品页显示2019年上架，按成熟西部SLG的榜尾回补观察。", {"leyi.westgame"}),
    card("googlePlay", "League of Legends", "exit", "上期Google #56后掉榜，iOS未入榜。MOBA产品在策略分类榜尾未连续留位，不据单次掉榜判断核心市场走势。"),
    card("googlePlay", "Supremacy: World War 3", "exit", "上期Google #60后掉榜，iOS同产品仍位于#43。Android末位退出与iPhone中后段留榜形成平台分化。"),
    card("googlePlay", "Sea War", "up", "Google上升9位至#48，iOS同步上升6位至#28。潜艇编队与海上基地出现双端改善，但仍需下一快照确认持续性。"),
    card("googlePlay", "Warline", "up", "Google上升5位至#20，iOS上升3位至#44。双端同向但名次层级差异较大，不将单日位移直接解释为版本拉升。"),
    card("googlePlay", "Game of Thrones: Conquest", "up", "Google上升4位至#36，iOS反向下跌3位至#38。九周年更新仍是近期背景，但跨端反向不足以支持确定因果。"),
    card("googlePlay", "Last Shelter: War Z", "up", "Google上升4位至#28，iOS同步上升7位至#50。地下庇护所产品双端改善，但iPhone仍在后十名附近。"),
    card("googlePlay", "Duck Survival", "down", "Google下跌7位至#59，iOS未入榜。武装鸭子与昼建夜守已接近掉榜线，属于明确榜尾风险信号。"),
    card("googlePlay", "Lords Mobile", "down", "Google下跌5位至#33，iOS同步下跌5位至#60。成熟联盟4X两端同向回落，iPhone已压线留榜。"),
    card("googlePlay", "Overgeared", "down", "Google下跌5位至#42，iOS同步下跌3位至#57。背包合成与放置RPG双端同向回落，iPhone已接近榜尾。"),
    card("googlePlay", "Clash Royale", "down", "Google下跌4位至#25，iOS下跌3位至#14。双端同向回落但仍在各自中前段，不外推为长线衰退。"),
]


ios_products = [
    card("ios", "Limbus Company", "entry", "回到iOS #35，Google本期未入榜。10月29日定期更新与回榜时间相邻，但只能记录为待验证信号。"),
    card("ios", "Last Fortress", "entry", "回到iOS #55，Google未入榜。地下堡垒与幸存者经营重新压线进入，需下一快照确认留位。"),
    card("ios", "Last Day on Earth", "entry", "回到iOS #56，Google未入榜。成熟生存产品回到后十名，当前按榜尾轮换处理。"),
    card("ios", "GIRLS' FRONTLINE 2", "entry", "回到iOS #58，Google未入榜。战棋与角色活动盘仅在iPhone末段回补，尚不足以确认持续改善。"),
    card("ios", "Kingdom Guard", "entry", "回到iOS #59，Google未入榜。塔防获量与联盟SLG再次压线进入，仍属掉榜线附近信号。"),
    card("ios", "The Tower", "exit", "上期iOS #50后掉榜，Google未入榜。永久研究、卡牌和锦标赛构成的成熟盘未连续守住中后段。"),
    card("ios", "Evo Defense", "exit", "上期iOS #56后掉榜，Google未入榜。合成与塔防产品未连续守住后十名，按榜尾轮换记录。"),
    card("ios", "Hearthstone", "exit", "上期iOS #58后掉榜，Google未入榜。资料片首发窗口后的末段留位未延续，不据此判断长线表现。"),
    card("ios", "Age of Spirits", "exit", "上期iOS #59后掉榜，Google仍位于#55。9月上架的新品转为Android单端留榜，需继续验证首发承接。"),
    card("ios", "Avatar: Realms Collide", "exit", "上期首次项目收录于iOS #60后即掉榜，Google未入榜。SvS预赛结束附近的短暂入榜未形成连续留位。"),
    card("ios", "Dragon Traveler", "up", "iOS上升12位至#41，Google未入榜。卡通放置RPG回到中后段，但单日跳升不等于收入增长。"),
    card("ios", "Kiss of War", "up", "iOS上升10位至#39，Google同日回榜#54。双端同向改善，但Android仍在榜尾。"),
    card("ios", "Last Shelter: War Z", "up", "iOS上升7位至#50，Google同步上升4位至#28。双端改善但平台层级差异仍大。"),
    card("ios", "Foundation", "up", "iOS上升6位至#31，Google位于#32。两端名次接近，但需连续快照确认是否形成共同信号。"),
    card("ios", "Sea War", "up", "iOS上升6位至#28，Google同步上升9位至#48。海战SLG双端改善，是本日最清晰的共同位移之一。"),
    card("ios", "Arknights", "down", "iOS下跌14位至#46，Google持平于#17。10月28日新活动开启后两端表现分化，不能把节点写成统一拉升。"),
    card("ios", "Last Shelter: Survival", "down", "iOS下跌7位至#53，Google持平于#51。成熟末日SLG两端均处后十名附近，榜尾风险上升。"),
    card("ios", "Lords Mobile", "down", "iOS下跌5位至#60，Google同步下跌5位至#33。成熟联盟4X两端同向回落，iPhone已压线留榜。"),
    card("ios", "Plants on Fire", "down", "iOS下跌5位至#47，Google未入榜。8月上架的近90天新品继续回吐，但新品分类不变。"),
]


news = [
    {
        "category": "战术RPG / 定期更新", "date": "2026-10-29",
        "title": "Limbus Company完成10月29日定期更新",
        "summary": "Project Moon官方Steam动态记录10月29日定期更新；本期iOS同名产品回榜#35。更新节点与回榜时间相邻，但公开资料不能证明单一因果。",
        "impact": "Limbus Company回到iOS中段而Google未入榜；下一有效快照将验证是更新窗口的短期回补，还是能形成连续留位。",
        "source": "Project Moon官方Steam页面", "url": "https://store.steampowered.com/app/1973530/Limbus_Company/",
    },
    {
        "category": "塔防RPG / 活动运营", "date": "2026-10-28",
        "title": "Arknights开启Reclamation Algorithm限时活动",
        "summary": "官方公告显示Reclamation Algorithm活动及Orienteering定向寻访于10月28日开启，寻访窗口持续至11月11日。",
        "impact": f"产品本期Google持平于#{current_rank('googlePlay', 'Arknights')}、iOS下跌14位至#{current_rank('ios', 'Arknights')}；事件后平台表现分化，不能写成统一拉升。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4980",
    },
    {
        "category": "冰雪城建 / 节日运营", "date": "2026-10-27",
        "title": "Whiteout Survival万圣活动进入主窗口",
        "summary": "跟踪游戏内公告的社区资料列出10月27日至11月2日的Halloween Party、Pumpkin Invasion和Nightmare Pumpkin King等活动。",
        "impact": f"产品当前Google#{current_rank('googlePlay', 'Whiteout')}、iOS#{current_rank('ios', 'Whiteout')}，继续双端榜首；活动与榜位时间相邻，但不写成唯一原因。",
        "source": "Whiteout Survival Wiki（社区转录）", "url": "https://www.whiteoutsurvival.wiki/sneak-peek/102514638en/",
    },
    {
        "category": "海战SLG / 回归运营", "date": "2026-10-21",
        "title": "Sea War 1.175.0加入精英招募角色与回归福利",
        "summary": "Apple版本记录列出两名精英招募角色与回归指挥官福利，继续围绕舰长、潜艇编队和海上基地运营。",
        "impact": f"产品本期Google上升9位至#{current_rank('googlePlay', 'Sea War')}、iOS上升6位至#{current_rank('ios', 'Sea War')}；这是本日较清晰的双端共同信号，仍待连续快照确认。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/sea-war-uboat-raid/id6447612873",
    },
    {
        "category": "IP 4X / 九周年", "date": "2026-10-15",
        "title": "Game of Thrones: Conquest 2026_10扩充研究树与操作优化",
        "summary": "官方九周年更新加入研究扩展、援军排序、配方收藏、书签分类、Dragon Lore计数及多项界面和性能修复。",
        "impact": f"产品本期Google上升4位至#{current_rank('googlePlay', 'Game of Thrones: Conquest')}、iOS下跌3位至#{current_rank('ios', 'Game of Thrones: Conquest')}；跨端反向不足以支持确定因果。",
        "source": "Game of Thrones: Conquest官方", "url": "https://www.gotconquest.com/news/2026/10/15/release-notes-2026_10/",
    },
    {
        "category": "科幻4X / 联盟运营", "date": "2026-10-22",
        "title": "Star Trek Fleet Command调整联盟锦标赛并公布11月Rally",
        "summary": "官方确认Alliance Tournaments于10月23日回归并调整任务；11月9日至11日将测试两日Rally。",
        "impact": f"产品当前Google#{current_rank('googlePlay', 'Star Trek')}、iOS未入榜；联盟运营节点尚未对应为双端同步改善。",
        "source": "Star Trek Fleet Command官方", "url": "https://startrekfleetcommand.com/news/alliance-tournaments-updates-october-2026/",
    },
    {
        "category": "实时PvP / 新品", "date": "2026-10-15",
        "title": "Plants on Fire 2.0.2870加入Pirate Captain与Ace Plan",
        "summary": "Apple版本资料显示该更新加入新传奇卡Pirate Captain、新植物和四种变体、Ace Plan活动与Auto Chess相关内容。",
        "impact": f"产品本期下跌5位至iOS#{current_rank('ios', 'Plants on Fire')}，仍按8月26日releaseDate归类为近90天新品；版本后承接需继续验证。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/plants-on-fire/id6776076449",
    },
    {
        "category": "西部SLG / 成熟产品回补", "date": "2026-10-22",
        "title": "West Game更新后首次进入项目Google榜",
        "summary": "Google美国区商品页记录West Game于10月22日更新；产品2019年上架，本期首次进入项目Google记录#56。",
        "impact": "这是项目记录层面的首次收录，不等于新品；iOS本期未入榜，先按成熟产品的Android榜尾回补观察。",
        "source": "Google Play美国区商品页", "url": "https://play.google.com/store/apps/details?id=leyi.westgame&hl=en_US&gl=US",
    },
    {
        "category": "卡牌策略 / 资料片", "date": "2026-10-20",
        "title": "Hearthstone 37.0资料片窗口后退出iOS TOP60",
        "summary": "Blizzard官方37.0说明确认10月20日开放135张卡的Reign of the Black Empire，引入Assemble关键词并刷新Rewards Track。",
        "impact": "产品上期iOS #58、本期掉榜，Google也未入榜；只能记录为首发窗口后未连续留位，不能外推长线收入。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
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
        "type": "判断", "title": "Google两进两出，主体稳定但中后段位移放大",
        "detail": "Google有Kiss of War回榜、West Game首次项目收录，并由Wild Rift与Supremacy退出；58款共同产品中46款位移不超过2名。Sea War +9与Duck Survival −7说明波动不只发生在最后两席。",
    },
    {
        "type": "判断", "title": "iOS五进五出，波动显著高于Google",
        "detail": "iOS有5款进入/回榜、5款掉榜，55款共同产品中只有31款位移不超过2名；Dragon Traveler +12与Arknights −14形成两端极值，榜尾轮换也更密集。",
    },
    {
        "type": "判断", "title": "双端共同上扬集中于少数产品，90天状态保持克制",
        "detail": "Sea War、Kiss of War与Last Shelter: War Z双端同向改善；Arknights则Google持平、iOS −14。Google近90天新品仅Age of Spirits与Last Human，iOS仅Plants on Fire；两端仍无可判定的90天飙升。",
    },
    {
        "type": "关注", "title": "下一有效快照：核验七款进入/回榜产品的留位",
        "detail": "观察Google的Kiss of War #54、West Game #56，以及iOS的Limbus Company #35、Last Fortress #55、Last Day on Earth #56、GFL2 #58、Kingdom Guard #59；快速退出则继续按榜尾轮换或短期回补记录。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：复核双端同向与榜尾风险",
        "detail": "重点看Sea War、Kiss of War、Last Shelter: War Z能否延续双端改善，以及Duck Survival #59、Lords Mobile iOS #60、Last Shelter: Survival iOS #53是否继续下探。",
    },
    {
        "type": "关注", "title": "至11月2日与11月11日：分开核验活动窗口",
        "detail": "Whiteout万圣活动预计至11月2日，Arknights定向寻访至11月11日；另看Limbus在10月29日更新后的留位。时间窗口只作验证条件，不把相邻事件写成确定榜位原因。",
    },
]
google_history = load("data/history/google-play/2026-10-30.json")
ios_history = load("data/history/ios/2026-10-30.json")
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
    "title": "Google两进两出、iOS五进五出；Sea War双端上扬",
    "summary": "较10月29日前一有效快照，Google Play两进两出，58款共同产品中46款位移不超过2名；Sea War +9、Duck Survival −7，West Game首次进入项目Google记录。iOS五进五出，Dragon Traveler +12、Arknights −14；Sea War双端同向上升，Arknights在Google持平、iOS回落。Google近90天新品2款、iOS 1款；两端缺少8月1日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261030.json",
    "rankingSources": {"googlePlay": "data/games-20261030.json", "ios": "data/ios-games-20261030.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261029.json", "ios": "data/ios-games-20261029.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Clash Royale · #60 Raid Rush: Tower Defense TD",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Castle Busters · #60 Lords Mobile: Kingdom Wars",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-08-01"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-08-01"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-30.md", "json": "data/market-brief-20261030.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-29；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-08-01精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261030.json", brief)
(ROOT / "reports/2026-10-30.md").write_text(build_markdown(brief), encoding="utf-8")
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
