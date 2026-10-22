#!/usr/bin/env python3
"""Generate the Beijing 2026-10-22 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-22", "20261022"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261022.json"), "prior": load("data/games-20261021.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261022.json"), "prior": load("data/ios-games-20261021.json"), "id": "appId"},
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
        label = f"回榜 · #{current['rank']}"
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
    card("googlePlay", "Raid Rush", "entry", "回到Google #59，前一快照刚从#60掉榜；iOS未入榜。连续两日压线进出更像榜尾轮换，本次仍只记为待验证信号。"),
    card("googlePlay", "Limbus Company", "exit", "上期回榜#60后本期立即掉榜，iOS也未进入TOP60。两端都缺少连续留位证据，不支持写成长期回升。"),
    card("googlePlay", "Arknights", "down", "Google下跌6位至#14，iOS当前#36。Episode 17与Extreme Mode仍在开放窗口，但版本和活动存在不等于榜位必然上升。"),
    card("googlePlay", "Last Shelter: War Z", "down", "Google下跌3位至#36；iOS榜内的Last Shelter: Survival是另一商店条目，不作为同一产品跨端名次。未发现与今天同步的重大节点。"),
    card("googlePlay", "Call of Dragons", "down", "Google下跌3位至#49，iOS未入榜。产品仍在中后段，未找到与今天同步的重大官方节点。"),
    card("googlePlay", "Lands of Jail", "down", "Google下跌3位至#25，iOS持平于#43。10月19日新英雄与护甲内容没有对应为今天的双端上行，版本只作时间背景。"),
    card("googlePlay", "Game of Thrones: Conquest", "down", "Google下跌3位至#60，iOS从上期#52掉榜。九周年月度内容仍在，但双端均转弱，不能直接写成活动拉升。"),
    card("googlePlay", "Rise of Castles", "up", "Google上升3位至#40，iOS上升1位至#54。两端小幅同向，但没有发现与今天同步的重大版本或活动证据。"),
    card("googlePlay", "Stormshot", "up", "Google上升3位至#47，iOS未入榜。单日回升仍在后20名，尚不足以确认稳定改善。"),
]


ios_products = [
    card("ios", "Fire Emblem", "entry", "回到iOS #60。10.10.0加入七名英雄武器精炼与限时Combat Manuals，但当前仍是最后一名，只能作为版本窗口内的压线信号。"),
    card("ios", "Last Day on Earth", "entry", "回到iOS #57，Google仍高居#5。两端差距达52位，最近iOS版本仅简化授权和进度恢复，不足以解释回榜。"),
    card("ios", "Jurassic World Alive", "entry", "回到iOS #59。3.23.55只预告新恐龙并修复问题，缺少直接收入或活动证据，本次按榜尾回补处理。"),
    card("ios", "Kiss of War", "exit", "上期回榜#59后本期掉榜，Google当前#43。一次压线回补未形成连续留位。"),
    card("ios", "Game of Thrones: Conquest", "exit", "上期回榜#52后本期退出，Google也降至#60。九周年内容与榜位变化时间相邻，但未形成双端正向承接。"),
    card("ios", "Vikings", "exit", "上期回榜#54后本期掉榜，Google当前#26。iPhone端仍呈榜尾轮换，缺少连续改善证据。"),
    card("ios", "Summoners War", "up", "iOS上升15位至#38。9.3.6加入Cosmic Worm且SWC内容仍在，但单一快照不能证明具体内容造成跃升。"),
    card("ios", "Lords Mobile", "up", "iOS上升12位至#48，Google同步上升2位至#34。2.208 Heroic Saga于10月21日上线，与双端改善相邻，仍需后续快照验证持续性。"),
    card("ios", "Forge Master", "up", "iOS上升9位至#26。10月8日版本仅加入成就、聊天翻译和稳定性修复，未找到与今日同步的重大运营节点。"),
    card("ios", "Sea War", "down", "iOS下跌8位至#53，Google当前#58。1.175.0同日加入两名精英招募角色与回归福利，但更新没有对应为即时上行。"),
    card("ios", "Age of Empires", "down", "iOS下跌8位至#45，Google当前#41，双端名次仍接近。最近版本只披露修复，未发现可确认的重大转折。"),
    card("ios", "Rise of Kingdoms", "down", "iOS下跌6位至#31，Google维持#7。跨端差距扩大，单日名次回落不等于收入跌幅。"),
]


news = [
    {
        "category": "4X / 英雄养成", "date": "2026-10-21",
        "title": "Lords Mobile 2.208上线Heroic Saga与Battle Spirit突破",
        "summary": "Apple官方版本记录确认：Rank 8且装备完整的英雄可觉醒Battle Spirit，并通过Heroic Saga任务获取Armament与强化资源。",
        "impact": f"产品本期iOS上升12位至#{current_rank('ios', 'Lords Mobile')}、Google升至#{current_rank('googlePlay', 'Lords Mobile')}；双端同向与版本相邻，但需继续验证留位。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/lords-mobile-kingdom-wars/id1071976327",
    },
    {
        "category": "塔防RPG / 主线大版本", "date": "2026-10-21",
        "title": "Arknights Episode 17开放Extreme Mode",
        "summary": "官方Episode 17公告将Extreme Mode开放时间定为10月21日16:00（UTC-7）；章节活动、限定干员与兑换商店仍处开放期。",
        "impact": f"产品本期Google下跌6位至#{current_rank('googlePlay', 'Arknights')}、iOS位于#{current_rank('ios', 'Arknights')}，说明内容窗口不能直接等同于当天畅销抬升。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4814",
    },
    {
        "category": "卡牌策略 / 资料片", "date": "2026-10-20",
        "title": "Hearthstone正式上线Reign of the Black Empire",
        "summary": "Blizzard官方37.0说明确认资料片于10月20日上线，带来135张卡、四位Old Gods、Assemble关键词和新奖励轨。",
        "impact": f"产品本期iOS位于#{current_rank('ios', 'Hearthstone')}；昨日大幅跃升后仍需用连续快照区分首发峰值与稳定承接。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "回合RPG / 新魔灵", "date": "2026-10-14",
        "title": "Summoners War 9.3.6加入Cosmic Worm",
        "summary": "Apple官方版本记录确认新增Monster: Cosmic Worm，并同步进行体验优化和错误修复。",
        "impact": f"产品本期iOS上升15位至#{current_rank('ios', 'Summoners War')}；版本处于近期窗口，但没有证据支持把全部升幅归因于单一内容。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/summoners-war/id852912420",
    },
    {
        "category": "海战SLG / 回归运营", "date": "2026-10-21",
        "title": "Sea War 1.175.0加入精英招募角色与回归福利",
        "summary": "Apple官方版本记录写明Saoirse和Samantha进入Elite Recruitment，并新增Returning Commander福利。",
        "impact": f"产品本期iOS反而下跌8位至#{current_rank('ios', 'Sea War')}、Google位于#{current_rank('googlePlay', 'Sea War')}；更新与下跌并存，不作增长推断。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/sea-war-uboat-raid/id6447612873",
    },
    {
        "category": "4X / 九周年", "date": "2026-10-13",
        "title": "Game of Thrones: Conquest继续九周年月度内容",
        "summary": "Apple官方版本记录确认九周年奖励贯穿整月，并加入Viserion、Free Folk装备与新龙装。",
        "impact": f"产品本期iOS掉榜、Google降至#{current_rank('googlePlay', 'Game of Thrones: Conquest')}；周年内容没有在当天表现为双端同步改善。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/game-of-thrones-conquest/id1035712810",
    },
    {
        "category": "战棋RPG / 英雄强化", "date": "2026-10-06",
        "title": "Fire Emblem Heroes 10.10.0扩充武器精炼",
        "summary": "Apple官方版本记录确认七名英雄新增可精炼武器，并更新Divine Codes: Ephemera 10的限时Combat Manuals。",
        "impact": f"产品本期回到iOS #{current_rank('ios', 'Fire Emblem')}，但仍在最后一名，先按榜尾版本窗口信号处理。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/fire-emblem-heroes/id1181774280",
    },
    {
        "category": "IP收集 / 实时PvP", "date": "2026-10-08",
        "title": "Jurassic World Alive 3.23.55预告新恐龙",
        "summary": "Apple官方版本记录仅确认新恐龙将陆续出现，并包含错误修复和性能优化，没有披露大型系统或商业化改动。",
        "impact": f"产品本期回到iOS #{current_rank('ios', 'Jurassic World Alive')}；因证据有限，不把回榜写成版本直接驱动。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/jurassic-world-alive/id1231085864",
    },
    {
        "category": "科幻4X / 万圣节", "date": "2026-10-15",
        "title": "Star Trek Fleet Command上线Division 12",
        "summary": "Scopely官方加入Villains Rose Harper、Division 12 Battle Pass、限时Haven Exchange、舰船改装及跨服活动。",
        "impact": f"产品当前Google #{current_rank('googlePlay', 'Star Trek')}，iOS未入榜；活动尚未表现为双端同步留位。",
        "source": "Star Trek Fleet Command官方", "url": "https://startrekfleetcommand.com/news/division-12-patch-notes/",
    },
    {
        "category": "全球市场 / 收入榜", "date": "2026-10",
        "title": "Sensor Tower最新官方全球收入榜仍为2026年9月",
        "summary": "官方9月全球手游收入TOP10的核心策略子集为Whiteout Survival #6、Last War #7与Kingshot #9；口径覆盖App Store和Google Play并排除第三方Android商店。",
        "impact": "本工作日单次检查未发现更新一期完整图表，因此继续保留9月真实统计期；全球月榜不代替美国单区日榜。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google继续只在榜尾换位，但Arknights带来唯一明显回落",
        "detail": "Google一进一出，59款共同产品中52款位移不超过2名；Raid Rush与Limbus在#59—60轮换，Arknights−6是唯一超过3位的变动。",
    },
    {
        "type": "判断", "title": "iOS三进三出，主要上行动能集中在长线产品",
        "detail": "iOS有57款共同产品、45款位移不超过2名；Summoners War +15、Lords Mobile +12、Forge Master +9，而三款回榜产品全部位于#57以后。",
    },
    {
        "type": "判断", "title": "跨端同步只在Lords Mobile局部出现，平台差异仍占主导",
        "detail": "Lords Mobile两端同向改善至Google #34与iOS #48；Game of Thrones则Google降至#60、iOS掉榜，Last Day on Earth为Google #5而iOS仅回榜#57。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证四款榜尾回榜的留榜率",
        "detail": "Raid Rush、Fire Emblem Heroes、Last Day on Earth和Jurassic World Alive均位于#57以后；若迅速退出，继续按榜尾轮换而非趋势反转处理。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：区分Heroic Saga与Cosmic Worm的短峰和持续承接",
        "detail": "若Lords Mobile继续双端改善、Summoners War维持iOS前40，可再结合版本窗口判断承接；否则只保留为时间相邻信号。",
    },
    {
        "type": "关注", "title": "至10月28日：复核Episode 17与九周年内容的后续表现",
        "detail": "Arknights Episode 17仍在开放期，Game of Thrones九周年内容贯穿整月；观察两款是否出现连续快照回升，而不是依据单日活动直接下结论。",
    },
]


google_history = load("data/history/google-play/2026-10-22.json")
ios_history = load("data/history/ios/2026-10-22.json")
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
    "title": "Google榜尾互换、iOS三进三出；Summoners War与Lords Mobile上行",
    "summary": "较10月21日前一有效快照，Google Play由Raid Rush回榜#59、Limbus Company掉榜，59款共同产品中52款位移不超过2名；Arknights −6至#14。iOS三进三出，Fire Emblem Heroes、Last Day on Earth与Jurassic World Alive在#57—60回榜；Summoners War +15、Lords Mobile +12、Forge Master +9，Sea War与Age of Empires各−8。近90天新品为Google 2款、iOS 0款；两端缺少7月24日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261022.json",
    "rankingSources": {"googlePlay": "data/games-20261022.json", "ios": "data/ios-games-20261022.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261021.json", "ios": "data/ios-games-20261021.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Lands of Jail · #60 Game of Thrones: Conquest",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Magic: The Gathering Arena · #60 Fire Emblem Heroes",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-24"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-24"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-22.md", "json": "data/market-brief-20261022.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-21；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-24精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261022.json", brief)
(ROOT / "reports/2026-10-22.md").write_text(build_markdown(brief), encoding="utf-8")
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
