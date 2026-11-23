#!/usr/bin/env python3
"""Build the 2026-11-23 market brief, archive report and local icon bundles."""

from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, PREV, BASELINE = "2026-11-23", "20261123", "20261120", "2026-08-25"


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
    card("googlePlay","com.sivona.stormshot.e","entry","从上周五掉榜后回到#53，仍处后八名；弹道解谜获量层与联盟4X承接能否重新站稳，需要下一有效快照确认。"),
    card("googlePlay","leyi.ageofspirits","entry","进入#58且按Google美国区released日期归类为近90天新品。原始部落、萨满与联盟4X仍处首发验证，当前仅是榜尾进入信号。"),
    card("googlePlay","com.farlightgames.samo.gp","entry","Call of Dragons回到#59。奇幻自由行军与巨兽围猎产品仅进入末二位，先按榜尾轮换处理。"),
    card("googlePlay","com.more.lastfortress.gp","exit","上周五#54后掉榜。地下堡垒经营与联盟战争产品再次失守榜尾，单次退出尚不足以判断长线衰退。"),
    card("googlePlay","com.more.dayzsurvival.gp","exit","上周五#57后掉榜；成熟末日SLG未能守住末四位，属于榜尾风险信号。"),
    card("googlePlay","com.wireless.defenseland","exit","上周五#60后掉榜。塔防产品的末位进入未能延续到周一快照，暂记为短暂轮换。"),
    card("googlePlay","com.riotgames.league.wildrift","up","上升18位至#37；iOS同步上升16位至#38。两端同向改善，但MOBA只因商店分类进入本榜，不纳入核心策略收入子集。"),
    card("googlePlay","com.Sunborn.SnqxExilium.Glo","up","上升13位至#16，而iOS下跌30位至#60。11月19日活动仍在进行，强跨端分化不支持简单归因。"),
    card("googlePlay","com.wb.goog.got.conquest","up","上升13位至#45，iOS反向下降11位至#43；同一IP产品跨端方向相反，先按平台排序差异观察。"),
    card("googlePlay","com.ProjectMoon.LimbusCompany","down","继续下降13位至#60；上周五已下跌25位，Google端形成连续回落，但iOS本期已掉榜，仍需更多快照确认持续性。"),
    card("googlePlay","com.snowprintstudios.tacticus","down","下降10位至#50，而iOS上升16位至#41。Warhammer产品出现明显跨端反向变化，不据单日榜位推断活动效果。"),
    card("googlePlay","com.spark.sp.gp","down","Salvage Empire下降7位至#32，仍在中段；没有发现可确认的同步重大节点，先记为周末后回摆。"),
]

ios_products = [
    card("ios","6755585789","entry","Overgeared Hero回到#47；Google同产品下降6位至#48。背包合成RPG跨端反向，暂不把回榜归因于单一活动。"),
    card("ios","1619254071","entry","Honor of Kings回榜#48。MOBA仅因Apple策略分类进入本榜，不纳入核心策略收入子集。"),
    card("ios","6476261995","entry","Age of Empires Mobile回榜#49。经典IP与移动联盟4X产品仍处中后段，需观察能否连续留榜。"),
    card("ios","1427744264","entry","Star Trek Fleet Command回榜#53；Google端下降4位至#21。成熟IP长线产品仅在iOS榜尾重新出现。"),
    card("ios","6482291732","entry","Lucky Defense回榜#55。双人随机塔防接近榜尾，当前没有足够证据确认由具体活动推动。"),
    card("ios","1529067679","entry","Warpath回榜#59。军团RTS与狙击获量层产品仅进入末二位，属于待验证的榜尾信号。"),
    card("ios","6503702666","exit","上周五回榜#42后再次掉榜，合作塔防只维持一个有效快照，尚未形成连续在榜。"),
    card("ios","1464872022","exit","上周五#50后掉榜；Monster Hunter联动仍在窗口内，但iOS退出与Google升至#20并不同向。"),
    card("ios","6444112366","exit","上周五#53后掉榜；Google同产品已连续两次大幅回落至#60，形成需要继续验证的双端压力信号。"),
    card("ios","1411917616","exit","上周五#56后掉榜。成熟城建联盟SLG未守住后五名，暂不外推为长线衰退。"),
    card("ios","1071976327","exit","上周五回榜#58后再次掉榜，Lords Mobile的本次进入只维持一个有效快照。"),
    card("ios","1274354704","exit","上周五#60后掉榜；Google端反而升至#29并满足90天飙升条件，跨端表现明显分化。"),
    card("ios","1480616990","up","上升16位至#38，Google同步上升18位至#37；这是本期最清晰的双端同向改善信号，但仍仅代表周末后一个快照。"),
    card("ios","1599937506","up","上升16位至#41，Google反向下降10位至#50；同一产品跨端排名互换，不据此推断收入方向。"),
    card("ios","6741568655","up","Mobile Legends上升15位至#23。产品属于MOBA分类交叉，不纳入本页核心策略市场结论。"),
    card("ios","6502505286","down","从#30下降30位至#60，而Google升13位至#16。11月19日活动仍在进行，极端分化更需要排除平台与榜单波动。"),
    card("ios","6751086804","down","Dragon Traveler下降16位至#56，上周五曾上升12位；两次快照快速回摆，现阶段更像活动/榜面波动而非稳定趋势。"),
    card("ios","6760406772","down","Last Shelter: War Z下降12位至#57，进入榜尾风险区；未发现可确认的同步重大运营节点。"),
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
    {"category":"角色策略 / 限时活动","date":"2026-11-18","title":"GIRLS' FRONTLINE 2公布11月19日Iliad等活动与Welrod招募","summary":"官方更新预告列出Iliad、Voyage Logs、Clearsky Pact等活动，并延续Welrod定向招募。","impact":"本期Google升至#16、iOS跌至#60；活动窗口与强跨端分化同窗，但不能据单个快照判断活动效果。","source":"SUNBORN官方Steam公告","url":"https://steamcommunity.com/app/3308670/allnews/"},
    {"category":"现代战争 / IP联动","date":"2026-11-17","title":"Supremacy: World War 3宣布十周年G.I. Joe联动","summary":"Stillfront旗下Twin Harbour宣布将推出专属G.I. Joe赛季，并称这是该产品首次IP联动。","impact":"产品本期Google #57、iOS #35；正式赛季时间尚未公布，当前只能作为未来版本关注点，不能解释今日位移。","source":"Twin Harbour / Games Press","url":"https://www.gamespress.com/GI-Joe-Joins-the-Fight-in-Supremacy-World-War-3-for-the-Games-10th-Ann"},
    {"category":"塔防 / IP联动","date":"2026-11-12","title":"Arknights × Monster Hunter联动于11月16日开启","summary":"官方公告确认Thunder in the Azure Dream活动持续至12月7日，第一阶段开放至11月30日，并配套限定寻访和活动商店。","impact":"产品本期Google升至#20、iOS掉榜；活动窗口内跨端表现不同，不能直接断言联动带来统一收入增长。","source":"Arknights官方","url":"https://www.arknights.global/news/5092"},
    {"category":"IP新品 / 首发运营","date":"2026-11-16","title":"Transformers: Eternal War上线后进入首个限时活动窗口","summary":"Apple商品页显示1.2.1版本于11月16日更新，并列出11月14—20日限时活动和Optimus Prime付费活动。","impact":"产品当前iOS #21且仍属近90天新品；活动结束后能否继续维持前30是首发承接的重要观察点。","source":"Apple App Store","url":"https://apps.apple.com/us/app/id6772922295"},
    {"category":"长线运营 / 服务器迁移","date":"2026-11-06","title":"Whiteout Survival扩大State Transfer覆盖范围","summary":"Century Games官方公告列出State 4—4487的迁移分组，并于11月8日开放服务器迁移。","impact":"头部城建生存产品用大规模分组迁移维护成熟服务器生态；这类联盟关系重组是长线SLG留存的重要运营节点。","source":"Century Games官方","url":"https://www.centurygames.com/whiteout-survival-state-transfer/"},
    {"category":"科幻策略 / 周年运营","date":"2026-10-20","title":"Foundation: Galactic Frontier完成首周年Astral Alignment活动","summary":"FunPlus官方称周年活动于10月19日至11月7日分阶段开放，并提供不同玩法与奖励。","impact":"产品本期Google #30、iOS #31；活动已结束，当前榜位更适合观察周年用户留存，而非继续当作活动峰值。","source":"FunPlus官方","url":"https://funplus.com/foundation-galactic-frontier-anniversary-event/"},
    {"category":"公司 / 投融资","date":"2026-11-02","title":"Gamehaus拟收购Anamana多数股权","summary":"Gamehaus公告称将通过股份购买与增发对价取得Techforge/Anamana多数权益，并计划结合发行、买量、数据分析与AI辅助制作平台。","impact":"交易反映移动发行商继续把买量与AI内容生产能力打包整合；在策略品类高素材消耗环境下值得跟踪，但目前不直接对应双榜单品位移。","source":"Gamehaus投资者关系","url":"https://ir.gamehaus.com/2026-11-02-Gamehaus-Signs-Definitive-Agreement-to-Acquire-Majority-Stake-in-Anamana"},
    {"category":"IP长线运营","date":"2026-11-03","title":"Game of Thrones: Conquest发布Highgarden Harvest Festival月度预告","summary":"官方11月预告公布新装备、英雄与龙装，并围绕Highgarden主题安排当月内容。","impact":"产品Google #45、iOS #43且跨端方向相反；仍需后续快照确认活动支撑是否持续。","source":"Game of Thrones: Conquest官方","url":"https://www.gotconquest.com/news/2026/11/03/november-preview-highgarden-harvest-festival-6/"},
    {"category":"IP长线运营 / 社区","date":"2026-10-27","title":"Star Trek Fleet Command以Join the Fleet活动收录八名玩家","summary":"Scopely官方公布八名社区玩家将进入游戏宇宙，延续Star Trek 60周年的用户共创活动。","impact":"成熟IP策略产品通过社区身份与内容共创维持核心用户关系；本期Google #21、iOS回榜#53。","source":"Scopely官方","url":"https://www.scopely.com/en/news/a-place-among-the-stars-star-trek-fleet-command-honors-eight-fans-with-join-the-fleet-campaign"},
]
for index, item in enumerate(news, 1): item["rank"] = index


closing = [
    {"type":"判断","title":"周末后iOS换位显著多于Google","detail":"Google 3进3出，iOS 6进6出；iOS同时出现GFL2 −30、Dragon Traveler −16及三款至少+15的上涨，榜面波动明显更高。"},
    {"type":"判断","title":"Wild Rift是本期最清晰的双端同向改善","detail":"Google +18至#37、iOS +16至#38；但它属于MOBA分类交叉，不应被扩展为核心SLG或4X市场结论。"},
    {"type":"判断","title":"GFL2与Tacticus呈现强跨端反向变化","detail":"GFL2 Google +13而iOS −30；Tacticus Google −10而iOS +16。活动或IP节点不能直接解释两个商店相反的单次排序。"},
    {"type":"关注","title":"下一有效快照：核验九款进入/回榜产品","detail":"重点观察Age of Spirits、Call of Dragons、Age of Empires Mobile、Star Trek Fleet Command、Lucky Defense与Warpath能否连续留榜。"},
    {"type":"关注","title":"未来2—3个快照：确认Limbus与GFL2是否持续承压","detail":"Limbus在Google连续大跌并于iOS掉榜；GFL2则跨端极端分化。只有连续快照重复，才升级为持续趋势判断。"},
    {"type":"关注","title":"G.I. Joe赛季公布后：观察Supremacy跨端反应","detail":"联动目前只确认即将推出；待正式日期及内容上线后，再比较Google #57与iOS #35是否形成同步改善。"},
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
    "date":DATE,"timezone":"Asia/Shanghai","title":"周末后双榜换位扩大；Wild Rift双端同升、GFL2强分化",
    "summary":"较11月20日前一有效快照，Google Play 3进3出，Wild Rift +18、GFL2 +13、Limbus Company −13；iOS 6进6出，GFL2 −30、Wild Rift与Tacticus各+16。Google榜首为Total Battle，iOS榜首为Pokémon GO。两端精确8月25日基准均可用；Google有1款近90天新品、7款飙升，iOS有2款新品、12款飙升。",
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
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{value['title']}**","",value["summary"],"","## 数据源与口径","",f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-20。","- 近90天：两端2026-08-25精确同口径TOP60基准均可用；新品先按各自商店releaseDate判定。","","## 1. 双榜当日异动产品",""]
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
