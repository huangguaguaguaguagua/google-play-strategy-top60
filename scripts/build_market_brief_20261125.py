#!/usr/bin/env python3
"""Build the 2026-11-25 market brief, archive report and local icon bundles."""

from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, PREV, BASELINE = "2026-11-25", "20261125", "20261124", "2026-08-27"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=None if compact else 2, separators=(",", ":") if compact else None) + "\n", encoding="utf-8")


datasets = {
    "googlePlay":{"now":load(f"data/games-{STAMP}.json"),"prior":load(f"data/games-{PREV}.json"),"id":"packageName","label":"Google Play · Android"},
    "ios":{"now":load(f"data/ios-games-{STAMP}.json"),"prior":load(f"data/ios-games-{PREV}.json"),"id":"appId","label":"App Store · iPhone/iOS"},
}


def row(store, product_id, current=True):
    source = datasets[store]["now"] if current else datasets[store]["prior"]
    return next(x for x in source if str(x[datasets[store]["id"]]) == str(product_id))


def card(store, product_id, kind, analysis):
    current = kind != "exit"
    item = row(store, product_id, current)
    change = item.get("dailyChange", "") if current else "OUT"
    labels = {
        "entry":f"进入/回榜 #{item['rank']}", "exit":f"从 #{item['rank']} 掉榜",
        "up":f"上升 {change[1:]} 位至 #{item['rank']}", "down":f"下降 {change[1:]} 位至 #{item['rank']}",
    }
    return {
        "store":store,"productId":str(product_id),"gameName":item["gameName"],
        "currentRank":item["rank"] if current else None,"previousRank":item["rank"] if not current else next((x["rank"] for x in datasets[store]["prior"] if str(x[datasets[store]["id"]]) == str(product_id)), None),
        "changeType":kind,"changeLabel":labels[kind],"analysis":analysis,
        "iconKey":f"{store}:{product_id}","assetRank":item["assetRank"],
    }


google_products = [
    card("googlePlay","leyi.ageofspirits","entry","前一日掉榜后回到#57，并按Google美国区released日期归类为近90天新品。连续进出说明仍处首发验证和榜尾轮换。"),
    card("googlePlay","com.more.dayzsurvival.gp","entry","Last Shelter: Survival回榜#60，只占据末位；同系列War Z仍在#29，两个package必须分别观察。"),
    card("googlePlay","com.YoStarEN.MahjongSoul","exit","前一日首次进入当前历史池并位于#58，本期即掉榜；成熟立直麻将产品尚未形成连续在榜。"),
    card("googlePlay","com.doradogames.conflictnations.worldwar3","exit","前一日已降至#60，本期掉榜；G.I. Joe联动尚未公布正式赛季时间，不能把退出解释为活动效果。"),
    card("googlePlay","com.topwar.gp","up","Top War上升5位至#47，部分收复前一日跌幅，但仍处中后段；需连续快照确认是否脱离榜尾压力。"),
    card("googlePlay","com.greenmushroom.boomblitz.gp","up","Top Heroes上升5位至#37；轻量战斗获量层与城建英雄养成承接出现单日改善，未发现可确认的同步节点。"),
    card("googlePlay","com.YoStarEN.Arknights","down","继前一日−17后再下降13位至#50，形成连续两日回落；Monster Hunter联动仍在进行，但不能据榜位直接判断活动效果。"),
    card("googlePlay","com.hariwn.legendofcivilizations","down","Forge Master下降6位至#51，进入后十名；iOS同产品反而上升4位至#33，跨端方向相反。"),
]

ios_products = [
    card("ios","1554247785","entry","Yu-Gi-Oh! Master Duel进入#22。卡组竞技产品位于前25，但属于卡牌策略交叉分类，不扩写为SLG市场变化。"),
    card("ios","6476261995","entry","Age of Empires Mobile回榜并升至#26，按8月27日精确基准#40归类为近90天飙升；Chaos Rift版本是可核验背景，但不能直接解释名次。"),
    card("ios","6776076449","entry","Plants on Fire进入#34；11月24日Magic Fortune赛季与感恩节活动同窗，当前只记为进入信号，不断言活动带动。"),
    card("ios","6755173751","entry","Evo Defense回榜#43。塔防产品进入中后段，尚无足够证据确认由特定活动推动。"),
    card("ios","1575590830","entry","The Tower回榜#45。放置塔防产品暂处中后段，需观察下一有效快照能否持续留榜。"),
    card("ios","6761043541","entry","Last Beacon进入#54，并按Apple Lookup releaseDate归类为近90天新品；仍处首发验证和榜尾区。"),
    card("ios","6450953550","entry","Top Heroes回榜#59，而Google同产品升至#37；双端同向但iOS仅位于末二位。"),
    card("ios","1529067679","exit","前一日上升至#50后掉榜；Google同产品仍#56，Warpath的双端改善未能延续到iOS。"),
    card("ios","1427744264","exit","Star Trek Fleet Command从#53掉榜；Google仍#21，成熟IP产品的跨端差距扩大。"),
    card("ios","6740189002","exit","Galaxy Defense前一日进入#54后即掉榜，未形成连续在榜。"),
    card("ios","6740232087","exit","Aliens vs Zombies从#55掉榜；单次退出只作为榜尾风险信号。"),
    card("ios","6479020757","exit","DC: Dark Legion前一日回榜#56后即掉榜，IP角色与基地策略产品仍表现为榜尾轮换。"),
    card("ios","1619254071","exit","Honor of Kings前一日降至#58后掉榜；MOBA交叉分类不纳入核心策略子集。"),
    card("ios","1611722542","exit","Kingdom Clash前一日末位进入，本期即掉榜，未形成连续信号。"),
    card("ios","1181774280","up","Fire Emblem Heroes从#59回升4位至#55，仍处后六名；更像前一日下跌后的回摆。"),
    card("ios","850057092","down","The Battle Cats下降14位至#58，是iOS最大跌幅并进入榜尾风险区。"),
    card("ios","6760406772","down","Last Shelter: War Z下降12位至#60，回吐前一日涨幅；Google同产品仍#29，跨端表现重新分化。"),
    card("ios","1599937506","down","Tacticus下降10位至#44，而Google维持#40；两端均回到中后段，暂不归因于单一节点。"),
    card("ios","1035712810","down","Game of Thrones: Conquest下降9位至#47，Google同产品#49；两端排名接近但均处中后段。"),
]


def asset_map(store):
    manifest = load("assets/manifest.json" if store == "googlePlay" else "assets/ios-manifest.json")
    result = {}
    for name in manifest["files"]:
        result.update(load("assets/" + name))
    return result


assets = {"googlePlay":asset_map("googlePlay"),"ios":asset_map("ios")}
cards = google_products + ios_products
for start in range(0, len(cards), 5):
    bundle = {}
    for item in cards[start:start + 5]:
        key = f"{int(item['assetRank']):02d}_icon"
        value = assets[item["store"]].get(key)
        if not str(value).startswith("data:image/"):
            raise RuntimeError(f"Missing local icon {item['store']} {key} for {item['gameName']}")
        bundle[item["iconKey"]] = value
    save(f"assets/market-icons-{STAMP}-{start // 5 + 1:02d}.json", bundle, compact=True)


news = [
    {"category":"全球市场 / 收入榜","date":"2026-11-04","title":"Sensor Tower最新官方全球收入榜仍为2026年10月","summary":"官方完整TOP10显示ROBLOX位居全球手游收入第一，Whiteout Survival为第5、Kingshot为第9；全球App Store与Google Play消费者支出为62.6亿美元，排除第三方Android市场。","impact":"本页策略子集继续保留Whiteout Survival与Kingshot两款及10月真实统计期，不把工作日检查伪装成11月新榜。","source":"Sensor Tower官方","url":"https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-october-2026"},
    {"category":"城建生存 / 节日活动","date":"2026-11-23","title":"Kingshot公布Harvest Season节日活动","summary":"公告列出Feast Preparations等丰收庆典内容，以烹饪和提交菜品累积个人庆典积分。","impact":"Kingshot本期Google #1、iOS #2；活动与榜首位置同窗，但单日排名不能直接证明活动效果。","source":"Kingshot公告汇总","url":"https://kingshot.net/game-announcements"},
    {"category":"经典IP / 版本更新","date":"2026-11-19","title":"Age of Empires Mobile上线Chaos Rift等新内容","summary":"官方维护公告列出Chaos Rift跨帝国战场，并要求更新至Android 1.15.103.0、iOS 1.15.104.0和PC 1.15.100.0。","impact":"产品本期iOS回榜#26且按精确基准归类为近90天飙升；版本节点是背景，但不能直接解释名次。","source":"Age of Empires Mobile官方Steam公告","url":"https://steamcommunity.com/app/2783360/allnews/"},
    {"category":"现代战争 / IP联动","date":"2026-11-17","title":"Supremacy: World War 3宣布十周年G.I. Joe联动","summary":"Stillfront旗下Twin Harbour宣布将推出专属G.I. Joe赛季，并称这是该产品首次IP联动。","impact":"产品本期Google掉榜、iOS #40；正式赛季时间尚未公布，当前只能作为未来版本关注点。","source":"Twin Harbour / Games Press","url":"https://www.gamespress.com/GI-Joe-Joins-the-Fight-in-Supremacy-World-War-3-for-the-Games-10th-Ann"},
    {"category":"塔防 / IP联动","date":"2026-11-12","title":"Arknights × Monster Hunter联动于11月16日开启","summary":"官方公告确认Thunder in the Azure Dream活动持续至12月7日，第一阶段开放至11月30日，并配套限定寻访和活动商店。","impact":"产品Google连续两日下跌至#50、iOS未进榜；活动窗口与回落同窗，但不能直接推断因果。","source":"Arknights官方","url":"https://www.arknights.global/news/5092"},
    {"category":"IP新品 / 首发运营","date":"2026-11-16","title":"Transformers: Eternal War上线后进入首个限时活动窗口","summary":"Apple商品页显示1.2.1版本于11月16日更新，并列出11月14—20日限时活动和Optimus Prime付费活动。","impact":"产品当前iOS #28且仍属近90天新品；活动结束后能否继续维持前30是首发承接的重要观察点。","source":"Apple App Store","url":"https://apps.apple.com/us/app/id6772922295"},
    {"category":"长线运营 / 新玩法","date":"2026-11-06","title":"Whiteout Survival开放Mergeventure并扩充社交与竞技系统","summary":"官方更新说明新增Mergeventure合成活动、Chief Gift社交功能、每周Expedition Arena与新Expert Justus。","impact":"Whiteout Survival仍在双榜前列且位于Sensor Tower全球收入总榜#5；新玩法展示成熟城建生存产品如何并行维护轻活动、社交与核心竞技。","source":"Whiteout Survival官方更新资料","url":"https://www.whiteoutsurvival.wiki/sneak-peek/101898521en/"},
    {"category":"塔防 / 赛季更新","date":"2026-11-24","title":"Plants on Fire开启Magic Fortune赛季","summary":"Apple版本资料列出Magic Fortune赛季、新随从、四种变体、Astral Blessings及感恩节登录活动。","impact":"产品本期iOS进入#34；赛季节点可核验，但当前仅有一个快照，不能断言活动形成持续收入提升。","source":"Apple App Store","url":"https://apps.apple.com/us/app/id6776076449"},
    {"category":"科幻策略 / 周年运营","date":"2026-10-20","title":"Foundation: Galactic Frontier完成首周年Astral Alignment活动","summary":"FunPlus官方称周年活动于10月19日至11月7日分阶段开放，并提供不同玩法与奖励。","impact":"产品本期Google #31、iOS #38；活动已结束，当前榜位更适合观察周年用户留存。","source":"FunPlus官方","url":"https://funplus.com/foundation-galactic-frontier-anniversary-event/"},
    {"category":"IP长线运营","date":"2026-11-03","title":"Game of Thrones: Conquest发布Highgarden Harvest Festival月度预告","summary":"官方11月预告公布新装备、英雄与龙装，并围绕Highgarden主题安排当月内容。","impact":"产品Google #49、iOS #47；两端均处中后段，仍需后续快照确认活动支撑。","source":"Game of Thrones: Conquest官方","url":"https://www.gotconquest.com/news/2026/11/03/november-preview-highgarden-harvest-festival-6/"},
]
for index, item in enumerate(news, 1): item["rank"] = index


closing = [
    {"type":"判断","title":"iOS榜尾轮换进一步扩大","detail":"Google 2进2出，iOS 7进7出；iOS七款退出中六款前一日位于#50以后，榜尾产品继续快速换位。"},
    {"type":"判断","title":"两端榜首分别被Century Games产品占据","detail":"Google榜首为Kingshot，iOS榜首为Whiteout Survival；两款同时命中Sensor Tower 10月全球收入TOP10策略子集。"},
    {"type":"判断","title":"前一日双端改善未形成统一延续","detail":"Warpath iOS掉榜、Last Shelter: War Z iOS跌至#60，而Google分别保持#56与#29；成熟SLG再次出现平台分化。"},
    {"type":"关注","title":"下一有效快照：核验九款进入/回榜产品","detail":"重点观察Age of Spirits、Plants on Fire、Age of Empires Mobile、Last Beacon与Top Heroes能否连续留榜。"},
    {"type":"关注","title":"未来2—3个快照：确认Arknights连续回落是否持续","detail":"Google两日累计下降30位至#50，iOS未进榜；只有后续继续回落，才升级为持续压力判断。"},
    {"type":"关注","title":"感恩节活动窗口后：复核Plants on Fire和Kingshot","detail":"两款均有可核验的节日/赛季节点；待活动窗口结束后比较连续榜位，不用单日排名替代效果判断。"},
]


google_history = load(f"data/history/google-play/{DATE}.json")
ios_history = load(f"data/history/ios/{DATE}.json")
revenue = load("data/sensortower-global-strategy-revenue-latest.json")
ios_source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


def anchors(rows):
    return " · ".join(f"#{rank} {rows[rank - 1]['gameName']}" for rank in (1,25,60))


def count_status(store, status):
    return sum(x["comparison90d"]["status"] == status for x in datasets[store]["now"])


brief = {
    "date":DATE,"timezone":"Asia/Shanghai","title":"Kingshot与Whiteout分占双榜榜首；iOS榜尾轮换扩大",
    "summary":"较11月24日前一有效快照，Google Play 2进2出，Top War与Top Heroes各+5、Arknights −13；iOS 7进7出，Age of Empires Mobile回榜#26、The Battle Cats −14、Last Shelter: War Z −12。Google榜首换为Kingshot，iOS榜首换为Whiteout Survival。两端精确8月27日基准均可用；Google有1款近90天新品、7款飙升，iOS有3款新品、8款飙升。",
    "newsMethod":"编辑热度：按时效、厂商/IP体量、双榜关联度与品类影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle":f"assets/market-icons-{STAMP}-01.json","iconOverrideBundles":[f"assets/market-icons-{STAMP}-{i:02d}.json" for i in range(2,(len(cards)+4)//5+1)],
    "rankingSources":{"googlePlay":f"data/games-{STAMP}.json","ios":f"data/ios-games-{STAMP}.json"},
    "previousRankingSources":{"googlePlay":f"data/games-{PREV}.json","ios":f"data/ios-games-{PREV}.json"},
    "rankingDynamics":{
        "googlePlay":{"label":datasets["googlePlay"]["label"],"sourceTime":f"北京时间 {google_history['sourceCapturedAt']} 直连抓取","anchors":"榜单锚点："+anchors(datasets["googlePlay"]["now"]),"products":google_products},
        "ios":{"label":datasets["ios"]["label"],"sourceTime":f"Apple RSS 北京时间 {ios_source_date:%Y-%m-%d %H:%M:%S}（源更新：{ios_history['sourceUpdated']}）","anchors":"榜单锚点："+anchors(datasets["ios"]["now"]),"products":ios_products},
    },
    "marketNews":news,"closing":closing,"globalStrategyRevenue":revenue,
    "status":{
        "googlePlay":{"top60":60,"newRelease90d":count_status("googlePlay","new"),"surge90d":count_status("googlePlay","surge"),"baselineAvailable":True,"baselineDate":BASELINE},
        "ios":{"top60":60,"newRelease90d":count_status("ios","new"),"surge90d":count_status("ios","surge"),"baselineAvailable":True,"baselineDate":BASELINE},
    },
    "sources":[
        {"label":"Google Play美国区策略畅销榜直连","url":google_history["sourceUrl"],"capturedAt":google_history["sourceCapturedAt"]},
        {"label":"Apple官方美国区iPhone策略畅销RSS","url":ios_history["sourceUrl"],"updated":ios_history["sourceUpdated"],"sourceDateBeijing":ios_history["dataDate"]},
        {"label":"Sensor Tower全球收入榜中的策略产品","url":revenue["sourceUrl"],"period":revenue["period"],"estimateAsOf":revenue["estimateAsOf"]},
    ],
    "downloads":{"markdown":f"reports/{DATE}.md","json":f"data/market-brief-{STAMP}.json"},
}


def markdown(value):
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{value['title']}**","",value["summary"],"","## 数据源与口径","",f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-24。","- 近90天：两端2026-08-27精确同口径TOP60基准均可用；新品先按各自商店releaseDate判定。","","## 1. 双榜当日异动产品",""]
    for store in ("googlePlay","ios"):
        section=value["rankingDynamics"][store]; lines += [f"### {section['label']}","",section["sourceTime"]+"。",""]
        for item in section["products"]: lines += [f"#### {item['gameName']}｜{item['changeLabel']}","",item["analysis"],""]
    lines += ["## 2. 策略手游市场热点","",value["newsMethod"],""]
    for item in news: lines += [f"### {item['rank']}. [{item['title']}]({item['url']})","",f"- 类别：{item['category']}｜发布日期：{item['date']}｜来源：{item['source']}",f"- 事实摘要：{item['summary']}",f"- 市场含义：{item['impact']}",""]
    lines += ["## 3. 综合判断与后续关注",""]
    for item in closing: lines += [f"### {item['type']}｜{item['title']}","",item["detail"],""]
    lines += ["## 4. Sensor Tower 全球收入榜中的策略产品","",f"- 数据期：{revenue['periodLabel']}｜估算截至：{revenue['estimateAsOf']}",f"- 策略筛选：官方全球收入TOP10中命中{revenue['strategyMatches']}款核心策略产品；这不是完整策略品类TOP10",f"- 原始来源：[{revenue['source']}]({revenue['sourceUrl']})","","| 全球总榜 | 游戏 | 发行商 | 策略类型 | 较上月榜位 | 单品收入同比 |","|---:|---|---|---|---|---|"]
    for item in revenue["rankings"]: lines.append(f"| {item['rank']} | {item['gameName']} | {item['publisher']} | {item['strategyGenre']} | {item['movementLabel']} | {item['yoyRevenueLabel']} |")
    lines += ["",revenue["methodologyNote"],"","## 下载与来源","",f"- JSON：`{value['downloads']['json']}`",f"- Markdown：`{value['downloads']['markdown']}`",""]
    return "\n".join(lines)


save(f"data/market-brief-{STAMP}.json",brief)
(ROOT/f"reports/{DATE}.md").write_text(markdown(brief),encoding="utf-8")
manifest=load("reports/manifest.json")
entry={"date":DATE,"title":brief["title"],"summary":brief["summary"],"markdown":brief["downloads"]["markdown"],"json":brief["downloads"]["json"]}
manifest["updated"]=DATE
manifest["reports"]=sorted([entry]+[x for x in manifest["reports"] if x["date"]!=DATE],key=lambda x:x["date"],reverse=True)
save("reports/manifest.json",manifest)
print(f"Wrote {len(cards)} product cards, {len(news)} news items and {(len(cards)+4)//5} icon bundles")
