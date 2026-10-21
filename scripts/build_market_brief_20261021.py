#!/usr/bin/env python3
"""Generate the Beijing 2026-10-21 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-21", "20261021"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261021.json"), "prior": load("data/games-20261020.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261021.json"), "prior": load("data/ios-games-20261020.json"), "id": "appId"},
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
    card("googlePlay", "Limbus Company", "entry", "回到Google #60，而iOS在前一快照已退出。两端连续呈反向榜尾轮换，说明核心用户支撑仍有平台差异；本次只记为待验证回榜信号。"),
    card("googlePlay", "Raid Rush", "exit", "上期位于Google #60，本期掉榜；iOS未进入TOP60。产品此前主要在截线附近出现，本次退出不支持稳定回升判断。"),
    card("googlePlay", "Frost & Flame", "up", "Google上升4位至#34，iOS当前#39，双端名次接近；未找到与今日同步的重大官方节点，因此先记录为中段改善而非长期转折。"),
    card("googlePlay", "Lords Mobile", "down", "Google下跌3位至#36，iOS则回到#60。Heroic Saga与新版本提供运营背景，但两端方向和位置不同，不能直接归因为版本拉动。"),
]


ios_products = [
    card("ios", "Evo Defense", "entry", "回到iOS #49。9月Everbloom活动与Style Switch仍是最近可核验内容，但距本次回榜已有时间，当前按成熟产品榜尾回补处理。"),
    card("ios", "Game of Thrones: Conquest", "entry", "回到iOS #52；Google当前#57。官方10月13日开启九周年月度内容并加入Viserion等更新，节点与回榜相邻但不证明单独造成名次变化。"),
    card("ios", "Vikings", "entry", "回到iOS #54，Google当前#28。10月1日版本仅加入新的Asgard商店增益，证据不足以解释今天回榜，先看后续能否连续留榜。"),
    card("ios", "Boom Beach", "entry", "回到iOS #56，Google当前#42。10月5日版本推出Blitz逐关挑战与排行榜，回榜位于版本后窗口，但仍在高掉榜风险区。"),
    card("ios", "Cell Survivor", "entry", "回到iOS #57。10月14日周年活动与本次回榜时间接近，但单一快照不能证明活动峰值；当前仍属榜尾待验证信号。"),
    card("ios", "Last Shelter", "entry", "回到iOS #58，Google当前#58，双端同位但都压线。Apple端最近版本主要为模块、扭蛋、宠物和Crisis Cube优化，未披露重大结构变化。"),
    card("ios", "Kiss of War", "entry", "回到iOS #59，Google当前#41。最近公开版本只写界面和错误修复，缺少重大内容依据；先按榜尾回补处理。"),
    card("ios", "Lords Mobile", "entry", "回到iOS #60，Google下跌3位至#36。Heroic Saga已于10月15日上线，但iOS仅压线回榜，跨端并未形成同步改善。"),
    card("ios", "Kingdom Clash", "exit", "上期随3.3.0回榜#45，本期即掉榜；冰系Boss与新兵种没有在相邻快照中形成留位，仍按一次版本窗口榜尾信号处理。"),
    card("ios", "Aliens vs Zombies", "exit", "上期回榜#51后本期掉榜。Boss Hunt虽已开启，榜位没有连续承接；10月26日Halloween Night仍可作为下一验证窗口。"),
    card("ios", "Fire Emblem", "exit", "上期已回落至#53，本期掉榜。10月16日新英雄与章节窗口后的高位回吐继续，但不能换算为收入跌幅。"),
    card("ios", "Guns of Glory", "exit", "上期回榜#55后本期退出，Google仍在#38。近期版本只确认体验优化，缺少能解释单端短时变化的重大内容证据。"),
    card("ios", "Watcher of Realms", "exit", "上期已降至#57，本期掉榜。召唤和活动背景未转化为连续留位证据，仍属于成熟产品榜尾轮换。"),
    card("ios", "League of Legends", "exit", "上期#58，本期掉榜；Google仍在#48。7.3b平衡更新处于窗口内，但iPhone端退出说明不能把版本直接等同于畅销改善。"),
    card("ios", "The Tower", "exit", "上期#59，本期掉榜。v29的预设、联赛和Vault/Harmony Tree重做未在相邻快照中维持TOP60位置。"),
    card("ios", "Last Day on Earth", "exit", "上期#60，本期掉榜；Google当前#5。跨端差距极大，iOS最后一名回补只维持一个快照。"),
    card("ios", "Hearthstone", "up", "iOS上升38位至#12。Reign of the Black Empire于10月20日正式上线，与跃升时间高度相邻；仍需后续快照区分首日峰值和持续承接。"),
    card("ios", "Star Wars", "up", "iOS上升24位至#7，Google未入榜。公开版本记录只写后台优化，未找到与今日同步的重大内容节点，因此不推断具体原因。"),
    card("ios", "The Battle Cats", "up", "iOS上升12位至#40。15.6.1主要为错误修复，15.6.0加入震动、新形态和关卡；距离当前已有两周，单日抬升仍待验证。"),
    card("ios", "Sea War", "up", "iOS上升11位至#45，Google当前#59。iOS最近版本只写界面和错误修复，缺少活动证据，先记录为单端改善。"),
    card("ios", "Age of Empires", "down", "iOS下跌8位至#37，Google当前#39，双端名次仍接近。10月8日版本只披露修复，当前更像中段波动而非可确认转折。"),
    card("ios", "Lands of Jail", "down", "iOS下跌8位至#43，Google当前#22，跨端差距扩大。10月19日新英雄、护甲与Forticlad等级上限更新与下跌并存，不能以有版本推断增长。"),
    card("ios", "Overgeared Hero", "down", "iOS下跌7位至#48，Google当前#35。Raven联动与万圣节皮肤仍在运营窗口，但榜位未同步改善，需观察活动后段。"),
]


news = [
    {
        "category": "卡牌策略 / 资料片", "date": "2026-10-20",
        "title": "Hearthstone正式上线Reign of the Black Empire",
        "summary": "Blizzard官方37.0说明确认资料片于10月20日上线，带来135张卡、四位Old Gods、Assemble关键词、新奖励轨和Tavern Rewards。",
        "impact": f"产品本期iOS上升38位至#{current_rank('ios', 'Hearthstone')}；上线日与跃升相邻，但需后续快照区分首日峰值与持续承接。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "4X / 九周年", "date": "2026-10-13",
        "title": "Game of Thrones: Conquest开启九周年月度内容",
        "summary": "Apple官方版本记录写明九周年活动、奖励与惊喜贯穿整月，并加入Viserion、Free Folk装备和新龙装。",
        "impact": f"产品本期回到iOS #{current_rank('ios', 'Game of Thrones: Conquest')}、Google位于#{current_rank('googlePlay', 'Game of Thrones: Conquest')}；节点只作时间背景。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id1035712810",
    },
    {
        "category": "4X / 英雄养成", "date": "2026-10-15",
        "title": "Lords Mobile推出Heroic Saga与Battle Spirit突破",
        "summary": "Apple官方2.205说明：Rank 8且装备完整的英雄可解锁Battle Spirit与Heroic Saga，通过Saga任务继续强化英雄。",
        "impact": f"产品本期iOS回榜#{current_rank('ios', 'Lords Mobile')}、Google回落至#{current_rank('googlePlay', 'Lords Mobile')}，暂未形成双端同步改善。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id1071976327",
    },
    {
        "category": "科幻4X / 万圣节", "date": "2026-10-15",
        "title": "Star Trek Fleet Command上线Division 12",
        "summary": "Scopely官方加入Villains Rose Harper、Division 12 Battle Pass、限时Haven Exchange、舰船改装及跨服活动。",
        "impact": f"产品当前Google #{current_rank('googlePlay', 'Star Trek')}，本期iOS未入榜；活动仍未表现为双端同步留位。",
        "source": "Star Trek Fleet Command官方", "url": "https://startrekfleetcommand.com/news/division-12-patch-notes/",
    },
    {
        "category": "塔防RPG / 主线大版本", "date": "2026-10-14",
        "title": "Arknights Episode 17继续处于开放窗口",
        "summary": "官方公告将Episode 17开放日定为10月14日，并在10月28日前临时降低主线解锁要求。",
        "impact": f"产品当前Google #{current_rank('googlePlay', 'Arknights')}、iOS #{current_rank('ios', 'Arknights')}；两端仍存在明显名次差。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4814",
    },
    {
        "category": "MOBA / 平衡更新", "date": "2026-10-14",
        "title": "Wild Rift 7.3b调整英雄、装备、符文与野区",
        "summary": "Riot官方7.3b调整Volibear、Jhin、Hwei等英雄，修改多件装备与符文，并调整野怪和AAA ARAM。",
        "impact": f"产品本期iOS掉榜，Google位于#{current_rank('googlePlay', 'League of Legends')}；更新存在不等于畅销榜抬升。",
        "source": "Riot Games官方", "url": "https://wildrift.leagueoflegends.com/en-us/news/game-updates/wild-rift-patch-notes-7-3b/",
    },
    {
        "category": "基地策略 / 挑战模式", "date": "2026-10-05",
        "title": "Boom Beach推出Blitz逐关挑战与排行榜",
        "summary": "Apple官方63.211说明加入Blitz活动，玩家使用领袖阵容挑战递增难度关卡，并竞争新排行榜。",
        "impact": f"产品本期回到iOS #{current_rank('ios', 'Boom Beach')}，Google同口径未入TOP60；回榜仍靠近截线。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id672150402",
    },
    {
        "category": "轻量塔防 / 周年活动", "date": "2026-10-14",
        "title": "Cell Survivor开启一周年活动",
        "summary": "Apple官方4.1版本说明确认一周年活动上线，并修复已知问题。",
        "impact": f"产品本期回到iOS #{current_rank('ios', 'Cell Survivor')}；周年节点与回榜相邻，但尚无连续留位证据。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id6746465127",
    },
    {
        "category": "监狱经营 / 新内容", "date": "2026-10-19",
        "title": "Lands of Jail加入七代英雄与护甲内容",
        "summary": "Apple官方1.0.52记录限时活动、新七代英雄与强力护甲，并将Forticlad等级上限提升至10级。",
        "impact": f"产品本期iOS下跌8位至#{current_rank('ios', 'Lands of Jail')}、Google位于#{current_rank('googlePlay', 'Lands of Jail')}；版本与名次方向相反。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/id6738469826",
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
        "type": "判断", "title": "Google仅在#60换位，主体结构维持高稳定度",
        "detail": "Google一进一出，59款共同产品中56款位移不超过2名；除King of Avalon上升4位外，没有其他共同产品移动超过3位。",
    },
    {
        "type": "判断", "title": "iOS八进八出并伴随两次20位以上跃升，波动显著放大",
        "detail": "iOS仅52款共同产品，29款位移不超过2名；Hearthstone +38、Star Wars +24，与八款榜尾回榜共同构成本期重排，但单日异动仍不能直接定义长期趋势。",
    },
    {
        "type": "判断", "title": "跨端信号仍分化：Limbus与Lords Mobile均呈反向换位",
        "detail": "Limbus回到Google #60但iOS未入榜；Lords Mobile在iOS回榜#60、Google降至#36。Last Shelter则双端同为#58，却仍处截线附近，平台差异和榜尾轮换同时存在。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证八款iOS回榜的留榜率",
        "detail": "Evo Defense、GoT、Vikings、Boom Beach、Cell Survivor、Last Shelter、Kiss of War和Lords Mobile均在#49以后；若迅速退出，继续按榜尾轮换处理。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：区分Hearthstone资料片首日峰值与持续承接",
        "detail": "若Hearthstone在Reign of the Black Empire上线后继续保持前20，可再结合官方活动窗口判断承接；若快速回落，只记录为首日高位信号。",
    },
    {
        "type": "关注", "title": "至10月26日：复核万圣节内容与榜尾变化",
        "detail": "Aliens vs Zombies本期退出，但官方Halloween Night排期在10月26日；同时观察Overgeared的万圣节内容和Star Trek Division 12能否产生后续跨端变化。",
    },
]


google_history = load("data/history/google-play/2026-10-21.json")
ios_history = load("data/history/ios/2026-10-21.json")
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
    "title": "Google榜面近乎静止，iOS八进八出；Hearthstone与Star Wars大幅上行",
    "summary": "较10月20日前一有效快照，Google Play仅在#60发生Limbus回榜、Raid Rush掉榜，59款共同产品中56款位移不超过2名；King of Avalon +4。iOS八进八出，Hearthstone +38至#12、Star Wars +24至#7，Battle Cats +12、Sea War +11；Age of Empires、War and Order和Lands of Jail各−8。近90天新品为Google 2款、iOS 0款；两端缺少7月23日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261021.json",
    "rankingSources": {"googlePlay": "data/games-20261021.json", "ios": "data/ios-games-20261021.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261020.json", "ios": "data/ios-games-20261020.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Age of Origins · #60 Limbus Company",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Rise of Kingdoms · #60 Lords Mobile",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-23"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-23"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-21.md", "json": "data/market-brief-20261021.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-20；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-23精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261021.json", brief)
(ROOT / "reports/2026-10-21.md").write_text(build_markdown(brief), encoding="utf-8")
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
