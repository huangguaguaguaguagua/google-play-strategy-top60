#!/usr/bin/env python3
"""Generate the Beijing 2026-11-06 dual-store market brief and archive."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from daily_update_20260820 import data_uri

ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, PREV = "2026-11-06", "20261106", "20261105"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=None if compact else 2, separators=(",", ":") if compact else None) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load(f"data/games-{STAMP}.json"), "prior": load(f"data/games-{PREV}.json"), "id": "packageName"},
    "ios": {"now": load(f"data/ios-games-{STAMP}.json"), "prior": load(f"data/ios-games-{PREV}.json"), "id": "appId"},
}


def card(store, product_id, tone, analysis):
    data = datasets[store]
    current = next((x for x in data["now"] if str(x[data["id"]]) == str(product_id)), None)
    previous = next((x for x in data["prior"] if str(x[data["id"]]) == str(product_id)), None)
    row = current or previous
    if tone == "entry" and current and not previous:
        label = f"进入/回榜 · #{current['rank']}"
    elif tone == "exit" and previous and not current:
        label = f"掉榜 · 上期#{previous['rank']}"
    elif tone in ("up", "down") and current and previous:
        delta = previous["rank"] - current["rank"]
        if (delta > 0) != (tone == "up"):
            raise RuntimeError(f"direction mismatch: {store}:{product_id}:{delta}")
        label = f"{'+' if delta > 0 else '−'}{abs(delta)} · #{current['rank']}"
    else:
        raise RuntimeError(f"membership mismatch: {store}:{product_id}:{tone}")
    return {"gameName": row["gameName"], "productId": str(product_id), "iconKey": f"{store}:{product_id}", "tone": tone, "changeLabel": label, "analysis": analysis}


google_products = [
    card("googlePlay", "leyi.westgame", "entry", "回榜#59，上一次项目收录后曾迅速掉榜；本次仍按成熟产品榜尾轮换处理。"),
    card("googlePlay", "com.bw.ud.googleplay", "exit", "上期#59后掉榜，iOS已于前一快照退出；双端连续退出是风险信号，但不外推长期衰退。"),
    card("googlePlay", "com.avenue.zombie.gp", "up", "回升5位至#52，仍处首发验证且位于后九名，需继续确认留位。"),
    card("googlePlay", "com.Sunborn.SnqxExilium.Glo", "down", "下跌21位至#46，是Google当日最大回落；iOS未入榜，单期变化只记为待验证信号。"),
    card("googlePlay", "com.wb.goog.hotd.socialstrategy", "down", "下跌8位至#42，而iOS同产品上升8位至#17；跨端完全反向，不能用单一活动统一解释。"),
    card("googlePlay", "com.gtarcade.ioe.global", "down", "下跌6位至#33，而iOS同产品上升8位至#42；两端层级和方向均分化。"),
]

ios_products = [
    card("ios", "1554247785", "entry", "Yu-Gi-Oh! Master Duel回榜#21；10月29日版本更新了决斗动画与UI，但只作为相邻背景。"),
    card("ios", "1181774280", "entry", "Fire Emblem Heroes回榜#51；11月5日版本加入七名英雄的武器精炼与新兑换目录，时间相邻但不作确定归因。"),
    card("ios", "6760406772", "entry", "Last Shelter: War Z回榜#53；10月版本加入联盟批量管理等功能，当前仍在后八名。"),
    card("ios", "1599937506", "entry", "Warhammer 40,000: Tacticus回榜#58；11月活动仍在内容窗口，但当前压线留榜。"),
    card("ios", "1619254071", "entry", "Honor of Kings回榜#60。产品属于MOBA，保留官方商店榜位但不纳入核心策略收入子集。"),
    card("ios", "6450953550", "exit", "Top Heroes上期#54后掉榜，Google仍在榜；前一快照的双端改善未连续保持。"),
    card("ios", "1606685106", "exit", "Path to Nowhere首次项目收录#52后立即掉榜，只记录为一次榜尾回补。"),
    card("ios", "1529067679", "exit", "Warpath上期回榜#53后立即掉榜，近期版本未形成连续TOP60席位。"),
    card("ios", "6741503079", "exit", "Pokémon Champions上期#56后掉榜，修复版窗口未形成连续席位。"),
    card("ios", "1570095804", "exit", "Kingdom Guard上期#60后掉榜，Google仍位于#60；跨端共同处于风险线。"),
    card("ios", "1480616990", "down", "下跌8位至#20，Google仍在#26；双端均留在中前段，但核心玩法仍是MOBA。"),
    card("ios", "1642607669", "up", "Game of Thrones: Dragonfire上升8位至#17，而Google反向下跌8位至#42。"),
    card("ios", "1487451427", "up", "Infinity Kingdom上升8位至#42，而Google反向下跌6位至#33；跨端分化明显。"),
    card("ios", "6751086804", "up", "Dragon Traveler上升7位至#33，仍处上线早期验证；未发现同步重大官方节点。"),
    card("ios", "6479020757", "up", "DC: Dark Legion再升5位至#44，连续两个快照改善，但Google仍未入榜。"),
    card("ios", "6476261995", "down", "Age of Empires Mobile下跌16位至#54，Google位于#45；iPhone端已进入后七名。"),
    card("ios", "1592081003", "down", "MARVEL SNAP下跌12位至#35，Google位于#51；前一快照的跨端改善未延续。"),
    card("ios", "625257520", "down", "Hearthstone下跌10位至#45；扩展内容仍在窗口，但活动与单日榜位并非必然同向。"),
    card("ios", "6743368869", "down", "Draft Showdown再跌6位至#52，Season 3开启后连续回落，仍需下一快照确认。"),
]

all_cards = google_products + ios_products
for start in range(0, len(all_cards), 4):
    part = all_cards[start:start + 4]
    bundle = {}
    for item in part:
        store = "googlePlay" if item["iconKey"].startswith("googlePlay:") else "ios"
        data = datasets[store]
        row = next((x for x in data["now"] + data["prior"] if str(x[data["id"]]) == item["productId"]), None)
        bundle[item["iconKey"]] = data_uri(row.get("iconUrl") or row.get("rankIconUrl"), (160, 160))
    save(f"assets/market-icons-{STAMP}-{start // 4 + 1:02d}.json", bundle, compact=True)

news = [
    {"category":"全球市场 / 收入榜","date":"2026-11-03","title":"Sensor Tower最新完整全球收入榜仍为2026年10月","summary":"官方全球App Store与Google Play收入榜仍以10月为最新期，Whiteout Survival位列全球总榜第5。","impact":"策略子集继续保留Whiteout Survival #5与Kingshot #9；未发布新期，因此月榜文件不改。","source":"Sensor Tower官方","url":"https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-october-2026"},
    {"category":"战棋RPG / 版本","date":"2026-11-05","title":"Fire Emblem Heroes更新武器精炼与兑换目录","summary":"10.11.0为包括Gullveig在内的七名英雄加入可精炼武器，并更新限时Combat Manuals。","impact":"产品本期回榜iOS #51；版本与回榜相邻，但仍需连续快照确认。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/fire-emblem-heroes/id1181774280"},
    {"category":"MOBA / 回榜","date":"2026-09-22","title":"Honor of Kings仍处Season 16周期","summary":"12.1.1.1版本记录Season 16、限定皮肤返场及多名英雄平衡调整。","impact":"产品回榜iOS #60；虽进入商店策略榜，核心玩法为MOBA，不纳入核心策略收入子集。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/honor-of-kings/id1619254071"},
    {"category":"战术RPG / 活动","date":"2026-10-27","title":"Warhammer 40,000: Tacticus推进11月活动","summary":"1.43.161列出Lost and the Damned、Fabius Bile传奇活动及多轮阵营内容。","impact":"产品回榜iOS #58；当前仍在掉榜线附近，活动只作为背景。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/warhammer-40-000-tacticus/id1599937506"},
    {"category":"卡牌竞技 / UI更新","date":"2026-10-29","title":"Yu-Gi-Oh! Master Duel更新决斗动画与UI","summary":"2.9.0新增决斗动画并优化多项UI/UX。","impact":"产品回榜iOS #21，已进入中前段；仍需后续快照验证。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/yu-gi-oh-master-duel/id1554247785"},
    {"category":"末日4X / 联盟管理","date":"2026-10-29","title":"Last Shelter: War Z加入联盟批量管理","summary":"26.1003.001新增聊天动态表情、联盟成员批量管理并优化PVE连续挑战。","impact":"产品回榜iOS #53；当前仍处后八名。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/last-shelter-war-z/id6760406772"},
    {"category":"MOBA / 版本","date":"2026-11-02","title":"Wild Rift Patch 7.3仍在Center Stage内容窗口","summary":"版本列出Hwei、Sylas、Rek’Sai及3v3v3v3模式等内容。","impact":"产品iOS升至#20、Google #26；保留官方榜位但不纳入核心策略收入子集。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/league-of-legends-wild-rift/id1480616990"},
    {"category":"超级英雄卡牌 / 赛季","date":"2026-10-20","title":"MARVEL SNAP仍在Vampires vs Zombies赛季窗口","summary":"58.15.1加入新角色、Grand Arena、Team Clash及Deadpool's Diner。","impact":"本期iOS下跌12位至#35、Google #51，说明内容窗口与单日榜位并非必然同向。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/marvel-snap-hero-card-game/id1592081003"},
    {"category":"卡牌RPG / 扩展","date":"2026-10-23","title":"Hearthstone推进Reign of the Black Empire扩展","summary":"37.0加入Old God卡牌、Assemble关键词、Arena赛季与新版Journal。","impact":"本期iOS下跌10位至#45；不把扩展窗口写成确定拉升。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/hearthstone/id625257520"},
    {"category":"历史4X / 修复","date":"2026-10-08","title":"Age of Empires Mobile近期版本以错误修复为主","summary":"1.14.202仅披露修复既有问题。","impact":"本期iOS下跌16位至#54、Google #45；缺少重大节点时只记为榜尾风险。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/age-of-empires-mobile/id6476261995"},
]
for i, item in enumerate(news, 1): item["rank"] = i

closing = [
    {"type":"判断","title":"Google一进一出，最大波动来自中段产品","detail":"West Game回榜#59、Sea War掉榜；GIRLS' FRONTLINE 2从#25跌至#46，波动显著高于榜首区。"},
    {"type":"判断","title":"iOS五进五出，回榜稳定性仍弱","detail":"昨日新进的Path to Nowhere、Warpath、Pokémon Champions当天即退出；今日五款新进中四款位于#51以后。"},
    {"type":"判断","title":"跨端反向信号增加","detail":"Dragonfire与Infinity Kingdom均在iOS上升、Google下跌；平台人群与运营节奏不能合并解释。"},
    {"type":"关注","title":"下一有效快照：核验五款iOS回榜产品","detail":"重点观察Yu-Gi-Oh! Master Duel能否稳定中段，以及Fire Emblem、Last Shelter: War Z、Tacticus、Honor of Kings能否留榜。"},
    {"type":"关注","title":"未来1—2个快照：观察GIRLS' FRONTLINE 2与Age of Empires Mobile","detail":"两款均单日大幅回落；只有继续下滑或掉榜才提高风险判断。"},
    {"type":"关注","title":"持续区分商店分类与核心策略口径","detail":"Honor of Kings和Wild Rift可出现在商店策略榜，但全球收入策略子集继续排除MOBA。"},
]

g_hist = load(f"data/history/google-play/{DATE}.json")
i_hist = load(f"data/history/ios/{DATE}.json")
global_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
source_date = datetime.fromisoformat(i_hist["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))

def anchors(rows):
    return " · ".join(f"#{n} {rows[n-1]['gameName']}" for n in (1,25,60))

brief = {
    "date": DATE, "timezone":"Asia/Shanghai",
    "title":"Google一进一出、iOS五进五出；跨端反向信号增加",
    "summary":"较11月5日前一有效快照，Google Play一进一出，West Game回榜#59、Sea War掉榜，GIRLS' FRONTLINE 2下跌21位至#46。iOS五进五出，Yu-Gi-Oh! Master Duel回榜#21，Fire Emblem、Last Shelter: War Z、Tacticus与Honor of Kings进入后十名附近；Age of Empires Mobile −16、MARVEL SNAP −12。Dragonfire与Infinity Kingdom均在iOS上升、Google下跌。Google近90天新品2款、iOS 1款；两端缺少8月8日精确基准，不判断较老产品的90天飙升。",
    "newsMethod":"编辑热度：按时效、厂商/IP体量、双榜关联度与品类影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle":f"assets/market-icons-{STAMP}-01.json",
    "iconOverrideBundles":[f"assets/market-icons-{STAMP}-{i:02d}.json" for i in range(2, (len(all_cards)+3)//4+1)],
    "rankingSources":{"googlePlay":f"data/games-{STAMP}.json","ios":f"data/ios-games-{STAMP}.json"},
    "previousRankingSources":{"googlePlay":f"data/games-{PREV}.json","ios":f"data/ios-games-{PREV}.json"},
    "rankingDynamics":{
        "googlePlay":{"label":"Google Play · Android","sourceTime":f"北京时间 {g_hist['sourceCapturedAt']} 直连抓取","anchors":"榜单锚点："+anchors(datasets['googlePlay']['now']),"products":google_products},
        "ios":{"label":"App Store · iPhone/iOS","sourceTime":f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{i_hist['sourceUpdated']}）","anchors":"榜单锚点："+anchors(datasets['ios']['now']),"products":ios_products},
    },
    "marketNews":news, "closing":closing, "globalStrategyRevenue":global_revenue,
    "status":{
        "googlePlay":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['googlePlay']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-08"},
        "ios":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['ios']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-08"},
    },
    "sources":[
        {"label":"Google Play美国区策略畅销榜直连","url":g_hist['sourceUrl'],"capturedAt":g_hist['sourceCapturedAt']},
        {"label":"Apple官方美国区iPhone策略畅销RSS","url":i_hist['sourceUrl'],"updated":i_hist['sourceUpdated'],"sourceDateBeijing":i_hist['dataDate']},
        {"label":"Sensor Tower全球收入榜中的策略产品","url":global_revenue['sourceUrl'],"period":global_revenue['period'],"estimateAsOf":global_revenue['estimateAsOf']},
    ],
    "downloads":{"markdown":f"reports/{DATE}.md","json":f"data/market-brief-{STAMP}.json"},
}


def markdown(value):
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{value['title']}**","",value['summary'],"","## 数据源与口径","",f"- Google Play：`{g_hist['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={i_hist['sourceUpdated']}`，对应北京时间榜单日期 `{i_hist['dataDate']}`",f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-05；升降为相邻有效快照变化，不等于收入增减。","- 近90天：缺少2026-08-08精确同口径TOP60基准，较老产品内部pending、页面按常规展示。","","## 1. 双榜当日异动产品",""]
    for store in ("googlePlay","ios"):
        section=value['rankingDynamics'][store]; lines += [f"### {section['label']}","",section['sourceTime']+"。",""]
        for item in section['products']: lines += [f"#### {item['gameName']}｜{item['changeLabel']}","",item['analysis'],""]
    lines += ["## 2. 策略手游市场热点","",value['newsMethod'],""]
    for item in news: lines += [f"### {item['rank']}. [{item['title']}]({item['url']})","",f"- 类别：{item['category']}｜发布日期：{item['date']}｜来源：{item['source']}",f"- 事实摘要：{item['summary']}",f"- 市场含义：{item['impact']}",""]
    lines += ["## 3. 综合判断与后续关注",""]
    for item in closing: lines += [f"### {item['type']}｜{item['title']}","",item['detail'],""]
    rev=global_revenue; lines += ["## 4. Sensor Tower 全球收入榜中的策略产品","",f"- 数据期：{rev['periodLabel']}｜估算截至：{rev['estimateAsOf']}",f"- 策略筛选：官方全球收入TOP10中命中{rev['strategyMatches']}款核心策略产品；这不是完整策略品类TOP10",f"- 原始来源：[{rev['source']}]({rev['sourceUrl']})","","| 全球总榜 | 游戏 | 发行商 | 策略类型 | 较上月榜位 | 单品收入同比 |","|---:|---|---|---|---|---|"]
    for x in rev['rankings']: lines.append(f"| {x['rank']} | {x['gameName']} | {x['publisher']} | {x['strategyGenre']} | {x['movementLabel']} | {x['yoyRevenueLabel']} |")
    lines += ["",rev['methodologyNote'],"","## 下载与来源","",f"- JSON：`{value['downloads']['json']}`",f"- Markdown：`{value['downloads']['markdown']}`",""]
    return "\n".join(lines)


save(f"data/market-brief-{STAMP}.json", brief)
(ROOT / f"reports/{DATE}.md").write_text(markdown(brief), encoding="utf-8")
manifest=load("reports/manifest.json")
entry={"date":DATE,"title":brief['title'],"summary":brief['summary'],"markdown":brief['downloads']['markdown'],"json":brief['downloads']['json']}
manifest['updated']=DATE
manifest['reports']=sorted([entry]+[x for x in manifest['reports'] if x['date'] != DATE],key=lambda x:x['date'],reverse=True)
save("reports/manifest.json",manifest)
print(f"Wrote {len(all_cards)} product cards, {len(news)} news items and {(len(all_cards)+3)//4} icon bundles")
