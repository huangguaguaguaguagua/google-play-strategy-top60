#!/usr/bin/env python3
"""Generate the Beijing 2026-11-17 dual-store market brief and archive."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from daily_update_20260820 import data_uri

ROOT=Path(__file__).resolve().parents[1]
DATE,STAMP,PREV="2026-11-17","20261117","20261116"

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
 card("googlePlay","com.YoStarEN.Arknights","entry","回榜#45。官方11月12日开启《Monster Hunter》联动支线，活动时间与回榜相邻；当前只能记为待验证信号，不能据此确认单一因果。"),
 card("googlePlay","com.wb.goog.got.conquest","entry","回榜#60。权游IP城堡经营与联盟战争以末位重返，11月Highgarden Harvest Festival正在进行，但留榜稳定性仍弱。"),
 card("googlePlay","leyi.ageofspirits","exit","前一快照#56后掉榜。该近90天新品未守住Google末五位；其官方ICON此前已通过逐产品核验。"),
 card("googlePlay","com.farlightgames.samo.gp","exit","前一快照#60回榜后即掉榜；奇幻自由行军与联盟4X的榜尾承接未形成连续性。"),
 card("googlePlay","com.gtarcade.ioe.global","up","单日上升10位至#30。官方3.0.1版本新增联盟商店、联盟奖励改版、护送/拦截事件与平衡调整，节点相邻但仍需下一快照确认持续性。"),
 card("googlePlay","com.a3.topgirl.gplay","up","单日上升5位至#29。角色经营与联盟战争回到前30边缘，暂无可确认的单一活动原因。"),
 card("googlePlay","com.diandian.gog","up","单日上升5位至#40。成熟火枪题材城建SLG改善至中后段，商品页11月13日更新与名次变化相邻。"),
 card("googlePlay","com.lavalabs.autodrill","down","单日下跌6位至#47。仍在近90天新品观察期，自动采矿与银河扩张产品已落入后十四名。"),
 card("googlePlay","com.funplus.kingofavalon","down","单日下跌5位至#42。成熟亚瑟王题材联盟SLG回落至中后段，当前仅视为单日波动。"),
 card("googlePlay","com.avenue.zombie.gp","down","单日下跌4位至#50。该近90天新品仍在榜，但已触及后十名，需观察首发获量后的付费承接。"),
]

ios_products=[
 card("ios","1464872022","entry","回榜#31。官方《Monster Hunter》联动支线已开放，活动时间与双端回榜相邻；Google同产品位于#45。"),
 card("ios","1181774280","entry","回榜#33。Nintendo官方11月5日公布10.11.0更新，本期回到榜单中段，仍需后续快照判断活动承接。"),
 card("ios","1035712810","entry","回榜#46。Highgarden Harvest Festival正在进行，Google同产品也回榜#60，但iOS仍处后十五名。"),
 card("ios","1274354704","entry","回榜#49。火枪题材城建与联盟战争重返后十二名；Google同产品同步上升至#40。"),
 card("ios","1427744264","exit","前一快照#47回榜后掉榜；Google同产品仍位于#16，双端位置再次分化。"),
 card("ios","6463715971","exit","前一快照#54回榜后掉榜；Google端同产品也未入榜，海盗舰队SLG未形成连续留榜。"),
 card("ios","6755173751","exit","前一快照#57后掉榜。近90天塔防新品的榜尾承接继续转弱。"),
 card("ios","1575590830","exit","前一快照#58后掉榜。放置塔防连续回落后离开TOP60，短期风险信号得到延续。"),
 card("ios","1487451427","up","单日上升21位至#30，为iOS最大涨幅。官方3.0.1联盟系统改版与名次上升相邻，但不能仅凭一日确认版本效果。"),
 card("ios","6761893238","up","单日上升11位至#16。现代军事经营产品进入前20，Google端未有同名产品可直接对照。"),
 card("ios","921022358","up","单日上升11位至#17。星战IP小队收集与回合战斗改善至前20，原因仍待官方节点和后续名次交叉验证。"),
 card("ios","6447612873","up","单日从#60回升10位至#50。潜艇突袭产品暂时脱离末位，但仍在后十一名。"),
 card("ios","852912420","down","单日下跌16位至#53，为iOS最大跌幅。成熟回合养成产品落入后八名，下一快照观察是否继续承压。"),
 card("ios","1599937506","down","单日下跌15位至#44。昨日回榜#29后明显回吐，说明高位回榜尚未稳定。"),
 card("ios","6444112366","down","单日下跌14位至#59。Google仍位于#23，跨端差距扩大至36位。"),
 card("ios","1592081003","down","单日下跌14位至#60。卡牌产品落到末位，Google端仍在#58，两端均接近掉榜线。"),
 card("ios","6751086804","down","单日下跌10位至#58。昨日回榜#48后回吐至末三位，属于明显的榜尾风险。"),
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
 {"category":"IP联动 / 塔防","date":"2026-11-12","title":"Arknights × Monster Hunter联动支线开放","summary":"Arknights官方站显示Thunder in the Azure Dream联动支线已开放，商品继续以干员编队、部署与塔防关卡为核心。","impact":"产品今日同时回到Google #45与iOS #31；活动窗口与榜位相邻，但仍需下一快照验证持续性。","source":"Arknights官方","url":"https://arknights.global/"},
 {"category":"联盟4X / 版本","date":"2026-11-06","title":"Infinity Kingdom 3.0.1重做联盟奖励体系","summary":"官方版本公告加入联盟商店、联盟战争点数、护送与拦截事件，并调整Immortal平衡。","impact":"产品今日Google +10至#30、iOS +21至#30，形成清晰双端同向信号；单日变化仍不能直接等同版本增收。","source":"Infinity Kingdom官方","url":"https://infinitykingdom.gtarcade.com/en/news"},
 {"category":"IP长线运营","date":"2026-11-03","title":"Game of Thrones: Conquest开启Highgarden Harvest Festival","summary":"官方11月预告公布Rose of the South装备、Hotpie与Mace Tyrell英雄及Terror of the Tundra龙装。","impact":"产品今日Google #60、iOS #46双端回榜；活动节点可核验，但末位Google排名仍有较高掉榜风险。","source":"Game of Thrones: Conquest官方","url":"https://www.gotconquest.com/news/2026/11/03/november-preview-highgarden-harvest-festival-6/"},
 {"category":"角色策略 / 版本","date":"2026-11-05","title":"Fire Emblem Heroes发布10.11.0更新说明","summary":"Nintendo官方更新页公布11月版本内容与后续数据支持，产品核心仍为跨作品英雄召唤与回合战斗。","impact":"今日iOS回榜#33，位置高于普通榜尾轮换；需要观察更新窗口结束后能否留榜。","source":"Fire Emblem Heroes官方","url":"https://fire-emblem-heroes.com/?locale=en-US"},
 {"category":"双端异动 / 火枪SLG","date":"2026-11-13","title":"Guns of Glory双端同步改善","summary":"Google Play商品页显示11月13日更新；产品今日Google +5至#40、iOS回榜#49。","impact":"双端同向比单端触榜更值得观察，但公开版本资料不足以确认具体功能是排名变化原因。","source":"Google Play美国区","url":"https://play.google.com/store/apps/details?id=com.diandian.gog&hl=en_US&gl=US"},
 {"category":"现代军事 / 榜位","date":"2026-11-17","title":"Top Force: Commander升至iOS #16","summary":"产品单日上升11位，以现代军事基地、英雄编队和联盟对抗为主要商店表达。","impact":"进入前20是本期iOS主要上涨信号之一；Google没有同名同口径榜位用于交叉验证。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/id6761893238"},
 {"category":"IP小队 / 榜位","date":"2026-11-17","title":"Star Wars: Galaxy of Heroes升至iOS #17","summary":"产品单日上升11位，围绕星战角色收集、小队编成与回合战斗长期运营。","impact":"名次进入前20，但尚未找到与当日位移直接对应的官方重大节点，因此只记录为待验证信号。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/id921022358"},
 {"category":"成熟产品 / 下跌","date":"2026-11-17","title":"Summoners War单日下跌16位至iOS #53","summary":"成熟回合养成产品从#37回落至后八名，是今日iOS最大跌幅。","impact":"若下一快照继续下行或掉榜，才升级为连续风险；单日下降不能直接解释为活动结束。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/id852912420"},
 {"category":"跨端分化 / 剧情养成","date":"2026-11-17","title":"Limbus Company iOS跌至#59、Google仍为#23","summary":"iOS单日下降14位，Google端仅小幅波动并保持前25。","impact":"36位跨端差距进一步说明榜位、素材和运营判断不能跨商店混用。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/id6444112366"},
]
for n,x in enumerate(news,1): x["rank"]=n

closing=[
 {"type":"判断","title":"Google相对稳定，iOS中后段继续快速轮换","detail":"Google仅2进2出，iOS为4进4出；变化主要集中在iOS #30以后，说明当天波动更多来自中后段与榜尾席位。"},
 {"type":"判断","title":"Infinity Kingdom是当天最清晰的双端同向信号","detail":"Google +10、iOS +21且两端都到#30，官方3.0.1联盟系统改版时间相邻；仍需至少下一份快照确认不是短时活动峰值。"},
 {"type":"判断","title":"IP活动带来双端回榜，但稳定性差异明显","detail":"Arknights回到Google #45/iOS #31，GOT Conquest回到#60/#46；前者位置更稳，后者Google末位仍有明显掉榜风险。"},
 {"type":"关注","title":"下一快照：核验八款进入/掉榜产品","detail":"重点看Arknights与Fire Emblem能否留在中段、GOT Conquest能否离开Google #60，以及昨日回榜后掉出的Star Trek与Sea of Conquest是否再次反复。"},
 {"type":"关注","title":"未来1—2个快照：观察iOS末位下跌组","detail":"Limbus #59、MARVEL SNAP #60、Dragon Traveler #58均出现双位数下跌；若继续掉榜，才确认连续风险。"},
 {"type":"关注","title":"本周内：验证Infinity Kingdom版本信号","detail":"若两端能持续保持#30附近或继续上升，可再结合联盟事件参与度与后续官方公告判断3.0.1的承接；否则按短期峰值处理。"},
]

gh=load(f"data/history/google-play/{DATE}.json"); ih=load(f"data/history/ios/{DATE}.json"); rev=load("data/sensortower-global-strategy-revenue-latest.json")
source_date=datetime.fromisoformat(ih["sourceUpdated"].replace("Z","+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
def anchors(rows): return " · ".join(f"#{n} {rows[n-1]['gameName']}" for n in (1,25,60))

brief={
 "date":DATE,"timezone":"Asia/Shanghai","title":"Google二进二出、iOS四进四出；Infinity Kingdom双端同步升至#30",
 "summary":"较11月16日有效快照，Google Play二进二出，Arknights与GOT Conquest回榜，Infinity Kingdom +10；iOS四进四出，Infinity Kingdom +21、Top Force与Star Wars均+11，Summoners War −16。Google近90天新品1款、iOS 1款；两端缺少8月19日精确基准，不判断较老产品的90天飙升。",
 "newsMethod":"编辑热度：按时效、厂商/IP体量、双榜关联度与品类影响综合排序；不是第三方阅读量或舆情指数。",
 "iconBundle":f"assets/market-icons-{STAMP}-01.json","iconOverrideBundles":[f"assets/market-icons-{STAMP}-{i:02d}.json" for i in range(2,(len(all_cards)+4)//5+1)],
 "rankingSources":{"googlePlay":f"data/games-{STAMP}.json","ios":f"data/ios-games-{STAMP}.json"},"previousRankingSources":{"googlePlay":f"data/games-{PREV}.json","ios":f"data/ios-games-{PREV}.json"},
 "rankingDynamics":{"googlePlay":{"label":"Google Play · Android","sourceTime":f"北京时间 {gh['sourceCapturedAt']} 直连抓取","anchors":"榜单锚点："+anchors(datasets['googlePlay']['now']),"products":google_products},
                    "ios":{"label":"App Store · iPhone/iOS","sourceTime":f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ih['sourceUpdated']}）","anchors":"榜单锚点："+anchors(datasets['ios']['now']),"products":ios_products}},
 "marketNews":news,"closing":closing,"globalStrategyRevenue":rev,
 "status":{"googlePlay":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['googlePlay']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-19"},
           "ios":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['ios']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-19"}},
 "sources":[{"label":"Google Play美国区策略畅销榜直连","url":gh['sourceUrl'],"capturedAt":gh['sourceCapturedAt']},{"label":"Apple官方美国区iPhone策略畅销RSS","url":ih['sourceUrl'],"updated":ih['sourceUpdated'],"sourceDateBeijing":ih['dataDate']},{"label":"Sensor Tower全球收入榜中的策略产品","url":rev['sourceUrl'],"period":rev['period'],"estimateAsOf":rev['estimateAsOf']}],
 "downloads":{"markdown":f"reports/{DATE}.md","json":f"data/market-brief-{STAMP}.json"},
}

def markdown(v):
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{v['title']}**","",v['summary'],"","## 数据源与口径","",f"- Google Play：`{gh['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={ih['sourceUpdated']}`，对应北京时间榜单日期 `{ih['dataDate']}`",f"- Google锚点：{v['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{v['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-16；本期为相邻有效快照，只记录单日榜面信号，不等于长期趋势或收入增减。","- 近90天：缺少2026-08-19精确同口径TOP60基准，较老产品内部pending、页面按常规展示。","","## 1. 双榜当日异动产品",""]
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
