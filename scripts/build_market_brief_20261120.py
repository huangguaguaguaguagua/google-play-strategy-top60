#!/usr/bin/env python3
"""Build the 2026-11-20 market brief, archive report and local icon bundles."""

from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, PREV, BASELINE = "2026-11-20", "20261120", "20261119", "2026-08-20"


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
    card("googlePlay","com.Sunborn.SnqxExilium.Glo","entry","回榜#29；iOS同日回榜#30。11月19日起限定招募券进入可用窗口，双端同步回榜与活动同窗，但一天数据不足以确认活动带来持续收入抬升。"),
    card("googlePlay","com.plarium.vikings","entry","回榜#56。成熟北欧联盟4X仅进入后五名，先记为榜尾轮换；未发现可核验的当日重大版本节点。"),
    card("googlePlay","com.bw.ud.googleplay","exit","前一快照#56后掉榜。潜艇题材产品未能连续守住后五名，属于榜尾风险信号。"),
    card("googlePlay","com.sivona.stormshot.e","exit","前一快照#55后掉榜。成熟解谜获量层与联盟SLG产品退出TOP60，暂不把一次退出写成长期衰退。"),
    card("googlePlay","com.YoStarEN.Arknights","up","上升5位至#23；iOS反向下跌10位至#50。Monster Hunter联动处于活动窗口，但跨端方向完全相反，不能用活动直接解释单日榜位。"),
    card("googlePlay","com.ProjectMoon.LimbusCompany","down","从#22下降25位至#47，为Google当日最大跌幅；iOS反向上升7位至#53，先按跨端分化的待验证信号处理。"),
    card("googlePlay","com.riotgames.league.wildrift","down","下降8位至#55，而iOS回榜#54。MOBA仅因商店策略分类口径出现在本榜，不纳入Sensor Tower核心策略子集。"),
]

ios_products = [
    card("ios","6502505286","entry","回榜#30；Google同日回榜#29。11月19日起限定招募券进入可用窗口，双端同步回榜值得继续观察，但仍不能把单日结果直接归因于活动。"),
    card("ios","6503702666","entry","回榜#42。合作塔防产品回到中后段，当前没有可核验的同步重大运营节点，先记为回榜信号。"),
    card("ios","1480616990","entry","回榜#54；Google同产品下降8位至#55。两端都在榜尾，且MOBA不属于本页Sensor Tower核心策略口径。"),
    card("ios","1071976327","entry","回榜#58。成熟联盟4X重返末三位，只能确认当日进入，需下一有效快照验证能否留榜。"),
    card("ios","6741674823","exit","前一快照#58后掉榜。角色塔防RPG未能守住末三位，属于榜尾轮换。"),
    card("ios","6755173751","exit","前一快照#50后掉榜。塔防新品退出TOP60，后续若未快速回榜，将成为首发验证承接不足的信号。"),
    card("ios","6755585789","exit","前一快照#59后掉榜。昨日回榜仅维持一个快照，首发产品仍未形成连续在榜。"),
    card("ios","1592081003","exit","前一快照#56后掉榜。昨日下跌8位后继续退出，形成连续两快照的榜尾风险。"),
    card("ios","6751086804","up","上升12位至#40，为iOS当日最大涨幅；未发现可核验的同步重大节点，先按单日待验证信号处理。"),
    card("ios","1035712810","up","上升9位至#32；Google同产品升2位至#58。双端同向改善，但Google仍接近榜尾，需观察能否持续。"),
    card("ios","1642607669","up","上升9位至#18进入前20；Google反向下降4位至#38，跨端方向分化明显。"),
    card("ios","1464872022","down","下降10位至#50；Google反向上升5位至#23。Monster Hunter联动窗口内跨端走势相反，不支持简单活动归因。"),
    card("ios","1181774280","down","下降10位至#55。长线角色战棋落入后六名，当前没有足够证据把回落归因于具体卡池或版本。"),
    card("ios","1371565796","down","下降7位至#46。RAID当前无可核验的当日重大节点，单日回落仅作待验证信号。"),
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
    {"category":"角色策略 / 限时招募","date":"2026-10-27","title":"GIRLS' FRONTLINE 2更新限定招募与Dreambound Neverland活动","summary":"官方维护公告确认Faelynn、Welrod等新角色、限时活动及限定招募，并注明Surprise Access Permission从11月19日起可用于多类限时招募。","impact":"产品今日Google #29、iOS #30双端回榜；活动与榜位同窗，但需要后续快照确认是否形成持续收入支撑。","source":"SUNBORN官方","url":"https://gf2exilium.sunborngame.com/NewsInfo?id=452&typeId=3"},
    {"category":"塔防 / IP联动","date":"2026-11-12","title":"Arknights × Monster Hunter联动于11月16日开启","summary":"官方公告确认Thunder in the Azure Dream活动持续至12月7日，第一阶段开放至11月30日，并配套限定寻访和活动商店。","impact":"产品今日Google升5位至#23、iOS跌10位至#50；活动窗口内跨端走势相反，不能直接断言联动带来收入增长。","source":"Arknights官方","url":"https://www.arknights.global/news/5092"},
    {"category":"IP新品 / 首发运营","date":"2026-11-16","title":"Transformers: Eternal War上线后进入首个限时活动窗口","summary":"Apple商品页显示1.2.1版本于11月16日更新，并列出11月14—20日限时活动和Optimus Prime付费活动。","impact":"产品当前iOS #23且仍属近90天新品；首发IP热度能否在活动结束后维持前30是关键验证点。","source":"Apple App Store","url":"https://apps.apple.com/us/app/id6772922295"},
    {"category":"长线运营 / 服务器迁移","date":"2026-11-06","title":"Whiteout Survival扩大State Transfer覆盖范围","summary":"Century Games官方公告列出State 4—4487的迁移分组，并于11月8日开放服务器迁移。","impact":"头部城建生存产品用大规模分组迁移维护成熟服务器生态；这类联盟关系重组是长线SLG留存的重要运营节点。","source":"Century Games官方","url":"https://www.centurygames.com/whiteout-survival-state-transfer/"},
    {"category":"科幻策略 / 周年运营","date":"2026-10-20","title":"Foundation: Galactic Frontier完成首周年Astral Alignment活动","summary":"FunPlus官方称周年活动于10月19日至11月7日分阶段开放，并提供不同玩法与奖励。","impact":"产品今日Google #31、iOS #35；活动已结束，当前榜位更适合观察周年用户留存，而非继续当作活动峰值。","source":"FunPlus官方","url":"https://funplus.com/foundation-galactic-frontier-anniversary-event/"},
    {"category":"公司 / 投融资","date":"2026-11-02","title":"Gamehaus拟收购Anamana多数股权","summary":"Gamehaus公告称将通过股份购买与增发对价取得Techforge/Anamana多数权益，并计划结合发行、买量、数据分析与AI辅助制作平台。","impact":"交易反映移动发行商继续把买量与AI内容生产能力打包整合；在策略品类高素材消耗环境下值得跟踪，但目前不直接对应双榜单品位移。","source":"Gamehaus投资者关系","url":"https://ir.gamehaus.com/2026-11-02-Gamehaus-Signs-Definitive-Agreement-to-Acquire-Majority-Stake-in-Anamana"},
    {"category":"IP长线运营","date":"2026-11-03","title":"Game of Thrones: Conquest发布Highgarden Harvest Festival月度预告","summary":"官方11月预告公布新装备、英雄与龙装，并围绕Highgarden主题安排当月内容。","impact":"产品Google #58、iOS #32且双端均上升；仍需后续快照确认是否形成持续活动支撑。","source":"Game of Thrones: Conquest官方","url":"https://www.gotconquest.com/news/2026/11/03/november-preview-highgarden-harvest-festival-6/"},
    {"category":"IP长线运营 / 社区","date":"2026-10-27","title":"Star Trek Fleet Command以Join the Fleet活动收录八名玩家","summary":"Scopely官方公布八名社区玩家将进入游戏宇宙，延续Star Trek 60周年的用户共创活动。","impact":"成熟IP策略产品通过社区身份与内容共创维持核心用户关系；今日Google #17，仍在前二十。","source":"Scopely官方","url":"https://www.scopely.com/en/news/a-place-among-the-stars-star-trek-fleet-command-honors-eight-fans-with-join-the-fleet-campaign"},
]
for index, item in enumerate(news, 1): item["rank"] = index


closing = [
    {"type":"判断","title":"两端同时换位，但Google中段波动更集中","detail":"Google 2进2出且Limbus Company单日−25；iOS 4进4出并有Dragon Traveler +12、Arknights与Fire Emblem各−10。今天不再是单纯榜尾微调。"},
    {"type":"判断","title":"GIRLS' FRONTLINE 2是最明确的双端同步信号","detail":"产品Google #29、iOS #30同日回榜，并与11月19日起可用的限定招募券同窗；现阶段只能确认同步，尚不能确认活动带来的持续性。"},
    {"type":"判断","title":"Arknights与Limbus Company均出现强跨端分化","detail":"Arknights Google +5而iOS −10；Limbus Company Google −25而iOS +7。单店一天变化不足以代表产品整体收入方向。"},
    {"type":"关注","title":"下一有效快照：核验六款双端进入产品","detail":"观察GIRLS' FRONTLINE 2、Vikings、Coop TD、Wild Rift与Lords Mobile能否连续留榜，并检查今日掉榜产品是否快速回归。"},
    {"type":"关注","title":"未来2—3个快照：验证Limbus Company与Arknights分化","detail":"只有跨端差异继续扩大或连续同向，才升级为平台差异信号；若迅速回摆，则保留为单日排序波动。"},
    {"type":"关注","title":"11月20日后：观察Transformers首发活动承接","detail":"限时活动结束后若iOS仍能维持前30，才说明IP首发用户对角色收集与放置循环有初步承接；否则保留为首发峰值。"},
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
    "date":DATE,"timezone":"Asia/Shanghai","title":"双端同步换位；GIRLS' FRONTLINE 2双榜回归",
    "summary":"较11月19日有效快照，Google Play 2进2出，Kingshot升至#1，Limbus Company −25；iOS四进四出，Dragon Traveler +12，Arknights与Fire Emblem Heroes各−10。GIRLS' FRONTLINE 2在Google #29、iOS #30同步回榜。两端精确8月20日基准均可用；Google 8款、iOS 8款为近90天飙升，iOS另有2款按当前Apple releaseDate归类为新品。",
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
    lines=[f"# {DATE} 美国区策略手游双端市场日报","",f"**{value['title']}**","",value["summary"],"","## 数据源与口径","",f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取）",f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}",f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}","- 对比基准：各自上一份最终有效快照为2026-11-18。","- 近90天：两端2026-08-20精确同口径TOP60基准均可用；新品先按各自商店releaseDate判定。","","## 1. 双榜当日异动产品",""]
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
