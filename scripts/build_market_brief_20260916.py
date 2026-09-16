#!/usr/bin/env python3
"""Generate the Beijing 2026-09-16 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-16"
STAMP = "20260916"
CURRENT = "20260916"
PREVIOUS = "20260915"


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


google_history = load("data/history/google-play/2026-09-16.json")
ios_history = load("data/history/ios/2026-09-16.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Vikings: War", "entry", "9月14日回到Google #60、15日掉榜，今天又压线回到#60；iOS仍在榜外。三个连续快照说明它处于榜尾反复进出阶段，不能写成稳定回暖。"),
    card("googlePlay", "Last Fortress: Underground", "exit", "昨日刚以#60回榜，今天立即退出Google TOP60，iOS当前也未入榜；这进一步确认昨日只是末位信号，尚不能据此判断长线收入。"),
    card("googlePlay", "Ant Legion", "up", "昨日回榜#59后再升7位至#52，开始脱离末两位，但iOS仍无同口径排名；需再看一至两个工作日能否进入前50。"),
    card("googlePlay", "Infinity Kingdom", "up", "Google由#33升5位至#28，iOS在昨日大涨后小幅回落至#23；两端仍同时位于前半区，延续了跨端改善，但当前没有可核验活动能解释幅度。"),
    card("googlePlay", "Top Heroes", "up", "Google升4位至#20，iOS却降6位至#43；同一产品出现明显平台分化，今天更像Android端改善而不是双端共同上行。"),
    card("googlePlay", "Sea War", "down", "Google跌6位至#58，iOS也跌3位至#56，两端同时进入后五名；这是今天较清晰的共同榜尾风险，但仍只是一日信号。"),
    card("googlePlay", "MARVEL SNAP", "down", "Google降3位至#56、iOS降1位至#51。9月15日57.x更新加入角色精通奖励改版并预告Draft回归，但尚无证据把双端回落归因于更新。"),
    card("googlePlay", "Game of Thrones: Conquest", "down", "Google再降2位至#59，iOS反而升4位至#38；Android已处掉榜线，iPhone则回到中段，跨端差距扩大。"),
]


ios_products = [
    card("ios", "Hearthstone", "entry", "回到iOS #53；36.4的世界冠军乱斗在9月16日结束、Kel'Thuzad神话皮肤仍在售。活动窗口与回榜相邻，但不能由榜位确认具体付费来源。"),
    card("ios", "Draft Showdown", "entry", "回到iOS #48，同时Google升1位至#57；两端都在榜内但仍偏后段，短局选秀和自动战斗是否形成连续付费需要后续快照确认。"),
    card("ios", "Rise of Castles", "entry", "回到iOS #54，而Google同产品位于#15；成熟4X仍呈显著Android优势，iPhone端当前只是榜尾回归。"),
    card("ios", "Lords Mobile", "entry", "以#60压线回到iOS，Google则在#27；Transformers联动仍是商店主视觉，但单日回榜不足以证明IP活动带来持续增量。"),
    card("ios", "League of Legends: Wild Rift", "exit", "上期iOS #52后掉榜，Google仍稳定在#40；7.2e补丁是近期可核验节点，但今天只显示iPhone端退出，不能外推为产品整体下滑。"),
    card("ios", "Last Shelter: Survival", "exit", "昨日回榜#59后立即退出，Google成熟版本仍在#49；这是一轮未脱离榜尾的短时回归，且不能与新作War Z合并判断。"),
    card("ios", "Last Shelter: War Z", "exit", "昨日首次进入#60后今天即掉榜，Google版本反而升至#44。联盟决斗锦标赛首轮仍在进行，跨端结果说明活动节点与单端榜位不能直接画等号。"),
    card("ios", "Last Day on Earth", "exit", "上期已降至#55，今天退出iOS TOP60；当前Google策略榜没有同产品排名，暂按单端榜尾风险记录，未发现可确认的重大运营转折。"),
    card("ios", "Last War:Survival", "up", "由#4升3位至iOS榜首，Google保持#3；这是今天头部最明确的变化，但单次登顶只代表当前快照，仍需观察能否连续保持。"),
    card("ios", "Evo Defense", "up", "由#56跃升19位至#37，脱离掉榜区；Google没有同口径排名，也没有匹配幅度的官方节点，因此先按iPhone端待验证脉冲处理。"),
    card("ios", "The Tower - Idle", "up", "由#49升19位至#30，成为另一款当日大涨塔防；Google未入榜，当前信号集中在iOS，不能据此判断品类整体上行。"),
    card("ios", "Kingdom Guard", "down", "iOS跌8位至#55，Google也小降至#51；两端共同靠近榜尾，与昨日的双端改善相反，后续能否守榜是关键。"),
    card("ios", "Top War", "down", "iOS跌8位至#46，Google却升1位至#35；方向分化显示平台付费节奏不同，不能用iOS回落概括双端。"),
    card("ios", "Raid Rush", "up", "iOS升7位至#39，Google也升3位至#53；两端方向一致但Android仍处后段，至少需要下一快照确认是否持续。"),
    card("ios", "Forge Master", "up", "iOS升6位至#29，Google小降至#45；iPhone端回到前半区，Android并未同步，当前属于平台分化。"),
    card("ios", "Top Heroes", "down", "iOS降6位至#43，Google则升4位至#20；与Google卡片相互印证，今天的改善明显集中在Android端。"),
]


news = [
    {"category": "版本 / 成长系统", "date": "2026-09-15", "title": "MARVEL SNAP 57.x重做角色精通奖励轨道", "summary": "官方更新加入Wild Boosters、Split Reroll Coins、额外Custom Card槽位与Level 27奖励，并预告Draft于9月28日回归。", "impact": "该作今天Google #56、iOS #51且两端均小幅回落；新系统是后续付费与回流的核验节点，不能解释为当天名次原因。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/patch-notes-september-15-2026/"},
    {"category": "卡牌 / 赛事", "date": "2026-08-24（9月9—16日乱斗）", "title": "Hearthstone 36.4叠加世界冠军乱斗与神话皮肤", "summary": "Blizzard在36.4加入四组职业套牌、新竞技场赛季和免费奖励；世界冠军乱斗运行至9月16日，Kel'Thuzad神话皮肤持续至10月13日。", "impact": "Hearthstone今天回到iOS #53，活动末日与回榜相邻；需继续观察活动结束后是否留榜。", "source": "Blizzard官方", "url": "https://news.blizzard.com/en-us/article/24293283/36-4-patch-notes"},
    {"category": "新品 / 联盟赛事", "date": "2026-09-10（9月13日首轮匹配）", "title": "Last Shelter: War Z开启四周制联盟决斗锦标赛", "summary": "Apple官方版本说明显示26.0902.001新增Alliance Duel Tournament，并以相近联盟实力进行四周匹配。", "impact": "该作今天从iOS #60掉榜、Google升至#44；同一运营节点对应不同平台结果，不能直接认定增收。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/last-shelter-war-z/id6760406772"},
    {"category": "IP活动 / 长线运营", "date": "2026-09-09", "title": "Clash of Clans推出WWE Equipment Blast活动", "summary": "Supercell公布9月9日至22日的勋章活动，玩家通过多人战斗获取Tag Tickets、Champ Medals、临时兵种与装备奖励。", "impact": "CoC继续位于双端头部；活动可用于观察头部稳定性，但不能拆算其单独收入贡献。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/news/equipment-blast-medal-event/"},
    {"category": "版本 / 跨端", "date": "2026-09-09", "title": "Wild Rift 7.2e调整Vi、Swain及多件装备", "summary": "Riot削弱Vi、Swain，并增强Janna、Nautilus、Malphite等英雄，同时修改多件装备。", "impact": "该作今天退出iOS策略TOP60而Google仍为#40；补丁只是背景，尚无官方材料证明与离榜存在因果。", "source": "Riot Games官方", "url": "https://wildrift.leagueoflegends.com/en-us/news/game-updates/wild-rift-patch-notes-72e/"},
    {"category": "赛季 / 平衡", "date": "2026-09-08", "title": "Clash Royale九月平衡覆盖Hero Balloon与Freeze", "summary": "Supercell调整Hero Balloon、Freeze、Fireball及多张进化卡，并重做Hero Mega Minion等单位。", "impact": "Clash Royale目前仍处双端头部；平衡更新用于解释竞技环境变化，不应由排名换算收入。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/september-balance-changes-2026/"},
    {"category": "竞技规则", "date": "2026-09-02（9月8日生效）", "title": "Pokémon Champions启用Regulation Set M-C", "summary": "宝可梦官方宣布9月8日至12月1日适用新规则，加入多种Mega Evolution与24只新可用宝可梦。", "impact": "该作当前仅在Google榜尾附近、iOS榜外；规则更新与Android留榜相邻，仍不足以认定商业化驱动。", "source": "Pokémon官方", "url": "https://www.pokemon.com/us/news/get-ready-for-regulation-set-m-c-in-pokemon-champions"},
    {"category": "全球收入月榜", "date": "2026-09-04", "title": "Sensor Tower公布8月全球手游收入TOP10", "summary": "全球App Store与Google Play手游消费者支出估算约65.7亿美元，Whiteout Survival全球总榜#3、Kingshot #7。", "impact": "两款核心策略产品较7月各升1位；官方未公开单品收入同比，不能由名次换算收入百分比。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"},
    {"category": "长线运营", "date": "2026-09-04", "title": "King of Avalon十周年活动持续至9月30日", "summary": "FunPlus公布整月周年内容，开放Merlin、传奇地点、遗物、拼图与兑换码。", "impact": "产品仍在Google榜、iOS未同步入榜；周年内容存在不等于已确认增收，后续需观察活动期排名。", "source": "FunPlus官方", "url": "https://funplus.com/king-of-avalon-celebrates-10th-anniversary/"},
    {"category": "IP活动 / 长线运营", "date": "2026-09-12", "title": "Star Trek Fleet Command完成Star Trek Day五日活动", "summary": "Scopely官方公布最终日挑战、ST60代币与船员碎片，代币商店开放至9月14日。", "impact": "产品已在前一快照退出iOS榜；活动收尾仍是近期长线运营样本，但不能把离榜直接归因于活动结束。", "source": "Scopely官方", "url": "https://startrekfleetcommand.com/news/star-trek-day-day-5-to-boldly-go/"},
]


closing = [
    {"type": "判断", "title": "Google边界稳定、iOS换血明显且榜首易位", "detail": "Google只有Vikings回榜、Last Fortress掉榜的一进一出；iOS四进四出，Last War由#4升至#1。两个商店的波动层级不同，不能用iOS换血概括Android。"},
    {"type": "判断", "title": "跨端共同信号少于平台分化", "detail": "Sea War与Kingdom Guard两端共同走弱，Raid Rush两端共同上升；Top Heroes、Top War、Forge Master与Game of Thrones: Conquest则方向相反。今天多数变化仍是平台节奏差异。"},
    {"type": "判断", "title": "运营节点与名次没有单一对应关系", "detail": "Hearthstone在世界冠军乱斗结束日回榜，Last Shelter: War Z却在联盟赛事进行期退出iOS，MARVEL SNAP更新后两端仍小降；这些相邻关系只提供后续核验线索。"},
    {"type": "关注", "title": "9月17—18日：复核所有榜尾进出", "detail": "观察Google的Vikings能否脱离#60，以及iOS的Hearthstone、Rise of Castles、Lords Mobile能否留榜；若再度退出，统一归档为边界脉冲。"},
    {"type": "关注", "title": "9月17—21日：验证iOS榜首与两款塔防大涨", "detail": "Last War需连续保持iOS前三，Evo Defense与The Tower需至少再维持一个快照的前40，才升级为短期趋势。"},
    {"type": "关注", "title": "截至9月22日：跟踪版本与活动承接", "detail": "在Clash of Clans活动窗口内继续观察双端头部，同时核对MARVEL SNAP 57.x、Hearthstone活动结束后及Last Shelter联盟赛事的排名变化。"},
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Last War升至iOS榜首；iOS四进四出、两款塔防各升19位",
    "summary": "较9月15日有效快照，Google Play一进一出：Vikings回榜#60、Last Fortress掉榜；iOS四进四出，Hearthstone、Draft Showdown、Rise of Castles与Lords Mobile回榜，Wild Rift、两款Last Shelter及Last Day on Earth掉榜。Last War由#4升至iOS榜首；Evo Defense与The Tower各升19位。近90天新品Google 4款、iOS 2款；两端缺少6月18日精确基准，较老产品不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": f"data/games-{CURRENT}.json", "ios": f"data/ios-games-{CURRENT}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREVIOUS}.json", "ios": f"data/ios-games-{PREVIOUS}.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 The Grand Mafia · #60 Vikings: War of Clans PvP", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）", "anchors": "榜单锚点：#1 Last War:Survival · #25 Top Lords · #60 Lords Mobile x Transformers", "products": ios_products},
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-18"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-18"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-16.md", "json": "data/market-brief-20260916.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份有效快照为2026-09-15；升降为相邻工作日变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-06-18精确同口径TOP60基准，较老产品暂不判断飙升。", "",
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


save("data/market-brief-20260916.json", brief)
(ROOT / "reports/2026-09-16.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
