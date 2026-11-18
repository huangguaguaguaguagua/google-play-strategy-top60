#!/usr/bin/env python3
"""Generate the Beijing 2026-11-18 dual-store market brief and archive."""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from daily_update_20260820 import data_uri

ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP, PREV = "2026-11-18", "20261118", "20261117"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value, compact=False):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=None if compact else 2,
                                 separators=(",", ":") if compact else None) + "\n", encoding="utf-8")


datasets = {
    "googlePlay": {"now": load(f"data/games-{STAMP}.json"), "prior": load(f"data/games-{PREV}.json"), "id": "packageName"},
    "ios": {"now": load(f"data/ios-games-{STAMP}.json"), "prior": load(f"data/ios-games-{PREV}.json"), "id": "appId"},
}


def card(store, product_id, tone, analysis):
    data = datasets[store]
    now = next((x for x in data["now"] if str(x[data["id"]]) == str(product_id)), None)
    old = next((x for x in data["prior"] if str(x[data["id"]]) == str(product_id)), None)
    row = now or old
    if tone == "entry" and now and not old:
        label = f"进入/回榜 · #{now['rank']}"
    elif tone == "exit" and old and not now:
        label = f"掉榜 · 上期#{old['rank']}"
    elif tone in ("up", "down") and now and old:
        delta = old["rank"] - now["rank"]
        if (delta > 0) != (tone == "up"):
            raise RuntimeError((store, product_id, delta))
        label = f"{'+' if delta > 0 else '−'}{abs(delta)} · #{now['rank']}"
    else:
        raise RuntimeError((store, product_id, tone))
    return {"gameName": row["gameName"], "productId": str(product_id),
            "iconKey": f"{store}:{product_id}", "tone": tone, "changeLabel": label, "analysis": analysis}


google_products = [
    card("googlePlay", "com.doradogames.conflictnations.worldwar3", "entry", "进入/回榜#58。现代全球战争产品以实时持久战局、经济与外交管理为核心，本次只触及末三位，先记为榜尾待验证信号。"),
    card("googlePlay", "com.nvsgames.snap", "exit", "前一快照#59后掉榜。卡组构筑与漫威角色收集未守住Google末位；iOS同产品今日反而上升至#48，跨端走势分化。"),
    card("googlePlay", "com.YoStarEN.Arknights", "up", "单日上升16位至#29，为Google最大涨幅。官方复刻活动持续至11月19日，时间相邻但不据此断言单一因果。"),
    card("googlePlay", "com.yottagames.mafiawar", "down", "单日下跌7位至#43，为Google最大跌幅。成熟黑帮城建与联盟战争仍在榜中后段，暂按单日回吐处理。"),
    card("googlePlay", "com.gtarcade.ioe.global", "up", "继昨日双端上行后再升5位至#25。3.0.1联盟商店、联盟奖励与护送事件改版形成可核验节点，但持续性仍需后续快照。"),
    card("googlePlay", "com.topwar.gp", "up", "单日上升4位至#44。合成升级与联盟战争产品改善至中后段，暂无足够一手证据确认具体活动原因。"),
]

ios_products = [
    card("ios", "1571873795", "entry", "回榜#46。200次免费招募窗口结束后，11月17日新泳装角色与总力战继续开放；活动与回榜相邻但仍只记录为待验证信号。"),
    card("ios", "1570095804", "entry", "回榜#49。塔防关卡承接英雄养成与联盟长期循环，位置仍在后十二名，需观察是否能连续留榜。"),
    card("ios", "6755173751", "entry", "回榜#51。塔防新品此前掉榜后重新进入后十名；单次回榜不能说明首发承接已经稳定。"),
    card("ios", "1611722542", "exit", "前一快照#52后掉榜。中世纪防守与合并成长产品未守住后十名，属于榜尾轮换。"),
    card("ios", "6755585789", "exit", "前一快照#55后掉榜。合并养成新品的短期回榜未形成连续性，仍处首发验证。"),
    card("ios", "1071976327", "exit", "前一快照#56后掉榜；Google同产品仍在#31，成熟联盟4X再次出现明显跨端位置差。"),
    card("ios", "6741674823", "down", "单日下跌18位至#60，为iOS最大跌幅并落到末位。若下一快照掉榜，才形成连续风险确认。"),
    card("ios", "1592081003", "up", "单日上升12位至#48。Google同产品已经掉榜，说明iOS回升只可按单端信号解读。"),
    card("ios", "6476261995", "down", "单日下跌12位至#53。IP城建与联盟战争落入后八名，暂未发现与当天位移直接对应的官方重大节点。"),
    card("ios", "6746636289", "up", "单日上升10位至#25。锻造经营、放置成长与战斗循环回到前25，仍需下一快照验证是否只是短时峰值。"),
    card("ios", "921022358", "up", "继昨日改善后再升9位至#8，进入前十。星战角色收集与小队回合战斗的长线运营出现连续两日上行信号。"),
]

all_cards = google_products + ios_products
for start in range(0, len(all_cards), 5):
    bundle = {}
    for item in all_cards[start:start + 5]:
        store = "googlePlay" if item["iconKey"].startswith("googlePlay:") else "ios"
        data = datasets[store]
        row = next(x for x in data["now"] + data["prior"] if str(x[data["id"]]) == item["productId"])
        bundle[item["iconKey"]] = data_uri(row.get("iconUrl") or row.get("rankIconUrl"), (160, 160))
    save(f"assets/market-icons-{STAMP}-{start // 5 + 1:02d}.json", bundle, compact=True)


news = [
    {"category":"全球市场 / 收入榜","date":"2026-11-03","title":"Sensor Tower最新官方全球收入榜仍为2026年10月","summary":"官方博客尚未发布11月榜；10月全球App Store与Google Play消费者支出为62.6亿美元，并排除第三方Android市场。","impact":"策略子集继续保留10月真实统计期与两款命中产品，不因工作日检查改写月份。","source":"Sensor Tower官方","url":"https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-october-2026"},
    {"category":"角色策略 / 活动","date":"2026-11-17","title":"Blue Archive进入泳装角色与总力战后半段窗口","summary":"官方活动页继续开放Pandemonium Upon the Waves，商店版本说明列出11月17日泳装角色招募与Hieronymus总力战。","impact":"产品今日iOS回榜#46；活动与榜位同窗，但当前仍处后十五名。","source":"Blue Archive官方","url":"https://bluearchive.nexon.com/events/2026/11/pandemonium"},
    {"category":"塔防 / 复刻活动","date":"2026-11-05","title":"Arknights复刻活动持续至11月19日","summary":"官方公告显示The Masses' Travels复刻阶段开放至11月19日，并将在结束后加入常驻Score。","impact":"产品今日Google +16至#29、iOS仍在#31附近；连续双端中段位置值得继续验证。","source":"Arknights官方","url":"https://arknights.global/news/5045"},
    {"category":"IP新品 / 全球上线","date":"2026-11-12","title":"Transformers: Eternal War完成全球上线","summary":"官方商店页以汽车人/霸天虎联合、角色小队与放置战斗为主，并于11月12日上线。","impact":"iOS仍位于#22且按releaseDate归类为近90天新品；观察首发IP热度后的留榜能力。","source":"Google Play官方商品页","url":"https://play.google.com/store/apps/details?id=com.wanda.transformers.gg.am&hl=en_US&gl=US"},
    {"category":"现代战争 / 回榜","date":"2026-11-18","title":"Supremacy: World War 3进入Google #58","summary":"官方资料将产品描述为跨数日或数周的实时全球战争，包含经济、研究、军队与外交管理。","impact":"此次只进入末三位，先判断为榜尾待验证信号，不推断获量原因。","source":"Conflict of Nations官方","url":"https://cm.conflictnations.com/"},
    {"category":"联盟4X / 连续上涨","date":"2026-11-18","title":"Infinity Kingdom连续第二天双端改善","summary":"3.0.1版本加入联盟商店、联盟奖励与护送/拦截事件；今日Google再升至#25，iOS维持#30。","impact":"双端连续性强于单日峰值，但仍不能把榜位变化等同版本收入增长。","source":"Infinity Kingdom官方","url":"https://infinitykingdom.gtarcade.com/en/news"},
    {"category":"IP长线运营","date":"2026-11-03","title":"Game of Thrones: Conquest继续Highgarden Harvest Festival","summary":"官方11月预告公布新装备、英雄与龙装；产品今日Google守在#60、iOS升至#40。","impact":"双端都在榜但Google仍是末位，活动承接呈现明显平台差异。","source":"Game of Thrones: Conquest官方","url":"https://www.gotconquest.com/news/2026/11/03/november-preview-highgarden-harvest-festival-6/"},
    {"category":"IP联动 / 素材更新","date":"2026-11-18","title":"Doomsday: Last Survivors商品ICON更新为Dune Part 3","summary":"Google美国区商品页当前名称与ICON均突出Dune Part 3联动，本次已同步本地静态ICON。","impact":"产品位于Google #55；联动素材可核验，但榜尾位置仍需观察。","source":"Google Play官方商品页","url":"https://play.google.com/store/apps/details?id=com.igg.android.doomsdaylastsurvivors&hl=en_US&gl=US"},
    {"category":"塔防RPG / 下跌","date":"2026-11-18","title":"Watcher of Realms单日跌18位至iOS #60","summary":"商品页仍以英雄收集、阵营编成与技能时机驱动的防守战斗为核心。","impact":"落到末位构成明确榜尾风险；是否掉榜需下一有效快照确认。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/id6741674823"},
    {"category":"IP城建 / 下跌","date":"2026-11-18","title":"Age of Empires Mobile下跌12位至iOS #53","summary":"产品以帝国城建、文明英雄与联盟战场为核心，今日进入后八名。","impact":"暂无可核验重大节点解释当天回落，按单日风险信号处理。","source":"Apple App Store美国区","url":"https://apps.apple.com/us/app/id6476261995"},
]
for index, item in enumerate(news, 1):
    item["rank"] = index

closing = [
    {"type":"判断","title":"Google席位稳定、但中段上行更集中","detail":"Google仅1进1出，Arknights +16、Infinity Kingdom +5；主要变化不是大规模榜尾换血，而是活动与版本窗口下的中段改善。"},
    {"type":"判断","title":"iOS榜尾轮换继续快于Google","detail":"iOS 3进3出，并出现Watcher −18、Age of Empires −12；后十名的单日波动仍显著高于Google。"},
    {"type":"判断","title":"精确90天基准首次可用，飙升状态不再pending","detail":"两端均有2026-08-20完整同口径快照：Google 7款、iOS 7款满足提升超过5位；iOS另有Transformers一款近90天新品。"},
    {"type":"关注","title":"下一快照：核验七款进入/掉榜产品","detail":"重点观察Supremacy能否离开Google末三位，Blue Archive与Kingdom Guard能否连续留榜，以及Watcher是否从iOS #60掉出。"},
    {"type":"关注","title":"未来1—2个快照：验证Arknights与Infinity Kingdom连续性","detail":"若Arknights在复刻结束后仍守住前30、Infinity Kingdom两端继续保持前30，才升级为更稳定的运营信号。"},
    {"type":"关注","title":"本周内：观察Transformers首发承接","detail":"以iOS #22和近90天新品状态为基准；若IP首发窗口后仍维持前30，才说明角色收集与放置循环具有初步承接。"},
]

google_history = load(f"data/history/google-play/{DATE}.json")
ios_history = load(f"data/history/ios/{DATE}.json")
revenue = load("data/sensortower-global-strategy-revenue-latest.json")
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


def anchors(rows):
    return " · ".join(f"#{rank} {rows[rank - 1]['gameName']}" for rank in (1, 25, 60))


def count_status(store, status):
    return sum(x["comparison90d"]["status"] == status for x in datasets[store]["now"])


brief = {
    "date": DATE, "timezone": "Asia/Shanghai",
    "title": "Google一进一出、iOS三进三出；精确90天基准首次生效",
    "summary": "较11月17日有效快照，Google Play一进一出，Supremacy回榜、MARVEL SNAP掉榜，Arknights +16；iOS三进三出，Blue Archive、Kingdom Guard与Evo Defense回榜，Watcher −18至#60。精确8月20日基准可用后，Google与iOS各识别7款近90天飙升，iOS另有1款近90天新品。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与品类影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}-01.json",
    "iconOverrideBundles": [f"assets/market-icons-{STAMP}-{i:02d}.json" for i in range(2, (len(all_cards) + 4) // 5 + 1)],
    "rankingSources": {"googlePlay": f"data/games-{STAMP}.json", "ios": f"data/ios-games-{STAMP}.json"},
    "previousRankingSources": {"googlePlay": f"data/games-{PREV}.json", "ios": f"data/ios-games-{PREV}.json"},
    "rankingDynamics": {
        "googlePlay": {"label":"Google Play · Android", "sourceTime":f"北京时间 {google_history['sourceCapturedAt']} 直连抓取", "anchors":"榜单锚点：" + anchors(datasets["googlePlay"]["now"]), "products":google_products},
        "ios": {"label":"App Store · iPhone/iOS", "sourceTime":f"Apple RSS 北京时间 {source_date:%Y-%m-%d}（源更新：{ios_history['sourceUpdated']}）", "anchors":"榜单锚点：" + anchors(datasets["ios"]["now"]), "products":ios_products},
    },
    "marketNews": news, "closing": closing, "globalStrategyRevenue": revenue,
    "status": {
        "googlePlay": {"top60":60, "newRelease90d":count_status("googlePlay", "new"), "surge90d":count_status("googlePlay", "surge"), "baselineAvailable":True, "baselineDate":"2026-08-20"},
        "ios": {"top60":60, "newRelease90d":count_status("ios", "new"), "surge90d":count_status("ios", "surge"), "baselineAvailable":True, "baselineDate":"2026-08-20"},
    },
    "sources": [
        {"label":"Google Play美国区策略畅销榜直连", "url":google_history["sourceUrl"], "capturedAt":google_history["sourceCapturedAt"]},
        {"label":"Apple官方美国区iPhone策略畅销RSS", "url":ios_history["sourceUrl"], "updated":ios_history["sourceUpdated"], "sourceDateBeijing":ios_history["dataDate"]},
        {"label":"Sensor Tower全球收入榜中的策略产品", "url":revenue["sourceUrl"], "period":revenue["period"], "estimateAsOf":revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown":f"reports/{DATE}.md", "json":f"data/market-brief-{STAMP}.json"},
}


def markdown(value):
    lines = [f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "", "## 数据源与口径", "",
             f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取）",
             f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
             f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors']}", f"- iOS锚点：{value['rankingDynamics']['ios']['anchors']}",
             "- 对比基准：各自上一份最终有效快照为2026-11-17；只记录相邻有效快照的榜面信号。",
             "- 近90天：两端2026-08-20精确同口径TOP60基准均可用；新品先按各自商店releaseDate判定，再计算较老产品的基准名次差。", "", "## 1. 双榜当日异动产品", ""]
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
    lines += ["## 4. Sensor Tower 全球收入榜中的策略产品", "", f"- 数据期：{revenue['periodLabel']}｜估算截至：{revenue['estimateAsOf']}", f"- 策略筛选：官方全球收入TOP10中命中{revenue['strategyMatches']}款核心策略产品；这不是完整策略品类TOP10", f"- 原始来源：[{revenue['source']}]({revenue['sourceUrl']})", "", "| 全球总榜 | 游戏 | 发行商 | 策略类型 | 较上月榜位 | 单品收入同比 |", "|---:|---|---|---|---|---|"]
    for item in revenue["rankings"]:
        lines.append(f"| {item['rank']} | {item['gameName']} | {item['publisher']} | {item['strategyGenre']} | {item['movementLabel']} | {item['yoyRevenueLabel']} |")
    lines += ["", revenue["methodologyNote"], "", "## 下载与来源", "", f"- JSON：`{value['downloads']['json']}`", f"- Markdown：`{value['downloads']['markdown']}`", ""]
    return "\n".join(lines)


save(f"data/market-brief-{STAMP}.json", brief)
(ROOT / f"reports/{DATE}.md").write_text(markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date":DATE, "title":brief["title"], "summary":brief["summary"], "markdown":brief["downloads"]["markdown"], "json":brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = sorted([entry] + [x for x in manifest["reports"] if x["date"] != DATE], key=lambda x: x["date"], reverse=True)
save("reports/manifest.json", manifest)
print(f"Wrote {len(all_cards)} product cards, {len(news)} news items and {(len(all_cards) + 4) // 5} icon bundles")
