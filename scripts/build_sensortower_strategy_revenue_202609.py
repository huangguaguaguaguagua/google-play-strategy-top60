#!/usr/bin/env python3
"""Archive the September 2026 Sensor Tower worldwide revenue strategy subset."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def save(path: str, value):
    target = ROOT / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


SOURCE_URL = "https://develop.sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-september-2026"
PREVIOUS_URL = "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-in-august-2026"
YOY_URL = "https://sensortower.com/blog/top-10-worldwide-mobile-games-by-revenue-and-downloads-september-2025"


source_top10 = {
    "schemaVersion": 1,
    "reportId": "sensortower-worldwide-mobile-games-revenue-2026-09",
    "title": "Sensor Tower 全球手游月收入 TOP10（来源审计）",
    "period": "2026-09",
    "periodLabel": "2026年9月",
    "publicationLabel": "2026年10月",
    "estimateAsOf": "2026-10-01",
    "checkedAt": "2026-10-06",
    "source": "Sensor Tower",
    "sourceUrl": SOURCE_URL,
    "sourceEvidence": "Sensor Tower官方文章及完整图表“2026-sep-top-10-mobile-games-rev”",
    "scope": {
        "region": "全球",
        "stores": "Apple App Store + Google Play",
        "metric": "Sensor Tower估算的移动游戏消费者支出排名",
        "exclusions": "不含第三方Android商店",
        "individualRevenueAmountsPublished": False,
    },
    "marketSummary": {
        "globalConsumerSpendingUsd": 6130000000,
        "monthOverMonthPercent": -7.0,
        "marketShares": [
            {"market": "美国", "percent": 28.7},
            {"market": "中国", "qualifier": "仅iOS", "percent": 15.7},
            {"market": "日本", "percent": 12.4},
        ],
    },
    "rankings": [
        {"rank": 1, "gameName": "Honor of Kings", "publisher": "Tencent", "previousPeriodRank": 1, "movement": "flat", "movementLabel": "较上月持平"},
        {"rank": 2, "gameName": "ROBLOX", "publisher": "Roblox Corporation", "previousPeriodRank": None, "movement": "new", "movementLabel": "上月未进全球TOP10"},
        {"rank": 3, "gameName": "Gossip Harbor", "publisher": "Microfun", "previousPeriodRank": 2, "movement": "down", "movementLabel": "较上月下降1位"},
        {"rank": 4, "gameName": "Candy Crush Saga", "publisher": "King", "previousPeriodRank": 5, "movement": "up", "movementLabel": "较上月上升1位"},
        {"rank": 5, "gameName": "MONOPOLY GO!", "publisher": "Scopely", "previousPeriodRank": 6, "movement": "up", "movementLabel": "较上月上升1位"},
        {"rank": 6, "gameName": "Whiteout Survival", "publisher": "Century Games", "previousPeriodRank": 3, "movement": "down", "movementLabel": "较上月下降3位"},
        {"rank": 7, "gameName": "Last War: Survival", "publisher": "FirstFun", "previousPeriodRank": None, "movement": "new", "movementLabel": "上月未进全球TOP10"},
        {"rank": 8, "gameName": "Pokémon GO", "publisher": "Niantic", "previousPeriodRank": None, "movement": "new", "movementLabel": "上月未进全球TOP10"},
        {"rank": 9, "gameName": "Kingshot", "publisher": "Century Games", "previousPeriodRank": 7, "movement": "down", "movementLabel": "较上月下降2位"},
        {"rank": 10, "gameName": "Royal Match", "publisher": "Dream Games", "previousPeriodRank": 4, "movement": "down", "movementLabel": "较上月下降6位"},
    ],
    "methodologyNote": "完整TOP10仅用于来源审计；公开模块与日报只展示其中符合核心策略定义的产品。",
}


strategy_subset = {
    "schemaVersion": 2,
    "reportId": "sensortower-worldwide-mobile-games-revenue-strategy-subset-2026-09",
    "title": "Sensor Tower 全球收入榜 · 策略产品",
    "period": "2026-09",
    "periodLabel": "2026年9月",
    "previousPeriod": "2026-08",
    "publicationLabel": "2026年10月",
    "estimateAsOf": "2026-10-01",
    "checkedAt": "2026-10-06",
    "source": "Sensor Tower",
    "sourceUrl": SOURCE_URL,
    "previousPeriodSourceUrl": PREVIOUS_URL,
    "yearOverYearSourceUrl": YOY_URL,
    "sourceEvidence": "Sensor Tower官方2026年9月全球手游收入TOP10图表，以及官方2026年8月、2025年9月报告",
    "sourceTop10Archive": "data/sensortower-global-revenue-top10-202609.json",
    "iconBundle": "assets/sensortower-strategy-icons-202609.json",
    "downloadPath": "data/sensortower-global-strategy-revenue-202609.json",
    "updatePolicy": "每个工作日仅检查Sensor Tower是否发布新一期官方全球收入月榜；发布后筛选其中核心策略产品并更新一次，未发布时不改月份或数值。",
    "scope": {
        "region": "全球",
        "stores": "Apple App Store + Google Play",
        "metric": "Sensor Tower估算的移动游戏消费者支出排名",
        "displayPopulation": "Sensor Tower全球手游收入TOP10中的核心策略产品",
        "strategyDefinition": "核心循环属于SLG、4X、城建生存、塔防或战术经营；不因商店多标签而纳入MOBA、体育、消除、派对、射击或RPG产品",
        "sourceTop10Size": 10,
        "strategyMatches": 3,
        "isCompleteStrategyCategoryRanking": False,
        "exclusions": "不含第三方Android商店",
        "individualRevenueAmountsPublished": False,
        "individualYoYPercentPublished": False,
    },
    "marketSummary": {
        "globalConsumerSpendingUsd": 6130000000,
        "monthOverMonthPercent": -7.0,
        "previousYearSameMonthConsumerSpendingUsd": 6600000000,
        "yearOverYearPercentApprox": -7.1,
        "yearOverYearCalculationNote": "以Sensor Tower公开的2026年9月61.3亿美元和2025年9月约66亿美元计算，因此只作为全市场约值，不代表单款游戏同比。",
        "marketShares": [
            {"market": "美国", "percent": 28.7},
            {"market": "中国", "qualifier": "仅iOS", "percent": 15.7},
            {"market": "日本", "percent": 12.4},
        ],
    },
    "rankings": [
        {
            "rank": 6,
            "gameName": "Whiteout Survival",
            "publisher": "Century Games",
            "strategyGenre": "4X生存策略",
            "iconKey": "whiteout-survival",
            "previousPeriodRank": 3,
            "rankChange": -3,
            "movement": "down",
            "movementLabel": "较上月下降3位",
            "yoyRevenuePercent": None,
            "yoyRevenueLabel": "单品同比未公开",
        },
        {
            "rank": 7,
            "gameName": "Last War: Survival",
            "publisher": "FirstFun",
            "strategyGenre": "数字门获量 + 末日城建4X",
            "iconKey": "last-war-survival",
            "previousPeriodRank": None,
            "rankChange": None,
            "movement": "new",
            "movementLabel": "上月未进全球TOP10，本月进入第7",
            "yoyRevenuePercent": None,
            "yoyRevenueLabel": "单品同比未公开",
        },
        {
            "rank": 9,
            "gameName": "Kingshot",
            "publisher": "Century Games",
            "strategyGenre": "塔防获量 + 城建4X",
            "iconKey": "kingshot",
            "previousPeriodRank": 7,
            "rankChange": -2,
            "movement": "down",
            "movementLabel": "较上月下降2位",
            "yoyRevenuePercent": None,
            "yoyRevenueLabel": "单品同比未公开",
        },
    ],
    "officialHighlights": [
        "Whiteout Survival位列9月全球手游收入总榜第6，较8月第3名下降3位；这是全球总榜名次变化，不代表收入环比或同比。",
        "Last War: Survival上月未进入全球TOP10，本月进入总榜第7；Kingshot由第7降至第9。官方公开材料均未披露单品收入同比。",
        "本期全球收入TOP10仅有3款符合核心策略口径，不能据此把它们重新编号为完整全球策略品类前三名。",
    ],
    "methodologyNote": "页面只展示Sensor Tower官方全球收入TOP10中的核心策略产品，并保留其全球总榜名次。逐款箭头和位数比较的是2026年8月至9月的榜位变化，不是收入同比。Sensor Tower公开材料未披露单款收入或单品同比百分比，因此不以排名变化换算收入增幅；页面所示约-7.1%仅为两期官方公开市场总额计算的全球手游市场同比。",
}


august_icons = load("assets/sensortower-strategy-icons-202608.json")
google_icons = load("assets/assets-01.json")
september_icons = {
    "whiteout-survival": august_icons["whiteout-survival"],
    "last-war-survival": google_icons["03_icon"],
    "kingshot": august_icons["kingshot"],
}


save("data/sensortower-global-revenue-top10-202609.json", source_top10)
save("data/sensortower-global-revenue-top10-latest.json", source_top10)
save("data/sensortower-global-strategy-revenue-202609.json", strategy_subset)
save("data/sensortower-global-strategy-revenue-latest.json", strategy_subset)
save("assets/sensortower-strategy-icons-202609.json", september_icons)
print("Wrote September 2026 Sensor Tower source audit, strategy subset and local icon bundle")
