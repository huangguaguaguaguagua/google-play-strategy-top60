#!/usr/bin/env python3
"""Build the 2026-11-26 market brief, archive report and local icon bundles."""

from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, PREV, BASELINE = "2026-11-26", "20261126", "20261125", "2026-08-28"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    (ROOT / path).write_text(json.dumps(value, ensure_ascii=False, indent=None if compact else 2,
                                      separators=(",", ":") if compact else None) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load(f"data/games-{STAMP}.json"), "prior": load(f"data/games-{PREV}.json"), "id": "packageName", "label": "Google Play · Android"},
    "ios": {"now": load(f"data/ios-games-{STAMP}.json"), "prior": load(f"data/ios-games-{PREV}.json"), "id": "appId", "label": "App Store · iPhone/iOS"},
}


def find(store, product_id, current=True):
    rows = datasets[store]["now" if current else "prior"]
    key = datasets[store]["id"]
    return next(row for row in rows if str(row[key]) == str(product_id))


def card(store, product_id, kind, analysis):
    current = kind != "exit"
    item = find(store, product_id, current)
    prior = None if not current else next((row for row in datasets[store]["prior"] if str(row[datasets[store]["id"]]) == str(product_id)), None)
    labels = {
        "entry": f"进入/回榜 #{item['rank']}",
        "exit": f"从 #{item['rank']} 掉榜",
        "up": f"上升 {str(item.get('dailyChange', '+0'))[1:]} 位至 #{item['rank']}",
        "down": f"下降 {str(item.get('dailyChange', '-0'))[1:]} 位至 #{item['rank']}",
    }
    return {
        "store": store, "productId": str(product_id), "gameName": item["gameName"],
        "currentRank": item["rank"] if current else None,
        "previousRank": item["rank"] if not current else (prior["rank"] if prior else None),
        "changeType": kind, "changeLabel": labels[kind], "analysis": analysis,
        "iconKey": f"{store}:{product_id}", "assetRank": item["assetRank"],
    }


google_products = [
    card("googlePlay", "com.proximabeta.aoemobile", "entry", "Age of Empires Mobile进入#55，iOS同步位于#31；11月19日Chaos Rift版本是可核验背景，但Google首次回榜只能记为待验证信号。"),
    card("googlePlay", "com.farlightgames.samo.gp", "entry", "Call of Dragons回榜#56，仍处后五名；缺少同步重大节点证据，先按榜尾轮换观察。"),
    card("googlePlay", "com.bw.ud.googleplay", "exit", "Sea War: Uboat Raid前一日#59，本期掉榜；成熟海战产品未形成连续改善。"),
    card("googlePlay", "com.more.dayzsurvival.gp", "exit", "Last Shelter: Survival前一日回榜#60后即退出；同系列War Z仍在#30，两个package继续分开记录。"),
    card("googlePlay", "com.wondergames.warpath.gp", "up", "Warpath上升4位至#52，修复部分榜尾压力；iOS前一日已掉榜，跨端改善尚未同步。"),
    card("googlePlay", "com.sivona.stormshot.e", "up", "Stormshot上升3位至#45，仍在中后段；未发现可确认的同步运营转折。"),
    card("googlePlay", "com.igg.android.lordsmobile", "up", "Lords Mobile上升3位至#35，属于长线4X的单日回摆，核心支撑仍来自存量联盟与周期活动。"),
    card("googlePlay", "com.plarium.vikings", "down", "Vikings: War of Clans下降4位至#58，进入后三级风险区；需下一有效快照确认是否掉榜。"),
    card("googlePlay", "com.im30.ROE.gp", "down", "Rise of Castles下降4位至#34，仍在中段；单日回落不足以判断长线趋势。"),
    card("googlePlay", "com.kingsgroup.sos", "down", "State of Survival下降3位至#48，iOS仍未进入TOP60；成熟丧尸SLG继续表现出平台分化。"),
]


ios_products = [
    card("ios", "1342290011", "entry", "Last Shelter: Survival进入#52，而Google同package本期掉榜；同一产品跨端方向相反。"),
    card("ios", "1274354704", "entry", "Guns of Glory回榜#57，仅处后四名；当前更接近榜尾轮换，尚无证据指向特定活动。"),
    card("ios", "1592081003", "entry", "MARVEL SNAP进入#59，属于卡牌策略交叉分类且位于末二位，不扩写为核心SLG变化。"),
    card("ios", "6761043541", "exit", "近90天新品Last Beacon前一日#54，本期掉榜；仍处首发验证，尚未形成稳定畅销位置。"),
    card("ios", "850057092", "exit", "The Battle Cats前一日大跌至#58后掉榜；成熟塔防产品的短期回落已延续到退出TOP60。"),
    card("ios", "6760406772", "exit", "Last Shelter: War Z前一日跌至#60后掉榜；Google仍#30，跨端差距继续扩大。"),
    card("ios", "1241932094", "up", "Last Day on Earth上升11位至#45，为iOS最大涨幅；暂无可核验重大节点，先视为待验证波峰。"),
    card("ios", "1575590830", "up", "The Tower上升10位至#35，回榜次日继续改善；放置塔防需再观察2—3个快照确认持续性。"),
    card("ios", "1479198816", "up", "Top War上升9位至#48，Google同产品#46；两端重新接近，但仍位于中后段。"),
    card("ios", "6738469826", "up", "Lands of Jail上升9位至#40，Google位于#26；双端同榜但商业化强度仍有明显差距。"),
    card("ios", "6741568655", "up", "Mobile Legends: Bang Bang.US上升9位至#26；属于MOBA交叉分类，不纳入核心策略子集。"),
    card("ios", "1354260888", "up", "Rise of Kingdoms上升7位至#23。早期文明选择/自由行军已转向战力逆袭情景剧与近期城建资源、真实会战素材；单日上涨仍需后续确认。"),
    card("ios", "1599937506", "down", "Tacticus下降7位至#51，Google位于#39；两端均处中后段，暂不归因于单一IP或版本节点。"),
    card("ios", "6776076449", "down", "Plants on Fire下降7位至#41，回吐前一日进入涨幅；Magic Fortune赛季仍在进行，但不能据此断言活动效果。"),
    card("ios", "1554247785", "down", "Yu-Gi-Oh! Master Duel回榜次日下降7位至#29，仍保住前30；卡牌策略产品波动需与核心SLG分开理解。"),
    card("ios", "1035712810", "down", "Game of Thrones: Conquest下降6位至#53，Google位于#47；两端均回到后段。"),
]


def assets(store):
    manifest = load("assets/manifest.json" if store == "googlePlay" else "assets/ios-manifest.json")
    result = {}
    for filename in manifest["files"]:
        result.update(load("assets/" + filename))
    return result


asset_maps = {"googlePlay": assets("googlePlay"), "ios": assets("ios")}
cards = google_products + ios_products
for start in range(0, len(cards), 5):
    bundle = {}
    for item in cards[start:start + 5]:
        value = asset_maps[item["store"]].get(f"{int(item['assetRank']):02d}_icon")
        if not str(value).startswith("data:image/"):
            raise RuntimeError(f"Missing local icon for {item['gameName']}")
        bundle[item["iconKey"]] = value
    save(f"assets/market-icons-{STAMP}-{start // 5 + 1:02d}.json", bundle, compact=True)


news = [
    {"category":"全球市场 / 收入榜","date":"2026-11-04","title":"Sensor Tower最新官方全球收入榜仍为2026年10月","summary":"官方完整TOP10显示ROBLOX位居全球手游收入第一，Whiteout Survival第5、Kingshot第9；全球App Store与Google Play消费者支出为62.6亿美元，排除第三方Android市场。","impact":"策略子集继续保留Whiteout Survival与Kingshot及10月真实统计期，不把每日检查伪装成新月榜。","source":"Sensor Tower官方","url":"https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-october-2026"},
    {"category":"城建生存 / 节日活动","date":"2026-11-20","title":"Kingshot发布Stories of Thanks感恩节活动","summary":"Century Games官方新闻页于11月20日列出Stories of Thanks活动，承接11月Harvest Season节日运营。","impact":"Kingshot继续位居Google #1、iOS #2；活动与高位同窗，但单日榜位不能证明活动效果。","source":"Century Games / Kingshot官方","url":"https://www.centurygames.com/games/kingshot"},
    {"category":"城建生存 / 节日活动","date":"2026-11-26","title":"Whiteout Survival同步开放丰收宴会与Cyber Week窗口","summary":"Google Play美国区商品页显示Grand Banquet与Cyber Week活动均持续至12月2日。","impact":"Whiteout Survival本期iOS #1、Google #2；节日内容覆盖社交活动和付费促销，需在12月2日后复核榜位。","source":"Google Play美国区商品页","url":"https://play.google.com/store/apps/details?id=com.gof.global&hl=en_US&gl=US"},
    {"category":"经典IP / 版本更新","date":"2026-11-19","title":"Age of Empires Mobile上线Chaos Rift跨帝国玩法","summary":"官方维护公告要求更新至Android 1.15.103.0、iOS 1.15.104.0，并开放Chaos Rift跨帝国资源战场。","impact":"产品本期Google进入#55、iOS #31；版本节点可核验，但不能直接解释回榜。","source":"Age of Empires Mobile官方","url":"https://steamcommunity.com/app/2783360/announcements/"},
    {"category":"塔防 / 赛季更新","date":"2026-11-24","title":"Plants on Fire开启Magic Fortune赛季","summary":"Apple版本资料列出新随从、四种变体、Astral Blessings与感恩节登录活动。","impact":"产品回榜次日下降至iOS #41，说明首日进入尚未形成稳定上涨证据。","source":"Apple App Store","url":"https://apps.apple.com/us/app/id6776076449"},
    {"category":"塔防 / IP联动","date":"2026-11-12","title":"Arknights × Monster Hunter联动持续至12月7日","summary":"官方确认Thunder in the Azure Dream、限定寻访及活动商店，第一阶段开放至11月30日。","impact":"产品Google回升至#44但iOS未进榜；联动窗口与榜位变化同窗，仍不能直接推断因果。","source":"Arknights官方","url":"https://www.arknights.global/news/5092"},
    {"category":"现代战争 / IP联动","date":"2026-11-17","title":"Supremacy: World War 3宣布十周年G.I. Joe联动","summary":"Twin Harbour宣布将推出专属G.I. Joe赛季，这是该产品首次IP联动。","impact":"产品本期iOS #34、Google #53；正式赛季时间尚未公布，继续作为未来版本观察点。","source":"Twin Harbour / Games Press","url":"https://www.gamespress.com/GI-Joe-Joins-the-Fight-in-Supremacy-World-War-3-for-the-Games-10th-Ann"},
    {"category":"IP新品 / 首发运营","date":"2026-11-16","title":"Transformers: Eternal War进入首发活动承接期","summary":"Apple版本资料显示1.2.1于11月16日更新，并列出Optimus Prime等限时付费活动。","impact":"产品当前iOS #32且仍属近90天新品；活动结束后能否保持前40是首发承接关键。","source":"Apple App Store","url":"https://apps.apple.com/us/app/id6772922295"},
    {"category":"科幻策略 / 周年运营","date":"2026-10-20","title":"Foundation: Galactic Frontier完成首周年活动","summary":"FunPlus官方称Astral Alignment于10月19日至11月7日分阶段开放。","impact":"产品本期Google #31、iOS #37；活动结束后的榜位更适合观察周年用户留存。","source":"FunPlus官方","url":"https://funplus.com/foundation-galactic-frontier-anniversary-event/"},
    {"category":"软启动 / 新品观察","date":"2026-11-23","title":"大型发行商软启动产品清单更新","summary":"Mobilegamer.biz更新Supercell、EA、Moon Active、Zynga等发行商在测产品，并明确相关信息仍可能变化。","impact":"软启动供给显示头部厂商继续测试跨品类玩法；未获得官方确认的项目只作为新品雷达，不写成正式发布。","source":"Mobilegamer.biz（报道）","url":"https://mobilegamer.biz/the-soft-launch-games-you-need-to-know-about/"},
]
for index, item in enumerate(news, 1):
    item["rank"] = index


closing = [
    {"type":"判断","title":"Google稳定、iOS波动仍集中在后半段","detail":"Google 2进2出且最大单日升降仅4位；iOS 3进3出，并出现+11、+10与多款±7以上变化，平台波动显著更高。"},
    {"type":"判断","title":"成熟SLG继续出现明显跨端分化","detail":"Last Shelter: Survival在iOS进入#52却从Google掉榜；War Z从iOS掉榜但Google仍#30，不能用单端榜位替代产品整体判断。"},
    {"type":"判断","title":"节日活动集中，但榜面尚未证明持续收益","detail":"Kingshot、Whiteout Survival与Plants on Fire均有可核验节日或赛季节点；当前只有同窗关系，不能把单日名次直接归因于活动。"},
    {"type":"关注","title":"下一有效快照：核验五款进入/回榜产品","detail":"重点观察Age of Empires Mobile、Call of Dragons、Last Shelter: Survival、Guns of Glory与MARVEL SNAP能否连续留榜。"},
    {"type":"关注","title":"未来2—3个快照：确认iOS塔防波动","detail":"The Tower升至#35、Plants on Fire降至#41、The Battle Cats掉榜；若方向连续，才升级为产品级持续判断。"},
    {"type":"关注","title":"12月2日后：复核Century Games双头部活动承接","detail":"Whiteout Survival的Grand Banquet/Cyber Week与Kingshot节日活动均处窗口期；活动结束后比较两端连续榜位。"},
]


google_history = load(f"data/history/google-play/{DATE}.json")
ios_history = load(f"data/history/ios/{DATE}.json")
revenue = load("data/sensortower-global-strategy-revenue-latest.json")
ios_source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


def anchors(rows):
    return " · ".join(f"#{rank} {rows[rank - 1]['gameName']}" for rank in (1, 25, 60))


def count_status(store, status):
    return sum(row["comparison90d"]["status"] == status for row in datasets[store]["now"])


brief = {
    "date": DATE, "timezone": "Asia/Shanghai", "title": "Google榜面趋稳，iOS后半段继续高换位",
    "summary": "较11月25日前一有效快照，Google Play 2进2出，Warpath +4、Vikings与Rise of Castles各−4；iOS 3进3出，Last Day on Earth +11、The Tower +10，Last Beacon、The Battle Cats与Last Shelter: War Z掉榜。Google有1款近90天新品、9款飙升，iOS有2款新品、9款飙升。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与品类影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}-01.json", "iconOverrideBundles": [f"assets/market-icons-{STAMP}-{i:02d}.json" for i in range(2, (len(cards) + 4) // 5 + 1)],
    "rankingSources": {"googlePlay": f"data/games-{STAMP}.json", "ios": f"data/ios-games-{STAMP}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREV}.json", "ios": f"data/ios-games-{PREV}.json"},
    "rankingDynamics": {
        "googlePlay": {"label": datasets["googlePlay"]["label"], "sourceTime": f"北京时间 {google_history['sourceCapturedAt']} 直连抓取", "anchors": "榜单锚点：" + anchors(datasets["googlePlay"]["now"]), "products": google_products},
        "ios": {"label": datasets["ios"]["label"], "sourceTime": f"Apple RSS 北京时间 {ios_source_date:%Y-%m-%d %H:%M:%S}（源更新：{ios_history['sourceUpdated']}）", "anchors": "榜单锚点：" + anchors(datasets["ios"]["now"]), "products": ios_products},
    },
    "marketNews": news, "closing": closing, "globalStrategyRevenue": revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": count_status("googlePlay", "new"), "surge90d": count_status("googlePlay", "surge"), "baselineAvailable": True, "baselineDate": BASELINE},
        "ios": {"top60": 60, "newRelease90d": count_status("ios", "new"), "surge90d": count_status("ios", "surge"), "baselineAvailable": True, "baselineDate": BASELINE},
    },
    "sources": [
        {"label":"Google Play美国区策略畅销榜直连", "url":google_history["sourceUrl"], "capturedAt":google_history["sourceCapturedAt"]},
        {"label":"Apple官方美国区iPhone策略畅销RSS", "url":ios_history["sourceUrl"], "updated":ios_history["sourceUpdated"], "sourceDateBeijing":ios_history["dataDate"]},
        {"label":"Sensor Tower全球收入榜中的策略产品", "url":revenue["sourceUrl"], "period":revenue["period"], "estimateAsOf":revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": f"reports/{DATE}.md", "json": f"data/market-brief-{STAMP}.json"},
}


def markdown(value):
    lines = [f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "", "## 数据源与口径", "", f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取）", f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`", f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}", f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}", "- 对比基准：各自上一份最终有效快照为2026-11-25。", f"- 近90天：两端{BASELINE}精确同口径TOP60基准均可用；新品先按各自商店releaseDate判定。", "", "## 1. 双榜当日异动产品", ""]
    for store in ("googlePlay", "ios"):
        section = value["rankingDynamics"][store]
        lines += [f"### {section['label']}", "", section["sourceTime"] + "。", ""]
        for item in section["products"]:
            lines += [f"#### {item['gameName']}｜{item['changeLabel']}", "", item["analysis"], ""]
    lines += ["## 2. 策略手游市场热点", "", value["newsMethod"], ""]
    for item in news:
        lines += [f"### {item['rank']}. [{item['title']}]({item['url']})", "", f"- 类别：{item['category']}｜发布日期：{item['date']}｜来源：{item['source']}", f"- 事实摘要：{item['summary']}", f"- 市场含义：{item['impact']}", ""]
    lines += ["## 3. 综合判断与后续关注", ""]
    for item in closing:
        lines += [f"### {item['type']}｜{item['title']}", "", item["detail"], ""]
    lines += ["## 4. Sensor Tower 全球收入榜中的策略产品", "", f"- 数据期：{revenue['periodLabel']}｜{revenue['strategyMatches']}款核心策略产品", ""]
    for item in revenue["rankings"]:
        lines += [f"- 全球总榜 #{item['rank']}｜{item['gameName']}｜{item['publisher']}｜{item['movementLabel']}｜{item['yoyRevenueLabel']}"]
    lines += ["", revenue["methodologyNote"], "", "## 下载与来源", "", f"- JSON：`{value['downloads']['json']}`", f"- Markdown：`{value['downloads']['markdown']}`", ""]
    return "\n".join(lines)


save(f"data/market-brief-{STAMP}.json", brief)
(ROOT / f"reports/{DATE}.md").write_text(markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = sorted([entry] + [item for item in manifest["reports"] if item["date"] != DATE], key=lambda item: item["date"], reverse=True)
save("reports/manifest.json", manifest)
print(f"Wrote {len(cards)} product cards, {len(news)} news items and {(len(cards) + 4) // 5} icon bundles")
