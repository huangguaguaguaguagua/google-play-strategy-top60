#!/usr/bin/env python3
"""Build the 2026-11-24 market brief, archive report and local icon bundles."""

from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, PREV, BASELINE = "2026-11-24", "20261124", "20261123", "2026-08-26"


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
    card("googlePlay","com.wondergames.warpath.gp","entry","从前一快照榜外回到#57；iOS同产品上升9位至#50。双端同向改善仍位于榜尾，只记为待验证信号。"),
    card("googlePlay","com.YoStarEN.MahjongSoul","entry","首次进入当前历史池并位于#58。产品2019年已上线，属于成熟立直麻将与角色外观长线运营，本次只按榜尾进入信号处理。"),
    card("googlePlay","com.bw.ud.googleplay","entry","Sea War回榜#59；iOS同步上升7位至#43。潜艇合成获量层与联盟海战承接出现同向改善，但尚不足以确认持续性。"),
    card("googlePlay","leyi.ageofspirits","exit","前一快照以近90天新品身份进入#58后即掉榜；仍处首发验证，尚未形成连续在榜。"),
    card("googlePlay","com.farlightgames.samo.gp","exit","前一快照回榜#59后再次掉榜，奇幻自由行军与巨兽围猎产品仍表现为榜尾轮换。"),
    card("googlePlay","com.ProjectMoon.LimbusCompany","exit","前一快照已降至#60，本期掉榜；连续回落构成需继续验证的Google端压力信号，但不能据此断言长期趋势。"),
    card("googlePlay","com.snowprintstudios.tacticus","up","上升10位至#40，iOS同步上升7位至#34；与前一日跨端反向不同，本次形成同向修复，仍需连续快照确认。"),
    card("googlePlay","com.more.lastshelter.gp","up","Last Shelter: War Z上升5位至#29，iOS同产品上升9位至#48；成熟末日SLG出现双端同向改善。"),
    card("googlePlay","com.spark.sp.gp","up","Salvage Empire上升5位至#27，回到前30；未发现可确认的同步重大节点，先记为单日改善。"),
    card("googlePlay","com.YoStarEN.Arknights","down","下降17位至#37，是Google最大跌幅；Monster Hunter联动仍在进行，单日下跌不能直接解释为活动效果。"),
    card("googlePlay","com.topwar.gp","down","Top War下降9位至#52并进入榜尾区；成熟4X产品需观察未来2—3个快照是否继续承压。"),
]

ios_products = [
    card("ios","1570095804","entry","Kingdom Guard回榜#46，并以8月26日精确基准#57计算为近90天飙升。塔防获量层与英雄养成回到中后段，仍需确认连续性。"),
    card("ios","1071976327","entry","Lords Mobile回榜#52，且精确基准#60到当前提升8位，归类为近90天飙升；当前仍处榜尾区。"),
    card("ios","6740189002","entry","Galaxy Defense进入#54。科幻塔防产品仅位于后七名，当前没有可核验原因，按待验证榜尾信号处理。"),
    card("ios","6479020757","entry","DC: Dark Legion回榜#56；IP角色收集与基地策略产品接近榜尾，不把本次回榜直接归因于某一活动。"),
    card("ios","1611722542","entry","Kingdom Clash进入#60，只占据末位；中世纪塔防与合成养成产品尚未形成连续在榜。"),
    card("ios","6476261995","exit","Age of Empires Mobile前一日回榜#49后再次掉榜；11月19日Chaos Rift版本节点未转化为连续在榜证据。"),
    card("ios","6482291732","exit","Lucky Defense前一日回榜#55后即掉榜，双人随机塔防仍表现为榜尾轮换。"),
    card("ios","6751086804","exit","Dragon Traveler前一日已降至#56，本期掉榜；短期两次快速回摆后退出，仍不能外推长期走势。"),
    card("ios","1342290011","exit","Last Shelter: Survival从#58掉榜；同产品另一版本Last Shelter: War Z升至#48，不能把不同appId混为同一排名轨迹。"),
    card("ios","6502505286","exit","GIRLS' FRONTLINE 2前一日大跌至#60后掉榜，Google端仍在#17；跨端分化继续扩大。"),
    card("ios","1529067679","up","Warpath上升9位至#50，Google同步回榜#57；两端同向但仍位于后段，先按待验证改善处理。"),
    card("ios","6760406772","up","Last Shelter: War Z上升9位至#48，Google同步升5位至#29；这是本期较明确的成熟SLG双端同向改善。"),
    card("ios","6744812012","up","X-Clash上升9位至#21；生存小游戏获量层与联盟策略承接进入前25，但单日异动不等于长期趋势。"),
    card("ios","1181774280","down","Fire Emblem Heroes下降13位至#59，是iOS最大跌幅并进入榜尾风险区。"),
    card("ios","1480616990","down","Wild Rift下降11位至#49，回吐前一日大部分升幅；Google仅下降1位至#38，跨端再度分化。"),
    card("ios","1619254071","down","Honor of Kings下降10位至#58，前一日回榜后迅速进入末三位；MOBA交叉分类不纳入核心策略子集。"),
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
    {"category":"经典IP / 版本更新","date":"2026-11-19","title":"Age of Empires Mobile上线Chaos Rift等新内容","summary":"官方维护公告列出Chaos Rift跨帝国战场，并要求更新至Android 1.15.103.0、iOS 1.15.104.0和PC 1.15.100.0。","impact":"产品本期iOS从#49掉榜；版本节点存在但没有形成连续在榜证据，不能据此断言活动效果。","source":"Age of Empires Mobile官方Steam公告","url":"https://steamcommunity.com/app/2783360/allnews/"},
    {"category":"现代战争 / IP联动","date":"2026-11-17","title":"Supremacy: World War 3宣布十周年G.I. Joe联动","summary":"Stillfront旗下Twin Harbour宣布将推出专属G.I. Joe赛季，并称这是该产品首次IP联动。","impact":"产品本期Google #60、iOS #41；正式赛季时间尚未公布，当前只能作为未来版本关注点，不能解释今日位移。","source":"Twin Harbour / Games Press","url":"https://www.gamespress.com/GI-Joe-Joins-the-Fight-in-Supremacy-World-War-3-for-the-Games-10th-Ann"},
    {"category":"塔防 / IP联动","date":"2026-11-12","title":"Arknights × Monster Hunter联动于11月16日开启","summary":"官方公告确认Thunder in the Azure Dream活动持续至12月7日，第一阶段开放至11月30日，并配套限定寻访和活动商店。","impact":"产品本期Google升至#20、iOS掉榜；活动窗口内跨端表现不同，不能直接断言联动带来统一收入增长。","source":"Arknights官方","url":"https://www.arknights.global/news/5092"},
    {"category":"IP新品 / 首发运营","date":"2026-11-16","title":"Transformers: Eternal War上线后进入首个限时活动窗口","summary":"Apple商品页显示1.2.1版本于11月16日更新，并列出11月14—20日限时活动和Optimus Prime付费活动。","impact":"产品当前iOS #25且仍属近90天新品；活动结束后能否继续维持前30是首发承接的重要观察点。","source":"Apple App Store","url":"https://apps.apple.com/us/app/id6772922295"},
    {"category":"长线运营 / 新玩法","date":"2026-11-06","title":"Whiteout Survival开放Mergeventure并扩充社交与竞技系统","summary":"官方更新说明新增Mergeventure合成活动、Chief Gift社交功能、每周Expedition Arena与新Expert Justus。","impact":"Whiteout Survival仍在双榜前列且位于Sensor Tower全球收入总榜#5；新玩法展示成熟城建生存产品如何并行维护轻活动、社交与核心竞技。","source":"Whiteout Survival官方更新资料","url":"https://www.whiteoutsurvival.wiki/sneak-peek/101898521en/"},
    {"category":"科幻策略 / 周年运营","date":"2026-10-20","title":"Foundation: Galactic Frontier完成首周年Astral Alignment活动","summary":"FunPlus官方称周年活动于10月19日至11月7日分阶段开放，并提供不同玩法与奖励。","impact":"产品本期Google #32、iOS #36；活动已结束，当前榜位更适合观察周年用户留存，而非继续当作活动峰值。","source":"FunPlus官方","url":"https://funplus.com/foundation-galactic-frontier-anniversary-event/"},
    {"category":"公司 / 投融资","date":"2026-11-02","title":"Gamehaus拟收购Anamana多数股权","summary":"Gamehaus公告称将通过股份购买与增发对价取得Techforge/Anamana多数权益，并计划结合发行、买量、数据分析与AI辅助制作平台。","impact":"交易反映移动发行商继续把买量与AI内容生产能力打包整合；在策略品类高素材消耗环境下值得跟踪，但目前不直接对应双榜单品位移。","source":"Gamehaus投资者关系","url":"https://ir.gamehaus.com/2026-11-02-Gamehaus-Signs-Definitive-Agreement-to-Acquire-Majority-Stake-in-Anamana"},
    {"category":"IP长线运营","date":"2026-11-03","title":"Game of Thrones: Conquest发布Highgarden Harvest Festival月度预告","summary":"官方11月预告公布新装备、英雄与龙装，并围绕Highgarden主题安排当月内容。","impact":"产品Google #49、iOS #38；仍需后续快照确认活动支撑是否持续。","source":"Game of Thrones: Conquest官方","url":"https://www.gotconquest.com/news/2026/11/03/november-preview-highgarden-harvest-festival-6/"},
    {"category":"IP长线运营 / 社区","date":"2026-10-27","title":"Star Trek Fleet Command以Join the Fleet活动收录八名玩家","summary":"Scopely官方公布八名社区玩家将进入游戏宇宙，延续Star Trek 60周年的用户共创活动。","impact":"成熟IP策略产品通过社区身份与内容共创维持核心用户关系；本期Google #21、iOS #53。","source":"Scopely官方","url":"https://www.scopely.com/en/news/a-place-among-the-stars-star-trek-fleet-command-honors-eight-fans-with-join-the-fleet-campaign"},
]
for index, item in enumerate(news, 1): item["rank"] = index


closing = [
    {"type":"判断","title":"iOS继续比Google更频繁轮换","detail":"Google 3进3出，iOS 5进5出；iOS五款退出中有四款前一日位于#55以后，说明榜尾竞争仍更拥挤。"},
    {"type":"判断","title":"成熟SLG出现两组双端同向改善","detail":"Last Shelter: War Z在Google +5、iOS +9；Warpath在Google回榜、iOS +9。两组都仍需连续快照验证，尚不能写成长期回升。"},
    {"type":"判断","title":"前一日大幅波动出现快速回摆","detail":"Wild Rift在iOS由+16转为−11，GFL2由−30转为掉榜，Arknights则Google −17；单日信号不宜直接关联活动成效。"},
    {"type":"关注","title":"下一有效快照：核验八款榜尾进入/回榜产品","detail":"重点观察Mahjong Soul、Sea War、Galaxy Defense、DC: Dark Legion与Kingdom Clash能否连续留榜。"},
    {"type":"关注","title":"未来2—3个快照：观察Limbus与GFL2的跨端压力","detail":"Limbus Google掉榜，GFL2 iOS掉榜而Google仍#17；只有相同方向持续出现，才升级为结构性判断。"},
    {"type":"关注","title":"11月30日前：复核Arknights联动窗口","detail":"Monster Hunter联动第一阶段仍在进行，但Google本期−17且iOS未进榜；后续只以连续榜位和官方活动节点交叉验证。"},
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
    "date":DATE,"timezone":"Asia/Shanghai","title":"iOS榜首换为Kingshot；成熟SLG双端同升、榜尾继续轮换",
    "summary":"较11月23日前一有效快照，Google Play 3进3出，Tacticus +10、Arknights −17；iOS 5进5出，Warpath、Last Shelter: War Z与X-Clash各+9，Fire Emblem Heroes −13。Google榜首仍为Total Battle，iOS榜首换为Kingshot。两端精确8月26日基准均可用；Google无近90天新品、6款飙升，iOS有2款新品、12款飙升。",
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
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{value['title']}**","",value["summary"],"","## 数据源与口径","",f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-23。","- 近90天：两端2026-08-26精确同口径TOP60基准均可用；新品先按各自商店releaseDate判定。","","## 1. 双榜当日异动产品",""]
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
