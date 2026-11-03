#!/usr/bin/env python3
"""Archive the October 2026 Sensor Tower worldwide revenue strategy subset."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_URL = "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-october-2026"
PREVIOUS_URL = "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026"


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path, value):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


rankings = [
    (1, "ROBLOX", "Roblox", 2),
    (2, "Honor of Kings", "Tencent", 1),
    (3, "Gossip Harbor", "Microfun", 3),
    (4, "Royal Match", "Dream Games", 10),
    (5, "Whiteout Survival", "Century Games", 6),
    (6, "Candy Crush Saga", "King", 4),
    (7, "MONOPOLY GO!", "Scopely", 5),
    (8, "Coin Master", "Moon Active", None),
    (9, "Kingshot", "Century Games", 9),
    (10, "Free Fire", "Garena", None),
]


def movement(rank, previous):
    if previous is None:
        return "new", "上月未进全球TOP10"
    change = previous - rank
    if change > 0:
        return "up", f"较上月上升{change}位"
    if change < 0:
        return "down", f"较上月下降{-change}位"
    return "flat", "较上月持平"


source_top10 = {
    "schemaVersion": 1,
    "reportId": "sensortower-worldwide-mobile-games-revenue-2026-10",
    "title": "Sensor Tower 全球手游月收入 TOP10（来源审计）",
    "period": "2026-10",
    "periodLabel": "2026年10月",
    "publicationLabel": "2026年11月",
    "estimateAsOf": "2026-11-04",
    "checkedAt": "2026-11-03",
    "source": "Sensor Tower",
    "sourceUrl": SOURCE_URL,
    "sourceEvidence": "Sensor Tower官方完整图表“Worldwide Top 10 Mobile Games by Revenue (October 2026)”",
    "scope": {
        "region": "全球",
        "stores": "Apple App Store + Google Play",
        "metric": "Sensor Tower估算的移动游戏消费者支出排名",
        "exclusions": "不含第三方Android商店",
        "individualRevenueAmountsPublished": False,
    },
    "marketSummary": {
        "globalConsumerSpendingUsd": 6260000000,
        "monthOverMonthPercent": 1.7,
        "marketShares": [
            {"market": "美国", "percent": 28.8},
            {"market": "中国", "qualifier": "仅iOS", "percent": 14.7},
            {"market": "日本", "percent": 12.5},
        ],
    },
    "rankings": [
        {"rank": rank, "gameName": name, "publisher": publisher,
         "previousPeriodRank": previous, "movement": movement(rank, previous)[0],
         "movementLabel": movement(rank, previous)[1]}
        for rank, name, publisher, previous in rankings
    ],
    "methodologyNote": "完整TOP10仅用于来源审计；公开模块与日报只展示其中符合核心策略定义的产品。",
}

strategy_rows = [
    {
        "rank": 5, "gameName": "Whiteout Survival", "publisher": "Century Games",
        "strategyGenre": "4X生存策略", "iconKey": "whiteout-survival",
        "previousPeriodRank": 6, "rankChange": 1, "movement": "up",
        "movementLabel": "较上月上升1位", "yoyRevenuePercent": None,
        "yoyRevenueLabel": "单品同比未公开",
    },
    {
        "rank": 9, "gameName": "Kingshot", "publisher": "Century Games",
        "strategyGenre": "塔防获量 + 城建4X", "iconKey": "kingshot",
        "previousPeriodRank": 9, "rankChange": 0, "movement": "flat",
        "movementLabel": "较上月持平", "yoyRevenuePercent": None,
        "yoyRevenueLabel": "单品同比未公开",
    },
]

strategy_subset = {
    "schemaVersion": 2,
    "reportId": "sensortower-worldwide-mobile-games-revenue-strategy-subset-2026-10",
    "title": "Sensor Tower 全球收入榜 · 策略产品",
    "period": "2026-10", "periodLabel": "2026年10月", "previousPeriod": "2026-09",
    "publicationLabel": "2026年11月", "estimateAsOf": "2026-11-04", "checkedAt": "2026-11-03",
    "source": "Sensor Tower", "sourceUrl": SOURCE_URL,
    "previousPeriodSourceUrl": PREVIOUS_URL, "yearOverYearSourceUrl": None,
    "sourceEvidence": "Sensor Tower官方2026年10月完整全球手游收入TOP10图表及2026年9月官方榜图",
    "sourceTop10Archive": "data/sensortower-global-revenue-top10-202610.json",
    "iconBundle": "assets/sensortower-strategy-icons-202610.json",
    "downloadPath": "data/sensortower-global-strategy-revenue-202610.json",
    "updatePolicy": "每个工作日仅检查Sensor Tower是否发布新一期官方全球收入月榜；发布后筛选其中核心策略产品并更新一次，未发布时不改月份或数值。",
    "strategyDefinition": "核心循环属于SLG、4X、城建生存、塔防或战术经营；不因商店多标签而纳入MOBA、体育、消除、派对、射击或RPG产品",
    "sourceTop10Size": 10, "strategyMatches": 2,
    "scope": {
        "region": "全球", "stores": "Apple App Store + Google Play",
        "metric": "Sensor Tower估算的移动游戏消费者支出排名",
        "displayPopulation": "Sensor Tower全球手游收入TOP10中的核心策略产品",
        "strategyDefinition": "核心循环属于SLG、4X、城建生存、塔防或战术经营；不因商店多标签而纳入MOBA、体育、消除、派对、射击或RPG产品",
        "sourceTop10Size": 10, "strategyMatches": 2,
        "isCompleteStrategyCategoryRanking": False, "exclusions": "不含第三方Android商店",
        "individualRevenueAmountsPublished": False, "individualYoYPercentPublished": False,
    },
    "marketSummary": {
        "globalConsumerSpendingUsd": 6260000000, "monthOverMonthPercent": 1.7,
        "previousYearSameMonthConsumerSpendingUsd": None, "yearOverYearPercentApprox": None,
        "yearOverYearCalculationNote": "未取得同口径的Sensor Tower 2025年10月官方四舍五入市场总额，因此不计算全市场同比约值。",
        "marketShares": source_top10["marketSummary"]["marketShares"],
    },
    "rankings": strategy_rows,
    "officialHighlights": [
        "Whiteout Survival位列10月全球手游收入总榜第5，较9月第6名上升1位；这是全球总榜名次变化，不代表收入环比或同比。",
        "Kingshot仍位列全球总榜第9；Last War: Survival从9月第7名退出全球TOP10。官方公开材料未披露这些产品的单品收入同比。",
        "本期全球收入TOP10仅有2款符合核心策略口径，不能据此把它们重新编号为完整全球策略品类前两名。",
    ],
    "methodologyNote": "页面只展示Sensor Tower官方全球收入TOP10中的核心策略产品，并保留其全球总榜名次。逐款箭头和位数比较的是2026年9月至10月的榜位变化，不是收入同比。官方公开材料未披露单款收入或单品同比百分比，因此不以排名变化换算收入增幅；本期也不展示全市场同比约值。",
}

previous_icons = load("assets/sensortower-strategy-icons-202609.json")
icons = {key: previous_icons[key] for key in ("whiteout-survival", "kingshot")}
save("data/sensortower-global-revenue-top10-202610.json", source_top10)
save("data/sensortower-global-revenue-top10-latest.json", source_top10)
save("data/sensortower-global-strategy-revenue-202610.json", strategy_subset)
save("data/sensortower-global-strategy-revenue-latest.json", strategy_subset)
save("assets/sensortower-strategy-icons-202610.json", icons)
print("Wrote October 2026 Sensor Tower source audit, strategy subset and local icons")
