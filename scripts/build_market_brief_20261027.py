#!/usr/bin/env python3
"""Generate the Beijing 2026-10-27 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-27", "20261027"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261027.json"), "prior": load("data/games-20261026.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261027.json"), "prior": load("data/ios-games-20261026.json"), "id": "appId"},
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
    card("googlePlay", "Last Shelter: Survival", "entry", "回到Google #48，iOS同名长期产品#59。两端均处后段，仅能确认Android回补，不能写成双端同步改善。"),
    card("googlePlay", "DC: Dark Legion", "entry", "回到Google #50，iOS#44。DC角色和地下基地经营双端同时留榜，但名次都在中后段，仍需连续快照确认。"),
    card("googlePlay", "Game of Thrones: Conquest", "entry", "回到Google #57，iOS升至#22。九周年2026_10更新仍在窗口，但两端强度差异明显，不能把Android末段回榜直接归因于活动。"),
    card("googlePlay", "Last Fortress", "entry", "回到Google #58，iOS未入榜。地下庇护所与联盟4X再次压线进入，未发现与今天同步的重大官方节点。"),
    card("googlePlay", "Last Human", "entry", "项目历史首次收录于Google #59，iOS未入榜。Google本店8月19日released落在90天窗口内，归类为近三个月新品；射击层如何承接庇护所与联盟SLG仍待验证。", {"com.avenue.zombie.gp"}),
    card("googlePlay", "Age of Empires", "exit", "上期Google #39后掉榜，但iOS回到#56。跨端反向说明这是平台节奏分化，不能写成产品整体走弱。"),
    card("googlePlay", "MARVEL SNAP", "exit", "上期Google #48后掉榜，iOS当前#53。两端都处后段，暂记为Android榜尾风险，不延伸为长线结论。"),
    card("googlePlay", "Ant Legion", "exit", "上期回榜#58后再次掉榜，iOS未入榜。连续两次末位进出更接近榜尾轮换。"),
    card("googlePlay", "Limbus Company", "exit", "上期回榜#59后掉榜，iOS未入榜。核心用户盘的单次回补没有形成连续留位。"),
    card("googlePlay", "Sea War", "exit", "上期跌至#60后本期掉榜，iOS同样未入榜。当前是双端榜外状态，但仍不据两个快照判断长期衰退。"),
    card("googlePlay", "Rise of Castles", "up", "Google上升17位至#25，iOS未入榜。Google商品页近期版本节点没有足够细节解释全部升幅，先记录为显著单期信号。"),
    card("googlePlay", "Infinity Kingdom", "up", "Google连续第二个有效快照上升，本期再+10至#18；iOS反向跌至#31。Android持续改善与跨端分化并存，需继续验证。"),
    card("googlePlay", "Stormshot", "up", "Google上升9位至#40，iOS未入榜。弹道解谜入口与海岛4X仍是既有结构，未找到同步重大节点。"),
    card("googlePlay", "Rise of Kingdoms", "up", "Google上升7位至#19，iOS#33。成熟文明4X两端仍处前中段，但单日名次不能替代收入判断。"),
    card("googlePlay", "Lands of Jail", "down", "Google下跌11位至#33，iOS反向升至#39。两端名次接近但方向相反，暂按平台节奏分化处理。"),
    card("googlePlay", "Top Girl", "down", "Google下跌8位至#28，iOS未入榜。仍在中段，未发现可确认的同步重大版本节点。"),
    card("googlePlay", "Palmon", "down", "Google下跌6位至#24，iOS未入榜。奇幻生物经营与联盟4X仍在前中段，单期回撤不足以确认结构变化。"),
    card("googlePlay", "Call of Dragons", "down", "Google再跌6位至#60，iOS未入榜。产品已落到末位，下一有效快照需重点验证是否掉榜。"),
]


ios_products = [
    card("ios", "Galaxy Defense", "entry", "回到iOS #47，Google未入榜。科幻塔防回到后段，当前只有一次回补，尚无连续留榜证据。"),
    card("ios", "Kingdom Guard", "entry", "回到iOS #48，Google未入榜。塔防合成与联盟循环再次进入后段，先按榜尾回补处理。"),
    card("ios", "Age of Empires", "entry", "回到iOS #56而Google掉榜。经典文明IP在iPhone端压线回补，跨端反向不支持写成整体上行。"),
    card("ios", "League of Legends", "exit", "上期回榜#53后掉榜，Google当前#54。两端都在榜尾附近，iPhone端回补没有延续。"),
    card("ios", "Top Heroes", "exit", "上期#55后掉榜，Google#37。iOS末段留位中断，但Android仍在中段，不写成双端同步转弱。"),
    card("ios", "Last Day on Earth", "exit", "上期回榜#57后掉榜，Google策略榜未收录。本次仍是iPhone榜尾轮换，没有跨端信号。"),
    card("ios", "Boom Beach", "up", "iOS上升22位至#37，Google未入榜。官方Blitz更新仍是近期背景，但不足以单独解释整段升幅，需观察活动后留位。"),
    card("ios", "Warhammer 40,000", "up", "iOS上升22位至#32，Google#43。10月生存活动与Battle Pass时间相邻，但单期跃升仍需后续确认。"),
    card("ios", "X-Clash", "up", "iOS上升19位至#12，Google未入榜。由中段进入前15是显著单期信号，未找到足以确认因果的官方节点。"),
    card("ios", "Game of Thrones: Conquest", "up", "iOS上升13位至#22，Google回榜#57。九周年更新仍在窗口，两端改善但强度差异较大。"),
    card("ios", "Hearthstone", "down", "iOS下跌17位至#51。Reign of the Black Empire资料片已上线，本期继续回落，需区分首发峰值与稳定承接。"),
    card("ios", "Overgeared", "down", "iOS下跌9位至#54，Google#36。双端差距扩大，未发现与今天同步的重大节点。"),
    card("ios", "Mobile Legends", "down", "iOS下跌7位至#24，Google未入策略榜。其核心是MOBA，本次仅作为Apple策略标签边界产品的波动记录。"),
    card("ios", "Lords Mobile", "down", "iOS再跌7位至#55，Google反向升至#26。Heroic Saga仍在近期窗口，但版本没有对应为双端同步上行。"),
    card("ios", "Last Shelter: Survival", "down", "iOS下跌7位至#59，Google同名产品回榜#48。两端当前均在后段且方向不同，继续按平台分化处理。"),
]


news = [
    {
        "category": "冰雪城建 / 节日运营", "date": "2026-10-26",
        "title": "Whiteout Survival万圣活动窗口开启，双端同时登顶",
        "summary": "近期活动资料显示Halloween Party与Pumpkin Invasion于10月27日前后开启，包含Pumpkin Fiend、Nightmare Pumpkin King与阶段奖励；该信息来自跟踪游戏公告的媒体/社区资料。",
        "impact": f"产品本期Google升至#{current_rank('googlePlay', 'Whiteout')}、iOS保持#{current_rank('ios', 'Whiteout')}；活动与双端榜首时间相邻，但仍不写成唯一原因。",
        "source": "Out of Games（报道）", "url": "https://outof.games/news/10205-new-halloween-season-coming-to-whiteout-survival-next-week/",
    },
    {
        "category": "丧尸生存 / 新品", "date": "2026-10-19",
        "title": "Last Human: Final Stand完成10月商品页更新并首次进入Google TOP60",
        "summary": "Google美国区商品页显示产品8月19日上架、10月19日更新；入口为尸潮射击，长期结构包含庇护所建设、英雄编队、废土探索与联盟资源争夺。",
        "impact": f"本期首次进入项目Google榜#{current_rank('googlePlay', 'Last Human')}并归类为近90天新品；当前仍在榜尾，需验证射击获量层能否承接SLG循环。",
        "source": "Google Play美国区商品页", "url": "https://play.google.com/store/apps/details?id=com.avenue.zombie.gp&hl=en_US&gl=US",
    },
    {
        "category": "基地攻防 / 竞技活动", "date": "2026-09-15",
        "title": "Boom Beach上线Blitz竞争型Leader活动",
        "summary": "Supercell官方9月更新介绍Blitz，活动从10月2日开启，围绕Leader构筑与竞争挑战扩展成熟基地攻防循环。",
        "impact": f"产品本期iOS上升22位至#{current_rank('ios', 'Boom Beach')}；活动仍是近期运营背景，但需要活动后快照判断留位。",
        "source": "Supercell官方", "url": "https://supercell.com/en/games/boombeach/blog/blog/september-update-blitz/",
    },
    {
        "category": "IP 4X / 九周年", "date": "2026-10-15",
        "title": "Game of Thrones: Conquest 2026_10扩充研究树与操作优化",
        "summary": "官方九周年更新加入研究扩展、援军排序、配方收藏、书签分类、Dragon Lore计数及多项界面和性能修复。",
        "impact": f"产品本期iOS升至#{current_rank('ios', 'Game of Thrones: Conquest')}、Google回榜#{current_rank('googlePlay', 'Game of Thrones: Conquest')}；两端改善但不能由单次快照确认活动因果。",
        "source": "Game of Thrones: Conquest官方", "url": "https://www.gotconquest.com/news/2026/10/15/release-notes-2026_10/",
    },
    {
        "category": "科幻4X / 联盟运营", "date": "2026-10-22",
        "title": "Star Trek Fleet Command调整联盟锦标赛并安排11月Rally",
        "summary": "官方确认联盟锦标赛于10月23日回归并调整任务，11月将加入两日Rally，为联盟协作与付费节奏提供后续观察窗口。",
        "impact": f"产品当前Google#{current_rank('googlePlay', 'Star Trek')}、iOS#{current_rank('ios', 'Star Trek')}；双端差距仍大，活动效果需分平台观察。",
        "source": "Star Trek Fleet Command官方", "url": "https://startrekfleetcommand.com/news/alliance-tournaments-updates-october-2026/",
    },
    {
        "category": "卡牌策略 / 资料片", "date": "2026-10-12",
        "title": "Hearthstone 37.0为Reign of the Black Empire预热",
        "summary": "Blizzard于10月12日发布37.0说明：补丁10月13日上线，并为10月20日开放的Reign of the Black Empire资料片、新竞技场赛季与新版Journal预热。",
        "impact": f"产品本期iOS下跌17位至#{current_rank('ios', 'Hearthstone')}；继续观察资料片首发峰值回落后能否稳定承接。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "战术RPG / 限时活动", "date": "2026-10-10",
        "title": "Tacticus推进Terminus生存活动与新Battle Pass",
        "summary": "官方App Store版本记录列出10月Terminus生存活动与新Battle Pass，继续以阵营角色、限时生存关卡和赛季奖励维持核心盘。",
        "impact": f"产品本期iOS上升22位至#{current_rank('ios', 'Warhammer 40,000')}、Google#{current_rank('googlePlay', 'Warhammer 40,000')}；时间相邻但仍需连续留位确认。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/warhammer-40-000-tacticus/id1599937506",
    },
    {
        "category": "4X / 英雄成长", "date": "2026-10-21",
        "title": "Lords Mobile上线Heroic Saga与Battle Spirit",
        "summary": "Apple版本记录确认Rank 8满装备英雄可觉醒Battle Spirit，并通过Heroic Saga任务获得Armament与强化资源。",
        "impact": f"产品本期iOS跌至#{current_rank('ios', 'Lords Mobile')}、Google升至#{current_rank('googlePlay', 'Lords Mobile')}；版本并未对应为跨端同步上行。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/lords-mobile-kingdom-wars/id1071976327",
    },
    {
        "category": "塔防RPG / 主线大版本", "date": "2026-10-21",
        "title": "Arknights Episode 17开放Extreme Mode",
        "summary": "官方Episode 17公告将Extreme Mode开放时间定在10月21日，章节活动、限定干员与兑换商店仍处开放期。",
        "impact": f"产品本期Google#{current_rank('googlePlay', 'Arknights')}、iOS#{current_rank('ios', 'Arknights')}；版本窗口内两端均回落，不能把内容节点等同于榜位抬升。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4814",
    },
    {
        "category": "全球市场 / 收入榜", "date": "2026-10-01",
        "title": "Sensor Tower最新官方全球收入榜仍为2026年9月",
        "summary": "官方9月全球手游收入TOP10的核心策略子集仍为Whiteout Survival #6、Last War #7与Kingshot #9；口径覆盖App Store和Google Play并排除第三方Android商店。",
        "impact": "本工作日只检查一次官方博客，未发现更新一期完整图表，因此保留9月真实统计期；全球月榜不替代美国单区日榜。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Whiteout Survival双端登顶，Google榜首完成单日换位",
        "detail": "Whiteout由Google #2升至#1并保持iOS #1，Kingshot在Google退至#2；万圣活动与榜首时间相邻，但只作为待验证背景，不据单日名次断言长期转折。",
    },
    {
        "type": "判断", "title": "Google五进五出且中段重排，iOS进出较少但大幅位移更多",
        "detail": "Google 55款共同产品中37款位移不超过2名，Rise of Castles +17、Lands of Jail −11；iOS三进三出，57款共同产品中仅27款位移不超过2名，Boom Beach与Tacticus均+22、Hearthstone −17。",
    },
    {
        "type": "判断", "title": "近90天新品增加到Google三款，iOS仍只有Age of Spirits",
        "detail": "Last Human首次收录Google #59并按本店8月19日上架日归类新品；Age of Spirits仍双端留榜但位于Google #55、iOS #58，两个新品信号都集中在后十名。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证Google五款入榜产品的留位",
        "detail": "重点看DC Dark Legion与Last Shelter能否留在前50，以及Last Fortress、GoT Conquest、Last Human是否仍停留后十名；再次掉榜则继续按轮换或首发验证处理。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：复核Whiteout双端榜首与两款新品承接",
        "detail": "只有Whiteout在活动开启后仍保持双端前列，且Last Human、Age of Spirits至少一端脱离后十名，才进一步判断节日运营和新品获量层形成连续承接。",
    },
    {
        "type": "关注", "title": "至10月30日：观察大幅上行产品是否回吐",
        "detail": "复核Rise of Castles、Boom Beach、Tacticus与X-Clash能否保留本次升幅，并关注Hearthstone、Lords Mobile在资料片或版本窗口内是否止跌。",
    },
]


google_history = load("data/history/google-play/2026-10-27.json")
ios_history = load("data/history/ios/2026-10-27.json")
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
    "title": "Whiteout双端登顶；Google五进五出，iOS三进三出",
    "summary": "较10月26日前一有效快照，Google Play五进五出，55款共同产品中37款位移不超过2名；Rise of Castles +17、Lands of Jail −11，Whiteout Survival升至#1。iOS三进三出，Boom Beach与Tacticus各+22、Hearthstone −17。Last Human首次进入项目Google榜#59并按本店上架日归类为近90天新品；两端缺少7月29日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261027.json",
    "rankingSources": {"googlePlay": "data/games-20261027.json", "ios": "data/ios-games-20261027.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261026.json", "ios": "data/ios-games-20261026.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Rise of Castles: Ice and Fire · #60 Call of Dragons",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Castle Busters · #60 Aliens vs Zombies: Invasion",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-29"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-29"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-27.md", "json": "data/market-brief-20261027.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-26；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-29精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261027.json", brief)
(ROOT / "reports/2026-10-27.md").write_text(build_markdown(brief), encoding="utf-8")
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
