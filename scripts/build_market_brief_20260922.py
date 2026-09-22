#!/usr/bin/env python3
"""Generate the Beijing 2026-09-22 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, CURRENT, PREVIOUS = "2026-09-22", "20260922", "20260922", "20260921"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {"ensure_ascii": False, "separators": (",", ":")} if compact else {"ensure_ascii": False, "indent": 2}
    target.write_text(json.dumps(value, **kwargs) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load(f"data/games-{CURRENT}.json"), "prior": load(f"data/games-{PREVIOUS}.json"), "id": "packageName"},
    "ios": {"now": load(f"data/ios-games-{CURRENT}.json"), "prior": load(f"data/ios-games-{PREVIOUS}.json"), "id": "appId"},
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
    data, ident = datasets[store], datasets[store]["id"]
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


google_history = load("data/history/google-play/2026-09-22.json")
ios_history = load("data/history/ios/2026-09-22.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "League of Legends: Wild Rift", "entry", "回到Google #59，iOS策略畅销榜未收录。它属于MOBA而非核心策略子集，本次更像Google Strategy分类边界的再次进入，不能外推为整体收入转强。"),
    card("googlePlay", "Aliens vs Zombies", "entry", "回到Google #60，紧贴掉榜线，iOS同口径未收录。该塔防产品前一有效快照刚掉榜，本次仅确认边界回归，未发现可确认的当天重大转折。"),
    card("googlePlay", "Kingdom Guard", "exit", "上期Google #58后掉榜，iOS策略榜未收录。成熟塔防与4X混合产品在榜尾失守，单次退出不足以判断长期衰退。"),
    card("googlePlay", "MARVEL SNAP", "exit", "上期Google #60后掉榜，但iOS仍在#49且只回落1位。当前是Android单端退出，不代表双端同步转弱。"),
    card("googlePlay", "Rise of Kingdoms", "up", "Google升6位至#14，iOS同步升14位至#16。官方周年庆版本提供跨王国偷瓜、联盟答题、护送与训练等活动，是今天最清晰的双端共同改善信号，但仍需下一快照确认持续性。"),
    card("googlePlay", "Lords Mobile", "up", "Google升5位至#32，iOS维持#53。Transformers联动仍是运营背景，但改善集中在Android端，跨端差距扩大到21位。"),
    card("googlePlay", "Titan Rush", "up", "Google升5位至#52，iOS策略榜未收录。产品从榜尾向上移动但仍在后十名，暂无公开节点可以确认涨幅原因。"),
    card("googlePlay", "The Grand Mafia", "down", "Google跌4位至#25，iOS当前未进榜。仍留在前25，今天只能记录为Android单端回调，未发现可确认的重大转折。"),
    card("googlePlay", "Warline", "down", "Google跌4位至#35，iOS却升6位至#41。Eye of the Storm八服战版本背景相同，但两端方向相反，暂不能认定版本带来统一增长。"),
    card("googlePlay", "War and Order", "down", "Google跌4位至#38，iOS持平#36。两端名次接近但仅Android回落，当前更像平台日度节奏差异。"),
]


ios_products = [
    card("ios", "Last Fortress", "entry", "回到iOS #56，Google维持#47。双端同时在榜但都处中后段，没有与本次回榜直接对应的公开重大版本节点，先按榜尾回归信号处理。"),
    card("ios", "Last Shelter: War Z", "entry", "回到iOS #60，Google位列#42。9月17日版本加入普通竞技场、巅峰竞技场与跨服对决，但iPhone仍在掉榜线，版本承接尚未稳定。"),
    card("ios", "Fire Emblem Heroes", "exit", "上期iOS #51后掉榜，Google策略榜未收录。9月8日《Fortune's Weave》预热未形成连续留榜，不能据此判断产品整体收入变化。"),
    card("ios", "DC: Dark Legion", "exit", "上期iOS回榜#55后即掉榜，Google仍在#51。9月18日Batcave弹珠活动暂未形成iPhone连续承接，双端同步进入信号已经转为Android单端留榜。"),
    card("ios", "Top Heroes", "up", "iOS升22位至#37，为今日最大涨幅；Google也小升至#31。9月21日Cloudsea Odyssey升级、Legendary Battlefield与Ranch保底节点时间贴近，但单日幅度仍按待验证信号记录。"),
    card("ios", "Overgeared Hero", "up", "iOS升14位至#40，Google也升2位至#37。9月16日《Surviving the Game as a Barbarian》联动加入角色、皮肤、任务和交换商店，双端同向但尚未进入头部。"),
    card("ios", "Rise of Kingdoms", "up", "iOS升14位至#16，Google同步升6位至#14。周年庆活动同时覆盖收集、跨王国交互、联盟答题和护送，是今天双端改善最完整的官方运营背景。"),
    card("ios", "Foundation", "up", "iOS升8位至#25，Google也升1位至#27。S2 The Usurper、Shared Moonlight与Combat Lab仍在部分服务器测试，双端中段改善需观察测试范围扩大后的延续。"),
    card("ios", "Guns of Glory", "up", "iOS升8位至#48，Google小升至#39。两端同向但iPhone仍在后13名，当前更适合作为回榜后的承接改善信号。"),
    card("ios", "Evo Defense", "up", "iOS升7位至#43，Google策略榜未收录。9月17日Everbloom限时活动与Style Switch上线，名次离开榜尾但仍是单端信号。"),
    card("ios", "Warline", "up", "iOS升6位至#41，Google反向跌4位至#35。Apple本店7月22日上架，继续按近90天新品计算；八服战版本尚未形成一致的跨端方向。"),
    card("ios", "X-Clash", "up", "iOS升6位至#15，Google策略榜未收录。产品回到前15，但当前商品页只披露性能优化，缺少可确认的内容节点解释涨幅。"),
    card("ios", "Tiles Survive", "up", "iOS升5位至#23，Google也升3位至#21。宠物系统、收藏套装与月卡治疗权益更新后，两端同步向上，是次于RoK的共同改善信号。"),
    card("ios", "Watcher of Realms", "down", "iOS跌17位至#54，为今日最大跌幅。9月22日同日版本刚加入Fallen Covenant公会Boss、Grey Blades阵营与新公会战赛季，当前榜位可能尚未覆盖完整活动窗口。"),
    card("ios", "Summoners War", "down", "iOS跌13位至#55，Google策略榜未收录。9月11日版本以攻城战策略信息与符文、神器体验优化为主，没有证据把今天回落归因于具体活动。"),
    card("ios", "The Battle Cats", "down", "iOS从昨日#22回落10位至#32，但仍比9月18日的#57高25位。15.6.0版本峰值正在回吐，尚不能判定已回到常态区间。"),
    card("ios", "Star Wars", "down", "iOS跌7位至#30，Google策略榜未收录。近期版本主要披露后台与性能优化，缺少可核验的内容节点解释当天回调。"),
    card("ios", "Dragon Traveler", "down", "iOS跌7位至#45，Google策略榜未收录。仍处中后段且没有公开重大节点，先记录为单端回落。"),
    card("ios", "Sea War", "down", "iOS跌6位至#51，Google策略榜未收录。跌入后十名后掉榜风险增加，但一次快照不足以确认长期承接转弱。"),
]


news = [
    {
        "category": "4X / 周年庆",
        "date": "2026-09-02",
        "title": "Rise of Kingdoms周年庆加入跨王国互动与联盟活动",
        "summary": "官方1.1.11.28版本列出Art Carnival、Melon Market跨王国偷取、Alliance Quiz、Arms Training、护送与多项庆典玩法。",
        "impact": "产品今天Google +6至#14、iOS +14至#16，是双端最一致的改善信号；仍需下一快照排除活动峰值。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/rise-of-kingdoms/id1354260888",
    },
    {
        "category": "SLG / 赛季更新",
        "date": "2026-09-21",
        "title": "Top Heroes升级Cloudsea Odyssey并开启Legendary Battlefield",
        "summary": "1.122.8取消World Boss体力消耗，为Ranch增加Legendary Puffel保底，并开启Legendary Battlefield与邮件收藏功能。",
        "impact": "iOS +22至#37、Google小升至#31；节点与异动同日，但不能由单日名次断言长期增长。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/top-heroes-kingdom-saga/id6450953550",
    },
    {
        "category": "塔防RPG / 新阵营",
        "date": "2026-09-22",
        "title": "Watcher of Realms加入新公会Boss与Grey Blades阵营",
        "summary": "1.6.38.829.1加入Fallen Covenant公会Boss、Grey Blades阵营、新公会战赛季与Doomripper单位，并调整多名英雄。",
        "impact": "iOS当前反而跌17位至#54；版本与RSS窗口几乎同时更新，需要后续快照观察而不能立即判定效果。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/watcher-of-realms-us/id6741674823",
    },
    {
        "category": "联动 / 轻策略RPG",
        "date": "2026-09-16",
        "title": "Overgeared Hero开启Surviving the Game as a Barbarian联动",
        "summary": "1.39.1加入Bjorn、Missha等联动角色、皮肤、签到、任务与交换商店，并新增Companion Recruitment。",
        "impact": "iOS +14至#40、Google升至#37；双端同向改善与联动时间相邻，但尚未进入前30。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/overgeared-hero-merge-rpg/id6755585789",
    },
    {
        "category": "末日SLG / 跨服竞技",
        "date": "2026-09-17",
        "title": "Last Shelter: War Z加入普通与巅峰竞技场",
        "summary": "26.0903.001加入本服竞技、跨服Peak Arena、联盟决斗联赛频道，并优化世界Boss与PVE表现。",
        "impact": "产品回到iOS #60，Google为#42；版本提供了明确背景，但iPhone仍处掉榜线。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/last-shelter-war-z/id6760406772",
    },
    {
        "category": "太空SLG / 赛季测试",
        "date": "2026-09-16",
        "title": "Foundation测试S2 The Usurper与Combat Lab",
        "summary": "1.1.153在部分服务器测试S2、新地面战斗活动与Ruins Raiders跨服功能，并预告Shared Moonlight特别行动。",
        "impact": "iOS +8至#25、Google升至#27；双端同步改善，但测试范围有限，需继续验证。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/foundation-galactic-frontier/id6737595599",
    },
    {
        "category": "城建生存 / 宠物系统",
        "date": "2026-09-17",
        "title": "Tiles Survive推出宠物系统与收藏套装",
        "summary": "2.6.100加入宠物蛋、孵化养成、队伍支援、收藏套装加成与月卡治疗权益升级。",
        "impact": "产品iOS +5至#23、Google +3至#21，形成温和双端改善；仍不能拆分各系统的单独收入贡献。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/tiles-survive/id6738109752",
    },
    {
        "category": "新品 / 八服战",
        "date": "2026-09-16",
        "title": "Warline推进Eye of the Storm八服战",
        "summary": "1.3.01加入Pulse Resist、Stormbreaker争夺、Signature Armaments、Insignia奖励与Conquest Trucks。",
        "impact": "iOS +6至#41、Google -4至#35；同一版本背景下两端方向相反，仍处新品验证期。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/warline-sniper-strike/id6742809194",
    },
    {
        "category": "塔防 / 限时活动",
        "date": "2026-09-17",
        "title": "Evo Defense上线Everbloom与Style Switch",
        "summary": "1.2.18开启Everbloom限时活动，并允许玩家在King与Queen外观之间切换。",
        "impact": "iOS +7至#43，Google策略榜未收录；目前只能确认单端中后段改善。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/evo-defense/id6755173751",
    },
    {
        "category": "全球收入月榜",
        "date": "2026-09-04",
        "title": "Sensor Tower最新官方月榜仍为2026年8月",
        "summary": "全球App Store与Google Play消费者支出估算约65.7亿美元；Whiteout Survival全球总榜#3、Kingshot #7，均较7月升1位。",
        "impact": "两款命中核心策略口径；官方未披露单品同比，不能由榜位变化换算收入增幅。",
        "source": "Sensor Tower官方",
        "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026",
    },
]


closing = [
    {
        "type": "判断",
        "title": "Google榜面重新趋稳，iOS仍保持高轮换",
        "detail": "Google两进两出，58款共同产品中48款变动不超过2位，中位绝对变动1位；iOS同样两进两出，但只有28款变动不超过2位，中位绝对变动3位。两端前10均更换1款，中后段波动差异更明显。",
    },
    {
        "type": "判断",
        "title": "RoK形成最明确的双端共同改善，iOS热点集中在版本与联动窗口",
        "detail": "Rise of Kingdoms升至Google #14、iOS #16；Top Heroes与Overgeared分别在iOS上涨22位和14位，Google也小幅上升。三款都有可核验运营节点，但单日异动仍只视为待验证信号。",
    },
    {
        "type": "判断",
        "title": "榜尾轮换继续呈现平台分化",
        "detail": "DC从iOS掉榜但守住Google #51；Last Fortress和Last Shelter进入iOS，同时已在Google #47与#42。MARVEL SNAP则只从Google退出、iOS仍为#49。近90天新品仍为Google 4款、iOS 2款。",
    },
    {
        "type": "关注",
        "title": "下一工作日：验证RoK与两款iOS跃升产品",
        "detail": "Rise of Kingdoms需双端继续保持前20；Top Heroes需守住iOS前45；Overgeared需守住iOS前45且Google不跌出前45。满足条件后才把今天的版本窗口视为连续承接。",
    },
    {
        "type": "关注",
        "title": "未来1—2个有效快照：观察Watcher与Battle Cats回摆",
        "detail": "Watcher需在新Boss/阵营版本后脱离iOS后十名；Battle Cats需稳定在前40。若继续下滑，则9月21日的上涨只归档为短期版本峰值。",
    },
    {
        "type": "关注",
        "title": "下一工作日：复核五款榜尾产品",
        "detail": "关注iOS #60 Last Shelter、#56 Last Fortress，以及Google #60 Aliens、#59 Wild Rift、#51 DC。任一产品连续留榜并离开后五名，才视为承接改善。",
    },
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(g["comparison90d"]["status"] == "new" for g in datasets["googlePlay"]["now"])
ios_new = sum(g["comparison90d"]["status"] == "new" for g in datasets["ios"]["now"])

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "RoK双端上扬，Top Heroes与Overgeared拉动iOS；榜尾继续轮换",
    "summary": "较9月21日最终有效快照，Google Play两进两出：Wild Rift和Aliens vs Zombies回榜，Kingdom Guard与MARVEL SNAP掉榜；最大上涨为Rise of Kingdoms +6至#14，The Grand Mafia、Warline和War and Order各跌4位。iOS两进两出：Last Fortress与Last Shelter回榜，Fire Emblem Heroes和DC: Dark Legion掉榜；Top Heroes +22、Overgeared与Rise of Kingdoms各+14，Watcher -17、Summoners War -13。近90天新品Google 4款、iOS 2款；两端缺少6月24日精确基准，较老产品不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": f"data/games-{CURRENT}.json", "ios": f"data/ios-games-{CURRENT}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREVIOUS}.json", "ios": f"data/ios-games-{PREVIOUS}.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 The Grand Mafia · #60 Aliens vs Zombies: Invasion",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Foundation: Galactic Frontier · #60 Last Shelter: War Z",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-24"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-24"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-22.md", "json": "data/market-brief-20260922.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报",
        "",
        f"**{value['title']}**",
        "",
        value["summary"],
        "",
        "## 数据源与口径",
        "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-09-21；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-06-24精确同口径TOP60基准，较老产品暂不判断飙升。",
        "",
        "## 1. 双榜当日异动产品",
        "",
    ]
    for store in ("googlePlay", "ios"):
        section = value["rankingDynamics"][store]
        lines += [f"### {section['label']}", "", f"{section['sourceTime']}。", ""]
        for item in section["products"]:
            lines += [f"#### {item['gameName']}｜{item['changeLabel']}", "", item["analysis"], ""]
    lines += ["## 2. 策略手游市场热点", "", value["newsMethod"], ""]
    for index, item in enumerate(value["marketNews"], 1):
        lines += [
            f"### {index}. [{item['title']}]({item['url']})",
            "",
            f"- 类别：{item['category']}｜发布日期：{item['date']}｜来源：{item['source']}",
            f"- 事实摘要：{item['summary']}",
            f"- 市场含义：{item['impact']}",
            "",
        ]
    lines += ["## 3. 综合判断与后续关注", ""]
    for item in value["closing"]:
        lines += [f"### {item['type']}｜{item['title']}", "", item["detail"], ""]
    revenue = value["globalStrategyRevenue"]
    lines += [
        "## 4. Sensor Tower 全球收入榜中的策略产品",
        "",
        f"- 数据期：{revenue['periodLabel']}｜官方页面：{revenue['publicationLabel']}｜估算截至：{revenue['estimateAsOf']}",
        f"- 口径：{revenue['scope']['region']}｜{revenue['scope']['stores']}｜{revenue['scope']['exclusions']}",
        f"- 策略筛选：官方全球收入TOP10中命中{revenue['scope']['strategyMatches']}款核心策略产品；这不是完整策略品类TOP10",
        f"- 市场总览：全球手游消费者支出约${revenue['marketSummary']['globalConsumerSpendingUsd'] / 1_000_000_000:g}B，环比{revenue['marketSummary']['monthOverMonthPercent']:g}%，全市场同比约{revenue['marketSummary']['yearOverYearPercentApprox']:g}%",
        f"- 原始来源：[{revenue['source']}]({revenue['sourceUrl']})",
        "",
        "| 全球总榜 | 游戏 | 发行商 | 策略类型 | 较上月榜位 | 单品收入同比 |",
        "|---:|---|---|---|---|---|",
    ]
    for item in revenue["rankings"]:
        lines.append(f"| {item['rank']} | {item['gameName']} | {item['publisher']} | {item['strategyGenre']} | {item['movementLabel']} | {item['yoyRevenueLabel']} |")
    lines += ["", "### 策略产品与同比口径", ""] + [f"- {item}" for item in revenue["officialHighlights"]]
    lines += [
        "",
        revenue["methodologyNote"],
        "",
        "## 下载与来源",
        "",
        f"- JSON：`{value['downloads']['json']}`",
        f"- Sensor Tower上月对照：{revenue['previousPeriodSourceUrl']}",
        f"- Sensor Tower同比对照：{revenue['yearOverYearSourceUrl']}",
        "- Google Play直连源：https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US",
        "- Apple官方RSS：https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json",
        "",
    ]
    return "\n".join(lines)


save("data/market-brief-20260922.json", brief)
(ROOT / "reports/2026-09-22.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {
    "date": DATE,
    "title": brief["title"],
    "summary": brief["summary"],
    "markdown": brief["downloads"]["markdown"],
    "json": brief["downloads"]["json"],
}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(all_products)} product cards, {len(icons)} local icons and {len(news)} news items")
