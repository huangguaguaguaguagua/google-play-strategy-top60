#!/usr/bin/env python3
"""Generate the Beijing 2026-10-28 market brief, local icons and archive entry."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-10-28", "20261028"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load("data/games-20261028.json"), "prior": load("data/games-20261027.json"), "id": "packageName"},
    "ios": {"now": load("data/ios-games-20261028.json"), "prior": load("data/ios-games-20261027.json"), "id": "appId"},
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
    card("googlePlay", "Supremacy: World War 3", "entry", "回到Google #60，iOS仍在#41。现代战争与联盟外交在Android仅压线进入，当前是榜尾回补而非双端同步上行。"),
    card("googlePlay", "Last Fortress", "exit", "上期Google #58后掉榜，iOS未入榜。地下庇护所与联盟4X未连续留位，仍按榜尾轮换处理。"),
    card("googlePlay", "Game of Thrones: Conquest", "up", "Google上升16位至#41，iOS反向跌至#27。九周年2026_10更新仍在窗口，但跨端方向相反，不能把Android升幅全归因于活动。"),
    card("googlePlay", "Lands of Jail", "up", "Google上升5位至#28，iOS也升至#30。双端名次接近且同向改善，但一个快照不足以确认共同活动峰值。"),
    card("googlePlay", "Rise of Castles", "up", "Google上升4位至#21，iOS未入榜。成熟城堡4X在Android回升，未找到足以解释全部变化的同步官方节点。"),
    card("googlePlay", "Warhammer 40,000", "up", "Google上升3位至#40，iOS反向下跌11位至#43。两端名次接近但方向相反，先按平台节奏分化记录。"),
    card("googlePlay", "Duck Survival", "down", "Google下跌4位至#46，iOS未入榜。武装鸭子与昼建夜守仍处中后段，本次只记为单期回落。"),
    card("googlePlay", "Last Shelter: Survival", "down", "Google下跌4位至#52；iOS的Last Shelter: War Z是另一商店条目，不因相似名称串榜。Android已落入后十名，需观察榜尾风险。"),
    card("googlePlay", "Narco Empire", "down", "Google下跌3位至#30。产品仍是2026年7月上线的近90天新品，单期回撤不改新品分类，也不外推成熟期走势。"),
    card("googlePlay", "Mafia City", "down", "Google下跌3位至#54。成熟黑帮SLG进入后十名，未发现与今天同步的重大官方节点。"),
]


ios_products = [
    card("ios", "Plants on Fire", "entry", "回到iOS #32。8月上架的三分钟植物PvP仍属近90天新品；10月版本与回榜时间相邻，但不能据此确定因果。"),
    card("ios", "Sea War", "entry", "回到iOS #37。10月21日版本加入精英招募角色与回归福利，当前只确认中段回补。"),
    card("ios", "The Tower", "entry", "回到iOS #41。永久研究、卡牌与锦标赛构成成熟长线盘，本次回补尚未形成连续留位证据。"),
    card("ios", "Last Shelter: War Z", "entry", "回到iOS #48。2026年6月上架的地下庇护所产品位于中后段，仍需验证首发期承接。"),
    card("ios", "Kiss of War", "entry", "回到iOS #53。二战军官收集与军团4X成熟盘只在榜尾回补，未发现同步重大节点。"),
    card("ios", "Evo Defense", "entry", "回到iOS #57。三分钟合成塔防仍在验证PvP与英雄养成承接，当前是榜尾信号。"),
    card("ios", "West Game", "entry", "项目历史首次收录于iOS #58。Apple显示2019年上架，因此不属于近90天新品；法律主体与产品体系已由Apple和Leyi官方产品页闭环核验。", {"1453356737"}),
    card("ios", "Galaxy Defense", "exit", "上期iOS #47后掉榜，Google未入榜。科幻塔防的前一日回补没有延续。"),
    card("ios", "Kingdom Guard", "exit", "上期iOS #48后掉榜，Google未入榜。塔防合成与联盟循环再次落出榜尾。"),
    card("ios", "Star Trek Fleet Command", "exit", "上期iOS #49后掉榜，Google仍在榜。10月联盟锦标赛更新未对应为iPhone端连续留位。"),
    card("ios", "The Battle Cats", "exit", "上期iOS #52后掉榜，Google未入策略榜。本次只记录Apple策略标签下的榜尾轮换。"),
    card("ios", "Age of Spirits", "exit", "上期iOS #58后掉榜，但Google仍在#56。9月上架的近90天新品出现跨端分化，不写成产品整体退潮。"),
    card("ios", "Last Shelter: Survival", "exit", "上期iOS #59后掉榜，Google同名长期产品跌至#52。双端都承受后段压力，但两条商店记录仍独立计算。"),
    card("ios", "Aliens vs Zombies", "exit", "上期iOS #60后掉榜，Google未入榜。末位留位未延续，先按榜尾风险记录。"),
    card("ios", "Lands of Jail", "up", "iOS上升9位至#30，Google也升至#28。双端同步进入前30附近，但仍需后续快照验证是否为活动峰值。"),
    card("ios", "Rise of Kingdoms", "up", "iOS上升7位至#26，Google#19。文明选择与自由行军的成熟4X双端仍在前中段；单日名次不等于收入增长。"),
    card("ios", "MARVEL SNAP", "up", "iOS上升7位至#46，Google未入策略榜。Marvel短局卡牌回到中后段，只按Apple策略标签内的单期信号处理。"),
    card("ios", "Game of Thrones: Dragonfire", "up", "iOS上升3位至#24。10月15日Kalspire内容仍是近期背景，但没有证据证明其单独造成本次上升。"),
    card("ios", "Boom Beach", "down", "iOS下跌14位至#51，Google未入榜。10月Blitz仍在近期窗口，本期大幅回吐需要活动后快照继续确认。"),
    card("ios", "Warhammer 40,000", "down", "iOS下跌11位至#43，Google反向升至#40。两端位置接近但方向相反，不能写成统一趋势。"),
    card("ios", "Summoners War", "down", "iOS下跌9位至#55。9.3.6版本与变化相邻，但成熟魔灵盘的本次回落仍只视为单期信号。"),
    card("ios", "Game of Thrones: Conquest", "down", "iOS下跌5位至#27，Google反向大升至#41。九周年更新没有形成双端同步方向。"),
    card("ios", "Overgeared", "down", "iOS下跌5位至#59，Google仍在中段。iPhone端已接近掉榜，需下一快照验证。"),
]


news = [
    {
        "category": "冰雪城建 / 节日运营", "date": "2026-10-27",
        "title": "Whiteout Survival万圣活动正式开启",
        "summary": "活动资料列出10月27日至11月2日的Halloween Party、Pumpkin Invasion、Nightmare Pumpkin King与阶段奖励，Kasia's Wish House于10月28日开启；来源为跟踪官方游戏内公告的社区资料。",
        "impact": f"产品当前Google#{current_rank('googlePlay', 'Whiteout')}、iOS#{current_rank('ios', 'Whiteout')}，仍居双端头部；活动与名次时间相邻，但不写成唯一原因。",
        "source": "Whiteout Survival Wiki（社区转录）", "url": "https://www.whiteoutsurvival.wiki/sneak-peek/102514638en/",
    },
    {
        "category": "IP 4X / 九周年", "date": "2026-10-15",
        "title": "Game of Thrones: Conquest 2026_10扩充研究树与操作优化",
        "summary": "官方九周年更新加入研究扩展、援军排序、配方收藏、书签分类、Dragon Lore计数及多项界面和性能修复。",
        "impact": f"本期Google升至#{current_rank('googlePlay', 'Game of Thrones: Conquest')}、iOS跌至#{current_rank('ios', 'Game of Thrones: Conquest')}；更新窗口内跨端反向，不能作确定归因。",
        "source": "Game of Thrones: Conquest官方", "url": "https://www.gotconquest.com/news/2026/10/15/release-notes-2026_10/",
    },
    {
        "category": "科幻4X / 联盟运营", "date": "2026-10-22",
        "title": "Star Trek Fleet Command调整联盟锦标赛并公布11月Rally",
        "summary": "官方确认Alliance Tournaments于10月23日回归并调整任务；11月9日至11日将测试两日Rally，以较短周期复用任务和个人奖励。",
        "impact": "产品本期从iOS掉榜、Google仍留榜；联盟运营节点没有对应为双端同步改善，需分平台观察。",
        "source": "Star Trek Fleet Command官方", "url": "https://startrekfleetcommand.com/news/alliance-tournaments-updates-october-2026/",
    },
    {
        "category": "卡牌策略 / 资料片", "date": "2026-10-12",
        "title": "Hearthstone 37.0与Reign of the Black Empire资料片落地",
        "summary": "Blizzard官方37.0说明确认10月20日开放135张卡的Reign of the Black Empire，引入Assemble关键词并刷新Rewards Track。",
        "impact": f"产品本期iOS#{current_rank('ios', 'Hearthstone')}且继续回落；观察资料片首发峰值后能否在未来1—2个快照稳定承接。",
        "source": "Blizzard官方", "url": "https://hearthstone.blizzard.com/en-us/news/24301454",
    },
    {
        "category": "塔防RPG / 主线大版本", "date": "2026-10-09",
        "title": "Arknights Episode 17进入Extreme Mode收尾窗口",
        "summary": "官方Episode 17公告将Extreme Mode开放时间定为10月21日，并说明限时较低解锁门槛与Factory scrip掉落将在10月28日结束。",
        "impact": f"产品当前Google#{current_rank('googlePlay', 'Arknights')}、iOS#{current_rank('ios', 'Arknights')}；版本节点用于解释运营窗口，不等同榜位必然抬升。",
        "source": "Arknights官方", "url": "https://www.arknights.global/news/4814",
    },
    {
        "category": "西部SLG / 长线回榜", "date": "2026-09-28",
        "title": "West Game 7.4.0扩充联盟科技与铁路事件",
        "summary": "Apple版本资料列出联盟科技无限捐赠、训练容量道具、集结提醒、Railway Rampage与Cargo Escort；Leyi官方产品页确认其为西部题材SLG。",
        "impact": f"产品首次进入项目iOS榜#{current_rank('ios', 'West Game')}；版本时间相邻但只记为成熟产品榜尾回补，不能写成增长因果。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/west-game/id1453356737",
    },
    {
        "category": "实时PvP / 新品", "date": "2026-10-15",
        "title": "Plants on Fire 2.0.2870加入Pirate Captain与Ace Plan",
        "summary": "Apple版本资料显示该更新加入新传奇卡Pirate Captain、新植物和四种变体、Ace Plan活动与Auto Chess相关内容。",
        "impact": f"产品本期回到iOS#{current_rank('ios', 'Plants on Fire')}，并按8月26日releaseDate归类为近90天新品；仍需验证版本后留位。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/plants-on-fire/id6776076449",
    },
    {
        "category": "海战SLG / 回归运营", "date": "2026-10-21",
        "title": "Sea War 1.175.0加入精英招募角色与回归福利",
        "summary": "Apple版本记录列出两名精英招募角色与回归指挥官福利，继续围绕舰长、潜艇编队和海上基地运营。",
        "impact": f"产品本期回到iOS#{current_rank('ios', 'Sea War')}；回榜与版本相邻，但当前只有一个有效快照。",
        "source": "Apple App Store美国区商品页", "url": "https://apps.apple.com/us/app/sea-war-uboat-raid/id6447612873",
    },
    {
        "category": "基地攻防 / 竞技活动", "date": "2026-09-15",
        "title": "Boom Beach Blitz活动后的榜位回吐进入观察期",
        "summary": "Supercell官方9月更新介绍Blitz竞争型Leader活动，10月2日开启，以Leader构筑和挑战扩展成熟基地攻防循环。",
        "impact": f"产品本期iOS下跌14位至#{current_rank('ios', 'Boom Beach')}；需观察活动后留位，不能由单次回吐判断长线衰退。",
        "source": "Supercell官方", "url": "https://supercell.com/en/games/boombeach/blog/blog/september-update-blitz/",
    },
    {
        "category": "全球市场 / 收入榜", "date": "2026-10-01",
        "title": "Sensor Tower最新完整全球收入榜仍为2026年9月",
        "summary": "官方9月全球手游收入TOP10的核心策略子集仍为Whiteout Survival #6、Last War #7与Kingshot #9；口径覆盖App Store和Google Play并排除第三方Android商店。",
        "impact": "本工作日仅检查一次官方博客，未发现更新一期完整图表，因此保留9月真实统计期；全球月榜不替代美国单区日榜。",
        "source": "Sensor Tower官方", "url": "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026",
    },
]
for rank, item in enumerate(news, 1):
    item["rank"] = rank


closing = [
    {
        "type": "判断", "title": "双端头部稳定，波动集中在中后段与榜尾",
        "detail": "Kingshot在Google和iOS均为#1，Whiteout Survival均为#2；Google仅一进一出且59款共同产品中48款位移不超过2名，iOS七进七出且53款共同产品中31款位移不超过2名。",
    },
    {
        "type": "判断", "title": "同产品跨端方向并不一致，活动节点不能替代平台榜面",
        "detail": "Game of Thrones: Conquest在Google +16至#41、iOS −5至#27；Tacticus在Google +3至#40、iOS −11至#43。Lands of Jail则双端同向升至#28/#30，仍只算待验证信号。",
    },
    {
        "type": "判断", "title": "近90天新品集中于少数产品，精确90天飙升仍不判定",
        "detail": "Google新品为Top Force #15、Age of Spirits #56、Last Human #57；iOS新品仅Plants on Fire #32。两端缺少2026-07-30精确同口径完整基准，因此较老产品内部pending、页面按常规展示。",
    },
    {
        "type": "关注", "title": "下一有效快照：核验七款iOS回榜产品与七款掉榜产品",
        "detail": "重点看Plants on Fire、Sea War与The Tower能否留在前45，以及Kiss of War、Evo Defense、West Game是否仍停留后十名；再次退出则继续按榜尾轮换处理。",
    },
    {
        "type": "关注", "title": "未来1—2个快照：复核Google显著上行与双端反向",
        "detail": "观察GoT Conquest能否保留+16，Lands of Jail能否双端维持前30附近，并核验Tacticus的Google/iOS反向是否快速收敛。",
    },
    {
        "type": "关注", "title": "至10月30日：观察iOS大幅回吐产品的榜尾风险",
        "detail": "Boom Beach、Tacticus、Summoners War分别下跌14、11、9位；若Boom Beach与Summoners War继续跌出TOP60，再结合活动/版本窗口评估是否只是短期峰值回吐。",
    },
]
google_history = load("data/history/google-play/2026-10-28.json")
ios_history = load("data/history/ios/2026-10-28.json")
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
    "title": "双端头部稳定；Google一进一出，iOS七进七出",
    "summary": "较10月27日前一有效快照，Google Play一进一出，59款共同产品中48款位移不超过2名；Game of Thrones: Conquest +16、Lands of Jail +5，Supremacy: World War 3压线回榜。iOS七进七出，Lands of Jail +9、Rise of Kingdoms与MARVEL SNAP各+7，Boom Beach −14、Tacticus −11。Google近90天新品3款、iOS 1款；两端缺少7月30日精确基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": "assets/market-icons-20261028.json",
    "rankingSources": {"googlePlay": "data/games-20261028.json", "ios": "data/ios-games-20261028.json"},
    "previousRankingSources": {"googlePlay": "data/games-20261027.json", "ios": "data/ios-games-20261027.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Palmon: Survival · #60 Supremacy: World War 3",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Kingshot · #25 Police Chief · #60 Lords Mobile: Kingdom Wars",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-30"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-07-30"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-10-28.md", "json": "data/market-brief-20261028.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-10-27；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-07-30精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20261028.json", brief)
(ROOT / "reports/2026-10-28.md").write_text(build_markdown(brief), encoding="utf-8")
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
