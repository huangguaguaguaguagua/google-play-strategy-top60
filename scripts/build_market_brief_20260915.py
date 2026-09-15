#!/usr/bin/env python3
"""Generate the Beijing 2026-09-15 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-15"
STAMP = "20260915"
CURRENT = "20260915"
PREVIOUS = "20260914"


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
        icon = local_assets[store].get(f"{game['assetRank']}_icon")
        if not icon or not icon.startswith("data:image/"):
            raise RuntimeError(f"No local icon for market card: {item['iconKey']}")
        bundle[item["iconKey"]] = icon
    if len(bundle) != len(products):
        raise RuntimeError("Duplicate market-card product keys")
    save(f"assets/market-icons-{STAMP}.json", bundle, compact=True)
    return bundle


google_history = load("data/history/google-play/2026-09-15.json")
ios_history = load("data/history/ios/2026-09-15.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Ant Legion", "entry", "成熟蚂蚁题材4X回到Google #59，iOS当前不在同口径TOP60；仅凭末二位无法判断活动或买量驱动，未来两个工作日若未脱离后十名，仍按榜尾脉冲处理。"),
    card("googlePlay", "Last Fortress: Underground", "entry", "上一个有效快照未在Google榜、今天回到#60，iOS同名Underground版本仍在榜外；这是压线回榜，不能与今天首次进入iOS的《Last Shelter: War Z》混作同一产品。"),
    card("googlePlay", "Doomsday:The Seven", "exit", "上期位于#57，本次掉出Google TOP60；该IP联动版此前已靠近榜尾，当前只构成一次离榜信号，需等后续回榜情况判断承接。"),
    card("googlePlay", "Vikings: War", "exit", "上期Google #60、iOS #56的双端榜尾回归均未延续，今天两端同时退出；这支持将昨日现象降级为短时末段信号，但仍不能由两个快照推断长期收入下滑。"),
    card("googlePlay", "Infinity Kingdom", "up", "从#43升10位至#33，iOS也由#45升至#22，是今天方向最一致的双端改善；没有找到与幅度直接对应的官方版本或投放材料，先验证能否连续维持中前段。"),
    card("googlePlay", "Kingdom Guard", "up", "从#59升9位至#50，同时iOS回榜#47；两端都在后段但共同出现，塔防入口与联盟经营是否形成持续付费仍需至少两个后续快照确认。"),
    card("googlePlay", "Game of Thrones: Conquest", "down", "Google从#44跌13位至#57、iOS则回榜#42，跨端方向相反；没有证据把本轮差异归因于单一活动，Android已接近掉榜线。"),
    card("googlePlay", "League of Legends: Wild Rift", "down", "Google下降6位至#40，iOS也下降7位至#45；9月9日7.2e补丁是已知背景，但官方没有披露其与本轮畅销榜变化的因果。MOBA只按商店类目收录，不进入核心策略收入子集。"),
    card("googlePlay", "Pokémon Champions", "up", "从首次入榜#58升至#55，仍处Google后十名；iOS仍在榜外。Regulation Set M-C已生效，但目前只能确认Android末段承接延续一天。"),
    card("googlePlay", "Clash Royale", "down", "从#8降至#12，仍在Google头部，iOS继续前列；9月赛季与平衡调整正在运行，四位回落不足以构成长期转弱结论。"),
]


ios_products = [
    card("ios", "Game of Thrones: Conquest", "entry", "回到iOS #42，而Google同日跌至#57；单产品跨端走势分化，尚无证据确认iPhone端回榜由版本或活动直接推动。"),
    card("ios", "Kingdom Guard", "entry", "回到iOS #47，Google同步由#59升至#50；两端后段共同改善比单端回榜更值得跟踪，但位置仍接近掉榜区。"),
    card("ios", "The Tower - Idle", "entry", "成熟放置塔防回到iOS #49，Google同口径未入榜；没有与今天回榜直接对应的官方重大节点，先按中后段待验证信号记录。"),
    card("ios", "Last Shelter: Survival", "entry", "成熟4X产品回到iOS #59，Google版本仍在榜中段；iPhone仅压线出现，不能与新作《Last Shelter: War Z》的上架日、发行主体或生命周期混用。"),
    card("ios", "Last Shelter: War Z", "entry", "Apple Lookup确认6月14日上架，早于本期90天窗口三天，因此不标记近90天新品。9月10日版本加入四周制联盟决斗锦标赛、9月13日首轮匹配，今天首次进入#60；时间相邻但因果未证实。", first=True),
    card("ios", "Lords Mobile", "exit", "上期iOS #48后掉榜，Google仍在#25；变形金刚联动标题继续存在，但今天表现为明显Android优势，不能把单端退出写成产品整体转弱。"),
    card("ios", "Idle Heroes", "exit", "上期回榜#54后立即退出，符合成熟放置产品的榜尾短时波动；公开资料不足以确认一次性付费或活动原因。"),
    card("ios", "DC: Dark Legion", "exit", "上期#55后离开iOS TOP60，Google当前仍在榜；IP产品的单端榜尾退出需要与后续版本活动分开核对。"),
    card("ios", "Vikings: War", "exit", "上期#56后与Google端同步掉榜，双端回归只维持一个有效快照；暂归档为短时榜尾信号，而非长期付费趋势。"),
    card("ios", "Star Trek Fleet Command", "exit", "上期回到末位#60，今天退出；官方Star Trek Day五日活动及代币商店均在9月14日结束，时间关系支持继续核对活动尾声，但不能证明活动结束造成离榜。"),
    card("ios", "Infinity Kingdom", "up", "由#45跃升23位至#22，Google也升10位至#33，是今天最清晰的双端共同上行；缺少对应官方运营节点，仍按待验证信号而非经营拐点处理。"),
    card("ios", "Mob Control", "up", "从#32升7位至#25，回到iOS前半区；Google没有同步榜位，当前只反映iPhone端改善，尚不能推断跨端收入。"),
    card("ios", "X-Clash", "up", "从#22升7位至#15，继续强化iOS端中前段位置；Google未入同口径TOP60，产品仍呈单端高位特征。"),
    card("ios", "Forge Master", "up", "由#42升至#35，脱离榜尾风险区；Google却下降4位至#44，跨端方向并不一致，需避免把iOS回升扩展成双端结论。"),
    card("ios", "Last Day on Earth", "down", "从#46跌9位至#55，进入后十名；成熟生存经营产品仍在Google前列，当前是iPhone端风险信号而非双端同步回落。"),
    card("ios", "Warhammer 40,000: Tacticus", "down", "从#36跌8位至#44，Google反而升3位至#34；跨端再次分化，尚无可确认的活动原因。"),
    card("ios", "Mobile Legends", "down", "从#38跌7位至#45，Google仍在前段；MOBA仅因Apple策略类目进入本榜，不纳入Sensor Tower核心策略筛选。"),
    card("ios", "Overgeared Hero", "down", "从回榜#52降至#58，已贴近掉榜线；上线时间较短但Apple上架日早于90天窗口，页面按常规展示，未来一至两个快照决定是否再次退出。"),
]


news = [
    {"category": "新品 / 联盟赛事", "date": "2026-09-10（9月13日首轮匹配）", "title": "Last Shelter: War Z加入四周制联盟决斗锦标赛", "summary": "Apple官方版本说明显示26.0902.001新增Alliance Duel Tournament，联盟按相近实力匹配，首轮于9月13日开始。", "impact": "该作今天首次进入iOS #60；节点与入榜相邻但无收入或投放证据，未来两次快照用于验证是否只是赛事首轮脉冲。", "source": "Apple App Store官方商品页", "url": "https://apps.apple.com/us/app/last-shelter-war-z/id6760406772"},
    {"category": "IP活动 / 离榜", "date": "2026-09-12", "title": "Star Trek Fleet Command五日Star Trek Day完成最终日", "summary": "Scopely官方公布最终日敌方单位挑战、ST60代币与船员碎片，代币商店持续至9月14日。", "impact": "该作由上期iOS #60退出；活动窗口结束与离榜相邻，只能作为待验证背景，不能直接认定因果。", "source": "Scopely官方", "url": "https://startrekfleetcommand.com/news/star-trek-day-day-5-to-boldly-go/"},
    {"category": "IP联动 / 长线运营", "date": "2026-09-09", "title": "Clash of Clans推出Equipment Blast勋章活动", "summary": "Supercell公布9月9日至22日的WWE主题战斗活动，玩家可取得Tag Tickets、Champ Medals、装备和临时兵种。", "impact": "CoC仍居双端头部；这是可核验的运营窗口，但头部名次不能拆算该活动收入。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/news/equipment-blast-medal-event/"},
    {"category": "卡牌平衡", "date": "2026-09-10", "title": "MARVEL SNAP调整Venus、Scorpion等卡牌", "summary": "官方OTA下调Venus和Scorpion Brand New Day力量，并调整Blink、Vulture与The Collector等卡牌。", "impact": "Google回升3位至#53、iOS跌3位至#50，跨端方向相反；平衡节点不能作为榜位变化的确定原因。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/balance-update-september-10-2026/"},
    {"category": "版本 / 跨端", "date": "2026-09-09", "title": "Wild Rift 7.2e重排Vi与Swain等英雄强度", "summary": "Riot说明Vi、Swain削弱，Janna、Nautilus、Malphite获得增强，并调整多件装备。", "impact": "今天两端均回落但仍在中段；补丁是可核验背景，官方未披露其与畅销榜变化的关系。", "source": "Riot Games官方", "url": "https://wildrift.leagueoflegends.com/en-us/news/game-updates/wild-rift-patch-notes-72e/"},
    {"category": "竞技规则", "date": "2026-09-02（9月8日生效）", "title": "Pokémon Champions启用Regulation Set M-C", "summary": "宝可梦官方宣布9月8日至12月1日适用新规则，加入多种Mega Evolution与24只新可用宝可梦。", "impact": "Google由#58升至#55而iOS继续榜外；规则更新与Android留榜相邻，仍不足以认定商业化驱动。", "source": "Pokémon官方", "url": "https://www.pokemon.com/us/news/get-ready-for-regulation-set-m-c-in-pokemon-champions"},
    {"category": "全球收入月榜", "date": "2026-09-04", "title": "Sensor Tower公布8月全球手游收入TOP10", "summary": "全球App Store与Google Play手游消费者支出估算约65.7亿美元，Whiteout Survival全球总榜#3、Kingshot #7。", "impact": "两款核心策略产品较7月各升1位；官方未公开单品收入同比，不能由名次换算收入百分比。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"},
    {"category": "赛季 / 平衡", "date": "2026-09-08", "title": "Clash Royale九月平衡调整覆盖Hero Balloon与Freeze", "summary": "Supercell公布Hero Balloon、Freeze等卡牌与法术平衡修改，配合9月赛季更新竞技环境。", "impact": "Google降至#12但仍属头部，iOS继续前列；一次回落不能替代赛季周期验证。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/september-balance-changes-2026/"},
    {"category": "新赛季", "date": "2026-09-07", "title": "Clash Royale Minion Academy引入新卡与2v2 League", "summary": "官方公布Minion Giant、Ice Wizard英雄、Album Event及2v2 League等9月内容。", "impact": "与平衡公告构成同一产品的多个内容节点；需等赛季首周后判断头部位置是否延续。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/new-season-minion-academy/"},
    {"category": "长线运营", "date": "2026-09-04", "title": "King of Avalon十周年活动持续至9月30日", "summary": "FunPlus宣布整月周年内容，开放Merlin、传奇地点、遗物、拼图与兑换码。", "impact": "产品仍在Google榜、iOS未同步入榜；活动存在不等于已确认增收，后续看持续期内排名。", "source": "FunPlus官方", "url": "https://funplus.com/king-of-avalon-celebrates-10th-anniversary/"},
]


closing = [
    {"type": "判断", "title": "iOS榜尾换血高于Google，Last Shelter形成两代产品并列", "detail": "较9月14日有效快照，Google两进两出，iOS五进五出；Last Shelter: Survival #59与War Z #60同时进入iOS，但前者是成熟IM30产品、后者仅确认LAST ORIGIN直接发行，不能合并上架日或集团归属。"},
    {"type": "判断", "title": "Infinity Kingdom是今天最一致的双端上行", "detail": "Google升10位至#33、iOS升23位至#22，幅度和方向均一致；当前没有匹配的官方活动或版本证据，因此只记录为待验证共同改善，不命名为长期拐点。"},
    {"type": "判断", "title": "已知活动窗口对应的榜位结果并不一致", "detail": "Star Trek Day结束后该作从iOS末位退出，Last Shelter: War Z在联盟决斗首轮后首次压线入榜，Clash Royale则在赛季内容期仍有Google四位回落；这些相邻关系只能提供核验线索。"},
    {"type": "关注", "title": "9月16—17日：验证Last Shelter双产品和Google回榜产品", "detail": "观察iOS的Survival与War Z能否同时留榜、War Z能否脱离#60，并检查Google的Ant Legion与Last Fortress是否摆脱后十名；否则按榜尾脉冲归档。"},
    {"type": "关注", "title": "9月16—18日：确认Infinity Kingdom双端持续性", "detail": "至少连续两个快照维持Google前40与iOS前30，才把今天的共同上行升级为短期趋势；任一端快速回落则保持单次异动判断。"},
    {"type": "关注", "title": "本周内：区分活动收尾与平台差异", "detail": "核对Star Trek在9月14日商店结束后是否回榜、Pokémon能否由Google #55继续上移，以及Clash Royale在Equipment Blast与九月赛季期的双端头部稳定度。"},
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Infinity Kingdom双端上扬；Last Shelter两代产品压线进入iOS",
    "summary": "较9月14日有效快照，Google Play两进两出：Ant Legion回榜#59、Last Fortress回榜#60，Doomsday联动版与Vikings掉榜；iOS五进五出，Game of Thrones、Kingdom Guard、The Tower、Last Shelter: Survival回榜，Last Shelter: War Z首次进入#60。Infinity Kingdom在Google升10位、iOS升23位，是今日最一致的跨端改善；90天新品Google 4款、iOS 2款，两端缺少6月17日精确基准，较老产品不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": f"data/games-{CURRENT}.json", "ios": f"data/ios-games-{CURRENT}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREVIOUS}.json", "ios": f"data/ios-games-{PREVIOUS}.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Lords Mobile x Transformers · #60 Last Fortress: Underground", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）", "anchors": "榜单锚点：#1 Kingshot · #25 Mob Control · #60 Last Shelter: War Z", "products": ios_products},
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": 4, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-17"},
        "ios": {"top60": 60, "newRelease90d": 2, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-17"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-15.md", "json": "data/market-brief-20260915.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份有效快照为2026-09-14；升降为相邻工作日变化，不等于收入增减。",
        "- 近90天状态：Google新上榜4款、iOS新上榜2款。两端均缺少2026-06-17精确同口径TOP60基准，较老产品暂不判断飙升；Last Shelter: War Z的Apple上架日为6月14日，按规则不标记新品。", "",
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


save("data/market-brief-20260915.json", brief)
(ROOT / "reports/2026-09-15.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
