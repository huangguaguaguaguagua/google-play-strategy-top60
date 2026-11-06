#!/usr/bin/env python3
"""Generate the Beijing 2026-11-05 dual-store market brief and archive."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from daily_update_20260820 import data_uri

ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, PREV = "2026-11-05", "20261105", "20261104"


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
    card("googlePlay", "com.riotgames.league.wildrift", "entry", "首次进入项目Google榜#26。产品被Google策略分类榜收录，但核心玩法是MOBA；本次只记录官方榜位，不将其纳入Sensor Tower核心策略定义。"),
    card("googlePlay", "com.igg.android.doomsdaylastsurvivors", "exit", "上期#60后掉榜；此前已处末位，本次属于榜尾轮换，不能外推长期衰退。"),
    card("googlePlay", "com.nvsgames.snap", "up", "上升8位至#48，连续第二个快照改善；iOS未出现同幅度变化，仍需验证Android留位。"),
    card("googlePlay", "com.yottagames.mafiawar", "up", "上升5位至#38，离开后二十名；未发现与本次位移同步的单一官方节点。"),
    card("googlePlay", "com.YoStarEN.Arknights", "down", "下跌13位至#52，进入后十名；单日回落只记为掉榜风险信号。"),
    card("googlePlay", "com.bw.ud.googleplay", "down", "下跌5位至#59，iOS同产品掉榜；双端同向转弱，但不能据单期认定长期趋势。"),
    card("googlePlay", "com.avenue.zombie.gp", "down", "下跌5位至#57，仍处首发验证且已接近掉榜线。"),
]

ios_products = [
    card("ios", "1480616990", "entry", "回榜#12，Google同步首次进入#26。Patch 7.3仍在近期窗口，但双端回归只记为待验证信号。"),
    card("ios", "1606685106", "entry", "Path to Nowhere首次进入项目iOS榜#52；Apple 10月27日版本仅列修复，缺少证据解释本次入榜。"),
    card("ios", "1529067679", "entry", "Warpath回榜#53；10月版本加入Alliance Assembly等内容，但当前仍在后八名。"),
    card("ios", "6741503079", "entry", "Pokémon Champions回榜#56；11月4日版本只披露问题修复，不能据此解释榜位。"),
    card("ios", "1411917616", "entry", "Rise of Castles回榜#58；11月2日版本以性能和错误修复为主，当前压线留榜。"),
    card("ios", "850057092", "exit", "The Battle Cats上期#49后掉榜；成熟产品单次退出只记为榜尾波动。"),
    card("ios", "6741674823", "exit", "Watcher of Realms上期#47后掉榜；近期内容未形成连续TOP60席位。"),
    card("ios", "1611722542", "exit", "Kingdom Clash上期回榜#53后立即掉榜，榜尾回补未连续保持。"),
    card("ios", "6447612873", "exit", "Sea War上期#55后掉榜，Google同步跌至#59；双端共同进入风险区。"),
    card("ios", "966810173", "exit", "Vikings上期回榜#59后立即掉榜；版本窗口未形成连续席位。"),
    card("ios", "6479020757", "up", "上升11位至#49，暂时离开末位；Google未入榜，平台节奏仍分化。"),
    card("ios", "6761893238", "up", "Top Force上升5位至#20；10月跨服活动仍属近期背景，单次改善不等于长期抬升。"),
    card("ios", "1342290011", "up", "Last Shelter上升6位至#51，但仍在后十名附近，继续观察留位。"),
    card("ios", "6743368869", "down", "Draft Showdown下跌11位至#46；Season 3已于11月2日开始，但榜位与活动并非必然同向。"),
    card("ios", "1570095804", "down", "Kingdom Guard下跌6位至#60，Google位于#60；双端同时压线，是明确的下一快照风险点。"),
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
    {"category":"MOBA / 版本","date":"2026-11-02","title":"Wild Rift Patch 7.3仍在Center Stage内容窗口","summary":"Apple版本记录列出Hwei、Sylas、Rek’Sai及3v3v3v3模式等内容。","impact":"产品本期Google #26、iOS #12；核心玩法为MOBA，虽进入商店策略榜但不纳入核心策略收入子集。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/league-of-legends-wild-rift/id1480616990"},
    {"category":"战术塔防 / 回榜","date":"2026-10-27","title":"Path to Nowhere版本1.9.54完成错误修复","summary":"Apple版本记录仅披露错误修复，未公开重大系统更新。","impact":"产品首次进入项目iOS榜#52；缺少确定节点时只记录为待验证信号。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/path-to-nowhere/id1606685106"},
    {"category":"军事4X / 版本","date":"2026-10-14","title":"Warpath加入Alliance Assembly与基地防御科技","summary":"14.50版本加入联盟集结、高级采集点搜索、基地防御科技及多项活动内容。","impact":"产品回榜iOS #53；版本距本期已有数周，不作直接因果判断。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/warpath-ace-shooter/id1529067679"},
    {"category":"竞技策略 / 修复","date":"2026-11-04","title":"Pokémon Champions发布1.2.3修复版","summary":"官方版本说明仅称处理若干问题以改善使用体验。","impact":"产品回榜iOS #56；修复版不足以解释商业榜位变化。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/pok%C3%A9mon-champions/id6741503079"},
    {"category":"城建4X / 修复","date":"2026-11-02","title":"Rise of Castles 26.1002.1优化性能","summary":"版本说明以性能优化和错误修复为主。","impact":"产品回榜iOS #58，仍处掉榜线附近。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/rise-of-castles-fire-and-war/id1411917616"},
    {"category":"超级英雄策略 / 修复","date":"2026-11-04","title":"DC: Dark Legion更新2.2.28","summary":"版本修复多项文本与显示问题。","impact":"iOS上升11位至#49，但Google未入榜，平台信号不一致。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/dc-dark-legion/id6479020757"},
    {"category":"轻量策略 / 赛季","date":"2026-10-31","title":"Draft Showdown Season 3于11月2日启动","summary":"1.20.0加入新Draft Pass、传奇单位，并优化排位匹配。","impact":"本期iOS下跌11位至#46，活动窗口与单日榜位并非必然同向。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/draft-showdown/id6743368869"},
    {"category":"末日4X / 系统","date":"2026-11-04","title":"Last Shelter加入宠物释放与Yesterday Tech榜","summary":"26.1002.1新增宠物释放、Yesterday Tech排行榜并优化榜单刷新。","impact":"产品iOS上升6位至#51，仍需后续快照验证持续性。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/last-shelter-survival/id1342290011"},
    {"category":"轻量4X / 跨服活动","date":"2026-10-20","title":"Top Force加入Nuclear Reckoning跨服活动","summary":"3.5.1加入Battlefield Assault、Nuclear Reckoning及联盟通知功能。","impact":"产品iOS上升5位至#20；内容作为背景，不将单期位移写成确定效果。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/top-force-commander/id6761893238"},
]
for i, item in enumerate(news, 1): item["rank"] = i

closing = [
    {"type":"判断","title":"Google成员仅一进一出，但中后段位移放大","detail":"Wild Rift进入#26、Doomsday从#60掉榜；Arknights −13至#52，MARVEL SNAP +8至#48。"},
    {"type":"判断","title":"iOS五进五出，换位继续集中于后段","detail":"五款进入产品中四款位于#52以后；五款掉榜产品上期均位于#47以后。"},
    {"type":"判断","title":"跨端共同风险比共同上涨更清晰","detail":"Sea War在iOS掉榜且Google跌至#59；Kingdom Guard双端同时位于#60。Wild Rift双端进入则仍需连续快照确认。"},
    {"type":"关注","title":"下一有效快照：核验iOS五款回榜产品","detail":"重点观察Path to Nowhere、Warpath、Pokémon Champions、Rise of Castles是否连续留榜，以及Wild Rift能否保持前20附近。"},
    {"type":"关注","title":"未来1—2个快照：观察Sea War与Kingdom Guard","detail":"若Google端继续掉榜或iOS未回补，才提高双端共同转弱判断。"},
    {"type":"关注","title":"11月上旬：区分MOBA分类收录与核心策略产品","detail":"Wild Rift保留商店官方榜位，但日报与全球收入策略子集继续明确排除MOBA。"},
]

g_hist = load(f"data/history/google-play/{DATE}.json")
i_hist = load(f"data/history/ios/{DATE}.json")
global_revenue = load("data/sensortower-global-strategy-revenue-latest.json")
source_date = datetime.fromisoformat(i_hist["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))

def anchors(rows):
    return " · ".join(f"#{n} {rows[n-1]['gameName']}" for n in (1,25,60))

brief = {
    "date": DATE, "timezone":"Asia/Shanghai",
    "title":"Google一进一出、iOS五进五出；Wild Rift双端进入策略分类榜",
    "summary":"较11月4日前一有效快照，Google Play一进一出，Wild Rift首次进入项目榜#26，Arknights −13至#52；iOS五进五出，Wild Rift回榜#12，Path to Nowhere首次项目收录#52。Sea War在iOS掉榜且Google跌至#59，Kingdom Guard双端均位于#60。Google近90天新品2款、iOS 1款；两端缺少8月7日精确基准，不判断较老产品的90天飙升。",
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
        "googlePlay":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['googlePlay']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-07"},
        "ios":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['ios']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-07"},
    },
    "sources":[
        {"label":"Google Play美国区策略畅销榜直连","url":g_hist['sourceUrl'],"capturedAt":g_hist['sourceCapturedAt']},
        {"label":"Apple官方美国区iPhone策略畅销RSS","url":i_hist['sourceUrl'],"updated":i_hist['sourceUpdated'],"sourceDateBeijing":i_hist['dataDate']},
        {"label":"Sensor Tower全球收入榜中的策略产品","url":global_revenue['sourceUrl'],"period":global_revenue['period'],"estimateAsOf":global_revenue['estimateAsOf']},
    ],
    "downloads":{"markdown":f"reports/{DATE}.md","json":f"data/market-brief-{STAMP}.json"},
}


def markdown(value):
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{value['title']}**","",value['summary'],"","## 数据源与口径","",f"- Google Play：`{g_hist['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={i_hist['sourceUpdated']}`，对应北京时间榜单日期 `{i_hist['dataDate']}`",f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-04；升降为相邻有效快照变化，不等于收入增减。","- 近90天：缺少2026-08-07精确同口径TOP60基准，较老产品内部pending、页面按常规展示。","","## 1. 双榜当日异动产品",""]
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
