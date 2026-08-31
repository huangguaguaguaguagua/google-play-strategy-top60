#!/usr/bin/env python3
"""Generate the Beijing 2026-08-31 market brief and archive entry."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-08-31"
STAMP = "20260831"


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


google_history = load("data/history/google-play/2026-08-31.json")
ios_history = load("data/history/ios/2026-08-31.json")
google_games = load("data/games-20260831.json")
ios_games = load("data/ios-games-20260831.json")
captured = datetime.fromisoformat(google_history["sourceCapturedAt"])
source_date = datetime.fromisoformat(ios_history["sourceUpdated"].replace("Z", "+00:00")).astimezone(ZoneInfo("Asia/Shanghai"))


brief = {
    "date": DATE,
    "timezone": "Asia/Shanghai",
    "title": "Tacticus双端同步上行，GFL2出现跨端分化；iOS周末后六进六出",
    "summary": "与8月28日上一份有效快照相比，Google Play两进两出，iOS六进六出。Warhammer 40,000: Tacticus在Google升至#33、iOS升至#30，是本期最清晰的双端共同信号；GIRLS' FRONTLINE 2则在Google跃升至#14、iOS由#21掉榜。iOS的六款进入产品全部位于#53—60，换防范围虽大但主要集中在榜尾。",
    "newsMethod": "编辑热度：按时效、厂商/IP体量、双榜关联度与对策略品类的影响综合排序；不是第三方阅读量或舆情指数。",
    "iconBundle": f"assets/market-icons-{STAMP}.json",
    "rankingSources": {
        "googlePlay": "data/games-20260831.json",
        "ios": "data/ios-games-20260831.json",
    },
    "previousRankingSources": {
        "googlePlay": "data/games-20260828.json",
        "ios": "data/ios-games-20260828.json",
    },
    "rankingDynamics": {
        "googlePlay": {
            "label": "Google Play · Android",
            "sourceTime": f"北京时间 {captured:%Y-%m-%d %H:%M:%S} 直连抓取",
            "anchors": "榜单锚点：#1 Kingshot · #25 Tiles Survive! · #60 Age of Apes",
            "products": [
                product("Stormshot: Isle of Adventure", "com.sivona.stormshot.e", "googlePlay", "entry", "回榜 · #47", "8月28日由#54掉榜，本期回到#47；iOS仍未进入TOP60，且未发现与周末严格对应的可确认重大节点，先按Android侧回补信号观察。"),
                product("Kiss of War: Dead Blood", "com.tap4fun.kissofwar.googleplay", "googlePlay", "entry", "回榜 · #58", "成熟战争SLG回到Google #58，iOS未进入同口径榜单；当前仍在最后三名，若下一次更新不能脱离#55—60，掉榜风险依然高。"),
                product("Age of Empires Mobile", "com.proximabeta.aoemobile", "googlePlay", "exit", "掉榜 · 上期#49", "上期仍在Google #49，本期掉出TOP60；iOS当前仍在#38，因此是Android侧回撤而非双端同步走弱，单次周末间隔不足以定义长期趋势。"),
                product("Raid Rush: Tower Defense TD", "com.wireless.defenseland", "googlePlay", "exit", "掉榜 · 上期#58", "从Google #58掉榜，iOS仍位于#40；变化集中在Android榜尾，暂未发现可确认版本节点，先作为平台差异与榜尾换防记录。"),
                product("GIRLS' FRONTLINE 2: EXILIUM", "com.Sunborn.SnqxExilium.Glo", "googlePlay", "up", "+21 · #14", "由#35跃升至#14，是Google本期最大上涨；8月27日新剧情、角色和Tile Transformation与上行窗口重合，但iOS同期由#21掉榜，不能把两端表现合并成同一结论。"),
                product("Warhammer 40,000: Tacticus ™", "com.snowprintstudios.tacticus", "googlePlay", "up", "+9 · #33", "由#42升至#33，iOS也由#52升至#30；官方排期显示Lysander传奇活动8月30日开启，时间与双端上行重合，是值得连续验证的活动信号。"),
                product("Age of Apes", "com.tap4fun.ape.gplay", "googlePlay", "down", "−10 · #60", "由#50降至#60，是Google最大下跌并压到最后一名；iOS没有对应排名，下一次更新若未回升就可能被榜尾换防挤出。"),
                product("Top Heroes: Kingdom Saga", "com.greenmushroom.boomblitz.gp", "googlePlay", "down", "−7 · #39", "由#32降至#39，iOS同时位于#50但较上期略升；当前不是双端同步下降，先观察Google侧是否继续下移。"),
            ],
        },
        "ios": {
            "label": "App Store · iPhone/iOS",
            "sourceTime": f"Apple RSS 北京时间 {source_date:%Y-%m-%d}",
            "anchors": "榜单锚点：#1 Pokémon GO · #25 Lordrush · #60 Kingdom Guard:Tower Defense TD",
            "products": [
                product("Idle Heroes - Idle Games", "1153461915", "ios", "entry", "进入 · #53", "2016年上线的成熟放置RPG首次进入本项目历史快照；Google未进入同口径TOP60，且没有足以解释本次排名的单一节点，先按iOS回榜信号处理。"),
                product("Vikings: War of Clans PvP", "966810173", "ios", "entry", "回榜 · #54", "iOS回到#54，Google当前#59；双端均在榜尾说明付费仍有承接，但位置尚未稳固，需区分短期回补与稳定留榜。"),
                product("Overgeared Hero: Merge RPG", "6755585789", "ios", "entry", "回榜 · #55", "iOS回到#55，Google则由#39降至#45；一端进入、另一端回落，现阶段更像平台节奏差异，不能断言产品整体走强。"),
                product("Galaxy Defense: Fortress TD", "6740189002", "ios", "entry", "回榜 · #56", "iOS回到#56，Google位于#54；双端都在榜尾六名内，形成共同留榜信号的同时也保留很高的再次掉榜风险。"),
                product("Star Trek Fleet Command", "1427744264", "ios", "entry", "回榜 · #58", "iOS以#58回榜，而Google稳定在#22；产品有明确Android收入基础，本期主要是iOS侧回补，是否能脱离榜尾仍待验证。"),
                product("Kingdom Guard:Tower Defense TD", "1570095804", "ios", "entry", "回榜 · #60", "iOS压线回榜，Google当前#57；两端都在最后四名，属于最典型的榜尾风险组合，下一次更新需优先检查是否继续留榜。"),
                product("GIRLS' FRONTLINE 2: EXILIUM", "6502505286", "ios", "exit", "掉榜 · 上期#21", "上期以#21进入，本期直接掉出iOS TOP60；与此同时Google由#35升至#14，显示同一版本窗口在两端的付费响应显著分化。"),
                product("TFT: Teamfight Tactics", "1480616748", "ios", "exit", "掉榜 · 上期#50", "18.1 Enchanted Wilds上线后进入#50，本期即掉榜；新Set首个快照未形成持续TOP60位置，后续仍需结合平衡补丁与外观/通行证节奏观察。"),
                product("Last Light: Wasteland", "6754545818", "ios", "exit", "掉榜 · 上期#56", "上期首次进入本项目快照#56，本期即掉榜；缺少可确认重大版本或开服证据，目前更接近一次榜尾脉冲。"),
                product("Hearthstone", "625257520", "ios", "exit", "掉榜 · 上期#58", "36.4带来的回榜路径从#44降至#58后继续掉榜，说明首轮版本峰值未能维持TOP60；仍不据此推断其长期用户盘。"),
                product("Warpath: Ace Shooter", "1529067679", "ios", "exit", "掉榜 · 上期#59", "由iOS #59掉榜，Google仍在#51；本期变化集中在iPhone榜尾，当前没有双端同步出榜证据。"),
                product("Jurassic World Alive", "1231085864", "ios", "exit", "掉榜 · 上期#60", "上期压线#60，本期被六款回榜产品挤出，属于榜尾换防；没有证据支持补写特定活动原因。"),
                product("Warhammer 40,000: Tacticus ™", "1599937506", "ios", "up", "+22 · #30", "由#52升至#30，是iOS最大上涨，Google也升9位至#33；8月30日Lysander传奇活动提供了同期节点，但仍需后续排名确认持续性。"),
                product("RAID: Shadow Legends", "1371565796", "ios", "up", "+19 · #22", "由#41升至#22；Echoes of Oz仍在进行并通过登录、融合与活动副本覆盖多条付费/活跃入口，时间相关性较强，但单次排名不能拆分各模块贡献。"),
                product("Summoners War", "852912420", "ios", "up", "+17 · #16", "由#33升至#16；8月29日SWC2026美洲区与亚太区预选赛、Frieren联动末期与上行窗口重合，先视为赛事/联动共同作用的待验证信号。"),
                product("Top Force: Commander", "6761893238", "ios", "up", "+13 · #36", "由#49升至#36，并与Google版同处#36；产品仍在近90天新品窗口，双端同位值得继续观察是否形成首发后的稳定中段。"),
                product("Dragon Traveler", "6751086804", "ios", "down", "−21 · #52", "由#31降至#52，是iOS最大下跌，且Google未进入同口径榜单；排名重新落入高风险区，暂无可确认的同期重大节点。"),
                product("Game of Thrones: Conquest ™", "1035712810", "ios", "down", "−17 · #49", "由#32降至#49，而Google当前#48；尽管iOS跌幅较大，两端位置反而收敛到榜尾中段，更适合观察共同中枢而非只看单端跌幅。"),
            ],
        },
    },
    "marketNews": [
        {
            "category": "活动与榜单", "date": "2026-08-30",
            "title": "Tacticus开启Lysander传奇活动，双端同步升至#30附近",
            "summary": "官方商店版本说明排期8月30日开启Heroes of the Chapter传奇活动，主角为Lysander；本期Google升至#33、iOS升至#30。",
            "impact": "这是本期唯一同时出现显著双端上涨且有明确同期活动节点的产品，但需要至少两个后续工作日确认活动峰值是否沉淀。",
            "source": "Apple App Store / Snowprint Studios",
            "url": "https://apps.apple.com/us/app/warhammer-40-000-tacticus/id1599937506",
        },
        {
            "category": "赛事运营", "date": "2026-08-27",
            "title": "Summoners War进入SWC2026预选赛收官周末",
            "summary": "Com2uS公布8月28—29日亚太C/D组和8月29日美洲区第三日赛程，并以预测、直播兑换码和徽章奖励连接游戏内活动。",
            "impact": "iOS本期上涨17位至#16；赛事曝光与游戏内奖励时间重合，但仍需在预选赛结束后观察榜位是否回落。",
            "source": "Com2uS / Summoners War",
            "url": "https://sw.com2us.com/en/skyarena/news/list/6882?category=swc",
        },
        {
            "category": "长线活动", "date": "2026-08-19",
            "title": "RAID以Echoes of Oz覆盖登录、融合与限时副本",
            "summary": "活动加入Dorothy Gale等五名传奇角色、登录追逐、融合活动和限时Event Dungeon，持续至11月的不同节点。",
            "impact": "iOS本期上涨19位至#22；多入口长周期活动有能力制造多个付费波峰，后续应看榜位是否在活动中段继续维持。",
            "source": "Plarium官方论坛",
            "url": "https://forum.plarium.com/raid-shadow-legends/843_news/43770_echoes-of-oz/",
        },
        {
            "category": "版本与跨端", "date": "2026-08-25",
            "title": "GFL2上线Chiral Redundancy、新角色与Tile Transformation",
            "summary": "8月26日维护加入OTs-14、Nemesis: Gnosis、限时剧情、Frontier Conquest、Assault Simulation及地格融合系统。",
            "impact": "Google本期升21位至#14而iOS从#21掉榜，说明同一内容包在两端形成不同收入节奏，不能只用单平台推断版本成效。",
            "source": "GIRLS' FRONTLINE 2官方公告",
            "url": "https://gf2exilium.sunborngame.com/NewsInfo?id=393&typeId=3",
        },
        {
            "category": "版本更新", "date": "2026-08-26",
            "title": "TFT 18.1 Enchanted Wilds上线Wisps与新阵营",
            "summary": "新Set以Wisps作为单次商店效果，并加入Elderwood等主题阵营和新外观；这是迁移新技术栈后的首个完整Set窗口。",
            "impact": "iOS上期进入#50后本期掉榜，表明首日版本曝光尚未转化为稳定TOP60，后续平衡与通行证节奏更关键。",
            "source": "Riot Games / Teamfight Tactics",
            "url": "https://teamfighttactics.leagueoflegends.com/en-us/news/game-updates/teamfight-tactics-patch-18-1/",
        },
        {
            "category": "IP联动", "date": "2026-08-25",
            "title": "State of Survival开启《如龙8》联动",
            "summary": "活动加入春日一番、桐生一马与真岛吾朗，并配置联盟Boss、节奏玩法、感染摩托和排行榜内容。",
            "impact": "产品本期Google #37、较上期下降3位，尚未出现联动后的明确上行；应继续用7日窗口而非首日判断回流效率。",
            "source": "FunPlus",
            "url": "https://funplus.com/state-of-survival-x-like-a-dragon-infinite-wealth-crossover-event/",
        },
        {
            "category": "开发工具", "date": "2026-08-28",
            "title": "腾讯游戏在Gamescom集中展示AI研发与运营工具",
            "summary": "腾讯Central Tech展示GIGA自主智能体、Motus 3D动画、WeTest Acorn自动化测试与ACE安全能力。",
            "impact": "对内容密集、版本频繁的策略产品而言，AI测试与资产管线若能降低迭代成本，影响将先体现在版本频率和运营响应，而非单日榜位。",
            "source": "PocketGamer.biz / Tencent Games",
            "url": "https://www.pocketgamer.biz/tencent-games-showcases-ai-tools-for-game-development-at-gamescom/",
        },
        {
            "category": "市场报告", "date": "2026-08-26",
            "title": "Moloco：19万款新手游中仅2500款首年突破50万下载",
            "summary": "研究覆盖55款新游、超过15亿美元IAP和2000多万付费用户，并指出高价值用户往往在首发月之后才开始付费。",
            "impact": "Top Force、Top Lords等近90天产品不能只看首发榜位；持续创意和中长期高价值用户培养更决定能否留在畅销榜。",
            "source": "PocketGamer.biz / Moloco",
            "url": "https://www.pocketgamer.biz/report-only-2500-of-190000-mobile-games-released-in-2025-surpassed-500000-downloads/",
        },
        {
            "category": "社交能力", "date": "2026-08-26",
            "title": "Discord将Social Layer扩展到移动端",
            "summary": "Discord称其对15款以上PC游戏的因果研究显示留存最高提升31%、启动天数最高提升57%，并已针对手机屏幕适配。",
            "impact": "联盟和跨服关系是SLG留存核心，但PC研究结果不能直接套用移动端；应关注实际接入后的召回和组队转化。",
            "source": "Discord",
            "url": "https://discord.com/press-releases/introducing-new-tools-to-power-game-discovery-and-social-play",
        },
        {
            "category": "渠道变现", "date": "2026-08-25",
            "title": "Sensor Tower披露部分手游D2C收入占比超过30%",
            "summary": "美国H1 2026数据中，部分头部手游已有30%以上销售来自商店外Web Store，赌场、RPG和桌游占比较高。",
            "impact": "应用商店畅销榜只反映平台内收入；成熟策略产品的真实收入判断需要同时观察官网直购、联盟社群与商店榜位。",
            "source": "PocketGamer.biz / Sensor Tower",
            "url": "https://www.pocketgamer.biz/sensor-tower-reveals-the-hidden-impact-of-d2c-revenue-in-mobile-games/",
        },
    ],
    "closing": [
        {
            "type": "判断", "title": "iOS换防数量扩大，但主要是榜尾产品轮换",
            "detail": "iOS六进六出看似波动很大，但六款进入产品全部位于#53—60，四款掉榜产品上期也在#56—60；因此主要反映周末后的榜尾重排，而非榜单核心层全面改写。",
        },
        {
            "type": "判断", "title": "Tacticus是最清晰的双端活动信号，GFL2则形成平台分化",
            "detail": "Tacticus两端分别+9和+22，并与8月30日Lysander活动同期；GFL2却在Google升至#14、iOS由#21掉榜。相同内容窗口不保证两端收入节奏一致。",
        },
        {
            "type": "判断", "title": "上期iOS进入产品多数未能跨过周末",
            "detail": "GFL2、TFT、Last Light、Hearthstone、Warpath与Jurassic World Alive均从上期榜内退出；其中多款原本就在榜尾，进一步说明单次进入只能视为待验证信号。",
        },
        {
            "type": "关注", "title": "截至9月2日：验证Tacticus是否建立双端新中枢",
            "detail": "以Google #33、iOS #30为起点；若活动开启后三个工作日两端仍保持TOP35，再把本期上涨从短峰升级为可持续信号。",
        },
        {
            "type": "关注", "title": "截至9月3日：跟踪GFL2跨端差异是否收敛",
            "detail": "检查Google能否守住TOP20及iOS是否回榜；只有iOS重新进入或Google快速回落，才能判断当前分化是支付节奏差还是单平台事件。",
        },
        {
            "type": "关注", "title": "9月1—4日：观察Summoners War与榜尾回榜组的持续性",
            "detail": "SWC周末与Frieren联动收尾后，观察Summoners War能否保持TOP20；同时检查Idle Heroes、Vikings、Galaxy Defense、Kingdom Guard等iOS回榜产品能否至少连续两次留榜。",
        },
    ],
    "status": {
        "googlePlay": {
            "top60": len(google_games),
            "newRelease90d": sum(game["comparison90d"]["status"] == "new" for game in google_games),
            "surge90d": sum(game["comparison90d"]["status"] == "surge" for game in google_games),
            "baselineAvailable": False,
        },
        "ios": {
            "top60": len(ios_games),
            "newRelease90d": sum(game["comparison90d"]["status"] == "new" for game in ios_games),
            "surge90d": sum(game["comparison90d"]["status"] == "surge" for game in ios_games),
            "baselineAvailable": False,
        },
    },
    "sources": [
        {"label": "Google Play美国区策略畅销榜直连", "url": google_history["sourceUrl"], "capturedAt": google_history["sourceCapturedAt"]},
        {"label": "Apple官方美国区iPhone策略畅销RSS", "url": ios_history["sourceUrl"], "updated": ios_history["sourceUpdated"], "sourceDateBeijing": ios_history["dataDate"]},
    ],
    "downloads": {
        "markdown": "reports/2026-08-31.md",
        "json": "data/market-brief-20260831.json",
    },
}


def markdown_for(value):
    lines = [
        f"# {value['date']} 美国区策略手游双端市场日报",
        "",
        f"**{value['title']}**",
        "",
        value["summary"],
        "",
        "## 数据源与口径",
        "",
        f"- Google Play：`{google_history['sourceCapturedAt']}`（北京时间直连抓取；PlayStoreUi / vyAe2 / US / GAME_STRATEGY / topgrossing / TOP60）",
        f"- Apple App Store：RSS `updated={ios_history['sourceUpdated']}`，对应北京时间榜单日期 `{ios_history['dataDate']}`",
        f"- Google锚点：{value['rankingDynamics']['googlePlay']['anchors'].replace('榜单锚点：', '')}",
        f"- iOS锚点：{value['rankingDynamics']['ios']['anchors'].replace('榜单锚点：', '')}",
        f"- 对比基准：各自上一份有效快照为2026-08-28；8月29—30日按既定规则不更新。",
        f"- 近90天状态：Google新上榜{value['status']['googlePlay']['newRelease90d']}款、iOS新上榜{value['status']['ios']['newRelease90d']}款；两端均缺少2026-06-02精确同口径TOP60基准，较老产品暂不判断飙升。",
        "",
        "## 1. 双榜当日异动产品",
    ]
    for key in ("googlePlay", "ios"):
        section = value["rankingDynamics"][key]
        lines.extend(["", f"### {section['label']}", "", section["sourceTime"] + "。"])
        for item in section["products"]:
            lines.extend(["", f"#### {item['gameName']}｜{item['changeLabel']}", "", item["analysis"]])
    lines.extend(["", "## 2. 策略手游市场热点", "", value["newsMethod"]])
    for index, item in enumerate(value["marketNews"], 1):
        lines.extend([
            "", f"### {index}. [{item['title']}]({item['url']})", "",
            f"- 类别：{item['category']}｜发布日期：{item['date']}｜来源：{item['source']}",
            f"- 事实摘要：{item['summary']}",
            f"- 市场含义：{item['impact']}",
        ])
    lines.extend(["", "## 3. 综合判断与后续关注", ""])
    for item in value["closing"]:
        lines.extend([f"### {item['type']}｜{item['title']}", "", item["detail"], ""])
    return "\n".join(lines).rstrip() + "\n"


save(f"data/market-brief-{STAMP}.json", brief)
(ROOT / f"reports/{DATE}.md").write_text(markdown_for(brief), encoding="utf-8")

manifest = load("reports/manifest.json")
entry = {
    "date": DATE,
    "title": brief["title"],
    "summary": brief["summary"],
    "markdown": brief["downloads"]["markdown"],
    "json": brief["downloads"]["json"],
}
reports = [report for report in manifest.get("reports", []) if report.get("date") != DATE]
reports.append(entry)
reports.sort(key=lambda report: report["date"], reverse=True)
save("reports/manifest.json", {"updated": DATE, "timezone": "Asia/Shanghai", "reports": reports})

print(f"Wrote {brief['downloads']['json']}, {brief['downloads']['markdown']}, and manifest")
