#!/usr/bin/env python3
"""Generate the Beijing 2026-09-01 market brief and archive entry."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-09-01"
STAMP = "20260901"


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, value):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def product(game_name, product_id, store, tone, label, analysis):
    return {"gameName": game_name, "productId": product_id, "iconKey": f"{store}:{product_id}", "tone": tone, "changeLabel": label, "analysis": analysis}


google_history = load("data/history/google-play/2026-09-01.json")
ios_history = load("data/history/ios/2026-09-01.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))

google_products = [
    product("Age of Empires Mobile", "com.proximabeta.aoemobile", "googlePlay", "entry", "回榜 · #49", "8月31日刚掉出Google，本期回到#49；iOS同时上升8位至#30。官方Hero Reset活动于8月31日开启并与双端回升窗口重合，但仍需后续排名确认是否只是活动期回补。"),
    product("Age of Apes", "com.tap4fun.ape.gplay", "googlePlay", "exit", "掉榜 · 上期#60", "上期已经降至Google最后一名，本期掉榜，符合明确的榜尾风险兑现；iOS仍无对应TOP60排名，暂无跨端承接证据。"),
    product("Overgeared Hero: Merge RPG", "com.fiveminlab.overgeared.hero.backpack.merge", "googlePlay", "up", "+8 · #37", "由#45升至#37，iOS也由#55升至#46；这是今日少数双端同向上涨产品，但未发现可确认的同期重大版本节点，先记为共同付费回补信号。"),
    product("Lordrush", "com.s01.global", "googlePlay", "up", "+8 · #27", "由#35升至#27，iOS保持#24附近；两端都位于TOP30，且仍在近90天新品窗口，说明首发后仍有双端收入承接，但单日上涨不等于建立新中枢。"),
    product("Game of Thrones: Conquest ™", "com.wb.goog.got.conquest", "googlePlay", "down", "−11 · #59", "由#48降至#59并进入高风险区，而iOS反而升至#45；本期是Android侧明显回撤，不能据此判断产品整体收入同步走弱。"),
    product("Warpath: Ace Shooter", "com.wondergames.warpath.gp", "googlePlay", "down", "−7 · #58", "由#51降至#58，iOS继昨日掉榜后仍未回榜；双端都靠近或低于TOP60边界，下一次更新若Google继续下移，才可确认短期共同走弱。"),
]

ios_products = [
    product("Fire Emblem Heroes", "1181774280", "ios", "entry", "回榜 · #31", "成熟战棋RPG从榜外回到#31，是今日iOS最高位进入产品。官方9月1—7日竞技场奖励英雄排期与回榜同期，但没有证据可把收入变化完全归因于这一项。"),
    product("Kingdom Clash：Medieval Defense", "1611722542", "ios", "entry", "回榜 · #47", "8月25日曾位于同样的#47，随后掉榜，本期回到原位置；Google未进入对应TOP60，先按iOS侧周期性回补而非新增长处理。"),
    product("Last Light: Wasteland", "6754545818", "ios", "entry", "回榜 · #50", "8月28日以#56进入、8月31日掉榜，本期回到#50。产品上架已超过90天，仍需至少两次连续留榜才能区分买量脉冲与稳定收入。"),
    product("SD Gundam G Generation ETERNAL", "6692615881", "ios", "entry", "进入 · #53", "项目历史首次进入iOS #53；8月28日500日庆典及限定机体活动与进榜窗口重合，但Google美国策略TOP60没有对应排名，先视为iOS侧IP活动信号。"),
    product("The Tower - Idle Tower Defense", "1575590830", "ios", "entry", "回榜 · #59", "成熟放置塔防在8月20日后再次进入iOS，但位置仅#59且Google未入榜；没有可确认重大节点，属于高风险榜尾回补。"),
    product("Game of Kings:The Blood Throne", "1071673198", "ios", "entry", "进入 · #60", "九年长线联盟SLG首次进入本项目历史快照并压线#60；最近公开版本仅标错误修复，暂无证据支持活动归因，优先按存量核心用户短时付费信号观察。"),
    product("The Battle Cats", "850057092", "ios", "exit", "掉榜 · 上期#51", "上期仍在iOS #51，本期掉榜；Google策略榜没有对应位置，单端榜尾回撤暂不外推到产品整体表现。"),
    product("Idle Heroes - Idle Games", "1153461915", "ios", "exit", "掉榜 · 上期#53", "昨日首次进入项目快照#53，本期即掉榜，说明十周年长线活动尚未形成连续TOP60位置；这验证了昨日仅按待验证信号处理的必要性。"),
    product("Galaxy Defense: Fortress TD", "6740189002", "ios", "exit", "掉榜 · 上期#56", "iOS由#56掉榜，但Google仍位于#55；变化仍集中在双端榜尾，当前更像平台换防而非产品全面退出。"),
    product("Guns of Glory: Lost Island", "1274354704", "ios", "exit", "掉榜 · 上期#57", "iOS从#57掉榜，Google则升至#35；成熟SLG在两端表现分化，不能用iOS掉榜替代对Android收入的判断。"),
    product("Star Trek Fleet Command", "1427744264", "ios", "exit", "掉榜 · 上期#58", "昨日以#58回榜后立即退出，但Google仍稳定在#22；本期再次显示该产品当前收入重心明显偏Android。"),
    product("Lords Mobile x Transformers", "1071976327", "ios", "exit", "掉榜 · 上期#59", "iOS从#59掉榜，Google仍处#29；联动长线产品在Android仍有中段承接，本次只定义为iPhone榜尾退出。"),
    product("Kingdom Guard:Tower Defense TD", "1570095804", "ios", "up", "+19 · #41", "由#60升至#41，Google也由#57升至#52；两端同步回升但仍未脱离中后段，暂无明确活动证据，继续观察是否能连续两次上行。"),
    product("Watcher of Realms - US", "6741674823", "ios", "up", "+13 · #32", "由#45升至#32，是iOS第二大上涨；Google没有同口径排名，当前只能确认iPhone侧收入回补，原因仍待核验。"),
    product("Lands of Jail", "6738469826", "ios", "down", "−11 · #52", "由#41降至#52，而Google升至#25并成为今日榜单锚点；同产品跨端差扩大到27位，是今天最明显的平台分化之一。"),
    product("Sea War: Uboat Raid", "6447612873", "ios", "down", "−11 · #54", "由#43降至#54，Google则位于#48；两端都落入后段但尚未同步掉榜，下一次更新需关注iOS是否继续滑出。"),
    product("Warhammer 40,000: Tacticus ™", "1599937506", "ios", "down", "−8 · #38", "Lysander活动开启后昨日升至#30，今日回落至#38；Google反而升至#30。活动信号仍存在，但双端峰值开始分化，尚不能定义新的稳定中枢。"),
]

news = [
    {"category": "IP活动与榜单", "date": "2026-08-28", "title": "SD Gundam G Generation ETERNAL开启500日庆典", "summary": "官方英文账号宣布产品上线500日纪念活动；当前商店同时展示Full Armor Hyaku-Shiki Kai限定内容，iOS本期首次进入#53。", "impact": "高达IP与限定机体为本期iOS进榜提供了明确同期节点，但Google策略榜未同步进入，需要用后续三日区分单端活动峰值与持续增长。", "source": "Bandai Namco / G Generation ETERNAL官方", "url": "https://x.com/ggene_eternalEN"},
    {"category": "活动与跨端", "date": "2026-08-31", "title": "Age of Empires Mobile开启Hero Reset活动窗口", "summary": "官方排期显示Hero Reset自8月31日开始并持续7日；产品本期回到Google #49，iOS同时上升8位至#30。", "impact": "双端同期回升提高了活动相关性的可信度，但Google仍在榜尾，需验证活动结束前能否连续留榜。", "source": "Age of Empires Mobile官方", "url": "https://www.facebook.com/aoemobile/posts/758561977064142/"},
    {"category": "长线运营", "date": "2026-08-31", "title": "Fire Emblem Heroes公布9月首周竞技场奖励英雄", "summary": "官方公布9月1日0时至9月7日15:59（太平洋时间）的下一轮Arena Bonus Heroes；产品本期以#31回到iOS榜。", "impact": "成熟战棋产品以较高位置回榜，说明固定竞技场排期仍可形成付费/活跃窗口，但单一周榜不能替代连续收入观察。", "source": "Fire Emblem Heroes官方", "url": "https://www.facebook.com/FEHeroes.EN/posts/1640271828097926/"},
    {"category": "活动持续性", "date": "2026-08-30", "title": "Tacticus的Lysander活动出现双端峰值分化", "summary": "Heroes of the Chapter传奇活动开启后，Google由#33升至#30，iOS则从#30回落至#38。", "impact": "明确活动不一定在两端形成同日峰值；后续应分别追踪卡池/礼包承接，避免用一端曲线代替另一端。", "source": "Apple App Store / Snowprint Studios", "url": "https://apps.apple.com/us/app/warhammer-40-000-tacticus/id1599937506"},
    {"category": "版本与跨端", "date": "2026-08-25", "title": "GFL2的Chiral Redundancy继续维持Android高位", "summary": "8月26日维护加入OTs-14、Nemesis: Gnosis、限时剧情与Tile Transformation；本期Google仍在#13，iOS继续榜外。", "impact": "版本后的Android收入信号已连续两个快照保持TOP15，而iOS没有同步承接，跨端支付节奏分化仍在延续。", "source": "GIRLS' FRONTLINE 2官方公告", "url": "https://gf2exilium.sunborngame.com/NewsInfo?id=393&typeId=3"},
    {"category": "IP联动", "date": "2026-08-25", "title": "State of Survival继续推进《如龙8》联动", "summary": "活动加入春日一番、桐生一马与真岛吾朗，并配置联盟Boss、节奏玩法、感染摩托和排行榜内容。", "impact": "产品本期Google #40、继续小幅回落，暂未形成明确联动上行；应使用完整7日窗口判断回流和付费承接。", "source": "FunPlus", "url": "https://funplus.com/state-of-survival-x-like-a-dragon-infinite-wealth-crossover-event/"},
    {"category": "开发工具", "date": "2026-08-28", "title": "腾讯游戏在Gamescom展示AI研发与运营工具", "summary": "腾讯Central Tech展示GIGA自主智能体、Motus 3D动画、WeTest Acorn自动化测试与ACE安全能力。", "impact": "策略产品内容密集且版本频繁，工具价值应优先从版本频率、资产产能和运营响应验证，而不是直接对应单日榜位。", "source": "PocketGamer.biz / Tencent Games", "url": "https://www.pocketgamer.biz/tencent-games-showcases-ai-tools-for-game-development-at-gamescom/"},
    {"category": "市场报告", "date": "2026-08-26", "title": "Moloco研究强调首发月之后的高价值用户", "summary": "研究覆盖55款新游、超过15亿美元IAP和2000多万付费用户，并指出高价值用户常在首发月之后才开始付费。", "impact": "Lordrush、Top Force与Top Lords仍在近90天窗口，评估重点应从首发榜位转向持续创意、联盟沉淀和中期付费转化。", "source": "PocketGamer.biz / Moloco", "url": "https://www.pocketgamer.biz/report-only-2500-of-190000-mobile-games-released-in-2025-surpassed-500000-downloads/"},
    {"category": "社交能力", "date": "2026-08-26", "title": "Discord将Social Layer扩展到移动端", "summary": "Discord公布Social Layer移动端适配，并引用PC游戏研究中的留存和启动天数提升结果。", "impact": "联盟与跨服关系是SLG留存核心，但PC因果结果不能直接套用手机；需等实际接入后再看召回、组队和付费变化。", "source": "Discord", "url": "https://discord.com/press-releases/introducing-new-tools-to-power-game-discovery-and-social-play"},
    {"category": "渠道变现", "date": "2026-08-25", "title": "Sensor Tower披露部分手游D2C收入占比超过30%", "summary": "美国H1 2026数据中，部分头部手游已有30%以上销售来自商店外Web Store。", "impact": "商店畅销榜只覆盖平台内收入；Star Trek、Lords Mobile等成熟策略产品还需结合官网直购和联盟社群判断真实收入重心。", "source": "PocketGamer.biz / Sensor Tower", "url": "https://www.pocketgamer.biz/sensor-tower-reveals-the-hidden-impact-of-d2c-revenue-in-mobile-games/"},
]

closing = [
    {"type": "判断", "title": "Google恢复为一进一出，iOS换防仍大但已延伸到中段", "detail": "Google仅Age of Empires回榜、Age of Apes掉榜，整体稳定；iOS继续六进六出，其中四款进入位于#50—60，但Fire Emblem以#31回榜，说明本期波动不再完全局限于最后十名。"},
    {"type": "判断", "title": "Age of Empires与Overgeared形成双端同向信号", "detail": "Age of Empires在Google回榜且iOS升至#30，Overgeared两端分别+8与+9；两组都需要连续快照确认，但比单端上涨更值得优先跟踪。"},
    {"type": "判断", "title": "活动节点正在表现出明显的平台支付节奏差", "detail": "Tacticus在Google升至#30、iOS回落至#38；SD Gundam随500日庆典进入iOS却未进入Google策略榜。明确活动窗口仍不能推导两端同步收入。"},
    {"type": "关注", "title": "截至9月2日：验证SD Gundam与Fire Emblem回榜质量", "detail": "若SD Gundam守住TOP55、Fire Emblem保持TOP40，再把两者分别升级为可持续活动/长线回榜信号；任一立即掉榜则维持短峰判断。"},
    {"type": "关注", "title": "截至9月3日：跟踪Age of Empires与Overgeared双端同步性", "detail": "检查Age of Empires能否在Google继续留榜且iOS保持TOP35，并观察Overgeared两端是否至少守住当前区间；只有连续两次同向才判断共同上行。"},
    {"type": "关注", "title": "9月2—4日：复核Tacticus与iOS榜尾新进入产品", "detail": "观察Tacticus双端差是否继续扩大；同时检查Last Light、The Tower、Game of Kings等本期进入产品能否连续留榜，以评估iOS换防的留存率。"},
]

brief = {
    "date": DATE, "timezone": "Asia/Shanghai",
    "title": "Age of Empires双端回升，SD Gundam随500日庆典进入iOS；iOS继续六进六出",
    "summary": "与8月31日相比，Google Play仅一进一出，Age of Empires回到#49；iOS连续第二次六进六出，Fire Emblem以#31回榜、SD Gundam首次进入#53。Overgeared与Kingdom Guard双端同步上涨，但Tacticus出现Google升至#30、iOS回落至#38的活动峰值分化。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {"googlePlay": "data/games-20260901.json", "ios": "data/ios-games-20260901.json"},
    "previousRankingSources": {"googlePlay": "data/games-20260831.json", "ios": "data/ios-games-20260831.json"},
    "rankingDynamics": {
        "googlePlay": {"label": "Google Play · Android", "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取", "anchors": "榜单锚点：#1 Kingshot · #25 Lands of Jail · #60 Vikings: War of Clans PvP", "products": google_products},
        "ios": {"label": "App Store · iPhone/iOS", "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}", "anchors": "榜单锚点：#1 Pokémon GO · #25 Tiles Survive! · #60 Game of Kings:The Blood Throne", "products": ios_products},
    },
    "marketNews": news, "closing": closing,
    "status": {"googlePlay": {"top60": 60, "newRelease90d": 5, "surge90d": 0, "baselineAvailable": False}, "ios": {"top60": 60, "newRelease90d": 2, "surge90d": 0, "baselineAvailable": False}},
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
    ],
    "downloads": {"markdown": "reports/2026-09-01.md", "json": "data/market-brief-20260901.json"},
}


def build_markdown(value):
    lines = [f"# {DATE} 美国区策略手游双端市场日报", "", f"**{value['title']}**", "", value["summary"], "", "## 数据源与口径", "", f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）", f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`", "- Google锚点：#1 Kingshot · #25 Lands of Jail · #60 Vikings: War of Clans PvP", "- iOS锚点：#1 Pokémon GO · #25 Tiles Survive! · #60 Game of Kings:The Blood Throne", "- 对比基准：各自上一份有效快照为2026-08-31。", "- 近90天状态：Google新上榜5款、iOS新上榜2款；两端均缺少2026-06-03精确同口径TOP60基准，较老产品暂不判断飙升。", "", "## 1. 双榜当日异动产品", ""]
    for store in ("googlePlay", "ios"):
        section = value["rankingDynamics"][store]
        lines += [f"### {section['label']}", "", f"{section['sourceTime']}。", ""]
        for item in section["products"]:
            lines += [f"#### {item['gameName']}｜{item['changeLabel']}", "", item["analysis"], ""]
    lines += ["## 2. 策略手游市场热点", "", value["newsMethod"], ""]
    for index, item in enumerate(value["marketNews"], 1):
        lines += [f"### {index}. [{item['title']}]({item['url']})", "", f"- 类别：{item['category']}｜发布日期：{item['date']}｜来源：{item['source']}", f"- 事实摘要：{item['summary']}", f"- 市场含义：{item['impact']}", ""]
    lines += ["## 3. 综合判断与后续关注", ""]
    for item in value["closing"]:
        lines += [f"### {item['type']}｜{item['title']}", "", item["detail"], ""]
    lines += ["## 下载与来源", "", f"- JSON：`{value['downloads']['json']}`", "- Google Play直连源：https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US", "- Apple官方RSS：https://itunes.apple.com/us/rss/topgrossingapplications/limit=200/genre=7017/json", ""]
    return "\n".join(lines)


save("data/market-brief-20260901.json", brief)
(ROOT / "reports/2026-09-01.md").write_text(build_markdown(brief), encoding="utf-8")
manifest = load("reports/manifest.json")
entry = {"date": DATE, "title": brief["title"], "summary": brief["summary"], "markdown": brief["downloads"]["markdown"], "json": brief["downloads"]["json"]}
manifest["updated"] = DATE
manifest["reports"] = [entry] + [item for item in manifest["reports"] if item["date"] != DATE]
save("reports/manifest.json", manifest)
print(f"Wrote market brief with {len(google_products) + len(ios_products)} product cards and {len(news)} news items")
