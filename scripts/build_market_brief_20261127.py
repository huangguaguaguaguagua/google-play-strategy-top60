#!/usr/bin/env python3
"""Build the 2026-11-27 market brief, archive report and local icon bundles."""

from datetime import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, PREV, BASELINE = "2026-11-27", "20261127", "20261126", "2026-08-29"


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
    key = datasets[store]["id"]
    return next(row for row in datasets[store]["now" if current else "prior"] if str(row[key]) == str(product_id))


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
    card("googlePlay", "com.ProjectMoon.LimbusCompany", "entry", "Limbus Company进入#58，iOS同步进入#33；11月26日1.120.0更新与热修信息是可核验同窗节点，但双端进榜仍只记为待验证信号。"),
    card("googlePlay", "com.more.dayzsurvival.gp", "entry", "Last Shelter: Survival回榜#60，iOS同产品降至#59；两端都处最后两名，属于明确榜尾风险。"),
    card("googlePlay", "com.plarium.vikings", "exit", "Vikings: War of Clans前一日#58后掉榜，延续昨日榜尾风险；未发现可确认的新运营节点。"),
    card("googlePlay", "com.mrtgd2us.google", "exit", "Duck Survival前一日#60后退出TOP60；缺少连续留榜证据，先按榜尾轮换处理。"),
    card("googlePlay", "leyi.ageofspirits", "up", "近90天新品Age of Spirits上升4位至#55，但仍在后六名；仍处首发验证，不能据一天变化推演后续。"),
    card("googlePlay", "com.wb.goog.got.conquest", "up", "Game of Thrones: Conquest上升4位至#45，iOS同日大升至#25；官方11月版本与活动窗口可核验，跨端同步改善仍需连续快照确认。"),
    card("googlePlay", "com.fiveminlab.overgeared.hero.backpack.merge", "up", "Overgeared Hero上升4位至#40，而iOS下降至#55；同一产品跨端方向相反，暂不归因于共同版本节点。"),
    card("googlePlay", "com.Sunborn.SnqxExilium.Glo", "down", "GIRLS' FRONTLINE 2下降17位至#34，为Google最大跌幅；仍在中段，单日回吐先作为待验证信号。"),
    card("googlePlay", "com.riotgames.league.wildrift", "down", "Wild Rift下降8位至#44且iOS掉榜；它属于MOBA交叉分类，不扩写为核心SLG趋势。"),
    card("googlePlay", "com.YoStarEN.Arknights", "down", "Arknights下降8位至#59，进入末二位风险区；此前联动窗口未形成可确认的持续榜位支撑。"),
]


ios_products = [
    card("ios", "6444112366", "entry", "Limbus Company进入#33，Google同步进入#58；11月26日官方更新与热修同窗，但尚无证据证明榜位由该更新直接驱动。"),
    card("ios", "6751086804", "entry", "Dragon Traveler回榜#39，仍属2026年上线产品；当前应按回榜信号观察，不把BUFF 101合作直接写成原因。"),
    card("ios", "850057092", "entry", "The Battle Cats回榜#42；PONOS宣布PAC-MAN联动11月26日开启，因此可列为活动峰值候选，但需后续快照验证持续性。"),
    card("ios", "6741674823", "entry", "Watcher of Realms - US回榜#43；美国专属包仍由Skystone与沐瞳产品体系运营，本次缺少新的同步重大节点。"),
    card("ios", "6760406772", "entry", "Last Shelter: War Z回榜#54，仍处后七名；最终集团证据仍不足，继续保留疑似标注。"),
    card("ios", "1570095804", "exit", "Kingdom Guard前一日#54后掉榜；成熟塔防产品未形成连续改善，先记榜尾轮换。"),
    card("ios", "1181774280", "exit", "Fire Emblem Heroes前一日#56后掉榜；成熟战术RPG的单日退出不足以判断长期衰退。"),
    card("ios", "1274354704", "exit", "Guns of Glory前一日回榜#57后即掉榜，回榜未形成连续留存。"),
    card("ios", "1480616990", "exit", "Wild Rift前一日#58后掉榜，Google同步下降至#44；MOBA交叉分类在两端同时走弱。"),
    card("ios", "6450953550", "exit", "Top Heroes前一日#60后掉榜，但Google上升至#36；跨端差距明显扩大。"),
    card("ios", "1035712810", "up", "Game of Thrones: Conquest上升28位至#25，为两端最大涨幅；11月版本与War for the Throne活动是可核验背景，仍需下一快照确认是否为活动峰值。"),
    card("ios", "1642607669", "up", "Game of Thrones: Dragonfire上升9位至#15，Google位于#35；iOS商业化位置明显更强，但一天变化不等同长期趋势。"),
    card("ios", "1496227521", "up", "Magic: The Gathering Arena上升5位至#31，仍处中段；卡牌策略与核心4X需分开理解。"),
    card("ios", "6776076449", "down", "近90天新品Plants on Fire下降12位至#53，连续回吐并进入后八名；仍处首发验证。"),
    card("ios", "6755173751", "down", "Evo Defense下降11位至#57，进入后四名风险区；下一有效快照将检验是否掉榜。"),
    card("ios", "6738469826", "down", "Lands of Jail下降10位至#50，而Google位于#27；两端商业化强度差距继续扩大。"),
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
    {"category":"双端异动 / 版本更新","date":"2026-11-26","title":"Limbus Company发布1.120.0定期更新及热修安排","summary":"Project Moon官方公告确认11月26日定期更新后发现若干问题，并公布热修时间。","impact":"产品本期iOS进入#33、Google进入#58；更新与双端进榜同窗，但没有公开归因数据，暂按待验证信号。","source":"Project Moon / Steam官方公告","url":"https://store.steampowered.com/news/app/1973530/view/667257305800114906"},
    {"category":"塔防 / IP联动","date":"2026-11-26","title":"The Battle Cats开启PAC-MAN联动","summary":"PONOS宣布PAC-MAN限定角色、关卡与任务于11月26日开放。","impact":"The Battle Cats本期iOS回榜#42，可列为活动峰值候选；是否持续需观察联动期后榜位。","source":"PONOS / Inven Global","url":"https://www.invenglobal.com/articles/29165/the-battle-cats-begins-pac-man-collaboration-on-november-26"},
    {"category":"全球市场 / 收入榜","date":"2026-11-04","title":"Sensor Tower最新官方全球收入榜仍为2026年10月","summary":"官方完整TOP10显示Whiteout Survival全球收入第5、Kingshot第9；口径为全球App Store与Google Play消费者支出，排除第三方Android市场。","impact":"策略子集继续保留10月真实统计期，不把每日检查伪装成新月榜。","source":"Sensor Tower官方","url":"https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-october-2026"},
    {"category":"长线4X / 版本更新","date":"2026-11-17","title":"Game of Thrones: Conquest发布2026_11版本说明","summary":"官方11月版本说明更新功能与问题修复，随后又开放War for the Throne相关SOP活动窗口。","impact":"产品本期iOS上升28位至#25、Google升至#45；活动与版本同窗，但单日涨幅仍需复核。","source":"Game of Thrones: Conquest官方","url":"https://www.gotconquest.com/news/2026/11/17/release-notes-2026_11/"},
    {"category":"城建生存 / 节日活动","date":"2026-11-23","title":"Kingshot进入Harvest Feast活动窗口","summary":"官方商店活动卡显示Harvest Feast持续至12月3日。","impact":"Kingshot本期Google与iOS均为#1；高位与活动同窗不等于活动单独驱动收入。","source":"Apple App Store美国区商品页","url":"https://apps.apple.com/us/app/id6739554056"},
    {"category":"城建生存 / 节日活动","date":"2026-11-24","title":"Whiteout Survival开放感恩节与Cyber Week内容","summary":"美国区商店活动信息显示宴会、节日任务与促销窗口覆盖11月底至12月初。","impact":"Whiteout Survival本期两端均为#2；应在活动结束后复核连续名次。","source":"Google Play美国区商品页","url":"https://play.google.com/store/apps/details?id=com.gof.global&hl=en_US&gl=US"},
    {"category":"塔防 / 赛季更新","date":"2026-11-24","title":"Plants on Fire开启Magic Fortune赛季","summary":"Apple版本资料列出新随从、变体、Astral Blessings与感恩节登录活动。","impact":"产品本期iOS下降12位至#53，说明活动上线没有形成可确认的连续榜位改善。","source":"Apple App Store","url":"https://apps.apple.com/us/app/id6776076449"},
    {"category":"现代战争 / IP联动","date":"2026-11-17","title":"Supremacy: World War 3宣布十周年G.I. Joe联动","summary":"Twin Harbour宣布将推出专属G.I. Joe赛季，为该产品首次IP联动。","impact":"产品本期iOS升至#40、Google位于#55；正式赛季时间仍是后续验证点。","source":"Twin Harbour / Games Press","url":"https://www.gamespress.com/GI-Joe-Joins-the-Fight-in-Supremacy-World-War-3-for-the-Games-10th-Ann"},
    {"category":"IP新品 / 首发运营","date":"2026-11-16","title":"Transformers: Eternal War进入首发活动承接期","summary":"Apple版本资料显示1.2.1更新并列出Optimus Prime等限时付费活动。","impact":"产品当前iOS #30且属近90天新品；活动结束后能否守住前40是首发承接关键。","source":"Apple App Store","url":"https://apps.apple.com/us/app/id6772922295"},
    {"category":"软启动 / 新品观察","date":"2026-11-23","title":"大型发行商软启动产品清单更新","summary":"Mobilegamer.biz更新Supercell、EA、Moon Active、Zynga等发行商在测产品，并明确相关信息仍可能变化。","impact":"未获官方确认的项目只作为新品雷达，不写成正式发布或当前榜单趋势。","source":"Mobilegamer.biz（报道）","url":"https://mobilegamer.biz/the-soft-launch-games-you-need-to-know-about/"},
]
for index, item in enumerate(news, 1):
    item["rank"] = index


closing = [
    {"type":"判断","title":"iOS波动显著高于Google","detail":"Google 2进2出，除GIRLS' FRONTLINE 2下降17位外多数变动不超过8位；iOS 5进5出，并出现+28、−12、−11与−10，后半段轮换更剧烈。"},
    {"type":"判断","title":"Limbus双端同步进入，但证据只支持同窗关系","detail":"Limbus Company在11月26日官方更新后同时进入iOS #33和Google #58；现阶段只能视为待验证信号，不能断言更新造成收入增长。"},
    {"type":"判断","title":"节日与IP活动密集，产品承接出现分化","detail":"The Battle Cats在PAC-MAN联动首日回榜，Game of Thrones: Conquest大涨；Plants on Fire则在赛季窗口内跌至#53，活动存在不等于榜位必然改善。"},
    {"type":"关注","title":"下一有效快照：核验七款进入/回榜产品","detail":"重点观察Limbus Company双端、Last Shelter Google包，以及Dragon Traveler、The Battle Cats、Watcher of Realms和Last Shelter: War Z能否连续留榜。"},
    {"type":"关注","title":"未来2—3个快照：确认两项活动峰值候选","detail":"若Game of Thrones: Conquest与The Battle Cats继续保持或提升，才将单日信号升级为短期活动承接；快速回落则保留为脉冲。"},
    {"type":"关注","title":"下一个工作日：恢复精确90天基准","detail":"11月27日对应基准日8月29日无快照，老产品内部为pending；下次精确工作日基准可用时再恢复飙升判定。"},
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
    "date": DATE, "timezone": "Asia/Shanghai", "title": "Limbus双端同步进入，iOS榜面高波动",
    "summary": "较11月26日前一有效快照，Google Play 2进2出，GIRLS' FRONTLINE 2下降17位；iOS 5进5出，Game of Thrones: Conquest上升28位，Plants on Fire下降12位。Google有1款、iOS有2款近90天新品；因8月29日精确基准缺失，老产品内部保持pending并按常规展示。",
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
        "googlePlay": {"top60": 60, "newRelease90d": count_status("googlePlay", "new"), "surge90d": 0, "pending90d": count_status("googlePlay", "pending"), "baselineAvailable": False, "baselineDate": BASELINE},
        "ios": {"top60": 60, "newRelease90d": count_status("ios", "new"), "surge90d": 0, "pending90d": count_status("ios", "pending"), "baselineAvailable": False, "baselineDate": BASELINE},
    },
    "sources": [
        {"label":"Google Play美国区策略畅销榜直连", "url":google_history["sourceUrl"], "capturedAt":google_history["sourceCapturedAt"]},
        {"label":"Apple官方美国区iPhone策略畅销RSS", "url":ios_history["sourceUrl"], "updated":ios_history["sourceUpdated"], "sourceDateBeijing":ios_history["dataDate"]},
        {"label":"Sensor Tower全球收入榜中的策略产品", "url":revenue["sourceUrl"], "period":revenue["period"], "estimateAsOf":revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": f"reports/{DATE}.md", "json": f"data/market-brief-{STAMP}.json"},
}


def markdown(value):
    lines = [f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "", "## 数据源与口径", "", f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取）", f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`", f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}", f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}", "- 对比基准：各自上一份最终有效快照为2026-11-26。", f"- 近90天：精确基准日{BASELINE}无同口径快照；近期上架产品仍按各商店releaseDate标记新品，较老产品内部pending并按常规展示。", "", "## 1. 双榜当日异动产品", ""]
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
