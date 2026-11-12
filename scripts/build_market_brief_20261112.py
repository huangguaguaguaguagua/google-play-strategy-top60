#!/usr/bin/env python3
"""Generate the Beijing 2026-11-12 dual-store market brief and archive."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from daily_update_20260820 import data_uri

ROOT=Path(__file__).resolve().parents[1]
DATE,STAMP,PREV="2026-11-12","20261112","20261111"

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
 card("googlePlay","com.wireless.defenseland","entry","进入#60。产品以英雄编队、塔位升级与连续波次为核心，当前只是末位进入信号，尚不能确认稳定留榜。"),
 card("googlePlay","leyi.westgame","exit","上期#59后掉榜；西部题材联盟SLG未能连续守住榜尾席位。"),
 card("googlePlay","com.yottagames.mafiawar","up","上升5位至#36。黑帮城建与联盟经营仍处中后段，本次仅记为单日回升。"),
 card("googlePlay","com.riotgames.league.wildrift","down","下跌8位至#30。该产品核心为MOBA，不因商店策略标签纳入核心策略收入子集。"),
 card("googlePlay","com.im30.ROE.gp","down","下跌6位至#42。冰火题材城建与联盟战争仍在中后段，下一快照用于判断是否止跌。"),
]

ios_products=[
 card("ios","6447612873","entry","回榜#36。潜艇突袭、海上基地与联盟对抗重新进入中后段，当前只确认回榜，不推断长期上升。"),
 card("ios","850057092","entry","回榜#45。长期运营的猫咪横版塔防回到中后段，未发现可确认的单一重大转折。"),
 card("ios","913292932","entry","回榜#55。城市规划与长期经营产品重返榜尾，需下一有效快照确认留位。"),
 card("ios","625257520","entry","回榜#59。卡牌产品仅以末二位进入，当前属于高掉榜风险的待验证信号。"),
 card("ios","1599937506","exit","上期#49后掉榜；战术小队养成未能守住中后段席位。"),
 card("ios","1571873795","exit","上期活动同窗回榜#53后即掉榜，说明该次回补尚未形成连续留榜。"),
 card("ios","6740232087","exit","上期#56后掉榜；上线期产品的榜尾连续性仍弱。"),
 card("ios","6450953550","exit","上期#59后掉榜；城建、英雄养成与联盟玩法未守住末位区间。"),
 card("ios","852912420","up","上升8位至#39。长期运营回合制RPG回到前40附近，仍需后续快照区分短期回补。"),
 card("ios","1592081003","up","上升6位至#34；Google同产品仍在榜，但本次未出现同幅同步信号。"),
 card("ios","1487451427","up","上升5位至#47。炼金与元素克制包装下的联盟4X回升至中后段。"),
 card("ios","1510997559","down","下跌6位至#40。现代战争大地图与联盟博弈仍在前40边缘。"),
 card("ios","1570095804","down","下跌7位至#53；Google同产品本期仍在TOP60，但未形成同步上升。"),
 card("ios","1575590830","down","下跌11位至#48。前日回榜后的名次回吐使其重新落入后十三名。"),
 card("ios","1619254071","down","下跌13位至#57。核心为MOBA且已接近掉榜线，不纳入核心策略收入子集。"),
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
 {"category":"塔防 / 新进","date":"2026-11-12","title":"Raid Rush进入Google Play #60","summary":"官方商品页以英雄编队、塔位升级、波次防守与首领战为核心。","impact":"当前是榜尾进入信号；下一有效快照决定其能否从一次性触榜转为连续留榜。","source":"Google Play美国区","url":"https://play.google.com/store/apps/details?id=com.wireless.defenseland&hl=en_US&gl=US"},
 {"category":"海战SLG / 回榜","date":"2026-11-12","title":"Sea War: Uboat Raid回榜iOS #36","summary":"商品页聚焦潜艇突袭、海上基地扩张与联盟对抗。","impact":"回榜位置高于一般末位轮换，但仍需连续快照确认稳定性。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/sea-war-uboat-raid/id6447612873"},
 {"category":"塔防 / 长线运营","date":"2026-11-12","title":"The Battle Cats回榜iOS #45","summary":"长期运营产品以猫咪编队、横版出击与关卡克制为核心。","impact":"回榜说明成熟产品仍可占据中后段，但未发现可确认的单一重大转折。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/the-battle-cats/id850057092"},
 {"category":"城市经营 / 回榜","date":"2026-11-12","title":"SimCity BuildIt回榜iOS #55","summary":"官方商品页延续城市规划、资源生产与市长竞赛等长期经营内容。","impact":"本次只确认榜尾回补，尚不足以判断长线收入重新抬升。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/simcity-buildit/id913292932"},
 {"category":"卡牌 / 回榜","date":"2026-11-12","title":"Hearthstone回榜iOS #59","summary":"成熟卡牌产品回到末二位，官方页面仍以套牌构筑与对战为主。","impact":"位置接近掉榜线，下一份有效快照是首要验证点。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/hearthstone/id625257520"},
 {"category":"卡牌 / 榜位","date":"2026-11-12","title":"MARVEL SNAP上升至iOS #34","summary":"iOS上升6位，Google端仍在TOP60但没有同幅同步上升。","impact":"暂记为iPhone端回升，不把单日名次直接归因于具体活动。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/marvel-snap-hero-card-game/id1592081003"},
 {"category":"塔防 / 榜位","date":"2026-11-12","title":"The Tower回吐11位至iOS #48","summary":"前日回榜后，本期从#37回落至#48。","impact":"仍在榜但重新进入后十三名，回榜后的连续承接能力需要复核。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/the-tower-idle-tower-defense/id1575590830"},
 {"category":"MOBA / 榜尾风险","date":"2026-11-12","title":"Honor of Kings跌至iOS #57","summary":"本期下跌13位，核心玩法为MOBA而非本报告定义的核心策略。","impact":"可作为商店榜面异动观察，但不纳入Sensor Tower核心策略子集。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/honor-of-kings/id1619254071"},
 {"category":"4X / 榜位","date":"2026-11-12","title":"Kingdom Guard下跌至iOS #53","summary":"iOS下跌7位；Google端仍在TOP60，但两端没有形成同步上行。","impact":"iPhone端已靠近榜尾，需观察跨端差异是否在下一快照收敛。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/kingdom-guard-tower-defense-td/id1570095804"},
]
for n,x in enumerate(news,1): x["rank"]=n

closing=[
 {"type":"判断","title":"Google榜面稳定，变动集中在末位","detail":"Google仅1进1出，Raid Rush与West Game都发生在#59—#60；主要波动是Wild Rift −8，但其核心为MOBA。"},
 {"type":"判断","title":"iOS轮换与下跌信号同时扩大","detail":"iOS四进四出，且The Tower与Honor of Kings分别下跌11、13位；进入产品中只有Sea War达到#36。"},
 {"type":"判断","title":"近90天新品仍少且未新增","detail":"Google继续为Age of Spirits、Last Human两款，iOS继续为Last Beacon、Age of Spirits两款；今日进入产品均非新增新品。"},
 {"type":"关注","title":"下一有效快照：核验五款进入产品","detail":"观察Raid Rush及iOS四款回榜产品能否连续留榜，尤其是#59的Hearthstone。"},
 {"type":"关注","title":"未来1—2个快照：复核iOS下跌组","detail":"若The Tower、Honor of Kings、Kingdom Guard继续下行，将从单日波动转为连续风险信号。"},
 {"type":"关注","title":"本周内：观察Sea War的回榜承接","detail":"Sea War回到#36，若能连续维持前40附近，才可区别于其此前的榜尾短暂回补。"},
]

gh=load(f"data/history/google-play/{DATE}.json"); ih=load(f"data/history/ios/{DATE}.json"); rev=load("data/sensortower-global-strategy-revenue-latest.json")
source_date=datetime.fromisoformat(ih["sourceUpdated"].replace("Z","+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
def anchors(rows): return " · ".join(f"#{n} {rows[n-1]['gameName']}" for n in (1,25,60))

brief={
 "date":DATE,"timezone":"Asia/Shanghai","title":"Google末位一进一出、iOS四进四出；中后段轮换继续",
 "summary":"较11月11日前一有效快照，Google Play一进一出，Raid Rush进入#60、West Game掉榜；Mafia City +5，Wild Rift −8。iOS四进四出，Sea War回榜#36，Summoners War +8；The Tower −11、Honor of Kings −13。Google近90天新品2款、iOS 2款；两端缺少8月14日精确基准，不判断较老产品的90天飙升。",
 "newsMethod":"编辑热度：按时效、厂商/IP体量、双榜关联度与品类影响综合排序；不是第三方阅读量或舆情指数。",
 "iconBundle":f"assets/market-icons-{STAMP}-01.json","iconOverrideBundles":[f"assets/market-icons-{STAMP}-{i:02d}.json" for i in range(2,(len(all_cards)+4)//5+1)],
 "rankingSources":{"googlePlay":f"data/games-{STAMP}.json","ios":f"data/ios-games-{STAMP}.json"},"previousRankingSources":{"googlePlay":f"data/games-{PREV}.json","ios":f"data/ios-games-{PREV}.json"},
 "rankingDynamics":{"googlePlay":{"label":"Google Play · Android","sourceTime":f"北京时间 {gh['sourceCapturedAt']} 直连抓取","anchors":"榜单锚点："+anchors(datasets['googlePlay']['now']),"products":google_products},
                    "ios":{"label":"App Store · iPhone/iOS","sourceTime":f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ih['sourceUpdated']}）","anchors":"榜单锚点："+anchors(datasets['ios']['now']),"products":ios_products}},
 "marketNews":news,"closing":closing,"globalStrategyRevenue":rev,
 "status":{"googlePlay":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['googlePlay']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-14"},
           "ios":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['ios']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-14"}},
 "sources":[{"label":"Google Play美国区策略畅销榜直连","url":gh['sourceUrl'],"capturedAt":gh['sourceCapturedAt']},{"label":"Apple官方美国区iPhone策略畅销RSS","url":ih['sourceUrl'],"updated":ih['sourceUpdated'],"sourceDateBeijing":ih['dataDate']},{"label":"Sensor Tower全球收入榜中的策略产品","url":rev['sourceUrl'],"period":rev['period'],"estimateAsOf":rev['estimateAsOf']}],
 "downloads":{"markdown":f"reports/{DATE}.md","json":f"data/market-brief-{STAMP}.json"},
}

def markdown(v):
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{v['title']}**","",v['summary'],"","## 数据源与口径","",f"- Google Play：`{gh['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={ih['sourceUpdated']}`，对应北京时间榜单日期 `{ih['dataDate']}`",f"- Google锚点：{v['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{v['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-11；升降为相邻有效快照变化，不等于收入增减。","- 近90天：缺少2026-08-14精确同口径TOP60基准，较老产品内部pending、页面按常规展示。","","## 1. 双榜当日异动产品",""]
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
