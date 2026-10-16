#!/usr/bin/env python3
"""Generate the Beijing 2026-10-16 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-16", "20261016"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261016.json"), "prior": load("data/games-20261015.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261016.json"), "prior": load("data/ios-games-20261015.json"), "id": "appId"},
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
    row = find_game(store, prefix, include_prior=False)
    return row["rank"]


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
        game = next(
            (row for row in data["now"] + data["prior"] if str(row[data["id"]]) == product_id),
            None,
        )
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
    card("googlePlay", "Call of Dragons", "entry", "回到Google #53，并同步回到iOS #60。双端共同进入比单端榜尾回补更值得跟踪，但两端都在后八名，未发现与今天同步的官方重大节点。"),
    card("googlePlay", "League of Legends: Wild Rift", "entry", "回到Google #60，同时回到iOS #50。官方7.3b于10月14日发布并在10月15日开放限定兑换内容；时间相邻但Google位于最后一名，仍是待验证信号。"),
    card("googlePlay", "GIRLS' FRONTLINE 2", "exit", "从Google上期#45掉榜，iOS当前也未进入TOP60。产品此前位于中后段，本次直接滑出但没有同日可确认的重大运营节点，不能据此推断长期下行。"),
    card("googlePlay", "Vikings: War of Clans", "exit", "从Google上期#58掉榜，iOS未进入TOP60。成熟长线4X原已贴近截线，本次更接近榜尾自然轮换，仍需后续快照确认是否回归。"),
    card("googlePlay", "Arknights", "up", "继昨日双端回榜后，Google再升6位至#9，iOS仅小幅回落至#7。Episode 17窗口已延续到第二个快照，但榜位变化仍不能等同于收入增幅。"),
    card("googlePlay", "Age of Empires Mobile", "up", "Google上升6位至#41，iOS当前#27。双端均在榜但名次差14位；10月8日版本说明仅披露修复，暂不把本次改善归为内容拉动。"),
    card("googlePlay", "Top Heroes", "up", "Google上升5位至#34，iOS也上升4位至#51，形成温和同向改善。近期Lord Runes与赛季交互调整是可核验背景，但还不足以证明持续趋势。"),
    card("googlePlay", "Overgeared Hero", "down", "Google下跌4位至#37，同时从iOS上期#56掉榜。Raven联动与万圣节内容仍在，但跨端同步走弱表明版本存在并不保证单日榜位上涨。"),
    card("googlePlay", "Rise of Castles", "down", "Google下跌4位至#39，iOS当前未进入TOP60。变动幅度不大且仍在中段，未发现同日可确认的重大转折，先按正常区间震荡记录。"),
]


ios_products = [
    card("ios", "Limbus Company", "entry", "回到iOS #35，而Google从上期#45掉榜。最近可确认节点仍是9月Season 8，今天未发现同步重大更新；跨端相反方向不支持统一归因。"),
    card("ios", "League of Legends: Wild Rift", "entry", "回到iOS #50，并同步回到Google #60。7.3b调整英雄、装备、符文与野区，是可核验背景；但该产品本质为MOBA分类边界，且两端均在后段。"),
    card("ios", "Last Shelter: War Z", "entry", "回到iOS #54，对应Google同名产品当前#35。双端均在榜但名次差19位，未发现与源更新时间同步的重大节点，先按iPhone端回补观察。"),
    card("ios", "Star Trek Fleet Command", "entry", "回到iOS #55，Google仍在#25。Division 12于10月15日加入SNW Rose Harper、Haven Exchange与限时活动；时间相邻但iOS仍靠近榜尾。"),
    card("ios", "Call of Dragons", "entry", "回到iOS #60，并同步回到Google #53。双端共同进入是待验证信号，但iOS恰处最后一名，下一快照留榜比单日名次更重要。"),
    card("ios", "SimCity BuildIt", "exit", "Haunted Metropolis赛季开启后仅回榜一个快照，本期从#52掉榜。赛季内容真实存在，但短时退出说明首日回补尚未形成稳定承接。"),
    card("ios", "Lords Mobile", "exit", "从iOS上期#54掉榜，Google仍在#31。当前Transformers联动仍体现在商店标题，但跨端结果不同，不能把退出外推为产品整体转弱。"),
    card("ios", "Overgeared Hero", "exit", "从iOS上期#56掉榜，Google同步下跌4位至#37。Raven联动与万圣节内容仍在，今天只能确认双端走弱，不能据此判断活动失效。"),
    card("ios", "Kiss of War", "exit", "昨日回榜#59后即掉出iOS TOP60，Google当前未进榜。一次榜尾回补只维持一个快照，符合成熟军事4X的截线轮换特征。"),
    card("ios", "War Machines", "exit", "昨日回到#60后本期即掉榜。9月29日版本只披露修复与性能优化，连续两天的一进一出更接近榜尾短时波动。"),
    card("ios", "Dragon Traveler", "up", "iOS大涨25位至#26，为本端最大变化。现有可确认节点仍是BUFF 101合作内容；单日跃升需看下一快照能否守住前30。"),
    card("ios", "Foundation: Galactic Frontier", "up", "iOS上升8位至#32，Google当前未进入TOP60。产品仍处上线后验证期，今天只记录为iPhone端改善，尚无双端共振。"),
    card("ios", "Game of Thrones: Dragonfire", "up", "iOS上升8位至#12，Google则下跌2位至#29。仍处首发后的运营验证阶段，跨端分化使单一活动解释缺少支撑。"),
    card("ios", "The Tower - Idle Tower Defense", "down", "iOS再跌16位至#59，继昨日−9后连续回吐，已进入掉榜风险区。v29是可核验背景，但连续回落更像版本峰值消退信号。"),
    card("ios", "Warhammer 40,000: Tacticus", "down", "iOS下跌10位至#58，Google当前未进TOP60。成熟IP战术RPG进入后三区间，未发现同日重大节点，先按掉榜风险信号处理。"),
    card("ios", "Sea War: Uboat Raid", "down", "昨日大涨19位后，本期回落9位至#47，仍高于10月14日位置。Google小幅升至#55，一升一降更像iPhone端短峰回吐。"),
    card("ios", "Hearthstone", "down", "37.0预发布窗口内从#24回落7位至#31。10月20日资料片尚未正式发布，当前不能把预发布阶段的一次回落等同于内容表现。"),
]


news = [
    {
        "category": "IP 4X / 限时版本", "date": "2026-10-15",
        "title": "Star Trek Fleet Command上线Division 12",
        "summary": "Scopely官方说明Division 12加入Epic Officer SNW Rose Harper、Haven Exchange与多组Heroic Solo Milestone，限时活动于10月15日开启。",
        "impact": f"产品本期回到iOS #{current_rank('ios', 'Star Trek Fleet Command')}，Google位于#{current_rank('googlePlay', 'Star Trek Fleet Command')}；版本与回榜时间相邻，但跨端强度差异明显。",
        "source": "Star Trek Fleet Command官方", "url": "https://startrekfleetcommand.com/news/division-12-patch-notes/",
    },
    {
        "category": "MOBA / 平衡补丁", "date": "2026-10-14",
        "title": "Wild Rift 7.3b调整英雄、装备、符文与野区",
        "summary": "Riot官方7.3b对Volibear、Jhin、Hwei等英雄及多件装备、符文和野怪数值进行调整，并于10月15日开放Legends Showdown限定兑换内容。",
        "impact": f"产品同步回到Google #{current_rank('googlePlay', 'League of Legends: Wild Rift')}与iOS #{current_rank('ios', 'League of Legends: Wild Rift')}；双端共同进入值得跟踪，但它属于MOBA分类边界且Google恰在榜尾。",
        "source": "Wild Rift官方", "url": "https://wildrift.leagueoflegends.com/en-us/news/game-updates/wild-rift-patch-notes-7-3b/",
    },
    {
        "category": "塔防RPG / 主线大版本", "date": "2026-10-14",
        "title": "Arknights开放Episode 17《Critical Phase Transition》",
        "summary": "官方公告将Episode 17开放时间定为10月14日08:00（UTC-7），并在10月28日前临时降低主线解锁要求，部分内容限时开放。",
        "impact": f"产品本期Google继续升至#{current_rank('googlePlay', 'Arknights')}、iOS仍守#{current_rank('ios', 'Arknights')}，活动窗口延续到第二个快照；仍不能把名次直接换算为收入变化。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4814",
    },
    {
        "category": "城市经营 / 万圣节赛季", "date": "2026-10-13",
        "title": "SimCity BuildIt开启Haunted Metropolis 28日赛季",
        "summary": "EA官方说明赛季从10月14日至11月11日运行，加入13级Rift Tower、全城02:00夜景效果、Haunted Street及多组哥特建筑。",
        "impact": "产品昨日回到iOS #52后本期掉榜；赛季内容与首日回补时间相邻，但未形成连续留榜。",
        "source": "Electronic Arts官方", "url": "https://www.ea.com/games/simcity/simcity-buildit/news/welcome-to-haunted-metropolis-streets-of-fright",
    },
    {
        "category": "回合制策略RPG / 电竞", "date": "2026-10-14",
        "title": "Summoners War发布SWC2026美洲杯结果并预告亚太杯",
        "summary": "Com2uS官方公布美洲杯前三名晋级世界总决赛，并将亚太杯直播安排在10月16日，区域杯进入最后席位争夺。",
        "impact": f"产品本期iOS位于#{current_rank('ios', 'Summoners War')}；亚太杯直播窗口提供曝光背景，但今天的榜位未出现同量级跃升。",
        "source": "Summoners War官方", "url": "https://summonerswar.com/en/skyarena/news",
    },
    {
        "category": "卡牌策略 / 资料片预发布", "date": "2026-10-12",
        "title": "Hearthstone 37.0进入Black Empire预发布窗口",
        "summary": "Blizzard官方37.0于10月13日上线，加入新竞技场卡池、预发布乱斗、Journal与奖励内容；Reign of the Black Empire定于10月20日正式发布。",
        "impact": f"产品本期回落至iOS #{current_rank('ios', 'Hearthstone')}；10月20日正式资料片前仍需区分预发布短峰与正式内容承接。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "全球市场 / 收入榜", "date": "2026-10-01",
        "title": "Sensor Tower 9月全球收入TOP10策略子集仍为3款",
        "summary": "官方全球手游收入TOP10图中，核心策略产品为Whiteout Survival #6、Last War #7与Kingshot #9；统计覆盖Apple App Store与Google Play并排除第三方Android商店。",
        "impact": "月榜显示三款策略头部仍在全球收入总榜，但不能把该全球月度结果当作美国单区日榜变化，也不能重新编号成策略第1至第3名。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
    {
        "category": "增量塔防 / 大版本", "date": "2026-10-06",
        "title": "The Tower v29后连续两日回吐",
        "summary": "Apple官方v29加入Global Presets、Preset Lab、Mythic联赛、重做Vault与Harmony Tree，以及新卡牌和模块内容。",
        "impact": f"产品本期继续回落至iOS #{current_rank('ios', 'The Tower')}，已接近掉榜线；版本存在不等于榜位单向上涨，当前更接近短峰消退观察。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id1575590830",
    },
    {
        "category": "长线4X / 九周年", "date": "2026-10-05",
        "title": "Game of Thrones: Conquest推进九周年月内容",
        "summary": "官方10月预览列出Military III、Dragon Combat研究树、Old Nan's Tales、Viserion与Free Folk装备，以及10月26日英雄活动。",
        "impact": f"产品本期Google #{current_rank('googlePlay', 'Game of Thrones: Conquest')}、iOS #{current_rank('ios', 'Game of Thrones: Conquest')}；两端都在中后段，九周年内容仍需连续快照观察。",
        "source": "Game of Thrones: Conquest官方", "url": "https://www.gotconquest.com/news/2026/10/05/october-preview-9th-anniversary-celebration/",
    },
    {
        "category": "背包策略 / IP联动", "date": "2026-10-13",
        "title": "Overgeared Hero加入Raven联动与万圣节内容",
        "summary": "Apple官方1.41.0加入Raven联动皮肤、三款万圣节传奇皮肤，以及装备分解与材料兑换的Gear Workshop。",
        "impact": f"产品本期Google下跌至#{current_rank('googlePlay', 'Overgeared Hero')}、iOS掉榜；联动内容真实存在，但今天不支持“版本必然拉升”的判断。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id6755585789",
    },
    {
        "category": "城建策略 / 体验改版", "date": "2026-10-13",
        "title": "Clash of Clans重做Builder菜单与村庄管理入口",
        "summary": "Apple官方18.647.2重做Builder Suggestions并增加筛选与分类，同时调整Battle菜单、玩家资料与Clan Chat。",
        "impact": f"产品当前Google #{current_rank('googlePlay', 'Clash of Clans')}、iOS #{current_rank('ios', 'Clash of Clans')}；头部位置仍稳，改版更适合作为长期留存背景。",
        "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/id529479190",
    },
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "Google两进两出，主体稳定但榜尾完成一轮替换",
        "detail": "Google 58款共同产品中52款位移不超过2名，中位绝对变动1名；Call of Dragons与Wild Rift回榜，GFL2与Vikings掉榜，Arknights和Age of Empires各+6。",
    },
    {
        "type": "判断", "title": "iOS五进五出，榜尾轮换与中段振幅同时扩大",
        "detail": "iOS 55款共同产品中31款位移不超过2名，中位绝对变动1名，11款变动至少5位；Dragon Traveler +25，The Tower −16，Tacticus −10。",
    },
    {
        "type": "判断", "title": "Call of Dragons与Wild Rift双端共同回归，Limbus和Overgeared反向分化",
        "detail": f"Call of Dragons与Wild Rift同步进入两端；Limbus回到iOS #{current_rank('ios', 'Limbus Company')}却从Google掉榜，Overgeared则Google下跌且iOS掉榜。Arknights仍维持双端前10。",
    },
    {
        "type": "关注", "title": "下一有效快照：验证两款双端回榜产品是否留榜",
        "detail": "Call of Dragons需至少守住Google后八名与iOS榜尾，Wild Rift需避免从Google #60立即退出；若任一端快速掉榜，仍按版本或活动窗口内短时回补处理。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：检查Division 12与iOS榜尾承接",
        "detail": "Star Trek、Last Shelter与Call of Dragons都在iOS #54以后；重点看Star Trek能否借Division 12脱离榜尾，以及另外两款是否维持双端在榜。",
    },
    {
        "type": "关注", "title": "10月20日前后：验证Dragon Traveler跃升与两款版本短峰",
        "detail": "Dragon Traveler需在下一快照守住前30；Hearthstone需观察正式资料片发布后的回升，The Tower若从#59掉榜则可将v29后的前期高点进一步视为短峰。",
    },
]


google_history = load("data/history/google-play/2026-10-16.json")
ios_history = load("data/history/ios/2026-10-16.json")
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
    "title": "Call of Dragons与Wild Rift双端回榜，iOS五进五出延续高波动",
    "summary": "较10月15日前一有效快照，Google Play两进两出：Call of Dragons与Wild Rift回榜，GFL2与Vikings掉榜；Arknights、Age of Empires各+6。iOS五进五出：Limbus、Wild Rift、Last Shelter: War Z、Star Trek与Call of Dragons回榜，SimCity、Lords Mobile、Overgeared、Kiss of War和War Machines掉榜；Dragon Traveler +25，The Tower −16，Tacticus −10。近90天新品为Google 1款、iOS 2款；两端缺少7月18日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261016.json",
    "rankingSources": {"googlePlay": "data/games-20261016.json", "ios": "data/ios-games-20261016.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261015.json", "ios": "data/ios-games-20261015.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Star Trek Fleet Command · #60 League of Legends: Wild Rift",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": f"榜单锚点：#1 Kingshot · #25 {datasets['ios']['now'][24]['gameName']} · #60 Call of Dragons",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-18"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-18"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-16.md", "json": "data/market-brief-20261016.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-15；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-18精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261016.json", brief)
(ROOT / "reports/2026-10-16.md").write_text(build_markdown(brief), encoding="utf-8")
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
