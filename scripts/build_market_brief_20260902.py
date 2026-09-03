#!/usr/bin/env python3
"""Generate the Beijing 2026-09-02 market brief and archive entry."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-02"
STAMP = "20260902"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, value):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def product(game_name, product_id, store, tone, label, analysis):
    return {
        "gameName": game_name,
        "productId": product_id,
        "iconKey": f"{store}:{product_id}",
        "tone": tone,
        "changeLabel": label,
        "analysis": analysis,
    }


google_history = load("data/history/google-play/2026-09-02.json")
ios_history = load("data/history/ios/2026-09-02.json")
global_revenue = load("data/sensortower-global-revenue-top10-latest.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))

google_products = [
    product("Raid Rush: Tower Defense TD", "com.wireless.defenseland", "googlePlay", "entry", "回榜 · #58", "8月28日曾位于Google #60，随后连续两个快照掉榜，本期回到#58；iOS同时上涨11位至#31。两端共同回升比单端榜尾噪声更值得观察，但8月26日商品页版本仅注明性能与错误修复，暂无证据确认具体原因。"),
    product("Last Shelter: War Z", "com.more.lastshelter.gp", "googlePlay", "entry", "进入 · #60", "2026年6月24日上架后首次进入项目Google TOP60，按上架日期标记为近三个月新上榜；iOS有对应商品但未入榜。当前仅压线#60，8月26日联盟玩法更新与进榜时间接近，仍只能作为待验证首发/版本信号。"),
    product("Warpath: Ace Shooter", "com.wondergames.warpath.gp", "googlePlay", "exit", "掉榜 · 上期#58", "上期已降至Google #58，本期掉榜；iOS也继续处于榜外。双端均无TOP60承接，是本期较明确的短期弱化信号，但两次快照仍不足以推导长期下行。"),
    product("Vikings: War of Clans PvP", "com.plarium.vikings", "googlePlay", "exit", "掉榜 · 上期#60", "Google从最后一名掉榜，iOS也由上期#57退出，是今日唯一双端共同掉榜产品。由于两边此前都处榜尾，先记为榜尾风险同步兑现，而不是产品长线收入结论。"),
    product("Game of Thrones: Conquest ™", "com.wb.goog.got.conquest", "googlePlay", "up", "+10 · #49", "从Google #59升至#49，iOS也上升3位至#42，形成双端同向回补；未发现与9月1日完全对应的官方重大活动节点，当前只确认收入位置回升，不能断言原因。"),
    product("MARVEL SNAP", "com.nvsgames.snap", "googlePlay", "up", "+6 · #37", "Google升6位至#37，iOS升13位至#22。官方8月31日开启AXIS: Inversion赛季，包含新季票、角色、地点和整月活动；节点与双端上涨重合，但仍需下一个快照验证是否形成持续赛季峰值。"),
]

ios_products = [
    product("Galaxy Defense: Fortress TD", "6740189002", "ios", "entry", "回榜 · #57", "昨日掉榜后立即回到iOS #57，Google则小降1位至#56；两端都紧贴榜尾，属于换防信号，尚未显示稳定上行。"),
    product("Guns of Glory: Lost Island", "1274354704", "ios", "entry", "回榜 · #58", "iOS在掉榜一天后回到#58，Google仍位于中段。成熟SLG的两端收入重心继续偏Android，本次iPhone回榜只能按短期付费回补观察。"),
    product("Lords Mobile x Transformers", "1071976327", "ios", "entry", "回榜 · #59", "iOS在掉榜一天后压线回到#59，Google则下降3位至#32。联动产品在Android仍有较强承接，但iPhone位置尚未摆脱榜尾风险。"),
    product("SD Gundam G Generation ETERNAL", "6692615881", "ios", "exit", "掉榜 · 上期#53", "昨日随500日庆典首次进入项目iOS #53，本期即掉榜，Google也未进入策略TOP60；庆典节点尚未转化为连续榜位，因此继续按短期IP活动峰值处理。"),
    product("Vikings: War of Clans PvP", "966810173", "ios", "exit", "掉榜 · 上期#57", "iOS从#57掉榜，Google也从#60退出，成为本期唯一双端共同掉榜产品；两端都是从榜尾离开，需要后续回榜情况判断是否只是日内换防。"),
    product("Game of Kings:The Blood Throne", "1071673198", "ios", "exit", "掉榜 · 上期#60", "昨日首次进入项目历史快照且仅位于#60，本期立即退出；公开版本仍以错误修复为主，没有证据支持特定活动解释，符合存量核心用户短时付费脉冲特征。"),
    product("The Tower - Idle Tower Defense", "1575590830", "ios", "up", "+26 · #33", "由#59跃升至#33，是今日iOS最大涨幅；Google策略榜无对应排名，也未找到同期可确认重大节点，因此只标记为单端强回补信号，下一次排名决定其是否脱离脉冲。"),
    product("Mobile Legends: Bang Bang.US", "6741568655", "ios", "up", "+23 · #13", "从#36升至#13，9月StarLight上线Hanzo“Fangs of Slaughter”皮肤及会员权益与上涨窗口重合。当前可确认的是iOS付费位置跃升，仍不能仅凭一天把全部变化归因于皮肤。"),
    product("MARVEL SNAP - Hero Card Game", "1592081003", "ios", "up", "+13 · #22", "iOS升至#22，Google也升至#37，是今日最明确的双端共同上涨之一。AXIS: Inversion新赛季于8月31日公布完整季票、角色与活动排期，为上涨提供同期节点，后续需看赛季首周留存。"),
    product("Raid Rush: Tower Defense TD", "1662335371", "ios", "up", "+11 · #31", "iOS由#42升至#31，Google同时从榜外回到#58。双端同步提高了信号质量，但现有商店版本只注明性能优化和错误修复，原因继续保持待核验。"),
    product("Last Day on Earth: Survival", "1241932094", "ios", "up", "+10 · #41", "由#51升至#41，Google策略榜无对应排名；成熟生存产品出现iPhone单端回补，但没有足以支撑活动归因的同期官方节点。"),
    product("Clash of Clans", "529479190", "ios", "up", "+6 · #2", "iOS升至#2，Google也升2位至#8；9月1日开启WWE“Search for Cena”整月活动，包含限定皮肤、场景、挑战、临时兵种和部落玩法。双端同向与节点重合，但需用9月首周判断峰值持续性。"),
    product("Kingdom Clash：Medieval Defense", "1611722542", "ios", "down", "−9 · #56", "昨日回榜#47后回落至#56，Google仍无对应TOP60排名；当前再次落入榜尾风险区，说明昨日回补尚未形成稳定位置。"),
    product("Age of Empires Mobile", "6476261995", "ios", "down", "−9 · #39", "iOS由#30降至#39，Google也小降2位至#51。8月31日Hero Reset活动后的双端回升只维持一个快照，本期表明活动相关信号正在降温，但仍未双端掉榜。"),
    product("Overgeared Hero: Merge RPG", "6755585789", "ios", "down", "−8 · #54", "iOS由#46降至#54，Google也下降2位至#39；昨日双端同向上涨后今天共同回吐，暂不能认定建立了更高榜位中枢。"),
]

news = [
    {"category": "IP联动", "date": "2026-09-01", "title": "Clash of Clans开启WWE“Search for Cena”整月活动", "summary": "官方列出9月1—30日限定WWE英雄皮肤与场景、John Cena挑战、临时兵种、部落冲刺和多段资源/装备活动。", "impact": "Clash of Clans本期iOS升至#2、Google升至#8，双端同向与活动首日重合；限定外观、部落玩法和战斗事件的贡献仍需拆分。", "source": "Supercell / Clash of Clans官方", "url": "https://supercell.com/en/games/clashofclans/blog/news/wwe-search-for-cena-steps-into-the-ring/"},
    {"category": "新赛季", "date": "2026-08-31", "title": "MARVEL SNAP发布AXIS: Inversion赛季", "summary": "新赛季加入Superior Iron Man季票、多个Series 5角色、两处新地点、21日登录日历、Draft与Team Clash等整月活动。", "impact": "产品本期Google +6、iOS +13，形成双端共同上行；赛季首周能否维持TOP25/40将决定这是首日付费峰值还是榜位抬升。", "source": "MARVEL SNAP官方", "url": "https://marvelsnap.com/new-season-axis-inversion/"},
    {"category": "皮肤与会员", "date": "2026-09-01", "title": "Mobile Legends美国版上线9月StarLight", "summary": "北美官方账号确认Hanzo“Fangs of Slaughter”专属皮肤与StarLight会员权益开放，包含皮肤、Crystals of Aurora等内容。", "impact": "iOS美国版本期从#36升至#13，节点与付费跃升重合；需验证皮肤热度能否维持两次以上快照。", "source": "Mobile Legends: Bang Bang北美官方", "url": "https://www.facebook.com/MobileLegendsNorthAmerica/posts/september-starlight-is-officially-available-for-only-300-diamonds-you-can-get-th/1079137584518950/"},
    {"category": "新品与榜单", "date": "2026-08-26", "title": "Last Shelter: War Z更新联盟玩法后首次进入Google TOP60", "summary": "Google Play商品页显示产品6月24日上架、8月26日更新联盟玩法与Doomsday Transport；本期以#60首次进入项目榜。", "impact": "这是近90天新品的首个可见Google收入信号，但位置仅在榜尾；需同时观察留榜率与iOS是否出现同步承接。", "source": "Google Play美国区商品页", "url": "https://play.google.com/store/apps/details?id=com.more.lastshelter.gp&hl=en_US&gl=US"},
    {"category": "报道 / 软启动", "date": "2026-08-31", "title": "报道：腾讯Level Infinite测试Crownstone Survival", "summary": "Mobilegamer.biz援引AppMagic称该生存新游拟在菲律宾、法国、印尼、土耳其和美国Google Play软启动；具体范围仍可能变化。", "impact": "腾讯继续测试生存经营赛道，新品若在美国开放，值得对照Last War、Kingshot等产品的轻玩法入口与4X承接方式。", "source": "Mobilegamer.biz（报道）", "url": "https://mobilegamer.biz/the-soft-launch-games-you-need-to-know-about/"},
    {"category": "报道 / 新品测试", "date": "2026-08-31", "title": "报道：Century Games准备Frozen Manor: Merge Mystery早期测试", "summary": "报道援引AppMagic称，Whiteout Survival厂商Century Games出现新的Android合成产品页面，目前尚未记录Google Play下载。", "impact": "若测试推进，将检验点点互动是否把冰雪题材从4X生存延伸到合成经营；当前尚处无下载早期阶段，不能视为正式发行。", "source": "Mobilegamer.biz（报道）", "url": "https://mobilegamer.biz/the-soft-launch-games-you-need-to-know-about/"},
    {"category": "报道 / 塔防测试", "date": "2026-08-31", "title": "报道：Small Giant在菲律宾软启动Defend the Castle", "summary": "报道援引AppMagic称，Zynga旗下Small Giant在菲律宾Google Play测试一款卡牌收集塔防产品。", "impact": "卡牌收集与塔防融合继续成为策略新品测试方向，可与Kingshot、Raid Rush等不同深度的塔防获量/长期养成结构对照。", "source": "Mobilegamer.biz（报道）", "url": "https://mobilegamer.biz/the-soft-launch-games-you-need-to-know-about/"},
    {"category": "活动复盘", "date": "2026-08-31", "title": "Age of Empires Mobile的Hero Reset信号开始回落", "summary": "官方Hero Reset活动于8月31日开启；昨日产品Google回榜、iOS升至#30，本期两端分别降至#51和#39。", "impact": "明确活动也可能只形成短时收入回补；后续应把活动持续时间与商店榜位分别记录，避免把单日回榜写成长期增长。", "source": "Age of Empires Mobile官方", "url": "https://www.facebook.com/aoemobile/posts/758561977064142/"},
    {"category": "IP联动", "date": "2026-08-28", "title": "State of Survival推进《如龙8》联动", "summary": "FunPlus公布春日一番、桐生一马和真岛吾朗英雄，以及联盟Boss、节奏挑战、感染摩托和排行榜活动。", "impact": "产品本期Google小降至#42、iOS仍未进榜，暂未显示联动带来双端同步上行；应继续观察完整活动周期。", "source": "FunPlus官方", "url": "https://funplus.com/state-of-survival-x-like-a-dragon-infinite-wealth-crossover-event/"},
    {"category": "版本运营", "date": "2026-08-25", "title": "GFL2的Chiral Redundancy版本继续维持Android高位", "summary": "官方公告列出OTs-14、Nemesis: Gnosis、限时剧情和Tile Transformation等内容；产品本期Google仍处#13，iOS继续榜外。", "impact": "版本后的Android信号已连续保持前段，而iOS没有对应承接；这是当前最明显的跨端支付节奏分化之一。", "source": "GIRLS' FRONTLINE 2官方", "url": "https://gf2exilium.sunborngame.com/NewsInfo?id=393&typeId=3"},
]

closing = [
    {"type": "判断", "title": "Google换榜扩大到两进两出，iOS换防收敛为三进三出", "detail": "Google新增Raid Rush与Last Shelter: War Z、掉出Warpath与Vikings；iOS进入/掉榜数量由昨日六组收敛到三组，但中段仍有多款两位数涨幅。"},
    {"type": "判断", "title": "MARVEL SNAP、Raid Rush和Clash of Clans形成双端共同信号", "detail": "MARVEL SNAP两端分别+6/+13，Raid Rush在Google回榜且iOS +11，Clash of Clans两端+2/+6；其中前者和后者有明确新赛季/IP活动节点，Raid Rush原因仍待核验。"},
    {"type": "判断", "title": "新品增加，但榜面主导权仍在成熟产品与活动窗口", "detail": "Google近90天新品增至6款，Last Shelter: War Z仅#60；当天最大位移仍来自The Tower、MLBB和MARVEL SNAP等成熟产品，说明新品入榜不等于改变头中部结构。"},
    {"type": "关注", "title": "截至9月3日：验证Last Shelter: War Z首个留榜结果", "detail": "若继续留在TOP60并脱离#60，才把本次进榜升级为可持续首发信号；若立即掉榜，则维持榜尾首次试探判断，同时检查iOS是否仍无排名。"},
    {"type": "关注", "title": "9月3—4日：跟踪MARVEL SNAP与Clash of Clans活动峰值", "detail": "检查MARVEL SNAP能否保持iOS TOP25、Google TOP40，以及Clash of Clans能否维持iOS TOP3、Google TOP10；满足条件再判断新赛季/IP活动形成短期中枢。"},
    {"type": "关注", "title": "截至9月4日：复核iOS两位数上涨留存率", "detail": "逐项检查The Tower、MLBB、Raid Rush与Last Day on Earth是否至少守住本期区间；若多数回吐，继续把本期定义为iOS单日波动而非市场整体上行。"},
]

brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Last Shelter: War Z首次进入Google；MARVEL SNAP与Clash of Clans双端上行",
    "summary": "与9月1日相比，Google Play两进两出：Raid Rush回榜#58、近90天新品Last Shelter: War Z进入#60；iOS三进三出，但The Tower、MLBB、MARVEL SNAP和Raid Rush出现两位数上涨。Vikings是唯一双端共同掉榜产品，MARVEL SNAP、Raid Rush与Clash of Clans则形成值得连续验证的双端共同信号。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": "data/games-20260902.json", "ios": "data/ios-games-20260902.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260901.json", "ios": "data/ios-games-20260901.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Lands of Jail · #60 Last Shelter: War Z", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}", "anchors": "榜单锚点：#1 Pokémon GO · #25 Castle Busters · #60 Top Heroes", "products": ios_products},
    },
    "marketNews": news,
    "closing": closing,
    "globalRevenueTop10": global_revenue,
    "status": {
        "googlePlay": {"top60": 60, "newRelease90d": 6, "surge90d": 0, "baselineAvailable": False},
        "ios": {"top60": 60, "newRelease90d": 2, "surge90d": 0, "baselineAvailable": False},
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
        {"label": "Sensor Tower全球手游月收入TOP10", "url": global_revenue["sourceUrl"], "period": global_revenue["period"], "estimateAsOf": global_revenue["estimateAsOf"]},
    ],
    "downloads": {"markdown": "reports/2026-09-02.md", "json": "data/market-brief-20260902.json"},
}


def build_markdown(value):
    lines = [
        f"# {DATE} 美国区策略手游双端市场日报",
        "",
        f"**{value['title']}**",
        "",
        value["summary"],
        "",
        "## 数据源与口径",
        "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        "- Google锚点：#1 Kingshot · #25 Lands of Jail · #60 Last Shelter: War Z",
        "- iOS锚点：#1 Pokémon GO · #25 Castle Busters · #60 Top Heroes",
        "- 对比基准：各自上一份有效快照为2026-09-01。",
        "- 近90天状态：Google新上榜6款、iOS新上榜2款；两端均缺少2026-06-04精确同口径TOP60基准，较老产品暂不判断飙升。",
        "",
        "## 1. 双榜当日异动产品",
        "",
    ]
    for store in ("googlePlay", "ios"):
        section = value["rankingDynamics"][store]
        lines += [f"### {section['label']}", "", f"{section['sourceTime']}。", ""]
        for item in section["products"]:
            lines += [f"#### {item['gameName']}｜{item['changeLabel']}", "", item["analysis"], ""]
    lines += ["## 2. 策略手游市场热点", "", value["newsMethod"], ""]
    for index, item in enumerate(value["marketNews"], 1):
        lines += [
            f"### {index}. [{item['title']}]({item['url']})",
            "",
            f"- 类别：{item['category']}｜发布日期：{item['date']}｜来源：{item['source']}",
            f"- 事实摘要：{item['summary']}",
            f"- 市场含义：{item['impact']}",
            "",
        ]
    lines += ["## 3. 综合判断与后续关注", ""]
    for item in value["closing"]:
        lines += [f"### {item['type']}｜{item['title']}", "", item["detail"], ""]
    revenue = value["globalRevenueTop10"]
    lines += [
        "## 4. Sensor Tower 全球手游月收入 TOP10",
        "",
        f"- 数据期：{revenue['periodLabel']}｜官方页面：{revenue['publicationLabel']}｜估算截至：{revenue['estimateAsOf']}",
        f"- 口径：{revenue['scope']['region']}｜{revenue['scope']['stores']}｜{revenue['scope']['exclusions']}",
        f"- 市场总览：全球手游消费者支出约${revenue['marketSummary']['globalConsumerSpendingUsd'] / 1_000_000_000:g}B，环比+{revenue['marketSummary']['monthOverMonthPercent']:g}%",
        f"- 原始来源：[{revenue['source']}]({revenue['sourceUrl']})",
        "",
        "| 排名 | 游戏 | 发行商 | 较上期 |",
        "|---:|---|---|---|",
    ]
    for item in revenue["rankings"]:
        lines.append(f"| {item['rank']} | {item['gameName']} | {item['publisher']} | {item['movementLabel']} |")
    lines += [
        "",
        "### 本期官方解读",
        "",
    ]
    lines += [f"- {item}" for item in revenue["officialHighlights"]]
    lines += ["", revenue["methodologyNote"], ""]
    lines += [
        "## 下载与来源",
        "",
        f"- JSON：`{value['downloads']['json']}`",
        "- Google Play直连源：https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US",
        "- Apple官方RSS：https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json",
        "",
    ]
    return "\n".join(lines)


save("data/market-brief-20260902.json", brief)
(ROOT / "reports/2026-09-02.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(google_products) + len(ios_products)} product cards and {len(news)} news items")
