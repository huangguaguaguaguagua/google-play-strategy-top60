#!/usr/bin/env python3
"""Generate the Beijing 2026-10-23 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-23", "20261023"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261023.json"), "prior": load("data/games-20261022.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261023.json"), "prior": load("data/ios-games-20261022.json"), "id": "appId"},
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


def card(store, prefix, tone, analysis):
    data, ident = datasets[store], datasets[store]["id"]
    row = find_game(store, prefix)
    product_id = str(row[ident])
    current = next((item for item in data["now"] if str(item[ident]) == product_id), None)
    previous = next((item for item in data["prior"] if str(item[ident]) == product_id), None)
    if tone == "entry" and current and not previous:
        label = f"{'首次收录' if product_id == '1080541643' else '回榜'} · #{current['rank']}"
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
    card("googlePlay", "Sea of Conquest", "entry", "回到Google #60，iOS未入榜。产品仍以海盗船队、寻宝与联盟海战维持长线盘；当前仅是末位回补，未找到与今天同步的重大官方节点。"),
    card("googlePlay", "Raid Rush", "exit", "上期回榜#59后本期掉榜，iOS仍在#38。Google端连续两日榜尾进出，更像末位轮换，不支持写成长线转弱。"),
    card("googlePlay", "Arknights", "up", "Google上升6位至#8，iOS反向下跌6位至#42。Episode 17 Extreme Mode仍处开放窗口，但双端分化说明不能把版本直接写成榜位拉升。"),
    card("googlePlay", "Game of Thrones: Dragonfire", "down", "Google下跌6位至#37，iOS反向上升13位至#11。10月15日Kalspire角色内容仍在近期窗口，单日跨端分化需继续验证。"),
    card("googlePlay", "Age of Origins", "down", "Google下跌5位至#29，iOS未入榜。未发现与今天同步的重大官方节点，暂按中段单日回落记录。"),
    card("googlePlay", "Call of Dragons", "up", "Google上升4位至#45，iOS未入榜。产品仍在后20名，单日回升不足以确认结构改善。"),
    card("googlePlay", "Lands of Jail", "up", "Google上升3位至#22，iOS反向下跌3位至#46。近期英雄内容只作时间背景，尚无双端同步信号。"),
    card("googlePlay", "Frost & Flame", "up", "Google上升3位至#32，iOS未入榜。长期4X产品的中段回升未对应到可确认的当日节点。"),
    card("googlePlay", "Last Shelter: War Z", "up", "Google上升3位至#33，iOS回榜#50。双端同时进入中后段，但尚无证据确认由同一活动驱动。"),
    card("googlePlay", "Stormshot", "down", "Google下跌3位至#50，iOS未入榜。射击解谜获量层与联盟4X仍是既有结构，今天只记为后段回落。"),
    card("googlePlay", "Game of Thrones: Conquest", "up", "Google上升3位至#57，iOS未入榜。九周年内容仍在月度窗口，但当前仍接近榜尾，不作活动直接拉升判断。"),
    card("googlePlay", "Age of Spirits", "down", "Google下跌3位至#59，仍属近90天新品。产品尚处首发验证，名次逼近榜尾是下一快照的留榜风险信号。"),
]


ios_products = [
    card("ios", "Coop TD", "entry", "回到iOS #36，Google未入榜。多人合作塔防位于中段，但只有单次回榜证据，先观察能否连续留位。"),
    card("ios", "Last Shelter: War Z", "entry", "回到iOS #50，Google同步升至#33。产品2026年6月上架、仍处首发验证；双端同日入段尚不足以确认长期承接。"),
    card("ios", "Kingdom Clash", "entry", "回到iOS #54，Google未入榜。中世纪塔防与领地经营重返后十名，尚无连续留榜证据。"),
    card("ios", "Infinite Borders", "entry", "项目历史首次收录于iOS #60。三国沙盘4X的周年活动与10月21日例行更新仍在窗口，但末位入榜只记为待验证信号。"),
    card("ios", "Age of Empires", "exit", "上期#45后本期掉榜，Google当前#39。iPhone端退出与Google中段留位形成分化，未发现当天重大官方节点。"),
    card("ios", "Boom Beach", "exit", "上期#56后本期掉榜，Google未入榜。长线基地攻防产品未形成连续后十名留位。"),
    card("ios", "Last Day on Earth", "exit", "上期回榜#57后本期掉榜，Google仍高居#5。跨端差距再次扩大，iPhone端更像一次榜尾回补。"),
    card("ios", "Jurassic World Alive", "exit", "上期回榜#59后本期掉榜，Google未入榜。一次末位回补未形成连续留位。"),
    card("ios", "Infinity Kingdom", "up", "iOS上升20位至#24。最近可确认的v2.9.9加入Horus、联盟章程与成长优化，但发布日期较早，不能解释今天全部升幅。"),
    card("ios", "Game of Thrones: Dragonfire", "up", "iOS上升13位至#11，Google反向降至#37。Kalspire内容与名次变化时间相邻，仍需未来1—2个快照验证平台承接。"),
    card("ios", "Dragon Traveler", "up", "iOS上升12位至#28，Google未入榜。未找到与今天同步的重大官方节点，暂按首发期单日跃升处理。"),
    card("ios", "Hearthstone", "down", "iOS下跌11位至#25。Reign of the Black Empire已于10月20日上线，本次回落需与资料片首发峰值后的稳定承接区分。"),
    card("ios", "Top Heroes", "down", "iOS下跌10位至#59，Google当前#44。两端都在后段，iPhone端已经逼近榜尾，未发现当日重大节点。"),
    card("ios", "Lords Mobile", "up", "iOS上升9位至#39，Google当前#35。10月21日Heroic Saga与Battle Spirit上线，与双端接近相邻，但需连续快照确认。"),
    card("ios", "Fire Emblem", "up", "iOS上升7位至#53。10.10.0武器精炼仍在近期窗口，但产品仍在后十名，先按版本窗口内波动处理。"),
    card("ios", "Arknights", "down", "iOS下跌6位至#42，Google反向升至#8。Episode 17窗口内的双端反向再次提示不能用单一活动解释两端名次。"),
    card("ios", "War and Order", "down", "iOS下跌6位至#45，Google未入榜。未发现与今天同步的重大官方节点，暂按中后段单日回落记录。"),
    card("ios", "Cell Survivor", "up", "iOS上升6位至#52，Google未入榜。2026年新作仍处首发验证，当前只是后十名改善，需看能否继续脱离榜尾。"),
]


news = [
    {
        "category": "三国4X / 周年运营", "date": "2026-10-20",
        "title": "Infinite Borders预告10月21日例行更新，周年内容仍在窗口",
        "summary": "产品官网确认10月21日例行更新安排；官方近期公告仍保留周年活动内容。游戏以三国武将、政策经营、联盟与实时地形天气沙盘为核心。",
        "impact": "产品本期首次进入项目保存的iOS榜#60；更新时间与入榜相邻，但没有证据证明单一更新直接造成名次变化。",
        "source": "Infinite Borders官方网站", "url": "https://www.infinitebordersgame.com/",
    },
    {
        "category": "IP 4X / 新角色", "date": "2026-10-15",
        "title": "Game of Thrones: Dragonfire发布Kalspire角色内容",
        "summary": "官方新闻页将Kalspire作为近期角色内容发布，继续强化坦格利安角色、巨龙与阵营叙事。",
        "impact": f"产品本期iOS升至#{current_rank('ios', 'Game of Thrones: Dragonfire')}、Google降至#{current_rank('googlePlay', 'Game of Thrones: Dragonfire')}，跨端反向需继续验证。",
        "source": "Game of Thrones: Dragonfire官方", "url": "https://news.gotdragonfire.com/",
    },
    {
        "category": "卡牌策略 / 资料片", "date": "2026-10-20",
        "title": "Hearthstone上线Reign of the Black Empire",
        "summary": "Blizzard官方37.0说明确认资料片于10月20日上线，带来135张卡、四位Old Gods、Assemble关键词和新奖励轨。",
        "impact": f"产品本期iOS下跌11位至#{current_rank('ios', 'Hearthstone')}；需区分首发峰值回落与后续稳定承接。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "4X / 英雄养成", "date": "2026-10-21",
        "title": "Lords Mobile 2.208上线Heroic Saga与Battle Spirit",
        "summary": "Apple官方版本记录确认高阶英雄可觉醒Battle Spirit，并通过Heroic Saga任务获取Armament与强化资源。",
        "impact": f"产品本期iOS升至#{current_rank('ios', 'Lords Mobile')}、Google位于#{current_rank('googlePlay', 'Lords Mobile')}；双端接近与版本相邻，仍需继续验证。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/lords-mobile-kingdom-wars/id1071976327",
    },
    {
        "category": "塔防RPG / 主线大版本", "date": "2026-10-21",
        "title": "Arknights Episode 17开放Extreme Mode",
        "summary": "官方Episode 17公告将Extreme Mode开放时间定在10月21日，章节活动、限定干员与兑换商店仍处开放期。",
        "impact": f"产品本期Google升至#{current_rank('googlePlay', 'Arknights')}、iOS降至#{current_rank('ios', 'Arknights')}，双端反向不支持直接因果判断。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4814",
    },
    {
        "category": "卡通4X / 英灵", "date": "2026-09-03",
        "title": "Infinity Kingdom v2.9.9加入Horus与Alliance Charter",
        "summary": "官方版本页列出新Immortal Horus、Tower of Knowledge技能、Alliance Charter及一系列成长优化。",
        "impact": f"产品本期iOS上升20位至#{current_rank('ios', 'Infinity Kingdom')}；节点较早，只能作为当前内容背景，不能解释单日全部升幅。",
        "source": "Infinity Kingdom官方", "url": "https://infinitykingdom.gtarcade.com/en/news/7024910.html",
    },
    {
        "category": "海战SLG / 回归运营", "date": "2026-10-21",
        "title": "Sea War 1.175.0加入精英招募角色与回归福利",
        "summary": "Apple官方版本记录写明Saoirse和Samantha进入Elite Recruitment，并新增Returning Commander福利。",
        "impact": f"产品本期iOS降至#{current_rank('ios', 'Sea War')}、Google位于#{current_rank('googlePlay', 'Sea War')}；更新没有对应为即时上行。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/sea-war-uboat-raid/id6447612873",
    },
    {
        "category": "战棋RPG / 英雄强化", "date": "2026-10-06",
        "title": "Fire Emblem Heroes 10.10.0扩充武器精炼",
        "summary": "Apple官方版本记录确认七名英雄新增可精炼武器，并更新Divine Codes: Ephemera 10的限时Combat Manuals。",
        "impact": f"产品本期iOS上升7位至#{current_rank('ios', 'Fire Emblem')}，但仍在后十名，先看版本窗口内能否连续留位。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/fire-emblem-heroes/id1181774280",
    },
    {
        "category": "科幻4X / 限时活动", "date": "2026-10-15",
        "title": "Star Trek Fleet Command上线Division 12",
        "summary": "Scopely官方加入Villains Rose Harper、Division 12 Battle Pass、限时Haven Exchange、舰船改装及跨服活动。",
        "impact": f"产品当前Google #{current_rank('googlePlay', 'Star Trek')}、iOS未入榜；活动尚未表现为双端同步留位。",
        "source": "Star Trek Fleet Command官方", "url": "https://startrekfleetcommand.com/news/division-12-patch-notes/",
    },
    {
        "category": "全球市场 / 收入榜", "date": "2026-10",
        "title": "Sensor Tower最新官方全球收入榜仍为2026年9月",
        "summary": "官方9月全球手游收入TOP10的核心策略子集为Whiteout Survival #6、Last War #7与Kingshot #9；口径覆盖App Store和Google Play并排除第三方Android商店。",
        "impact": "本工作日只检查一次官方博客，未发现更新一期完整图表，因此保留9月真实统计期；全球月榜不替代美国单区日榜。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google总体稳定，但头中部出现两组跨端反向",
        "detail": "Google一进一出，59款共同产品中49款位移不超过2名；Arknights +6而iOS −6，Dragonfire Google −6而iOS +13，平台差异比单一活动解释更突出。",
    },
    {
        "type": "判断", "title": "iOS四进四出且中段重排，波动显著高于Google",
        "detail": "iOS仅56款共同产品，29款位移不超过2名；Infinity Kingdom +20、Dragonfire +13、Dragon Traveler +12，而四款新进/回榜中仅Coop TD进入前40。",
    },
    {
        "type": "判断", "title": "新品仍少，榜面主导力量来自成熟长线盘",
        "detail": "近90天新品仍为Google 2款、iOS 0款；大幅上行主要来自Infinity Kingdom、Lords Mobile等成熟产品，Last Shelter: War Z则继续处于双端首发验证。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证四款iOS入榜产品的留榜率",
        "detail": "Coop TD、Last Shelter: War Z、Kingdom Clash与Infinite Borders需先连续留榜；Infinite Borders若仍停在#60附近，继续按周年窗口内榜尾信号处理。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：复核Dragonfire与Arknights的跨端反向",
        "detail": "只有当两款在后续快照延续当前方向，才进一步检查平台活动、付费节奏或榜单噪声；单日异动不直接下长期结论。",
    },
    {
        "type": "关注", "title": "至10月30日：观察Hearthstone与Lords Mobile的版本承接",
        "detail": "关注Hearthstone能否在资料片首发回落后稳住前30，以及Lords Mobile能否维持双端30—40名，而不是只出现单次版本峰值。",
    },
]


google_history = load("data/history/google-play/2026-10-23.json")
ios_history = load("data/history/ios/2026-10-23.json")
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
    "title": "Google一进一出、iOS四进四出；两组核心产品跨端反向",
    "summary": "较10月22日前一有效快照，Google Play由Sea of Conquest回榜#60、Raid Rush掉榜，59款共同产品中49款位移不超过2名；Arknights +6、Dragonfire −6。iOS四进四出，Infinity Kingdom +20、Dragonfire +13、Dragon Traveler +12，Hearthstone −11、Top Heroes −10。近90天新品为Google 2款、iOS 0款；两端缺少7月25日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261023.json",
    "rankingSources": {"googlePlay": "data/games-20261023.json", "ios": "data/ios-games-20261023.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261022.json", "ios": "data/ios-games-20261022.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Rise of Kingdoms: Lost Crusade · #60 Sea of Conquest: Pirate War",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Hearthstone · #60 Infinite Borders",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-25"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-25"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-23.md", "json": "data/market-brief-20261023.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-22；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-25精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261023.json", brief)
(ROOT / "reports/2026-10-23.md").write_text(build_markdown(brief), encoding="utf-8")
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
