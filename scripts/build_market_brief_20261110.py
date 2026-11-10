#!/usr/bin/env python3
"""Generate the Beijing 2026-11-10 dual-store market brief and archive."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from daily_update_20260820 import data_uri

ROOT=Path(__file__).resolve().parents[1]
DATE,STAMP,PREV="2026-11-10","20261110","20261109"

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
 card("googlePlay","com.more.lastfortress.gp","entry","回榜#59。当前仅以倒数第二名重返榜单，未发现足以确认持续拉升的单一官方节点。"),
 card("googlePlay","com.seaofconquest.global","entry","回榜#60；iOS同产品本期从#59掉榜，属于跨端反向榜尾轮换。"),
 card("googlePlay","com.wb.goog.got.conquest","exit","上期#58后掉榜，而iOS同产品回榜#58；两端出现同位反向进出。"),
 card("googlePlay","com.QuestLab.DraftWar","exit","上期回榜#59后再次掉榜；Season 3运行期内仍未形成连续留榜。"),
 card("googlePlay","com.snowprintstudios.tacticus","up","上升8位至#49，而iOS反向下跌10位至#45；跨端走势继续分化。"),
 card("googlePlay","com.supercell.clashroyale","down","下跌5位至#17，仍处中前段；单日变化不足以确认长期转弱。"),
 card("googlePlay","com.topwar.gp","down","下跌5位至#48，接近后十名；需观察下一有效快照是否继续靠近掉榜线。"),
 card("googlePlay","com.plarium.vikings","down","前日回榜后下跌5位至#58，已进入榜尾风险区。"),
]

ios_products=[
 card("ios","1619254071","entry","Honor of Kings回榜#32。核心玩法为MOBA，保留官方策略分类榜位但不纳入核心策略收入子集。"),
 card("ios","6447612873","entry","Sea War: Uboat Raid回榜#57；11月9日版本时间相邻，但当前仍是后四名待验证信号。"),
 card("ios","1035712810","entry","Game of Thrones: Conquest回榜#58，而Google同产品掉榜；属于跨端反向榜尾轮换。"),
 card("ios","6740189002","entry","Galaxy Defense回榜#60。11月8日版本处于近期窗口，但当前只确认末位回补。"),
 card("ios","6479020757","exit","DC: Dark Legion上期#49后掉榜；当前仅确认iPhone端退出TOP60。"),
 card("ios","1427744264","exit","Star Trek Fleet Command上期回榜#57后再次掉榜，榜尾席位尚不稳定。"),
 card("ios","6463715971","exit","Sea of Conquest上期#59后掉榜，而Google反向回榜#60。"),
 card("ios","6776076449","exit","Plants on Fire上期#60后掉榜；11月6日版本未维持本期TOP60席位。"),
 card("ios","1570095804","up","上升25位至#33，为iOS最大上涨；Google同产品仍未回榜，先按单日待验证信号处理。"),
 card("ios","6761893238","up","上升9位至#16，进入中前段；11月6日版本时间相邻，但不作确定归因。"),
 card("ios","6476261995","up","上升9位至#47，仍处后十四名；Google同产品未入榜。"),
 card("ios","6755585789","up","Overgeared Hero上升6位至#42；Google同产品仍在榜，需继续观察双端是否同步。"),
 card("ios","6740232087","up","Aliens vs Zombies上升6位至#49，仍接近榜尾风险区。"),
 card("ios","1554247785","down","下跌10位至#44，连续两份有效快照回落；仍不足以替代更长周期判断。"),
 card("ios","1599937506","down","下跌10位至#45，而Google反向升至#49；前日大涨未延续。"),
 card("ios","1181774280","down","下跌12位至#53，已进入后八名；11月5日更新未维持前一日榜位。"),
 card("ios","852912420","down","下跌13位至#56，为本期主要回落之一；11月7日版本时间相邻但不能直接归因。"),
 card("ios","1480616990","down","下跌7位至#39；属于MOBA，保留官方分类榜位但不纳入核心策略收入子集。"),
 card("ios","6751086804","down","继续下跌7位至#59，已接近掉榜；产品仍处上线早期验证。"),
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
 {"category":"全球市场 / 收入榜","date":"2026-11-03","title":"Sensor Tower最新完整全球收入榜仍为2026年10月","summary":"官方全球App Store与Google Play收入榜仍以10月为最新期，并明确排除第三方Android市场。","impact":"策略子集继续保留10月真实统计期；未发布新期，月榜文件不改。","source":"Sensor Tower官方","url":"https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-october-2026"},
 {"category":"MOBA / 回榜","date":"2026-11-10","title":"Honor of Kings回到iOS策略分类榜#32","summary":"Apple商品页明确其核心为5v5 MOBA，由腾讯天美开发、Level Infinite发行。","impact":"该产品计入官方商店榜异动，但继续排除在核心策略收入子集之外。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/honor-of-kings/id1619254071"},
 {"category":"海战SLG / 版本","date":"2026-11-09","title":"Sea War更新后回榜iOS #57","summary":"商品页显示11月9日更新；产品以潜艇、舰船、联盟和公会对抗为核心。","impact":"版本与回榜时间相邻，但当前名次仍靠近掉榜线。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/sea-war-uboat-raid/id6447612873"},
 {"category":"塔防 / 版本","date":"2026-11-08","title":"Galaxy Defense回榜iOS末位","summary":"商品页显示11月8日更新；玩法围绕炮塔组合、升级与外星入侵防守。","impact":"回榜#60只代表末位回补，下一有效快照是留位验证点。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/galaxy-defense-fortress-td/id6740189002"},
 {"category":"塔防4X / 榜位","date":"2026-11-03","title":"Kingdom Guard单日上升25位","summary":"商品页继续以合成兵种、守护龙蛋和联盟扩张为核心描述。","impact":"iOS升至#33但Google未回榜，属于需要跨端继续核验的单日信号。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/kingdom-guard-tower-defense-td/id1570095804"},
 {"category":"军事经营 / 版本","date":"2026-11-06","title":"Top Force: Commander进入iOS中前段","summary":"11月6日版本处于近期窗口；产品以基地经营、士兵武装与前线扩张为核心。","impact":"iOS上升9位至#16，需观察能否连续保持前二十。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/top-force-commander/id6761893238"},
 {"category":"战术RPG / 活动","date":"2026-11-08","title":"Tacticus活动窗口内跨端再次反向","summary":"Fabius Bile传奇活动于11月8日开启。","impact":"本期Google +8、iOS −10，说明同一活动不能直接解释两端榜位。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/warhammer-40-000-tacticus/id1599937506"},
 {"category":"SLG / IP长线","date":"2026-10-08","title":"Age of Empires Mobile回升至iOS #47","summary":"产品延续资源采集、军事建设、联盟与大地图帝国扩张。","impact":"单日+9仍位于后十四名，Google未入榜，跨端差距需要继续观察。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/age-of-empires-mobile/id6476261995"},
 {"category":"战棋RPG / 版本","date":"2026-11-05","title":"Fire Emblem Heroes回落至榜尾区","summary":"11月5日版本加入武器精炼及兑换目录更新。","impact":"本期下跌12位至#53，近期更新未维持前一日名次。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/fire-emblem-heroes/id1181774280"},
 {"category":"长线RPG / 版本","date":"2026-11-07","title":"Summoners War更新后单日下跌13位","summary":"商品页显示11月7日更新；产品仍以回合制编队、魔灵收集和公会战争为主。","impact":"本期降至#56，当前只记为榜尾风险信号。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/summoners-war/id852912420"},
]
for n,x in enumerate(news,1): x["rank"]=n

closing=[
 {"type":"判断","title":"榜尾轮换仍高于头部变化","detail":"Google 2进2出、iOS 4进4出，所有进出产品都位于#57—#60或来自前一日榜尾。"},
 {"type":"判断","title":"跨端反向进一步增加","detail":"Game of Thrones: Conquest与Sea of Conquest在两端反向进出；Tacticus则Google +8、iOS −10。"},
 {"type":"判断","title":"iOS中后段波动扩大","detail":"Kingdom Guard +25与Summoners War −13并存，单日异动集中在#33以后，暂不等同长期趋势。"},
 {"type":"关注","title":"下一有效快照：核验六款回榜产品","detail":"重点观察Google两款和iOS四款回榜产品能否连续留榜，尤其是#57—#60。"},
 {"type":"关注","title":"未来1—2个快照：观察Kingdom Guard与Tacticus","detail":"前者iOS单日+25、后者双端反向；只有连续同向变化才提高趋势可信度。"},
 {"type":"关注","title":"继续区分官方分类与核心策略口径","detail":"Honor of Kings与Wild Rift可进入官方策略分类榜，但Sensor Tower核心策略子集继续排除MOBA。"},
]

gh=load(f"data/history/google-play/{DATE}.json"); ih=load(f"data/history/ios/{DATE}.json"); rev=load("data/sensortower-global-strategy-revenue-latest.json")
source_date=datetime.fromisoformat(ih["sourceUpdated"].replace("Z","+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
def anchors(rows): return " · ".join(f"#{n} {rows[n-1]['gameName']}" for n in (1,25,60))

brief={
 "date":DATE,"timezone":"Asia/Shanghai","title":"Google两进两出、iOS四进四出；榜尾与跨端反向轮换延续",
 "summary":"较11月9日前一有效快照，Google Play两进两出，Last Fortress与Sea of Conquest回榜；Tacticus +8，Clash Royale、Top War与Vikings均−5。iOS四进四出，Kingdom Guard +25至#33，Summoners War −13至#56；Game of Thrones: Conquest与Sea of Conquest在双端反向进出。Google近90天新品2款、iOS 1款；两端缺少8月12日精确基准，不判断较老产品的90天飙升。",
 "newsMethod":"编辑热度：按时效、厂商/IP体量、双榜关联度与品类影响综合排序；不是第三方阅读量或舆情指数。",
 "iconBundle":f"assets/market-icons-{STAMP}-01.json","iconOverrideBundles":[f"assets/market-icons-{STAMP}-{i:02d}.json" for i in range(2,(len(all_cards)+4)//5+1)],
 "rankingSources":{"googlePlay":f"data/games-{STAMP}.json","ios":f"data/ios-games-{STAMP}.json"},"previousRankingSources":{"googlePlay":f"data/games-{PREV}.json","ios":f"data/ios-games-{PREV}.json"},
 "rankingDynamics":{"googlePlay":{"label":"Google Play · Android","sourceTime":f"北京时间 {gh['sourceCapturedAt']} 直连抓取","anchors":"榜单锚点："+anchors(datasets['googlePlay']['now']),"products":google_products},
                    "ios":{"label":"App Store · iPhone/iOS","sourceTime":f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ih['sourceUpdated']}）","anchors":"榜单锚点："+anchors(datasets['ios']['now']),"products":ios_products}},
 "marketNews":news,"closing":closing,"globalStrategyRevenue":rev,
 "status":{"googlePlay":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['googlePlay']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-12"},
           "ios":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['ios']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-12"}},
 "sources":[{"label":"Google Play美国区策略畅销榜直连","url":gh['sourceUrl'],"capturedAt":gh['sourceCapturedAt']},{"label":"Apple官方美国区iPhone策略畅销RSS","url":ih['sourceUrl'],"updated":ih['sourceUpdated'],"sourceDateBeijing":ih['dataDate']},{"label":"Sensor Tower全球收入榜中的策略产品","url":rev['sourceUrl'],"period":rev['period'],"estimateAsOf":rev['estimateAsOf']}],
 "downloads":{"markdown":f"reports/{DATE}.md","json":f"data/market-brief-{STAMP}.json"},
}

def markdown(v):
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{v['title']}**","",v['summary'],"","## 数据源与口径","",f"- Google Play：`{gh['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={ih['sourceUpdated']}`，对应北京时间榜单日期 `{ih['dataDate']}`",f"- Google锚点：{v['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{v['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-09；升降为相邻有效快照变化，不等于收入增减。","- 近90天：缺少2026-08-12精确同口径TOP60基准，较老产品内部pending、页面按常规展示。","","## 1. 双榜当日异动产品",""]
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
