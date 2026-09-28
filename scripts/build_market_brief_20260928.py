#!/usr/bin/env python3
"""Generate the Beijing 2026-09-28 market brief, local icons and archive entry."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, CURRENT, PREVIOUS = "2026-09-28", "20260928", "20260928", "20260925"


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


google_history = load("data/history/google-play/2026-09-28.json")
ios_history = load("data/history/ios/2026-09-28.json")
global_strategy_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


google_products = [
    card("googlePlay", "Kiss of War", "entry", "回到Google #49，iOS也回榜#36，是今天少数双端共同改善的产品；现有官方版本只列常规修复，没有足够证据把回榜归因于单一内容节点。"),
    card("googlePlay", "Kingdom Rush 6", "entry", "Google美国区released为9月16日，本次首次进入#57并归类为近90天新品；iOS首个完整快照曾到#26、今天回落至#46，首发承接出现平台与时间差异。", first=True),
    card("googlePlay", "Warpath", "entry", "回到Google #59，但iOS从上期#56掉榜。14.4长线版本仍是可核验背景，今天的相反方向只构成平台分化信号。"),
    card("googlePlay", "Game of Thrones: Conquest", "exit", "从Google上期#56掉榜，iOS也从#39掉榜。Dragonseed版本没有在周末后的相邻有效快照中维持TOP60，但不能据此推断整体收入趋势。"),
    card("googlePlay", "DC: Dark Legion", "exit", "从Google上期#59掉榜，iOS此前已退出。两端先后跌出TOP60，确认榜尾风险兑现；未发现可确认的当天运营节点。"),
    card("googlePlay", "Age of Spirits", "exit", "从Google上期#60掉榜。产品9月16日上架、仍属近90天新品，但两次可见记录都在榜尾，首发留榜尚不稳定。"),
    card("googlePlay", "Sea War", "up", "Google升17位至#38，iOS也升11位至#23，是今天最强的双端同向改善；没有找到同日官方重大节点，先按待验证信号记录。"),
    card("googlePlay", "GIRLS' FRONTLINE 2", "down", "Google跌18位至#52，为本端最大回落；iOS策略榜未收录。没有对应的官方当日节点，不能把单日跌幅解释为长期转弱。"),
    card("googlePlay", "Last Fortress", "down", "Google跌15位至#56，重新进入榜尾风险区；iOS本期未进入TOP60。成熟生存SLG的周末后回吐需要下一有效快照确认。"),
    card("googlePlay", "Infinity Kingdom", "down", "Google跌11位至#31，iOS也跌13位至#45，是今天较清晰的双端共同走弱信号；暂未发现可确认的同步活动结束节点。"),
    card("googlePlay", "Top Heroes", "down", "Google跌11位至#48，iOS继续缺席。两端可见度同步偏弱，但单个周末跨度仍不足以判断长线趋势。"),
    card("googlePlay", "Call of Dragons", "up", "Google升6位至#37，iOS却从上期#53掉榜；同一产品跨端方向相反，不能用Android改善代表整体回升。"),
]


ios_products = [
    card("ios", "Watcher of Realms", "entry", "回到iOS #35。9月22日版本加入Fallen Covenant公会Boss、Grey Blades阵营与新公会战赛季；节点与回榜相邻，但没有收入证据证明因果。"),
    card("ios", "Kiss of War", "entry", "回到iOS #36，Google也回榜#49。现有版本说明只有界面与缺陷修复，双端回归仍按待验证信号处理。"),
    card("ios", "Star Trek Fleet Command", "entry", "回到iOS #50。9月25日M95.1加入Ops 61+的Haven基地、U.S.S. Kelcie May与领地更新，为本次回榜提供可核验内容背景。"),
    card("ios", "Lords Mobile", "entry", "回到iOS #53；Google当前#35。Transformers联动第二阶段仍是官方可核验背景，但回榜位于后十名，未脱离榜尾风险。"),
    card("ios", "Boom Beach", "entry", "回到iOS #58。9月更新加入Blitz活动与新排行榜；今天只能确认版本窗口与榜尾回归同时存在。"),
    card("ios", "Guns of Glory", "entry", "回到iOS #57，Google升4位至#28。9月23日版本只披露界面与体验优化，不能据此断言回榜原因。"),
    card("ios", "Sea of Conquest", "entry", "首次进入本项目iOS TOP60，位列#60；9月24日版本提醒联动临近结束。Apple本店上架日为2024年1月3日，因此不是近90天新品。", first=True),
    card("ios", "Cell Survivor", "entry", "回到iOS #59。9月21日3.9版本只说明新增主题场景，当前仍在掉榜线附近，属于短期回榜信号。"),
    card("ios", "Game of Thrones: Conquest", "exit", "从iOS上期#39掉榜，Google也从#56掉榜。双端同日退出比单店信号更明确，但仍不能由榜位直接推算收入降幅。"),
    card("ios", "Honor of Kings", "exit", "从iOS上期#43掉榜，Google策略榜未收录；作为MOBA分类边界产品，不把本次退出解释为核心策略品类变化。"),
    card("ios", "Limbus Company", "exit", "从iOS上期#44掉榜，Google同时跌6位至#60。1.115.0内容窗口没有形成持续双端承接，下一次Google快照存在掉榜风险。"),
    card("ios", "Call of Dragons", "exit", "从iOS上期#53掉榜，但Google升6位至#37。跨端相反方向显示当前变化更像平台分化，而非统一趋势。"),
    card("ios", "Rise of Castles", "exit", "从iOS上期#55掉榜；Google本期升1位至#17。成熟4X产品在两店方向相反，暂不外推活动效果。"),
    card("ios", "Warpath", "exit", "从iOS上期#56掉榜，Google却回榜#59。两端都靠近榜尾，14.4内容承接仍需更多快照验证。"),
    card("ios", "Lucky Defense", "exit", "从iOS上期#57掉榜。2.0.13活动窗口没有形成连续留榜，且Google同口径未收录。"),
    card("ios", "League of Legends: Wild Rift", "exit", "从iOS上期#59掉榜，Google本期#47。该产品属于MOBA分类边界，今天只记录iPhone端退出。"),
    card("ios", "The Battle Cats", "up", "iOS升21位至#39，为本端最大上涨；15.6.0已加入新形态、地图与震动功能，但版本早于今天两周，不能直接归因。"),
    card("ios", "Kingdom Rush 6", "down", "iOS从首个完整快照#26跌20位至#46，Google则首次进入#57。两端仍在首发验证区间，需区分IP首发峰值与持续承接。"),
    card("ios", "Dragon Traveler", "down", "iOS跌21位至#56，重新进入榜尾风险区；Golden Night Reverie仍是现有活动背景，但没有证据说明本次回落原因。"),
    card("ios", "Star Wars", "down", "iOS跌13位至#22。9月15日版本仅列后端与性能优化，没有可确认的内容节点对应今天回落。"),
    card("ios", "Mobile Legends", "up", "iOS升14位至#24；10周年英雄重做与S42赛季仍在运营窗口，但该作属于MOBA分类边界，不纳入核心策略收入子集。"),
    card("ios", "Infinity Kingdom", "down", "iOS跌13位至#45，Google也跌11位至#31。双端共同回落值得继续观察，但不把名次变化换算为收入变化。"),
    card("ios", "Sea War", "up", "iOS升11位至#23、Google升17位至#38，是今天最清晰的双端改善；没有同日官方节点，暂不升级为持续趋势。"),
    card("ios", "MARVEL SNAP", "down", "iOS跌8位至#54，Vampires vs Zombies赛季仍在进行；该作属于卡牌分类边界，当前已接近榜尾风险区。"),
]


news = [
    {
        "category": "新品 / 经典塔防",
        "date": "2026-09-24",
        "title": "Kingdom Rush 6首发后出现双端不同节奏",
        "summary": "Apple与Google官方商品页确认产品以Linirea前传、15座塔、双英雄、9种法术及18个战役关卡回归；两店分别保存各自上架日期。",
        "impact": "本期Google首次进入#57，iOS则从#26回落至#46；新品已实现双端可见，但首发承接尚未稳定。",
        "source": "Google Play官方商品页",
        "url": "https://play.google.com/store/apps/details?id=com.ironhidegames.android.kingdomrush6.genesis&hl=en_US&gl=US",
    },
    {
        "category": "太空4X / 高等级基地",
        "date": "2026-09-25",
        "title": "Star Trek Fleet Command M95.1加入Haven基地",
        "summary": "Apple官方版本说明显示，Ops 61+玩家可建设Haven行星基地，解锁全账号增益、Frontier Prestige、U.S.S. Kelcie May及领地更新。",
        "impact": "产品回到iOS #50；版本节点新鲜且与回榜相邻，但仍需后续快照确认是否能脱离后十名。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1427744264",
    },
    {
        "category": "现代战争 / 平衡更新",
        "date": "2026-09-25",
        "title": "Supremacy更新兵种学说、动员与无障碍选项",
        "summary": "0.242版本调整Tank Destroyer学说与动员平衡，并修复飞机、导弹、情报人员及界面问题。",
        "impact": "产品iOS升12位至#37；更新与上涨相邻，但当前仍只记录为待验证信号。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id1510997559",
    },
    {
        "category": "海战SLG / 联动末期",
        "date": "2026-09-24",
        "title": "Sea of Conquest提醒联动英雄与奖励即将结束",
        "summary": "Apple 1.1.800版本说明明确提示跨界联动临近结束，尚未取得英雄或奖励的玩家需在结束前参与。",
        "impact": "产品首次进入项目iOS榜#60；活动末期与入榜相邻，但不能由此断言回榜原因或收入变化。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6463715971",
    },
    {
        "category": "塔防 / 公会赛季",
        "date": "2026-09-22",
        "title": "Galaxy Defense开启Season: Expedition与Kronos Exploration",
        "summary": "1.0.1加入60级公会参与的Season: Expedition测试期，并于9月24日开启Kronos Exploration活动。",
        "impact": "产品iOS跌8位至#55；内容更新没有在周末后形成榜位抬升，需继续观察赛季中段承接。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6740189002",
    },
    {
        "category": "策略RPG / 公会内容",
        "date": "2026-09-22",
        "title": "Watcher of Realms加入新公会Boss、阵营与公会战赛季",
        "summary": "1.6.38.829.1加入Fallen Covenant公会Boss、Grey Blades阵营、新公会战赛季及多名英雄调整。",
        "impact": "产品回到iOS #35，是本轮回榜产品中位置最高者；后续需验证内容窗口能否形成连续留榜。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6741674823",
    },
    {
        "category": "轻度塔防 / 场景更新",
        "date": "2026-09-21",
        "title": "Cell Survivor 3.9扩展主题场景",
        "summary": "Apple官方版本说明称3.9加入更多主题场景与新的冒险内容，产品继续以单屏射击和波次防守为入口。",
        "impact": "产品回到iOS #59，仍处掉榜线附近；版本存在但承接强度仍不足。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6746465127",
    },
    {
        "category": "MOBA / 周年赛季",
        "date": "2026-09-16",
        "title": "Mobile Legends美国版推进10周年英雄重做与S42",
        "summary": "2.2.16版本上线Masha、Bruno重做，并开启S42赛季及Popol and Kupa赛季皮肤奖励。",
        "impact": "产品iOS升14位至#24，但属于MOBA分类边界；其上涨不能代表核心SLG或塔防同步改善。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id6741568655",
    },
    {
        "category": "长线塔防 / 限时榜",
        "date": "2026-09-15",
        "title": "Boom Beach九月更新加入Blitz活动",
        "summary": "官方版本说明介绍Blitz：玩家使用领袖阵容挑战逐步提高的难度，并争夺奖励与新排行榜。",
        "impact": "产品回到iOS #58；活动为可核验背景，但当前仍是榜尾回归。",
        "source": "Apple App Store官方商品页",
        "url": "https://apps.apple.com/us/app/id672150402",
    },
    {
        "category": "全球收入月榜",
        "date": "2026-09-04",
        "title": "Sensor Tower最新官方月榜仍为2026年8月",
        "summary": "全球App Store与Google Play消费者支出估算约65.7亿美元；Whiteout Survival全球总榜#3、Kingshot #7。",
        "impact": "两款均较7月上升1位；官方未披露单品同比，不能把榜位变化换算成收入增幅。",
        "source": "Sensor Tower官方",
        "url": "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026",
    },
]


closing = [
    {
        "type": "判断",
        "title": "Google头部稳定，iOS周末后换榜显著放大",
        "detail": "Google三进三出，57款共同产品中40款变动不超过2位，中位绝对变动1位且前10全部保留；iOS八进八出，52款共同产品中25款变动不超过2位，中位绝对变动3.5位、前10只保留7款。",
    },
    {
        "type": "判断",
        "title": "Sea War与Kiss形成双端改善，Infinity Kingdom双端回落",
        "detail": "Sea War在Google +17、iOS +11，Kiss of War两端同时回榜；Infinity Kingdom则Google -11、iOS -13。前两者尚无足够官方节点解释涨幅，后者也不能由榜位推算收入下降。",
    },
    {
        "type": "判断",
        "title": "新品与活动产品主要挤在中后段，首发承接仍需验证",
        "detail": "Kingdom Rush 6本期Google首次进入#57、iOS回落至#46；Star Trek、Boom Beach、Sea of Conquest等有官方内容背景的回榜产品也多位于#50以后，只有Watcher回到#35。",
    },
    {
        "type": "关注",
        "title": "未来1—2个有效快照：检验Kingdom Rush 6双端留榜",
        "detail": "若Google能脱离后五名且iOS守住前50，可继续观察系列IP向稳定付费的承接；若两端同步下移，则更接近首发峰值回落。",
    },
    {
        "type": "关注",
        "title": "下一有效快照：验证Sea War与Kiss的双端持续性",
        "detail": "Sea War需在Google保持前40、iOS保持前25，Kiss需两端继续留榜，才把本次周末后共同改善升级为连续信号。",
    },
    {
        "type": "关注",
        "title": "未来一周：观察活动末期与榜尾产品的退出风险",
        "detail": "Sea of Conquest联动临近结束；Warpath、Cell Survivor、Limbus都处于#59—#60或单端退出状态，MARVEL SNAP也已回落至#54，下一快照将检验活动结束与榜尾轮换是否继续。",
    },
]


all_products = google_products + ios_products
icons = build_market_icons(all_products)
google_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["googlePlay"]["now"])
ios_new = sum(game["comparison90d"]["status"] == "new" for game in datasets["ios"]["now"])


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Google三进三出、iOS八进八出，Sea War双端同步上升",
    "summary": "较9月25日最终有效快照，Google Play三进三出：Kiss of War、Kingdom Rush 6、Warpath进入/回榜，Game of Thrones: Conquest、DC、Age of Spirits掉榜；Sea War +17，GFL2 -18、Last Fortress -15。iOS八进八出，Watcher回到#35、Sea of Conquest首次进入项目榜#60；Battle Cats +21，Kingdom Rush 6 -20、Dragon Traveler -21。Sea War两端同步上升，Infinity Kingdom两端同步回落；近90天新品两端各3款，较老产品因缺少6月30日精确基准不判断90天飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": f"data/games-{CURRENT}.json", "ios": f"data/ios-games-{CURRENT}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREVIOUS}.json", "ios": f"data/ios-games-{PREVIOUS}.json"},
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Police Chief · #60 Limbus Company",
            "products": google_products,
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）",
            "anchors": "榜单锚点：#1 Whiteout Survival · #25 X-Clash: Survival Challenge · #60 Sea of Conquest: Pirate War",
            "products": ios_products,
        },
    },
    "marketNews": news,
    "closing": closing,
    "globalStrategyRevenue": global_strategy_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": google_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-30"},
        "ios": {"top60": 60, "newRelease90d": ios_new, "surge90d": 0, "baselineAvailable": False, "baselineDate": "2026-06-30"},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球收入榜中的策略产品", "url": global_strategy_revenue["sourceUrl"], "period": global_strategy_revenue["period"], "estimateAsOf": global_strategy_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-28.md", "json": "data/market-brief-20260928.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "",
        "## 数据源与口径", "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
        "- 对比基准：各自上一份最终有效快照为2026-09-25；升降为相邻有效快照变化，不等于收入增减。",
        f"- 近90天状态：Google新上榜{google_new}款、iOS新上榜{ios_new}款。两端均缺少2026-06-30精确同口径TOP60基准，较老产品暂不判断飙升。",
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


save("data/market-brief-20260928.json", brief)
(ROOT / "reports/2026-09-28.md").write_text(build_markdown(brief), encoding="utf-8")
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
