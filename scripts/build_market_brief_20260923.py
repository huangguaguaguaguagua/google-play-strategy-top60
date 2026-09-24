#!/usr/bin/env python3
"""Generate the Beijing 2026-09-23 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, CURRENT, PREVIOUS = "2026-09-23", "20260923", "20260923", "20260922"


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


def build_market_icons(products, write=True):
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
    if write:
        save(f"assets/market-icons-{STAMP}.json", bundle, compact=True)
    return bundle


google_history = load("data/history/google-play/2026-09-23.json")
ios_history = load("data/history/ios/2026-09-23.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Kingdom Guard", "entry", "回到Google #60，同时进入iOS #59；两端都紧贴掉榜线。官方Fruit Market活动在9月22—27日开放，但当前只确认活动窗口与双端回榜重合，尚不能证明持续承接。"),
    card("googlePlay", "Aliens vs Zombies", "exit", "昨日回到Google #60后今天即掉榜，iOS同口径未收录。连续两次都发生在边界位，说明当前留榜尚不稳定，未发现可确认的重大运营转折。"),
    card("googlePlay", "League of Legends: Wild Rift", "up", "Google升8位至#51，同时进入iOS #32。Patch 7.3在Apple侧于9月22日上线，但产品属于MOBA而非核心策略子集；本次更像两个商店Strategy分类边界的同步进入，不能外推为核心策略市场增长。"),
    card("googlePlay", "Last Fortress", "up", "Google升4位至#43，iOS维持#56。双端都在榜但仍处中后段，今天没有与涨幅直接对应的公开重大节点，先按Android单端改善信号处理。"),
    card("googlePlay", "Guns of Glory", "up", "Google升3位至#36，iOS却从上期#48掉榜。相邻快照呈现明确平台分化，不能把Android改善解释为双端共同回升。"),
    card("googlePlay", "Top Heroes", "down", "Google跌3位至#34，iOS从昨日大涨后回落10位至#47。Cloudsea Odyssey与Legendary Battlefield节点仍在，但今日双端同向回吐，昨日峰值的持续性需要重新验证。"),
    card("googlePlay", "Lords Mobile", "down", "Google跌3位至#35，iOS跌7位至#60。两端同步走弱且iPhone已到掉榜线，但单日名次仍不能等同于Transformers联动收入下降。"),
    card("googlePlay", "DC: Dark Legion", "down", "Google跌3位至#54，iOS则回榜#58。9月22日Apple版本加入Nemesis Takedown活动，但两端都在后十名，当前只确认分类榜边缘留存。"),
    card("googlePlay", "Last Shelter: Survival", "down", "Google跌3位至#58，处于掉榜高风险区；iOS对应商店条目Last Shelter: War Z从#60掉榜。两个商店标识严格分开记录，今天只确认各自榜尾承接转弱。"),
    card("googlePlay", "Ant Legion", "down", "Google跌3位至#59，iOS同口径未收录。成熟产品滑到倒数第二位，下一有效快照若继续下移将触发掉榜；当前没有证据把回落归因于具体活动。"),
    card("googlePlay", "Raid Rush", "down", "Google跌3位至#46，iOS也跌4位至#37。两端同向回落但仍都在TOP50内，暂按需要连续快照验证的共同减弱信号处理。"),
]


ios_products = [
    card("ios", "League of Legends: Wild Rift", "entry", "回到iOS #32，Google同步升8位至#51。Apple侧Patch 7.3于9月22日上线；不过产品属于MOBA，本次只说明Strategy分类边界中的双端可见度改善，不纳入核心策略收入子集。"),
    card("ios", "Coop TD: Together", "entry", "回到iOS #49，Google同口径未收录。9月22日版本加入中秋Yut-Nori、Clara解放与Deep Sea巨人入侵难度，节点与回榜重合，但仍需验证能否离开后段。"),
    card("ios", "DC: Dark Legion", "entry", "回到iOS #58，而Google跌3位至#54。9月22日Nemesis Takedown活动提供分阶段Boss与多队挑战，但两端都在后十名，暂不能视为稳定增长。"),
    card("ios", "Kingdom Guard", "entry", "回到iOS #59，同时进入Google #60。Fruit Market在9月22—27日开放，但两个名次均紧贴掉榜线，今天只记录为双端边界回归。"),
    card("ios", "Guns of Glory", "exit", "上期iOS #48后掉榜，Google却升3位至#36。两端方向相反，当前属于明确的平台分化而非产品整体同步走弱。"),
    card("ios", "Watcher of Realms", "exit", "昨日跌至iOS #54后今天掉榜。9月22日版本刚加入Fallen Covenant公会Boss、Grey Blades阵营与新公会战赛季，但尚未在相邻RSS快照中形成留榜承接。"),
    card("ios", "The Tower", "exit", "上期iOS #59后掉榜，Google同口径未收录。产品连续处于边界位，未发现可确认的当天重大运营转折，先按榜尾风险兑现记录。"),
    card("ios", "Last Shelter: War Z", "exit", "昨日回到iOS #60后今天即掉榜。9月17日竞技场与跨服对决版本未形成连续留榜，单次回归归档为短期边界波动。"),
    card("ios", "Age of Empires Mobile", "up", "iOS升24位至#34，为今日最大涨幅；Google仅升1位至#57。Apple最新公开版本仍是7月20日的装备与赛季功能更新，缺少与今天跳升直接对应的新节点，先按单端待验证信号处理。"),
    card("ios", "Star Wars", "up", "iOS升23位至#7并进入前十，Google策略榜未收录。9月15日版本只披露后台优化与性能改进，没有证据把大幅上涨归因于具体内容活动。"),
    card("ios", "Last Day on Earth", "up", "iOS升11位至#41，Google策略榜未收录。9月16日版本重做Crooked Creek Farm并加入复活与工厂清障调整，节点提供运营背景，但名次仍在中后段。"),
    card("ios", "Supremacy", "up", "iOS升4位至#42，Google当前未进TOP60。8月31日版本以平衡、无障碍与缺陷修复为主，暂无公开新节点可解释今天涨幅。"),
    card("ios", "Sea War", "up", "iOS升3位至#48，Google同口径未收录。9月22日版本只披露界面与缺陷修复，当前改善仍是单端后段信号。"),
    card("ios", "Overgeared Hero", "down", "iOS从昨日上涨后回落12位至#52，Google仍在#37附近。9月16日联动仍在，但相邻快照快速回吐，昨日峰值尚未形成连续承接。"),
    card("ios", "Top Heroes", "down", "iOS从昨日大涨后回落10位至#47，Google也跌3位至#34。Cloudsea Odyssey与Legendary Battlefield节点仍在，今天的双端回吐削弱了昨日峰值的延续性。"),
    card("ios", "Game of Thrones: Conquest", "down", "iOS跌8位至#50，Google当前为#45。9月21日版本加入Dragonseed装备、两名新英雄与龙具，但今天没有形成iPhone榜位承接。"),
    card("ios", "Hearthstone", "down", "iOS跌8位至#55，Google策略榜未收录。9月15日版本预热Reign of the Black Empire并调整标准与酒馆战棋，当前跌入后六名，仍需后续快照判断活动效果。"),
    card("ios", "The Battle Cats", "down", "iOS跌7位至#39，已从9月21日#22连续两次回吐。15.6.0内容峰值仍未完全消失，但短期动量明显减弱。"),
    card("ios", "Lords Mobile", "down", "iOS跌7位至#60，Google也跌3位至#35。两端同步回落且iPhone触及掉榜线；今天只能确认短期榜面减弱，不能换算为联动收入降幅。"),
]


news = [
    {
        "category": "MOBA / 版本更新",
        "date": "2026-09-22",
        "title": "Wild Rift上线Patch 7.3 Center Stage",
        "summary": "Apple官方版本说明列出Hwei、Sylas、Rek'Sai三名新英雄、3v3v3v3模式、SMASH社区内容以及音乐主题皮肤与ARAM强化。",
        "impact": "产品回到iOS #32并在Google升8位至#51；它是MOBA，本次只作为Strategy分类边界信号，不计入核心策略收入子集。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1480616990",
    },
    {
        "category": "IP策略RPG / 榜面异动",
        "date": "2026-09-15",
        "title": "Star Wars: Galaxy of Heroes升入iOS前十，官方版本仅披露性能优化",
        "summary": "0.40.6版本说明只写明后台优化与性能改进，没有披露角色、活动或赛季内容。",
        "impact": "产品今天升23位至iOS #7；缺少直接内容节点意味着这次跃升只能记为待验证信号，不能臆测具体原因。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id921022358",
    },
    {
        "category": "塔防4X / 限时活动",
        "date": "2026-09-21",
        "title": "Kingdom Guard预告9月22—27日Fruit Market",
        "summary": "1.0.592版本确认Fruit Market活动开放时间，并修复酒馆月度英雄与Goddess of Justice弹窗显示问题。",
        "impact": "产品同时回到Google #60与iOS #59；活动窗口与双端回榜重合，但两个名次都在掉榜线附近。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1570095804",
    },
    {
        "category": "IP策略 / Boss活动",
        "date": "2026-09-22",
        "title": "DC: Dark Legion上线Nemesis Takedown",
        "summary": "2.2.26版本加入分阶段Boss挑战、限定与加成英雄规则、多队部署和服务器伤害排名奖励。",
        "impact": "产品回到iOS #58、Google回落至#54；活动尚未推动两端离开后十名，需继续观察。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6479020757",
    },
    {
        "category": "合作塔防 / 节庆活动",
        "date": "2026-09-22",
        "title": "Coop TD: Together加入中秋活动与Deep Sea难度",
        "summary": "1.6.10版本加入中秋Yut-Nori、Clara解放与九尾狐皮肤、Deep Sea巨人入侵难度，并更新赛季通行证。",
        "impact": "产品回到iOS #49，Google同口径未收录；目前只是单端后段回归，尚未证明活动承接。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6503702666",
    },
    {
        "category": "塔防RPG / 新阵营",
        "date": "2026-09-22",
        "title": "Watcher of Realms加入新公会Boss与Grey Blades阵营",
        "summary": "1.6.38.829.1加入Fallen Covenant公会Boss、Grey Blades阵营、新公会战赛季与Doomripper单位，并调整多名英雄。",
        "impact": "产品在昨日跌至#54后今天掉出iOS TOP60；版本窗口尚未形成连续留榜，不能提前判定长期效果。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6741674823",
    },
    {
        "category": "IP SLG / 龙裔更新",
        "date": "2026-09-21",
        "title": "Game of Thrones: Conquest加入Dragonseed装备与新英雄",
        "summary": "26.9.830115版本加入Alys Rivers、Hugh Hammer、Dragonseed装备和Ever-Ready Warrior Saddle龙具。",
        "impact": "iOS今天跌8位至#50、Google位列#45；新内容与单日名次没有形成同步改善。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1035712810",
    },
    {
        "category": "SLG / 赛季更新",
        "date": "2026-09-21",
        "title": "Top Heroes升级Cloudsea Odyssey并开启Legendary Battlefield",
        "summary": "1.122.8取消World Boss体力消耗，为Ranch增加Legendary Puffel保底，并开启Legendary Battlefield与邮件收藏功能。",
        "impact": "产品今天iOS回落10位至#47、Google回落3位至#34；昨日峰值正在回吐，需用后续快照检验活动承接。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6450953550",
    },
    {
        "category": "联动 / 轻策略RPG",
        "date": "2026-09-16",
        "title": "Overgeared Hero推进Surviving the Game as a Barbarian联动",
        "summary": "1.39.1加入Bjorn、Missha等联动角色、皮肤、签到、任务与交换商店，并新增Companion Recruitment。",
        "impact": "iOS今天回落12位至#52，Google仍在#37；联动窗口存在，但昨日上涨未形成连续榜位承接。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6755585789",
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
        "title": "Google高度稳定，iOS继续由中后段轮换与头部跳升驱动",
        "detail": "Google一进一出，59款共同产品中48款变动不超过2位，中位绝对变动1位，前10全部保留；iOS四进四出，56款共同产品中39款变动不超过2位，中位绝对变动2位，前10更换1款。",
    },
    {
        "type": "判断",
        "title": "iOS上涨与昨日热点回吐同时发生，单日活动峰值特征仍强",
        "detail": "Age of Empires Mobile与Star Wars分别上涨24位和23位，但前者没有同期新版本、后者官方只披露性能优化；Top Heroes与Overgeared则回吐10位和12位。榜面与官方节点结合后，仍不足以把任一单日跳升写成长期增长。",
    },
    {
        "type": "判断",
        "title": "双端共同回榜集中在分类边界，核心策略与跨平台方向仍需分开",
        "detail": "Wild Rift进入iOS并在Google上涨，但它是MOBA；Kingdom Guard双端回榜却分别仅列#59与#60。Guns of Glory则Google上涨、iOS掉榜，DC反向回到iOS但在Google下滑。Sensor Tower核心策略子集仍维持8月真实统计期。",
    },
    {
        "type": "关注",
        "title": "下一有效快照：验证两款双端回榜产品能否脱离掉榜线",
        "detail": "Kingdom Guard需至少一端升至前55且另一端继续留榜；Wild Rift需守住iOS前40、Google前55。若任一端立即掉榜，本次只归档为分类边界短期回归。",
    },
    {
        "type": "关注",
        "title": "未来1—2个有效快照：检验iOS两次大幅跳升与昨日峰值",
        "detail": "Star Wars需保持前15、Age of Empires Mobile需保持前40；Top Heroes与Overgeared若继续跌出TOP60，则9月22日的上涨按一次性峰值归档。",
    },
    {
        "type": "关注",
        "title": "未来2个有效快照：跟踪新版本的真实榜位承接",
        "detail": "DC需在iOS离开后五名、Coop TD需守住前50；Watcher若在新Boss与阵营版本后仍未回榜，则只能记录为版本已上线而榜面未承接。Game of Thrones也需避免继续滑出iOS TOP60。",
    },
]


all_products = google_products + ios_products
icons = build_market_icons(all_products, write=__name__ == "__main__")
google_new = sum(g["comparison90d"]["status"] == "new" for g in datasets["googlePlay"]["now"])
ios_new = sum(g["comparison90d"]["status"] == "new" for g in datasets["ios"]["now"])

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Wild Rift与Kingdom Guard双端回榜，iOS两款跳升后昨日热点回吐",
    "summary": "较9月22日最终有效快照，Google Play一进一出：Kingdom Guard回榜#60、Aliens vs Zombies掉榜；Wild Rift +8至#51，Last Fortress +4，Top Heroes、Lords Mobile等多款各跌3位。iOS四进四出：Wild Rift、Coop TD、DC与Kingdom Guard进入/回榜，Guns of Glory、Watcher、The Tower与Last Shelter掉榜；Age of Empires Mobile +24、Star Wars +23、Last Day on Earth +11，Overgeared -12、Top Heroes -10。近90天新品Google 3款、iOS 2款；两端缺少6月25日精确基准，较老产品不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": f"data/games-{CURRENT}.json", "ios": f"data/ios-games-{CURRENT}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREVIOUS}.json", "ios": f"data/ios-games-{PREVIOUS}.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Age of Origins · #60 Kingdom Guard: Tower Defense",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 Infinity Kingdom · #60 Lords Mobile x Transformers",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-25"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-25"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-23.md", "json": "data/market-brief-20260923.json"},
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
        "- 对比基准：各自上一份最终有效快照为2026-09-22；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-06-25精确同口径TOP60基准，较老产品暂不判断飙升。",
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


def main():
    save("data/market-brief-20260923.json", brief)
    (ROOT / "reports/2026-09-23.md").write_text(build_markdown(brief), encoding="utf-8")
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


if __name__ == "__main__":
    main()
