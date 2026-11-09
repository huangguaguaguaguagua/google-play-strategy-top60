#!/usr/bin/env python3
"""Generate the Beijing 2026-11-09 dual-store market brief and archive."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from daily_update_20260820 import data_uri

ROOT=Path(__file__).resolve().parents[1]
DATE,STAMP,PREV="2026-11-09","20261109","20261106"

def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))
def save(p,v,compact=False):
    t=ROOT/p; t.parent.mkdir(parents=True,exist_ok=True)
    t.write_text(json.dumps(v,ensure_ascii=False,indent=None if compact else 2,separators=(",",":") if compact else None)+"\n",encoding="utf-8")

datasets={
 "googlePlay":{"now":load(f"data/games-{STAMP}.json"),"prior":load(f"data/games-{PREV}.json"),"id":"packageName"},
 "ios":{"now":load(f"data/ios-games-{STAMP}.json"),"prior":load(f"data/ios-games-{PREV}.json"),"id":"appId"},
}

def card(store,pid,tone,analysis):
    d=datasets[store]; now=next((x for x in d["now"] if str(x[d["id"]])==str(pid)),None); old=next((x for x in d["prior"] if str(x[d["id"]])==str(pid)),None); row=now or old
    if tone=="entry" and now and not old: label=f"进入/回榜 · #{now['rank']}"
    elif tone=="exit" and old and not now: label=f"掉榜 · 上期#{old['rank']}"
    elif tone in ("up","down") and now and old:
        delta=old["rank"]-now["rank"]
        if (delta>0)!=(tone=="up"): raise RuntimeError((store,pid,delta))
        label=f"{'+' if delta>0 else '−'}{abs(delta)} · #{now['rank']}"
    else: raise RuntimeError((store,pid,tone))
    return {"gameName":row["gameName"],"productId":str(pid),"iconKey":f"{store}:{pid}","tone":tone,"changeLabel":label,"analysis":analysis}

google_products=[
 card("googlePlay","com.plarium.vikings","entry","回榜#53。11月2日版本加入Jötunn Rubies与Jotunheim商店兑换；版本时间相邻，但当前仍属后八名待验证信号。"),
 card("googlePlay","com.QuestLab.DraftWar","entry","回榜#59，Season 3已于11月2日开启；Android当前压线留榜，不能据此断言赛季形成持续拉升。"),
 card("googlePlay","com.doradogames.conflictnations.worldwar3","entry","回榜#60，iOS同产品位于#30；Android仅以末位回补，需下一有效快照确认留位。"),
 card("googlePlay","com.Sunborn.SnqxExilium.Glo","exit","上期#46后掉榜，前一快照曾单日下跌21位；当前只确认Android端退出TOP60。"),
 card("googlePlay","com.proximabeta.aoemobile","exit","上期#58后掉榜；iOS同产品仍在榜，跨端表现继续分化。"),
 card("googlePlay","com.tap4fun.odin.kingdomguard","exit","上期#60后掉榜，iOS同产品反向回榜#58；属于典型榜尾轮换。"),
 card("googlePlay","com.yottagames.gameofmafia","up","上升8位至#19，重新进入前二十；未发现足以确认单一原因的官方节点。"),
 card("googlePlay","com.wb.goog.hotd.socialstrategy","up","上升10位至#32，iOS同产品位于#18；双端均在榜但名次层级仍有差异。"),
 card("googlePlay","com.lavalabs.autodrill","up","上升8位至#40，仍处榜单后段；本次只记为周末后待验证信号。"),
 card("googlePlay","com.mrtgd2us.google","down","下跌10位至#50，仍留在后十一名；需观察是否继续接近掉榜线。"),
 card("googlePlay","com.snowprintstudios.tacticus","down","下跌8位至#57，而iOS反向上升23位至#35；跨端方向完全相反。"),
]

ios_products=[
 card("ios","6450953550","entry","Top Heroes回榜#53；11月2日Cloudsea Odyssey更新了首占首都规则，当前仍处后八名。"),
 card("ios","6740232087","entry","Aliens vs Zombies回榜#55；本次仍按成熟产品榜尾轮换处理。"),
 card("ios","1427744264","entry","Star Trek Fleet Command回榜#57，Google同产品仍在榜；当前iPhone端处于风险线附近。"),
 card("ios","1570095804","entry","Kingdom Guard回榜#58，而Google刚从#60掉榜；两端出现反向榜尾轮换。"),
 card("ios","6463715971","entry","Sea of Conquest回榜#59；当前仅以末二位回补，不外推为长期改善。"),
 card("ios","6776076449","entry","Plants on Fire回榜#60。11月6日3.0.2990加入Dracula、新随从与Astral Blessing，当前仍需验证留位。"),
 card("ios","1035712810","exit","Game of Thrones: Conquest上期#38后掉榜，Google同产品仍在榜；单次退出只作为平台分化信号。"),
 card("ios","625257520","exit","Hearthstone上期#45后掉榜，扩展内容窗口未维持本期TOP60席位。"),
 card("ios","6743368869","exit","Draft Showdown上期#52后掉榜，而Google反向回榜#59；Season 3期间跨端走势分化。"),
 card("ios","6760406772","exit","Last Shelter: War Z上期回榜#53后再次掉榜，只确认榜尾席位不稳定。"),
 card("ios","1411917616","exit","Rise of Castles上期#59后掉榜，Google同产品仍在榜；属于榜尾风险信号。"),
 card("ios","1619254071","exit","Honor of Kings上期#60后掉榜；核心玩法为MOBA，本就不纳入核心策略收入子集。"),
 card("ios","6741568655","up","上升16位至#9，进入前十；核心玩法为MOBA，保留商店榜位但不纳入核心策略收入子集。"),
 card("ios","1496227521","up","Magic: The Gathering Arena上升10位至#20，进入中前段；未将单日变化归因于单一卡包或活动。"),
 card("ios","1599937506","up","Warhammer 40,000: Tacticus上升23位至#35，为iOS最大上涨；11月8日Fabius Bile活动时间相邻，但Google反向下跌。"),
 card("ios","1071744151","up","War and Order上升12位至#36；Google同产品仍在榜，当前先按周末后待验证信号处理。"),
 card("ios","1181774280","up","Fire Emblem Heroes上升10位至#41；11月5日武器精炼更新仍在近期窗口，但不作确定归因。"),
 card("ios","1480616990","down","Wild Rift下跌12位至#32；属于MOBA，保留官方策略分类榜位但不纳入核心策略收入子集。"),
 card("ios","1554247785","down","Yu-Gi-Oh! Master Duel下跌13位至#34，仍位于中段；前一快照回榜后未维持#21。"),
 card("ios","1592081003","down","MARVEL SNAP下跌12位至#47，已接近后十名；Google同产品仍在榜。"),
 card("ios","6751086804","down","Dragon Traveler下跌19位至#52，是iOS最大回落之一；产品仍处上线早期验证。"),
]

all_cards=google_products+ios_products
for start in range(0,len(all_cards),5):
    bundle={}
    for item in all_cards[start:start+5]:
        store="googlePlay" if item["iconKey"].startswith("googlePlay:") else "ios"; d=datasets[store]
        row=next(x for x in d["now"]+d["prior"] if str(x[d["id"]])==item["productId"])
        bundle[item["iconKey"]]=data_uri(row.get("iconUrl") or row.get("rankIconUrl"),(160,160))
    save(f"assets/market-icons-{STAMP}-{start//5+1:02d}.json",bundle,compact=True)

news=[
 {"category":"全球市场 / 收入榜","date":"2026-11-03","title":"Sensor Tower最新完整全球收入榜仍为2026年10月","summary":"官方全球App Store与Google Play收入榜仍以10月为最新期，Whiteout Survival位列全球总榜第5。","impact":"策略子集继续保留Whiteout Survival #5与Kingshot #9；未发布新期，月榜文件不改。","source":"Sensor Tower官方","url":"https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-october-2026"},
 {"category":"战术RPG / 活动","date":"2026-11-08","title":"Tacticus开启Fabius Bile传奇活动","summary":"1.43.161版本日程列出11月8日Chosen of the Dark Gods传奇活动。","impact":"产品iOS升至#35、Google跌至#57；活动与跨端反向表现同时出现，不能写成统一拉升。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/warhammer-40-000-tacticus/id1599937506"},
 {"category":"轻量塔防 / 版本","date":"2026-11-06","title":"Plants on Fire加入Dracula与Astral Blessing","summary":"3.0.2990加入传奇Captain Count Dracula、四名新Minion、Astral Blessing及多项模式调整。","impact":"产品回榜iOS #60；版本时间紧邻，但当前仅能确认末位回补。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/plants-on-fire/id6776076449"},
 {"category":"战棋RPG / 版本","date":"2026-11-05","title":"Fire Emblem Heroes更新武器精炼与兑换目录","summary":"10.11.0为七名英雄加入可精炼武器，并更新限时Combat Manuals。","impact":"产品iOS上升10位至#41，仍需连续快照确认。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/fire-emblem-heroes/id1181774280"},
 {"category":"卡牌竞技 / 赛季","date":"2026-11-02","title":"Draft Showdown Season 3进入运行期","summary":"1.20.0宣布Season 3于11月2日开启，加入新Draft Pass与传奇单位。","impact":"产品Google回榜#59、iOS掉榜，跨端反向说明不能用赛季统一解释。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/draft-showdown/id6743368869"},
 {"category":"经营4X / 版本","date":"2026-11-02","title":"Top Heroes调整Cloudsea Odyssey首都规则","summary":"1.127.7调整公会首占首都判定，并加入Lite Mode与技能描述修复。","impact":"产品回榜iOS #53；当前仍在后八名。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/top-heroes-kingdom-saga/id6450953550"},
 {"category":"维京4X / 版本","date":"2026-11-02","title":"Vikings加入Jötunn Rubies","summary":"7.3.0新增Jötunn Rubies，由Clan在Jotunheim竞赛中获得并兑换高级商品。","impact":"产品回榜Google #53；当前只作榜尾待验证信号。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/vikings-war-of-clans-pvp/id966810173"},
 {"category":"MOBA / 版本","date":"2026-11-02","title":"Wild Rift仍处Patch 7.3 Center Stage窗口","summary":"版本列出Hwei、Sylas、Rek'Sai与3v3v3v3模式等内容。","impact":"产品iOS下跌12位至#32；商店分类不改变其MOBA核心口径。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/league-of-legends-wild-rift/id1480616990"},
 {"category":"卡牌竞技 / UI更新","date":"2026-10-29","title":"Yu-Gi-Oh! Master Duel更新决斗动画与UI","summary":"2.9.0新增决斗动画并改进多项UI/UX。","impact":"产品iOS由#21回落至#34，仍在中段。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/yu-gi-oh-master-duel/id1554247785"},
 {"category":"全球战争 / 稳定性","date":"2026-10-26","title":"Supremacy近期版本以稳定性优化为主","summary":"0.247仅披露稳定性与性能改进，未见可确认的重大内容转折。","impact":"产品Google回榜#60、iOS升至#30；跨端层级差异明显。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/supremacy-world-war-3/id1510997559"},
]
for n,x in enumerate(news,1): x["rank"]=n

closing=[
 {"type":"判断","title":"周末后双榜换位集中在中后段","detail":"Google 3进3出、iOS 6进6出；除Mobile Legends进入前十外，大多数回榜产品仍在#53以后。"},
 {"type":"判断","title":"跨端反向仍是主要特征","detail":"Draft Showdown与Kingdom Guard在Google/iOS之间反向进出；Tacticus则iOS +23、Google −8，不能用单一活动解释双端。"},
 {"type":"判断","title":"头部核心SLG相对稳定","detail":"Whiteout Survival仍位列双端#1；Google最大进出集中在#46以后，iOS显著波动主要位于中后段。"},
 {"type":"关注","title":"下一有效快照：核验九款榜尾回榜产品","detail":"重点观察Google三款回榜和iOS六款回榜能否连续留榜，尤其是两个商店的#58—#60。"},
 {"type":"关注","title":"未来1—2个快照：观察Tacticus与Dragon Traveler","detail":"两款iOS单日变化均超过19位；只有持续同向或掉榜，才提高趋势判断。"},
 {"type":"关注","title":"继续区分商店分类与核心策略收入口径","detail":"Mobile Legends与Wild Rift可进入官方策略分类榜，但Sensor Tower策略子集继续排除MOBA。"},
]

gh=load(f"data/history/google-play/{DATE}.json"); ih=load(f"data/history/ios/{DATE}.json"); rev=load("data/sensortower-global-strategy-revenue-latest.json")
source_date=datetime.fromisoformat(ih["sourceUpdated"].replace("Z","+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
def anchors(rows): return " · ".join(f"#{n} {rows[n-1]['gameName']}" for n in (1,25,60))

brief={
 "date":DATE,"timezone":"Asia/Shanghai","title":"Google三进三出、iOS六进六出；跨端反向换位增加",
 "summary":"较11月6日前一有效快照，Google Play三进三出，Vikings、Draft Showdown与Supremacy回榜；The Grand Mafia +8、Dragonfire +10，Duck Survival −10。iOS六进六出，Mobile Legends升至#9，Tacticus +23至#35，Dragon Traveler −19至#52。Google近90天新品2款、iOS 2款；两端缺少8月11日精确基准，不判断较老产品的90天飙升。",
 "newsMethod":"编辑热度：按时效、厂商/IP体量、双榜关联度与品类影响综合排序；不是第三方阅读量或舆情指数。",
 "iconBundle":f"assets/market-icons-{STAMP}-01.json","iconOverrideBundles":[f"assets/market-icons-{STAMP}-{i:02d}.json" for i in range(2,(len(all_cards)+4)//5+1)],
 "rankingSources":{"googlePlay":f"data/games-{STAMP}.json","ios":f"data/ios-games-{STAMP}.json"},"previousRankingSources":{"googlePlay":f"data/games-{PREV}.json","ios":f"data/ios-games-{PREV}.json"},
 "rankingDynamics":{"googlePlay":{"label":"Google Play · Android","sourceTime":f"北京时间 {gh['sourceCapturedAt']} 直连抓取","anchors":"榜单锚点："+anchors(datasets['googlePlay']['now']),"products":google_products},
                    "ios":{"label":"App Store · iPhone/iOS","sourceTime":f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ih['sourceUpdated']}）","anchors":"榜单锚点："+anchors(datasets['ios']['now']),"products":ios_products}},
 "marketNews":news,"closing":closing,"globalStrategyRevenue":rev,
 "status":{"googlePlay":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['googlePlay']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-11"},
           "ios":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['ios']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-11"}},
 "sources":[{"label":"Google Play美国区策略畅销榜直连","url":gh['sourceUrl'],"capturedAt":gh['sourceCapturedAt']},{"label":"Apple官方美国区iPhone策略畅销RSS","url":ih['sourceUrl'],"updated":ih['sourceUpdated'],"sourceDateBeijing":ih['dataDate']},{"label":"Sensor Tower全球收入榜中的策略产品","url":rev['sourceUrl'],"period":rev['period'],"estimateAsOf":rev['estimateAsOf']}],
 "downloads":{"markdown":f"reports/{DATE}.md","json":f"data/market-brief-{STAMP}.json"},
}

def markdown(v):
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{v['title']}**","",v['summary'],"","## 数据源与口径","",f"- Google Play：`{gh['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={ih['sourceUpdated']}`，对应北京时间榜单日期 `{ih['dataDate']}`",f"- Google锚点：{v['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{v['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-06；升降为相邻有效快照变化，不等于收入增减。","- 近90天：缺少2026-08-11精确同口径TOP60基准，较老产品内部pending、页面按常规展示。","","## 1. 双榜当日异动产品",""]
    for store in ("googlePlay","ios"):
        sec=v["rankingDynamics"][store]; lines += [f"### {sec['label']}","",sec["sourceTime"]+"。",""]
        for x in sec["products"]: lines += [f"#### {x['gameName']}｜{x['changeLabel']}","",x["analysis"],""]
    lines += ["## 2. 策略手游市场热点","",v["newsMethod"],""]
    for x in news: lines += [f"### {x['rank']}. [{x['title']}]({x['url']})","",f"- 类别：{x['category']}｜发布日期：{x['date']}｜来源：{x['source']}",f"- 事实摘要：{x['summary']}",f"- 市场含义：{x['impact']}",""]
    lines += ["## 3. 综合判断与后续关注",""]
    for x in closing: lines += [f"### {x['type']}｜{x['title']}","",x["detail"],""]
    lines += ["## 4. Sensor Tower 全球收入榜中的策略产品","",f"- 数据期：{rev['periodLabel']}｜估算截至：{rev['estimateAsOf']}",f"- 策略筛选：官方全球收入TOP10中命中{rev['strategyMatches']}款核心策略产品；这不是完整策略品类TOP10",f"- 原始来源：[{rev['source']}]({rev['sourceUrl']})","","| 全球总榜 | 游戏 | 发行商 | 策略类型 | 较上月榜位 | 单品收入同比 |","|---:|---|---|---|---|---|"]
    for x in rev["rankings"]: lines.append(f"| {x['rank']} | {x['gameName']} | {x['publisher']} | {x['strategyGenre']} | {x['movementLabel']} | {x['yoyRevenueLabel']} |")
    lines += ["",rev["methodologyNote"],"","## 下载与来源","",f"- JSON：`{v['downloads']['json']}`",f"- Markdown：`{v['downloads']['markdown']}`",""]
    return "\n".join(lines)

save(f"data/market-brief-{STAMP}.json",brief)
(ROOT/f"reports/{DATE}.md").write_text(markdown(brief),encoding="utf-8")
manifest=load("reports/manifest.json"); entry={"date":DATE,"title":brief["title"],"summary":brief["summary"],"markdown":brief["downloads"]["markdown"],"json":brief["downloads"]["json"]}
manifest["updated"]=DATE; manifest["reports"]=sorted([entry]+[x for x in manifest["reports"] if x["date"]!=DATE],key=lambda x:x["date"],reverse=True); save("reports/manifest.json",manifest)
print(f"Wrote {len(all_cards)} product cards, {len(news)} news items and {(len(all_cards)+4)//5} icon bundles")
