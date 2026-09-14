#!/usr/bin/env python3
"""Generate the Beijing 2026-09-14 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-14"
STAMP = "20260914"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


def product(game_name, product_id, store, tone, label, analysis):
    return {
        "gameName": game_name,
        "productId": product_id,
        "iconKey": f"{store}:{product_id}",
        "tone": tone,
        "changeLabel": label,
        "analysis": analysis,
    }


def asset_icons(manifest_path):
    result = {}
    for filename in load(manifest_path)["files"]:
        result.update(load(f"assets/{filename}"))
    return result


def build_market_icons(products):
    current = {
        "googlePlay": load("data/games-20260914.json"),
        "ios": load("data/ios-games-20260914.json"),
    }
    previous = {
        "googlePlay": load("data/games-20260911.json"),
        "ios": load("data/ios-games-20260911.json"),
    }
    id_fields = {"googlePlay": "packageName", "ios": "appId"}
    local_assets = {
        "googlePlay": asset_icons("assets/manifest.json"),
        "ios": asset_icons("assets/ios-manifest.json"),
    }
    bundle = {}
    for item in products:
        store = item["iconKey"].split(":", 1)[0]
        product_id = item["productId"]
        field = id_fields[store]
        games = current[store] + previous[store]
        game = next((row for row in games if str(row[field]) == str(product_id)), None)
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


google_history = load("data/history/google-play/2026-09-14.json")
ios_history = load("data/history/ios/2026-09-14.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


def card(store, prefix, tone, analysis, first=False):
    path = "data/games" if store == "googlePlay" else "data/ios-games"
    ident = "packageName" if store == "googlePlay" else "appId"
    now = load(f"{path}-20260914.json")
    prior = load(f"{path}-20260911.json")
    found = [row for row in now + prior if row["gameName"].startswith(prefix)]
    ids = {str(row[ident]) for row in found}
    if len(ids) != 1:
        raise RuntimeError(f"Ambiguous market card {store}:{prefix}: {ids}")
    product_id = ids.pop()
    a = next((row for row in now if str(row[ident]) == product_id), None)
    b = next((row for row in prior if str(row[ident]) == product_id), None)
    if tone == "entry" and a and not b:
        label = f"{'首次进入' if first else '回榜'} · #{a['rank']}"
    elif tone == "exit" and b and not a:
        label = f"掉榜 · 上期#{b['rank']}"
    elif tone in ("up", "down") and a and b:
        change = b["rank"] - a["rank"]
        if (change > 0) != (tone == "up"):
            raise RuntimeError(f"Incorrect direction {prefix}: {change}")
        label = f"{'+' if change > 0 else '−'}{abs(change)} · #{a['rank']}"
    else:
        raise RuntimeError(f"Incorrect membership for {store}:{prefix}:{tone}")
    return product((a or b)["gameName"], product_id, store, tone, label, analysis)


google_products = [
    card("googlePlay", "Pokémon Champions", "entry", "Google首次进入#58，但iOS从上期#33掉榜；美国Google商品页released为6月11日，早于90天窗口，不能误作近90天新品。9月8日竞技规则换季是已知节点，尚无证据证明其驱动今天的Android付费。观察能否脱离后十名。", first=True),
    card("googlePlay", "Vikings: War", "entry", "成熟4X战争游戏回到Google末位#60，同时iOS回榜#56，是双端榜尾共同出现；两个末段位置仍有立即掉榜风险，周末后的短时付费波动尚待确认。"),
    card("googlePlay", "Galaxy Defense", "exit", "上期Google #53、这次退出，iOS同样榜外；9月10日还曾出现在iOS末位，跨端末段反复进出不支持稳定增长判断。"),
    card("googlePlay", "Last Fortress: Underground", "exit", "上期Google压线#60后退出，iOS也从#51掉榜。两端同时离开TOP60是下一个快照需要验证的风险信号，不能凭两个快照推断长期衰退。"),
    card("googlePlay", "Top Heroes: Kingdom", "up", "从#47跃升至#25，iOS也升至#35，两端中段回升；周末跨度比常规单日长，尚无与这一跃升匹配的独立版本或投放证据，先看能否连续留在前40。"),
    card("googlePlay", "Call of Dragons", "up", "升8位至#50但仍在后十名；iOS今日不在同口径TOP60，因此暂只有Android末段上行信号，不能单凭这次跨周末回弹归因联盟活动。"),
    card("googlePlay", "Sea War: Uboat Raid", "up", "Google升8位至#51，iOS却跌16位至#58；同一产品跨端方向相反且双端均贴近榜尾，不应写为市场共同改善。"),
    card("googlePlay", "Doomsday:The Seven", "down", "Google下滑15位至#57，接近掉榜线；周末后的单次快照不足以确认用户或商业化转弱，未来两次更新若继续后十才提升风险等级。"),
    card("googlePlay", "Kingdom Guard", "down", "Google下降9位至#59，距离出榜仅一名；其塔防与联盟经营的长期循环不能由本次后段波动评价，先检查下一工作日是否回到#50以内。"),
    card("googlePlay", "MARVEL SNAP", "down", "Google下降7位至#56；官方9月10日调整Venus、Scorpion等卡牌，但现有证据只能说明平衡变更与榜位相邻，不能推断调整造成收入下滑。"),
]

ios_products = [
    card("ios", "Age of Empires Mobile", "entry", "由上期榜外回到iOS #28，Google仍在后段；iPhone回归中前段优于常见榜尾脉冲，周末跨度内具体驱动未核实，至少再看两个快照能否守住前40。"),
    card("ios", "Warline: Sniper Strike", "entry", "近90天上架的Warline回到iOS #49，Google仍在榜；双端继续有曝光但iPhone靠近后十，回榜能否留存需要观察到9月16日。"),
    card("ios", "Overgeared Hero", "entry", "iOS回榜#52，游戏以合成与角色成长经营为主、曾在项目榜尾进出；本次仍属高风险末段回补，暂没有已核验的版本因果。"),
    card("ios", "Idle Heroes", "entry", "2017年老产品重回iOS #54，属于成熟经营产品的榜尾回归，而非90天新品；未找到与今日排名直接对应的发行节点，先验证是否维持两天。"),
    card("ios", "Vikings: War", "entry", "回到iOS #56且Google同日回榜#60，双端在榜是共同现象、但都处末段；不能从两次入榜直接推出收入持续增长。"),
    card("ios", "Star Trek Fleet Command", "entry", "回到iOS末位#60。Scopely 9月12日Star Trek Day最后一日活动与9月14日代币商店截止已获官方确认；时间相邻但仍需下一工作日验证是否仅为活动尾声峰值。"),
    card("ios", "Pokémon Champions", "exit", "iOS上期#33后退出，Google却首次进入#58；官方9月8日启用Regulation Set M-C，跨端出现相反变化，未有证据认定规则调整解释了iOS退出。"),
    card("ios", "Game of Thrones: Conquest", "exit", "从上期#41离开iOS TOP60，Google仍在#44附近；双端排名分化但Android中段仍在榜，需等iOS连续离榜再判断风险。"),
    card("ios", "Last Fortress: Underground", "exit", "上期#51后掉榜，Google也由末位退出；成熟联盟SLG的双端同日离榜值得跟踪，但周末累计变动不能等同单日收入降幅。"),
    card("ios", "Draft Showdown", "exit", "上期#54后掉榜，Google仍在榜尾附近；轻量战术合成产品单端短暂上榜未获得持续位置，未来若Google同向退出需重新评估。"),
    card("ios", "Coop TD: Together", "exit", "上期iOS #55、这次离榜，9月10日Google商品页更新内容未在iOS形成可确认的持续TOP60承接；跨端不同步，不能据此否定版本长期表现。"),
    card("ios", "Last Shelter: Survival", "exit", "上期iOS #57后离榜，Google同名产品仍在榜中段；成熟SLG的iPhone端榜尾位置未延续，目前只记录设备侧分化。"),
    card("ios", "Warhammer 40,000: Tacticus", "up", "从上期#59回升23位至#36，摆脱立即掉榜区；没有与本轮幅度直接对应的官方活动证据，先看本周能否稳定在前40。"),
    card("ios", "Lands of Jail", "up", "iOS升16位至#44，Google仍在前段；Android与iPhone差距依然显著，iOS中后段的反弹需继续确认。"),
    card("ios", "War and Order", "up", "iOS上涨12位至#27，Google仍在中段；成熟4X跨端排名更接近，但单次工作日快照不构成经营拐点。"),
    card("ios", "League of Legends: Wild Rift", "down", "从#26下降27位至#53，Google却升6位到#34；Riot 9月9日7.2e是英雄与装备平衡更新，尚不能作为跨端相反榜位的确定原因。MOBA仅按Apple榜类目收录，不纳入核心4X收入子集。"),
    card("ios", "Fire Emblem Heroes", "down", "iOS下跌20位至#51，逼近后十名；任天堂战术RPG存量内容与角色活动不可凭本次排名推断强弱，后续观察是否继续滑落。"),
    card("ios", "Watcher of Realms", "down", "上期回榜#20后下跌17位至#37，iPhone端首个高位回归未完全维持；仍在榜中段，不能将周末后回落归因为活动结束。"),
]


news = [
    {"category": "IP活动 / 双端回榜", "date": "2026-09-12", "title": "Star Trek Fleet Command五日Star Trek Day迎来最终日", "summary": "Scopely官方公布To Boldly Go敌方单位挑战、ST60代币与船员碎片，代币商店和兑换码持续至9月14日。", "impact": "该作iOS今日回榜#60，Vikings同日双端回榜；活动与回榜时间相邻，仍需验证是否能在活动结束后留榜。", "source": "Scopely官方", "url": "https://startrekfleetcommand.com/news/star-trek-day-day-5-to-boldly-go/"},
    {"category": "IP联动 / 长线运营", "date": "2026-09-09", "title": "Clash of Clans推出Equipment Blast勋章活动", "summary": "Supercell公布9月9日至22日的WWE主题战斗活动，参与多人对战得Tag Tickets、Champ Medals并兑换装备、宝箱与临时兵种。", "impact": "CoC仍居双端头部；这是可验证的长线活动节点，但名次高位不能拆算该活动收入。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashofclans/blog/news/equipment-blast-medal-event/"},
    {"category": "竞技规则 / 跨端分化", "date": "2026-09-02（9月8日生效）", "title": "Pokémon Champions启用Regulation Set M-C", "summary": "宝可梦官方宣布9月8日至12月1日适用新规则，加入多种Mega Evolution与24只新可用宝可梦。", "impact": "今天Google首次入榜#58、iOS掉榜；规则更新与本轮跨端差异时间相近，但不足以确定其商业化因果。", "source": "Pokémon官方", "url": "https://www.pokemon.com/us/news/get-ready-for-regulation-set-m-c-in-pokemon-champions"},
    {"category": "卡牌平衡", "date": "2026-09-10", "title": "MARVEL SNAP调整Venus、Scorpion等卡牌", "summary": "官方OTA下调Venus和Scorpion Brand New Day的力量，并调整Blink、Vulture、The Collector等卡牌。", "impact": "Google下降至#56，iOS继续在榜；内容节点是真实的，但未提供足以解释日榜收入变化的材料。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/balance-update-september-10-2026/"},
    {"category": "版本 / 跨端", "date": "2026-09-09", "title": "Wild Rift 7.2e重排Vi与Swain等英雄强度", "summary": "Riot说明Vi、Swain削弱，Janna、Nautilus、Malphite获得增强，并对多件装备作平衡修订。", "impact": "iOS跌27位至#53、Google升6位到#34；不同平台方向相反，不能把版本更新视为确定驱动。", "source": "Riot Games官方", "url": "https://wildrift.leagueoflegends.com/en-us/news/game-updates/wild-rift-patch-notes-72e/"},
    {"category": "全球收入月榜", "date": "2026-09-04", "title": "Sensor Tower公布8月全球手游收入TOP10", "summary": "全球Apple App Store与Google Play手游消费者支出估算约65.7亿美元，Whiteout Survival全球总榜#3、Kingshot #7。", "impact": "两款核心策略产品较7月各升1位，但官方未公开单品收入同比，不能由名次换算收入百分比。", "source": "Sensor Tower官方", "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"},
    {"category": "赛季 / 平衡", "date": "2026-09-08", "title": "Clash Royale九月平衡调整覆盖Hero Balloon与Freeze", "summary": "Supercell公布Hero Balloon、Freeze等卡牌与法术平衡修改，配合9月赛季更新竞技环境。", "impact": "Clash Royale继续在Google与iOS头部；后续对局生态变化与畅销榜位置须分开验证。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/september-balance-changes-2026/"},
    {"category": "长线运营", "date": "2026-09-04", "title": "King of Avalon十周年活动持续至9月30日", "summary": "FunPlus宣布整月周年节点，开放Merlin与传奇地点、遗物、拼图及兑换码等内容。", "impact": "该作仍在Google榜，iOS未形成同步高位；应观察活动持续期内是否连续抬升，而非仅凭活动存在判断增收。", "source": "FunPlus官方", "url": "https://funplus.com/king-of-avalon-celebrates-10th-anniversary/"},
    {"category": "新赛季", "date": "2026-09-07", "title": "Clash Royale Minion Academy引入新卡和赛季玩法", "summary": "官方公布Minion Giant、Ice Wizard英雄、Album Event及2v2 League等9月内容。", "impact": "与上述平衡公告构成同一产品不同内容节点；双端前十仍需过赛季首周后观察，不可把榜位当单品营收。", "source": "Supercell官方", "url": "https://supercell.com/en/games/clashroyale/blog/release-notes/new-season-minion-academy/"},
    {"category": "合作塔防 / 离榜", "date": "2026-09-10", "title": "Coop TD商店更新加入Demon Legion与Deep Sea", "summary": "Google Play官方商品页9月10日更新，列出Clara Liberation、Deep Sea挑战与Demon Legion守墙等内容。", "impact": "该作由iOS上期#55离榜，版本时间相近但跨平台不一致，暂只列为运营观察、非收入原因。", "source": "Google Play官方商品页", "url": "https://play.google.com/store/apps/details?id=com.percent.aos.cooptd&hl=en_US&gl=US"},
]


closing = [
    {"type": "判断", "title": "周末后iOS换榜更密集，Google主要为榜尾换人", "detail": "较9月11日有效快照，Google两进两出且Pokémon Champions仅#58、Vikings #60；iOS六进六出，Age of Empires回到#28。Scopely 9月12日Star Trek Day末期与Star Trek iOS #60回榜时间相邻，但榜尾位置不足以确认持续反弹。"},
    {"type": "判断", "title": "同一产品跨端走出相反方向", "detail": "Pokémon Champions在Google首次入榜却从iOS退出，Wild Rift在Google升6位但iOS跌27位，Sea War Android升8位、iPhone跌16位；Pokémon规则更新、Wild Rift补丁提供背景而非确定榜位原因。"},
    {"type": "判断", "title": "长线4X仍守头部，局部名次不能替代全球收入", "detail": "Kingshot、Whiteout Survival继续处于双端前列；Sensor Tower的8月全球策略子集维持全球总榜#7与#3，且CoC的WWE活动正进行。Google与iOS日榜波动应与该全球月度口径分开。"},
    {"type": "关注", "title": "9月15—16日：验证榜尾双端回归是否留存", "detail": "Vikings需在Google与iOS同时维持TOP60，Star Trek需在9月14日代币商店关闭后仍留在iOS；若立即退出，按活动尾声/榜尾脉冲归档，不推断长期回升。"},
    {"type": "关注", "title": "9月16日前：核对Pokémon与Wild Rift的跨端落差", "detail": "Google版Pokémon若脱离后十、iOS重新进榜，才视为跨端承接改善；Wild Rift观察iOS能否由#53回到前40，并区分7.2e补丁与日榜变化。"},
    {"type": "关注", "title": "本周后半段：辨认长期运营和单点回弹", "detail": "结合CoC的Equipment Blast（至9月22日）与Clash Royale赛季，检查双端前列的延续性；Tacticus #36、Top Heroes Google #25若只保持一个快照，不升级为中期上升结论。"},
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Pokémon Champions跨端分化；Vikings与Star Trek榜尾回归",
    "summary": "较9月11日上一工作日快照，Google Play两进两出：Pokémon Champions首次进入#58、Vikings回榜#60，Galaxy Defense与Last Fortress掉榜；iOS六进六出，Age of Empires回榜#28、Star Trek末位#60。Top Heroes在Google升22位、Tacticus在iOS升23位；Wild Rift iOS跌27位而Google升6位。90天新品Google 5款、iOS 2款，缺少6月16日同口径基准，不判断较老产品的90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": "data/games-20260914.json", "ios": "data/ios-games-20260914.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260911.json", "ios": "data/ios-games-20260911.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Top Heroes: Kingdom Saga · #60 Vikings: War of Clans PvP", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）", "anchors": "榜单锚点：#1 Pokémon GO · #25 Top Lords · #60 Star Trek Fleet Command", "products": ios_products},
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": 5, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-16"},
        "ios": {"top60": 60, "newRelease90d": 2, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-16"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-14.md", "json": "data/market-brief-20260914.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份有效快照为2026-09-11；升降为相邻工作日（跨周末）变化，不等于24小时单日变化。",
        "- 近90天状态：Google新上榜5款、iOS新上榜2款；Google版Pokémon Champions上架于2026-06-11，早于90天窗口。两端均缺少2026-06-16精确同口径TOP60基准，较老产品暂不判断飙升。", "",
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


save("data/market-brief-20260914.json", brief)
(ROOT / "reports/2026-09-14.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
