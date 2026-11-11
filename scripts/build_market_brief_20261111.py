#!/usr/bin/env python3
"""Generate the Beijing 2026-11-11 dual-store market brief and archive."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from daily_update_20260820 import data_uri

ROOT=Path(__file__).resolve().parents[1]
DATE,STAMP,PREV="2026-11-11","20261111","20261110"

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
 card("googlePlay","com.tap4fun.odin.kingdomguard","entry","回榜#60。iOS同产品本期下跌13位至#46，双端没有形成同步拉升。"),
 card("googlePlay","com.more.lastfortress.gp","exit","上期回榜#59后立即掉榜，属于未能连续留位的榜尾轮换。"),
 card("googlePlay","com.yottagames.mafiawar","down","下跌5位至#41，仍在中后段；单日变化不足以确认长期转弱。"),
 card("googlePlay","com.nvsgames.snap","down","下跌10位至#53，而iOS同产品反向上升10位至#40。"),
]

ios_products=[
 card("ios","1575590830","entry","The Tower回榜#37。当前只确认中后段回补，未发现足以确认持续拉升的单一官方节点。"),
 card("ios","6755173751","entry","Evo Defense回榜#41；作为上线期产品，仍需下一有效快照确认留榜。"),
 card("ios","1571873795","entry","Blue Archive回榜#53。11月10日200次免费招募、Fest选择券与新主线同窗开启，但不据此断言单一因果。"),
 card("ios","6761043541","entry","Last Beacon首次进入#60；9月19日上架，按Apple releaseDate确认为近90天新品。"),
 card("ios","1181774280","exit","Fire Emblem Heroes上期#53后掉榜；11月5日版本未维持TOP60席位。"),
 card("ios","6447612873","exit","Sea War上期回榜#57后再次掉榜，榜尾留位尚不稳定。"),
 card("ios","6751086804","exit","Dragon Traveler上期已跌至#59，本期掉榜；上线期留榜连续性仍弱。"),
 card("ios","6740189002","exit","Galaxy Defense上期回榜#60后立即掉榜，符合末位轮换而非持续上行。"),
 card("ios","1035712810","up","上升16位至#42，为iOS最大上涨；Google同产品仍未回榜。"),
 card("ios","6446389130","up","上升13位至#30，进入中段；需观察下一有效快照能否守住前30附近。"),
 card("ios","1592081003","up","上升10位至#40，而Google同产品反向下跌10位至#53。"),
 card("ios","852912420","up","上升9位至#47，从前日榜尾回升，但仍处后十四名。"),
 card("ios","6476261995","down","下跌8位至#55，再次靠近掉榜线；Google同产品未入榜。"),
 card("ios","6805006706","down","Age of Spirits下跌11位至#57；仍属近90天新品，现已进入榜尾风险区。"),
 card("ios","1619254071","down","Honor of Kings下跌12位至#44；核心为MOBA，不纳入核心策略收入子集。"),
 card("ios","1570095804","down","前日大涨后下跌13位至#46，Google同产品则回榜#60。"),
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
 {"category":"二次元战术RPG / 活动","date":"2026-11-10","title":"Blue Archive开启免费招募与Fest选择券","summary":"Apple版本说明列出200次免费招募、Fest学生选择券、泳装角色Pick-Up与新主线。","impact":"活动与回榜#53时间相邻，但只记为待验证的活动峰值信号。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/blue-archive-free-fest-choice/id1571873795"},
 {"category":"海洋生存SLG / 新品","date":"2026-09-19","title":"Last Beacon首次进入iOS TOP60","summary":"官方商品页以漂浮庇护所、资源生产、舰队探索、联盟与海域争夺为核心。","impact":"按releaseDate确认为近90天新品；当前仅位于#60，仍需验证留榜。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/last-beacon-survival/id6761043541"},
 {"category":"塔防 / 回榜","date":"2026-11-11","title":"The Tower回榜iOS #37","summary":"商品页继续以持续升级塔体、技能与波次防守为核心。","impact":"名次高于一般榜尾回补，但尚无单一官方节点可解释持续性。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/the-tower-idle-tower-defense/id1575590830"},
 {"category":"塔防 / 上线期","date":"2026-11-11","title":"Evo Defense回榜iOS #41","summary":"商品页呈现塔防布阵、英雄养成与波次防守，产品仍处上线期。","impact":"回榜不等于趋势确立；下一份有效快照是留榜验证点。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/evo-defense/id6755173751"},
 {"category":"卡牌 / 跨端","date":"2026-11-11","title":"MARVEL SNAP双端反向10位","summary":"iOS升至#40，Google降至#53；两端同日幅度相同但方向相反。","impact":"单一版本或活动不能直接解释双端表现，需要继续积累快照。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/marvel-snap-hero-card-game/id1592081003"},
 {"category":"IP SLG / 榜位","date":"2026-11-11","title":"Game of Thrones: Conquest上升16位","summary":"iOS升至#42，而Google仍未回榜。","impact":"当前更像iPhone端单日峰值，跨端一致性仍不足。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/game-of-thrones-conquest/id1035712810"},
 {"category":"4X / 跨端","date":"2026-11-11","title":"Kingdom Guard跨端一进一跌","summary":"Google回榜#60，iOS则从#33跌至#46。","impact":"两端未形成同步上行，Google末位回榜仍是高风险席位。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/kingdom-guard-tower-defense-td/id1570095804"},
 {"category":"SLG / 榜尾风险","date":"2026-11-11","title":"Age of Empires Mobile跌至iOS #55","summary":"产品延续资源建设、联盟与大地图扩张，本期下跌8位。","impact":"Google未入榜且iOS接近掉榜线，短期留位需要继续观察。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/age-of-empires-mobile/id6476261995"},
 {"category":"新品 / 榜尾风险","date":"2026-11-11","title":"Age of Spirits回落至iOS #57","summary":"9月15日上架的新品本期下跌11位；Google同产品位于#45。","impact":"仍按近90天新品展示，但iOS已进入榜尾风险区。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/age-of-spirits/id6805006706"},
]
for n,x in enumerate(news,1): x["rank"]=n

closing=[
 {"type":"判断","title":"Google稳定、iOS中后段波动扩大","detail":"Google仅1进1出且进出位于#59—#60；iOS四进四出，并出现+16与−13的中后段异动。"},
 {"type":"判断","title":"跨端反向仍是主要信号","detail":"MARVEL SNAP两端同幅反向10位；Kingdom Guard则Google回榜、iOS大幅回落，尚无同步趋势。"},
 {"type":"判断","title":"活动与新品信号需要分开验证","detail":"Blue Archive活动同窗回榜，Last Beacon则按releaseDate确认为近90天新品；两者都不能由单日名次外推长期表现。"},
 {"type":"关注","title":"下一有效快照：核验五款进入产品","detail":"重点观察Google末位Kingdom Guard及iOS四款进入产品能否连续留榜。"},
 {"type":"关注","title":"未来1—2个快照：观察双端反向是否收敛","detail":"若MARVEL SNAP或Kingdom Guard恢复同向，当前更接近短期平台差异；若持续反向，再提高分端判断权重。"},
 {"type":"关注","title":"11月16日后复核Blue Archive","detail":"200次免费招募第一阶段于11月16日结束；届时榜位是否回落可帮助判断活动峰值强度。"},
]

gh=load(f"data/history/google-play/{DATE}.json"); ih=load(f"data/history/ios/{DATE}.json"); rev=load("data/sensortower-global-strategy-revenue-latest.json")
source_date=datetime.fromisoformat(ih["sourceUpdated"].replace("Z","+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
def anchors(rows): return " · ".join(f"#{n} {rows[n-1]['gameName']}" for n in (1,25,60))

brief={
 "date":DATE,"timezone":"Asia/Shanghai","title":"Google一进一出、iOS四进四出；新品与跨端反向并存",
 "summary":"较11月10日前一有效快照，Google Play一进一出，Kingdom Guard回榜#60、Last Fortress掉榜；MARVEL SNAP下跌10位至#53。iOS四进四出，Game of Thrones: Conquest +16、Kingdom Guard −13；Blue Archive回榜，近90天新品Last Beacon首次进入#60。Google近90天新品2款、iOS 2款；两端缺少8月13日精确基准，不判断较老产品的90天飙升。",
 "newsMethod":"编辑热度：按时效、厂商/IP体量、双榜关联度与品类影响综合排序；不是第三方阅读量或舆情指数。",
 "iconBundle":f"assets/market-icons-{STAMP}-01.json","iconOverrideBundles":[f"assets/market-icons-{STAMP}-{i:02d}.json" for i in range(2,(len(all_cards)+4)//5+1)],
 "rankingSources":{"googlePlay":f"data/games-{STAMP}.json","ios":f"data/ios-games-{STAMP}.json"},"previousRankingSources":{"googlePlay":f"data/games-{PREV}.json","ios":f"data/ios-games-{PREV}.json"},
 "rankingDynamics":{"googlePlay":{"label":"Google Play · Android","sourceTime":f"北京时间 {gh['sourceCapturedAt']} 直连抓取","anchors":"榜单锚点："+anchors(datasets['googlePlay']['now']),"products":google_products},
                    "ios":{"label":"App Store · iPhone/iOS","sourceTime":f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ih['sourceUpdated']}）","anchors":"榜单锚点："+anchors(datasets['ios']['now']),"products":ios_products}},
 "marketNews":news,"closing":closing,"globalStrategyRevenue":rev,
 "status":{"googlePlay":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['googlePlay']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-13"},
           "ios":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['ios']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-13"}},
 "sources":[{"label":"Google Play美国区策略畅销榜直连","url":gh['sourceUrl'],"capturedAt":gh['sourceCapturedAt']},{"label":"Apple官方美国区iPhone策略畅销RSS","url":ih['sourceUrl'],"updated":ih['sourceUpdated'],"sourceDateBeijing":ih['dataDate']},{"label":"Sensor Tower全球收入榜中的策略产品","url":rev['sourceUrl'],"period":rev['period'],"estimateAsOf":rev['estimateAsOf']}],
 "downloads":{"markdown":f"reports/{DATE}.md","json":f"data/market-brief-{STAMP}.json"},
}

def markdown(v):
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{v['title']}**","",v['summary'],"","## 数据源与口径","",f"- Google Play：`{gh['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={ih['sourceUpdated']}`，对应北京时间榜单日期 `{ih['dataDate']}`",f"- Google锚点：{v['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{v['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-10；升降为相邻有效快照变化，不等于收入增减。","- 近90天：缺少2026-08-13精确同口径TOP60基准，较老产品内部pending、页面按常规展示。","","## 1. 双榜当日异动产品",""]
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
