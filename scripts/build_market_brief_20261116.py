#!/usr/bin/env python3
"""Generate the Beijing 2026-11-16 dual-store market brief and archive."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from daily_update_20260820 import data_uri

ROOT=Path(__file__).resolve().parents[1]
DATE,STAMP,PREV="2026-11-16","20261116","20261112"

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
 card("googlePlay","com.ProjectMoon.LimbusCompany","entry","进入#23，是本期Google新进产品中位置最高的一款；其回合制身份养成与剧情运营是否能持续承接付费，仍需后续有效快照确认。"),
 card("googlePlay","com.more.lastfortress.gp","entry","回榜#53。地下避难所经营与联盟战争重新触及TOP60，但仍处后八名，当前只记为回榜信号。"),
 card("googlePlay","com.bw.ud.googleplay","entry","回榜#55。潜艇突袭、海上基地和联盟对抗回到榜尾区，暂不能据此断言活动带动。"),
 card("googlePlay","com.igg.android.doomsdaylastsurvivors","entry","回榜#57。僵尸生存城建与联盟SLG重新进入末四位，掉榜风险仍高。"),
 card("googlePlay","com.farlightgames.samo.gp","entry","进入#60。大地图自由行军与联盟作战产品以末位回榜，下一份有效快照决定能否留榜。"),
 card("googlePlay","com.doradogames.conflictnations.worldwar3","exit","前一有效快照#54后掉榜；现代战争大地图产品未守住榜尾。"),
 card("googlePlay","com.YoStarEN.Arknights","exit","前一有效快照#55后掉榜；塔防与角色养成产品本期离开TOP60。"),
 card("googlePlay","com.seaofconquest.global","exit","前一有效快照#57后掉榜；海盗舰队与联盟海战产品未连续守位。"),
 card("googlePlay","com.tap4fun.odin.kingdomguard","exit","前一有效快照#58后掉榜；合成塔防获量层与联盟4X的榜尾承接暂时中断。"),
 card("googlePlay","com.plarium.vikings","exit","前一有效快照#59后掉榜；成熟联盟SLG未守住末二位。"),
 card("googlePlay","com.scopely.startrek","up","较前一有效快照上升10位至#15。IP舰队经营进入前15，是Google端最明显的正向位移，但跨周末变化不等同单日活动峰值。"),
 card("googlePlay","com.riotgames.league.wildrift","down","较前一有效快照下跌13位至#43。其核心为MOBA，本次仅作为商店策略分类榜面异动观察。"),
 card("googlePlay","com.a3.topgirl.gplay","down","较前一有效快照下跌11位至#34。角色经营与联盟战争仍在中段，需观察是否继续回吐。"),
 card("googlePlay","com.sivona.stormshot.e","down","较前一有效快照下跌11位至#51。弹道解谜获量层与联盟SLG已落入后十名。"),
 card("googlePlay","leyi.ageofspirits","down","较前一有效快照下跌9位至#56。该产品仍属近90天新品，但已进入末五位；完整Google官方ICON核验通过。"),
 card("googlePlay","com.lilithgame.roc.gp","up","较前一有效快照上升5位至#17。自由行军与联盟会战产品回到前20，但跨周末位移仍视为待验证信号。"),
]

ios_products=[
 card("ios","6772922295","entry","新品进入#20。11月11日上架的《Transformers: Eternal War》以变形金刚IP、战术小队与方舟设施经营切入，目前仍处首发验证。"),
 card("ios","1599937506","entry","回榜#29。战锤40K小队战术养成回到前30附近，是本期iOS较高位回榜信号。"),
 card("ios","6741674823","entry","回榜#35。英雄编队、塔防与Boss战产品重新进入中段，尚无证据将回榜归因于特定活动。"),
 card("ios","6444112366","entry","回榜#45。回合制身份养成与剧情运营回到中后段，且Google同产品本期进入#23，形成双端同步在榜。"),
 card("ios","1427744264","entry","回榜#47。IP舰队经营与联盟作战重返后段；Google同产品已升至#15，跨端差距达32位。"),
 card("ios","6751086804","entry","回榜#48。轻量角色养成产品回到后十三名，当前只确认触榜。"),
 card("ios","6463715971","entry","回榜#54。海盗舰队与联盟海战在iOS进入榜尾，而Google同产品本期掉榜，出现跨端分化。"),
 card("ios","1611722542","entry","回榜#55。中世纪塔防与城建产品进入末六位，下一快照核验留榜。"),
 card("ios","6740232087","entry","回榜#56。上线期僵尸塔防产品再次触及榜尾，仍处留存与付费承接验证。"),
 card("ios","1035712810","exit","前一有效快照#44后掉榜；权游IP城堡与联盟战争产品离开TOP60。"),
 card("ios","1554247785","exit","前一有效快照#50后掉榜；成熟卡牌对战产品未守住后段。"),
 card("ios","1342290011","exit","前一有效快照#52后掉榜；末日城建联盟SLG的榜尾席位中断。"),
 card("ios","1570095804","exit","前一有效快照#53后掉榜；合成塔防与联盟4X产品离榜，Google端也同期掉榜。"),
 card("ios","913292932","exit","前一有效快照#55后掉榜；城市经营产品上期回榜未形成连续留榜。"),
 card("ios","6761043541","exit","前一有效快照#56后掉榜；近90天新品的榜尾承接仍不稳定。"),
 card("ios","1619254071","exit","前一有效快照#57后掉榜；核心为MOBA，不纳入核心策略收入子集。"),
 card("ios","625257520","exit","前一有效快照#59后掉榜；成熟卡牌产品上期末二位回补未延续。"),
 card("ios","6805006706","exit","前一有效快照#60后掉榜；近90天新品《Age of Spirits》iOS离榜，但Google仍在#56。"),
 card("ios","1330123889","up","较前一有效快照上升12位至#9。战术竞技产品进入前十，核心并非本报告定义的核心策略。"),
 card("ios","6476261995","up","较前一有效快照上升12位至#42。帝国经营与联盟战重新回到中后段，仍需连续快照确认。"),
 card("ios","1592081003","down","较前一有效快照下跌12位至#46。快节奏卡牌产品落入后十五名，Google端同期在#58。"),
 card("ios","6447612873","down","较前一有效快照下跌24位至#60。上期回榜#36后回吐至末位，是本期最显著的榜尾风险。"),
 card("ios","6755173751","down","较前一有效快照下跌19位至#57。新近塔防产品已进入末四位，当前只标记连续性风险。"),
 card("ios","1575590830","down","较前一有效快照下跌10位至#58。放置塔防连续两期回吐，已接近掉榜线。"),
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
 {"category":"IP新品 / 首发","date":"2026-11-11","title":"Transformers: Eternal War上架并进入iOS #20","summary":"Apple官方资料显示产品以变形金刚IP、战术小队、方舟设施经营和离线成长为核心；游戏由Hoolai Game Limited发行。","impact":"上架五天即进入前20，是本期最需要跟踪的新品信号，但仍处首发验证。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/transformers-eternal-war/id6772922295"},
 {"category":"公司归属 / 新品","date":"2026-11-16","title":"Hoolai发行主体纳入互爱互动/儒意电影娱乐体系","summary":"公司文件显示Hoolai Game Limited与互爱互动均为儒意电影娱乐100%持有的游戏发行主体；胡莱官网记录品牌沿革。","impact":"榜单公司字段按发行主体到最终集团记录，不把英文店铺名直接音译。","source":"儒意电影娱乐2026年半年报","url":"https://static.cninfo.com.cn/finalpage/2026-08-26/1225504733.PDF"},
 {"category":"战术养成 / 回榜","date":"2026-11-16","title":"Warhammer 40,000: Tacticus回榜iOS #29","summary":"官方商品页聚焦战锤40K小队收集、回合战术和公会协作。","impact":"回到前30附近，位置明显高于一般榜尾轮换，但仍需下一快照确认。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/warhammer-40-000-tacticus/id1599937506"},
 {"category":"塔防 / 回榜","date":"2026-11-16","title":"Watcher of Realms回榜iOS #35","summary":"官方页面以英雄编队、塔防部署和Boss挑战为核心。","impact":"进入榜单中段，当前没有足够证据将回榜归因于单一版本或活动。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/watcher-of-realms-us/id6741674823"},
 {"category":"双端异动 / 剧情养成","date":"2026-11-16","title":"Limbus Company双端同步进入TOP60","summary":"Google进入#23、iOS回榜#45，官方资料仍以身份编队、回合战斗和持续剧情为主。","impact":"双端同时在榜比单端触榜更值得复核，但跨端位置仍相差22位。","source":"Google Play美国区","url":"https://play.google.com/store/apps/details?id=com.ProjectMoon.LimbusCompany&hl=en_US&gl=US"},
 {"category":"IP策略 / 跨端差异","date":"2026-11-16","title":"Star Trek Fleet Command Google升至#15、iOS回榜#47","summary":"官方页面围绕星际基地、舰队养成与联盟冲突；两端都在榜，但名次相差32位。","impact":"Google端上升与iOS端回榜构成同向信号，仍不能仅凭跨周末快照断言活动峰值。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/star-trek-fleet-command/id1427744264"},
 {"category":"4X / 榜尾回补","date":"2026-11-16","title":"Call of Dragons回到Google #60","summary":"官方商品页强调奇幻大地图、自由行军、英雄与联盟战争。","impact":"目前仅为末位回榜，连续留榜是首要验证条件。","source":"Google Play美国区","url":"https://play.google.com/store/apps/details?id=com.farlightgames.samo.gp&hl=en_US&gl=US"},
 {"category":"战术竞技 / 前十","date":"2026-11-16","title":"PUBG MOBILE上升至iOS #9","summary":"较11月12日前一有效快照上升12位，进入前十。","impact":"这是iOS高位显著异动，但核心为战术竞技，不纳入核心策略收入子集。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/pubg-mobile/id1330123889"},
 {"category":"帝国经营 / 榜位","date":"2026-11-16","title":"Age of Empires Mobile上升至iOS #42","summary":"官方页面以帝国建设、英雄编队和联盟战争为核心，本期较前一有效快照上升12位。","impact":"产品回到中后段，下一快照用于区分跨周末回补与持续上升。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/age-of-empires-mobile/id6476261995"},
 {"category":"海战SLG / 跨端分化","date":"2026-11-16","title":"Sea of Conquest iOS回榜#54、Google掉榜","summary":"海盗舰队与联盟海战产品在两端出现相反结果。","impact":"跨端分化提示不能互用排名或素材结论，后续分别按商店追踪。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/sea-of-conquest-pirate-war/id6463715971"},
]
for n,x in enumerate(news,1): x["rank"]=n

closing=[
 {"type":"判断","title":"跨周末轮换显著扩大，不能当作单日变化","detail":"相对11月12日前一有效快照，Google五进五出、iOS九进九出；11月13日缺少有效快照，因此这些位移覆盖多个自然日。"},
 {"type":"判断","title":"Transformers是本期最强新品信号","detail":"11月11日上架后进入iOS #20，明显高于一般榜尾触榜；但上线时间短，当前结论仍是首发验证。"},
 {"type":"判断","title":"双端同品差异仍大","detail":"Star Trek为Google #15/iOS #47，Limbus为#23/#45；Sea of Conquest则iOS回榜、Google掉榜，榜单与素材必须继续按商店隔离。"},
 {"type":"关注","title":"下一有效快照：核验全部14款进入/回榜产品","detail":"重点看Transformers能否守住前30、Call of Dragons能否离开#60，以及iOS五款#48之后产品能否连续留榜。"},
 {"type":"关注","title":"未来1—2个快照：观察iOS榜尾下跌组","detail":"Sea War已从#36回落至#60，Evo Defense与The Tower也进入末四位；若继续下行才升级为连续风险信号。"},
 {"type":"关注","title":"本周内：复核双端同步与分化","detail":"跟踪Limbus、Star Trek是否保持双端在榜，并核验Sea of Conquest与Age of Spirits的端间差异是否收敛。"},
]

gh=load(f"data/history/google-play/{DATE}.json"); ih=load(f"data/history/ios/{DATE}.json"); rev=load("data/sensortower-global-strategy-revenue-latest.json")
source_date=datetime.fromisoformat(ih["sourceUpdated"].replace("Z","+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))
def anchors(rows): return " · ".join(f"#{n} {rows[n-1]['gameName']}" for n in (1,25,60))

brief={
 "date":DATE,"timezone":"Asia/Shanghai","title":"Google五进五出、iOS九进九出；Transformers新品进入iOS前20",
 "summary":"较11月12日前一有效快照（11月13日无有效快照），Google Play五进五出，Limbus进入#23、Star Trek +10，Wild Rift −13；iOS九进九出，11月11日上架的Transformers进入#20，PUBG与Age of Empires均+12，Sea War −24。Google近90天新品2款、iOS 1款；两端缺少8月18日精确基准，不判断较老产品的90天飙升。",
 "newsMethod":"编辑热度：按时效、厂商/IP体量、双榜关联度与品类影响综合排序；不是第三方阅读量或舆情指数。",
 "iconBundle":f"assets/market-icons-{STAMP}-01.json","iconOverrideBundles":[f"assets/market-icons-{STAMP}-{i:02d}.json" for i in range(2,(len(all_cards)+4)//5+1)],
 "rankingSources":{"googlePlay":f"data/games-{STAMP}.json","ios":f"data/ios-games-{STAMP}.json"},"previousRankingSources":{"googlePlay":f"data/games-{PREV}.json","ios":f"data/ios-games-{PREV}.json"},
 "rankingDynamics":{"googlePlay":{"label":"Google Play · Android","sourceTime":f"北京时间 {gh['sourceCapturedAt']} 直连抓取","anchors":"榜单锚点："+anchors(datasets['googlePlay']['now']),"products":google_products},
                    "ios":{"label":"App Store · iPhone/iOS","sourceTime":f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ih['sourceUpdated']}）","anchors":"榜单锚点："+anchors(datasets['ios']['now']),"products":ios_products}},
 "marketNews":news,"closing":closing,"globalStrategyRevenue":rev,
 "status":{"googlePlay":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['googlePlay']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-18"},
           "ios":{"top60":60,"newRelease90d":sum(x['comparison90d']['status']=='new' for x in datasets['ios']['now']),"surge90d":0,"baselineAvailable":False,"baselineDate":"2026-08-18"}},
 "sources":[{"label":"Google Play美国区策略畅销榜直连","url":gh['sourceUrl'],"capturedAt":gh['sourceCapturedAt']},{"label":"Apple官方美国区iPhone策略畅销RSS","url":ih['sourceUrl'],"updated":ih['sourceUpdated'],"sourceDateBeijing":ih['dataDate']},{"label":"Sensor Tower全球收入榜中的策略产品","url":rev['sourceUrl'],"period":rev['period'],"estimateAsOf":rev['estimateAsOf']}],
 "downloads":{"markdown":f"reports/{DATE}.md","json":f"data/market-brief-{STAMP}.json"},
}

def markdown(v):
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{v['title']}**","",v['summary'],"","## 数据源与口径","",f"- Google Play：`{gh['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={ih['sourceUpdated']}`，对应北京时间榜单日期 `{ih['dataDate']}`",f"- Google锚点：{v['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{v['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-12；11月13日没有有效快照，本期升降覆盖跨周末多个自然日，不等于单日变化或收入增减。","- 近90天：缺少2026-08-18精确同口径TOP60基准，较老产品内部pending、页面按常规展示。","","## 1. 双榜当日异动产品",""]
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
