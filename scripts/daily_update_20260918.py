#!/usr/bin/env python3
"""Build the Beijing 2026-09-18 Google Play and Apple App Store snapshots."""

from copy import deepcopy
from datetime import datetime
from zoneinfo import ZoneInfo

from daily_update_20260820 import comparison, data_uri, delta_label, load, lookup, parse_ios, save, trend
from daily_update_20260910 import ios_game_from_metadata
from daily_update_20260821 import play_metadata
from daily_update_20260825 import appbrain_audit, merged_records, records
from daily_update_20260828 import refresh_daily_rank_path
from google_play_direct import fetch_top_grossing_strategy


CAPTURE = "2026-09-18"
GOOGLE_DATE = "2026-09-18"
GOOGLE_BASELINE = "2026-06-20"
IOS_DATE = "2026-09-18"
IOS_BASELINE = "2026-06-20"

GOOGLE_DATES = (
    "20260917", "20260916", "20260915", "20260914", "20260911", "20260910", "20260909", "20260908",
    "20260907", "20260904", "20260903", "20260902", "20260901", "20260831", "20260828",
    "20260827", "20260826", "20260825", "20260824", "20260821", "20260820", "20260819d",
)
IOS_DATES = (
    "20260917", "20260916", "20260915", "20260914", "20260911", "20260910", "20260909", "20260908",
    "20260907", "20260904", "20260903", "20260902", "20260901", "20260831", "20260828",
    "20260827", "20260826", "20260825", "20260824", "20260821", "20260820", "20260819",
)


def history_specs(prefix, dates):
    return [
        (
            f"data/{prefix}games-{date}.json",
            f"data/{prefix}enrichment-{date}.json",
            f"data/{prefix}trends-{date}.json",
        )
        for date in dates
    ]


def clean_analysis(analysis):
    analysis = deepcopy(analysis)
    analysis["summary"] = analysis["summary"].replace("近三个月新上榜｜", "").replace("近三个月飙升｜", "")
    for audit_name in ("sourceAudit", "lifecycleAudit"):
        if analysis.get(audit_name):
            analysis[audit_name]["reviewedAt"] = CAPTURE
    return analysis


def audit_google(rows):
    try:
        return appbrain_audit(rows)
    except Exception as exc:
        return {
            "sourceRole": "audit-only",
            "sourceUrl": "https://www.appbrain.com/stats/google-play-rankings/top_grossing/strategy/us",
            "status": "unavailable",
            "error": f"{type(exc).__name__}: {exc}",
            "note": "审计源失败不覆盖或阻断Google Play直连榜单。",
        }


def aliens_profile(row, metadata):
    package = row["packageName"]
    store_url = metadata["url"]
    release = metadata.get("released") or "2024-11-15"
    if release != "2024-11-15":
        raise RuntimeError(f"Unexpected Aliens vs Zombies release date: {release}")
    game = {
        "rank": row["rank"],
        "packageName": package,
        "gameName": row["gameName"],
        "developer": metadata.get("developer") or row.get("developer", "GAMEGEARS LTD"),
        "totalInstalls": metadata.get("downloads", ""),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"],
        "store": "googlePlay",
        "storeUrl": store_url,
        "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"],
        "shortDescription": metadata.get("description", ""),
        "description": "Alien invasion tower defense：布置与升级防御塔、控制敌人路径、平衡资源，并抵御丧尸潮。",
        "releaseDate": release,
        "updatedDate": metadata.get("updated", ""),
        "genre": "塔防 / 丧尸 / 单机策略",
        "keywords": "外星入侵；丧尸；塔防；路径控制；防御塔升级；资源管理；离线",
        "note": "",
        "releaseDateIso": release,
        "assetRank": 76,
        "comparison90d": comparison(None, row["rank"], GOOGLE_DATE, GOOGLE_BASELINE, True, release),
    }
    company = {
        "en": "GAMEGEARS LTD",
        "cn": "GAMEGEARS LTD（塞浦路斯发行与研发主体；未发现更大集团归属披露）",
        "confidence": "已确认",
        "basis": "Google Play店铺发行名为GAMEGEARS LTD；官方隐私政策列明同名法律主体及塞浦路斯注册地址。未找到可确认的更上层集团披露。",
        "source": "https://www.gamegears.online/privacy-policy",
    }
    analysis = trend(
        "趋势：2024年以卡通外星人、丧尸潮和单机塔防上架，当前由路径控制、塔位布局与防御塔升级承接；关键转折：未发现可确认的重大转折/长期稳定运营，本次首次进入项目记录的Google TOP60；主力素材：密集丧尸波次、不同射程塔位、升级分支与基地防线。",
        "2024年11月上架，商品页从一开始即把外星入侵包装与经典塔防结合：玩家布置并升级防御塔、控制敌军行进路线、分配有限资源并抵御连续丧尸潮；离线单机是其区别于联盟4X产品的持续入口。",
        "上架日期早于本期90天窗口；本次首次出现在项目保存的Google Play美国策略畅销TOP60，位列第60名。因缺少2026-06-20同口径基准，内部保持pending并按常规展示。",
        "官方商品页显示2026年8月31日更新，并在当前商店活动中突出Boss挑战与Fire Crossbow Tower解锁；除这一活动节点外，未发现可确认的玩法重构或商业化重大转折。",
        "卡通外星人对抗丧尸、分路推进的尸潮、塔位覆盖范围、火力升级选择、资源不足压力、Boss攻城与Fire Crossbow Tower奖励。素材判断仅基于Google商品页和当前商店图，可信度为中。",
        "观察首次#60是否只是Boss活动附近的榜尾脉冲，以及活动结束后能否连续留榜；没有连续快照前不推断长期趋势。",
        store_url,
        [{"label": "GAMEGEARS官方隐私政策", "url": "https://www.gamegears.online/privacy-policy", "type": "primary"}],
    )
    return game, company, clean_analysis(analysis)


def age_of_spirits_profile(row, metadata):
    package = row["packageName"]
    store_url = metadata["url"]
    release = metadata.get("released") or "2026-09-16"
    if release != "2026-09-16":
        raise RuntimeError(f"Unexpected Age of Spirits release date: {release}")
    game = {
        "rank": row["rank"],
        "packageName": package,
        "gameName": row["gameName"],
        "developer": metadata.get("developer") or row.get("developer", "LeyiGames"),
        "totalInstalls": metadata.get("downloads", ""),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"],
        "store": "googlePlay",
        "storeUrl": store_url,
        "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"],
        "shortDescription": metadata.get("description", ""),
        "description": "以篝火建立部落，建设祭坛、采石场与伐木场，培养萨满和军队，并在世界地图争夺资源、圣地与联盟领土。",
        "releaseDate": release,
        "updatedDate": metadata.get("updated", ""),
        "genre": "SLG / 4X / 部落经营",
        "keywords": "原始部落；篝火；萨满；城建；世界地图；联盟；4X；资源争夺",
        "note": "",
        "releaseDateIso": release,
        "assetRank": 75,
        "comparison90d": comparison(None, row["rank"], GOOGLE_DATE, GOOGLE_BASELINE, True, release),
    }
    company = {
        "en": "LeyiGames / Shenzhen Leyi Network Co., Ltd. / APPLOVIN CYPRUS LIMITED",
        "cn": "LeyiGames（店铺品牌）/ 深圳乐易网络（产品体系）/ APPLOVIN CYPRUS LIMITED（Google Play法律主体）",
        "confidence": "已确认",
        "basis": "Google Play列明LeyiGames为店铺品牌、APPLOVIN CYPRUS LIMITED为开发者法律主体；Leyi官网以Shenzhen Leyi Network Co., Ltd.介绍其模拟策略游戏业务。未据此延伸推断当前更上层集团归属。",
        "source": "https://www.leyinetwork.com/",
    }
    analysis = trend(
        "趋势：美国区9月16日上架即以原始部落篝火、萨满和联盟4X进入首发验证，本次首次进入Google TOP60；关键转折：首发版本同步新增七种语言、11级兵种与萨满伤势机制，尚无更长期转折可判断；主力素材：从单一篝火扩建部落、萨满编队、巨兽威胁和联盟世界地图争夺。",
        "Google Play美国区released日期为2026年9月16日。首发入口以‘从一团火建立部落’呈现城建成长，再把祭坛、采石场、伐木场与兵种训练承接到萨满编队、世界地图资源争夺、圣地Boss和联盟战争；上线时间短，仍处首发验证。",
        "美国区上架次日首次进入项目保存的Google Play策略畅销TOP60，当前第59名；按同商店released日期落在90天窗口内，归类为近三个月新上榜。没有连续快照前不把首日排名写成稳定趋势。",
        "9月16日版本同时加入德、法、葡、西、日、韩与繁中七种语言，开放11级士兵，并重做萨满部署、伤势与升级；这是可确认的首发范围扩张和战斗系统节点，但尚不能判断其收入影响。",
        "篝火到聚落的建设前后对比、巨型野兽压迫、萨满与部族战士编队、祭坛和资源建筑升级、世界地图行军、圣地争夺与联盟集结。素材判断仅基于当前Google商品页与商店图，可信度为中。",
        "观察9月18—21日能否脱离榜尾并连续留榜，以及多语言与萨满改版后的首发买量是否在Google美国区形成可重复排名；不推演未来表现。",
        store_url,
        [{"label": "Leyi官方公司页", "url": "https://www.leyinetwork.com/", "type": "primary"}],
    )
    return game, company, clean_analysis(analysis)


def ios_arknights_profile(row, metadata):
    game = ios_game_from_metadata(
        row,
        metadata,
        90,
        "塔防 / 战术编队 / 角色养成",
        "明日方舟；塔防；干员；职业编队；部署顺序；技能时机；基地建设；关卡策略",
    )
    company = {
        "en": "YOSTAR (HONG KONG) LIMITED / Hypergryph",
        "cn": "悠星（海外发行）/ 鹰角网络（研发与产品体系）",
        "confidence": "已确认",
        "basis": "Apple美国区Lookup列明YOSTAR (HONG KONG) LIMITED为seller；Arknights官方全球站由Yostar运营，鹰角网络官方招聘页将《明日方舟》列为公司项目。未发现需进一步上溯的已披露集团归属。",
        "source": "https://career.hypergryph.com/",
    }
    analysis = trend(
        "趋势：2020年全球上线后，以职业克制、部署顺序和技能时机形成长期塔防核心，并由干员收集、章节活动与基地经营维持成熟运营；关键转折：当前Apple版本为8月13日强制更新，未发现与本次#58回榜直接对应的可确认重大转折；主力素材：多职业干员编队、格子部署、敌人路线、技能爆发和罗德岛世界观。",
        "Apple美国区于2020年1月15日上架。产品长期用不同职业干员、攻击范围、部署费用与技能时机构成塔防关卡，再由角色收集、养成、基地建设和剧情活动承接核心用户；现阶段属于成熟长线运营。",
        "本次首次出现在项目保存的iOS美国策略畅销TOP60，位列第58名；Apple本店releaseDate早于90天窗口，因此不是近三个月新上榜。因缺少2026-06-20精确同口径基准，内部保持pending并按常规展示。",
        "Apple Lookup显示当前36.7.22版本于8月13日发布，说明为强制更新及重新下载安装提醒。公开资料没有把该更新与今天回榜建立因果，也未发现更近的可确认重大转折。",
        "当前商店图集中展示多职业干员同场、格子塔防部署、敌人行进路线、技能范围与基地建设；早期到成熟期仍以角色叙事和高难关卡承接塔防核心。素材判断基于Apple商店图与官方产品资料，可信度为中。",
        "观察下一工作日能否脱离后五名并连续留榜；在没有官方活动或连续名次证据前，仅记录为成熟产品单日回榜信号。",
        game["storeUrl"],
        [
            {"label": "Arknights全球官网", "url": "https://www.arknights.global/", "type": "primary"},
            {"label": "鹰角网络官方招聘页", "url": "https://career.hypergryph.com/", "type": "company-research"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="上架日期、当前版本、玩法描述与商店图来自Apple美国区Lookup/商品页；官方全球站与鹰角网络官方招聘页用于交叉确认产品体系。",
        changeReason="首次进入项目iOS榜，补建Apple本店上架日期、本地素材、公司归属和独立生命周期档案；未把8月强制更新写成本次回榜原因。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2020年全球上线梳理至当前成熟塔防、角色养成与基地经营阶段。",
        evidenceNote="玩法、上架时间和公司关系有官方依据；本次榜位变化缺少公开活动或收入证据。",
    )
    return game, company, analysis


def google_limbus_profile(row, metadata):
    release = metadata.get("released") or "2023-02-26"
    game = {
        "rank": row["rank"],
        "packageName": row["packageName"],
        "gameName": row["gameName"],
        "developer": metadata.get("developer") or "Project Moon",
        "totalInstalls": metadata.get("downloads", ""),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"],
        "store": "googlePlay",
        "storeUrl": metadata["url"],
        "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"],
        "shortDescription": metadata.get("description", ""),
        "description": "Project Moon世界观下的回合制RPG：连接技能图标形成共鸣，在实时演出的Clash中比较硬币与技能结果，并用不同Identity、E.G.O和12名罪人应对异常体。",
        "releaseDate": release,
        "updatedDate": metadata.get("updated", ""),
        "genre": "回合制RPG / 队伍构筑 / 战术连锁",
        "keywords": "Project Moon；12名罪人；技能连锁；Clash；Identity；E.G.O；异常体；剧情RPG",
        "note": "",
        "releaseDateIso": release,
        "assetRank": 77,
        "comparison90d": comparison(None, row["rank"], GOOGLE_DATE, GOOGLE_BASELINE, True, release),
    }
    company = {
        "en": "Project Moon Co., Ltd.",
        "cn": "Project Moon（月亮计划；韩国独立研发与发行主体）",
        "confidence": "已确认",
        "basis": "Google Play发行名为Project Moon；Apple美国区Lookup列明Project Moon Co., Ltd.为seller，官方产品站将Limbus Company纳入Project Moon自有世界观。未发现需上溯的已披露集团归属。",
        "source": "https://limbuscompany.com/",
    }
    analysis = trend(
        "趋势：2023年以12名罪人、技能图标连锁和实时演出的Clash切入Project Moon核心用户，成熟期由章节、赛季、Identity与E.G.O更新支撑；关键转折：9月17日Apple 1.114.0明确上线Season 8、新Identity和新章节，时间上紧邻双端进榜但不直接认定因果；主力素材：反乌托邦都市、巴士小队、彩色技能链、硬币判定、E.G.O爆发和异常体Boss。",
        "2023年2月上线后，产品用12名罪人的公路式都市叙事承接Project Moon既有世界观；战斗把回合制队伍构筑与实时演出的Clash结合，玩家连接同色或同罪属性技能、切换Identity与E.G.O，并在异常体战中手动指定攻击目标。成熟期主要由章节剧情、赛季通行证与角色形态更新维持核心用户。",
        "本次由榜外进入Google Play美国策略畅销TOP60第43名；同日iOS进入第16名，形成明显的双端同步信号。Google本店released日期为2023年2月26日，早于90天窗口；因缺少2026-06-20精确基准，内部保持pending并按常规展示。",
        "Apple官方1.114.0版本于9月17日发布，明确包含Season 8、新Identity与新章节；这是可确认的运营节点，且与今天双端进入时间相邻。现有证据只能说明时间重合，不能把榜位变化全部归因于版本。",
        "12名罪人围绕巴士行动、阴郁反乌托邦都市、彩色技能图标连成共鸣、Clash硬币胜负、Identity立绘切换、E.G.O大招与异常体Boss。素材判断结合Google商品页、Apple版本说明与官方产品资料，可信度为中。",
        "观察下一工作日能否同时守住Google前50与iOS前20；若两端快速回落，则把本次记录为Season 8窗口附近的短时付费峰值，而非长期趋势。",
        game["storeUrl"],
        [
            {"label": "Limbus Company官方网站", "url": "https://limbuscompany.com/", "type": "primary"},
            {"label": "Apple美国区商品页与1.114.0版本说明", "url": "https://apps.apple.com/us/app/limbus-company/id6444112366", "type": "lifecycle-analysis"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="玩法、Google本店上架日期与素材来自Google商品页；Season 8、新Identity和新章节来自Apple官方1.114.0版本说明，官方产品站用于核验产品体系。",
        changeReason="双端当日进入，重新建立本店素材、公司归属与独立生命周期档案；仅记录版本与榜位时间相邻，不写成确定因果。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2023年上线、技能连锁与Clash入口梳理至Season 8、章节、Identity和E.G.O成熟运营阶段。",
        evidenceNote="上架、玩法和Season 8节点有官方依据；榜位原因与长期素材迁移缺少平台收入分拆证据。",
    )
    return game, company, analysis


def google_arknights_profile(row, metadata):
    release = metadata.get("released") or "2020-01-15"
    game = {
        "rank": row["rank"],
        "packageName": row["packageName"],
        "gameName": row["gameName"],
        "developer": metadata.get("developer") or "Yostar Limited.",
        "totalInstalls": metadata.get("downloads", ""),
        "recentInstalls30d": "",
        "dailyChange": "NEW",
        "rankIconUrl": metadata["icon"],
        "store": "googlePlay",
        "storeUrl": metadata["url"],
        "iconUrl": metadata["icon"],
        "screenshotUrl": metadata["screenshot"],
        "shortDescription": metadata.get("description", ""),
        "description": "以干员职业、攻击范围、部署费用、敌人路线与技能时机为核心的格子塔防，并由角色收集、章节活动和基地建设承接长线养成。",
        "releaseDate": release,
        "updatedDate": metadata.get("updated", ""),
        "genre": "塔防 / 战术编队 / 角色养成",
        "keywords": "明日方舟；塔防；干员；职业编队；部署顺序；技能时机；基地建设；关卡策略",
        "note": "",
        "releaseDateIso": release,
        "assetRank": 78,
        "comparison90d": comparison(None, row["rank"], GOOGLE_DATE, GOOGLE_BASELINE, True, release),
    }
    company = {
        "en": "Yostar Limited. / Hypergryph",
        "cn": "悠星（海外发行）/ 鹰角网络（研发与产品体系）",
        "confidence": "已确认",
        "basis": "Google Play列明Yostar Limited.为发行主体；Arknights官方全球站由Yostar运营，鹰角网络官方招聘页将《明日方舟》列为公司项目。",
        "source": "https://career.hypergryph.com/",
    }
    analysis = trend(
        "趋势：2020年全球上线后，以职业克制、部署顺序和技能时机构成长线塔防核心，并由干员收集、章节活动与基地经营维持成熟运营；关键转折：当前Google版本为8月13日更新，未发现与本次#57进榜直接对应的可确认重大转折；主力素材：多职业干员编队、格子部署、敌人路线、技能爆发和罗德岛世界观。",
        "2020年1月上线。产品长期用不同职业干员、攻击范围、部署费用与技能时机构成塔防关卡，再由角色收集、养成、基地建设和剧情活动承接核心用户；现阶段属于成熟长线运营。",
        "本次首次进入项目保存的Google Play美国策略畅销TOP60，位列第57名；iOS则从上期第58名掉榜，呈现跨端反向边界波动。Google本店released日期早于90天窗口，且缺少2026-06-20精确基准，因此内部保持pending并按常规展示。",
        "Google商品页显示当前版本于8月13日更新；公开资料没有把该更新与今天进榜建立因果，也未发现更近的可确认重大转折。",
        "当前商店图集中展示多职业干员同场、格子塔防部署、敌人行进路线、技能范围与基地建设；成熟期仍以角色叙事和高难关卡承接塔防核心。素材判断基于Google商店图与官方产品资料，可信度为中。",
        "观察下一工作日能否脱离后五名并连续留榜，同时对照iOS是否回榜；在没有官方活动或连续名次证据前，仅记录为成熟产品单日跨端反向信号。",
        game["storeUrl"],
        [
            {"label": "Arknights全球官网", "url": "https://www.arknights.global/", "type": "primary"},
            {"label": "鹰角网络官方招聘页", "url": "https://career.hypergryph.com/", "type": "company-research"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="上架日期、当前版本、玩法描述与商店图来自Google美国区商品页；官方全球站与鹰角网络官方招聘页用于交叉确认产品体系。",
        changeReason="首次进入项目Google榜，补建Google本店上架日期、本地素材、公司归属和独立生命周期档案；未把8月更新写成本次进榜原因。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2020年全球上线梳理至当前成熟塔防、角色养成与基地经营阶段。",
        evidenceNote="玩法、上架时间和公司关系有官方依据；本次榜位变化缺少公开活动或收入证据。",
    )
    return game, company, analysis


def ios_limbus_profile(row, metadata):
    game = ios_game_from_metadata(
        row,
        metadata,
        91,
        "回合制RPG / 队伍构筑 / 战术连锁",
        "Project Moon；12名罪人；技能连锁；Clash；Identity；E.G.O；异常体；剧情RPG",
    )
    company = {
        "en": "Project Moon Co., Ltd.",
        "cn": "Project Moon（月亮计划；韩国独立研发与发行主体）",
        "confidence": "已确认",
        "basis": "Apple美国区Lookup列明Project Moon Co., Ltd.为seller；官方产品站将Limbus Company纳入Project Moon自有世界观。未发现需上溯的已披露集团归属。",
        "source": "https://limbuscompany.com/",
    }
    analysis = trend(
        "趋势：2023年以12名罪人、技能图标连锁和实时演出的Clash切入Project Moon核心用户，成熟期由章节、赛季、Identity与E.G.O更新支撑；关键转折：9月17日1.114.0明确上线Season 8、新Identity和新章节，时间上紧邻双端进榜但不直接认定因果；主力素材：反乌托邦都市、巴士小队、彩色技能链、硬币判定、E.G.O爆发和异常体Boss。",
        "2023年2月上线后，产品用12名罪人的公路式都市叙事承接Project Moon既有世界观；战斗把回合制队伍构筑与实时演出的Clash结合，玩家连接同色或同罪属性技能、切换Identity与E.G.O，并在异常体战中手动指定攻击目标。成熟期主要由章节剧情、赛季通行证与角色形态更新维持核心用户。",
        "本次首次进入项目保存的iOS美国策略畅销TOP60，位列第16名；Google同日由榜外进入第43名，形成双端同步信号。Apple本店releaseDate为2023年2月27日，早于90天窗口；因缺少2026-06-20精确基准，内部保持pending并按常规展示。",
        "Apple官方1.114.0版本于9月17日发布，明确包含Season 8、新Identity与新章节；这是可确认的运营节点，且与今天双端进入时间相邻。现有证据只能说明时间重合，不能把榜位变化全部归因于版本。",
        "12名罪人围绕巴士行动、阴郁反乌托邦都市、彩色技能图标连成共鸣、Clash硬币胜负、Identity立绘切换、E.G.O大招与异常体Boss。素材判断结合Apple商店图、版本说明与官方产品资料，可信度为中。",
        "观察下一工作日能否同时守住iOS前20与Google前50；若两端快速回落，则把本次记录为Season 8窗口附近的短时付费峰值，而非长期趋势。",
        game["storeUrl"],
        [
            {"label": "Limbus Company官方网站", "url": "https://limbuscompany.com/", "type": "primary"},
            {"label": "Google Play美国区商品页", "url": "https://play.google.com/store/apps/details?id=com.ProjectMoon.LimbusCompany&hl=en_US&gl=US", "type": "lifecycle-analysis"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="Apple本店上架日期、1.114.0版本说明、玩法与商店图来自Apple Lookup/商品页；官方产品站用于核验产品体系。",
        changeReason="首次进入项目iOS榜，补建本店素材、公司归属和独立生命周期档案；仅记录Season 8与榜位时间相邻，不写成确定因果。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2023年上线、技能连锁与Clash入口梳理至Season 8、章节、Identity和E.G.O成熟运营阶段。",
        evidenceNote="上架、玩法和Season 8节点有官方依据；榜位原因与长期素材迁移缺少平台收入分拆证据。",
    )
    return game, company, analysis


def ios_mafia_city_profile(row, metadata):
    game = ios_game_from_metadata(
        row,
        metadata,
        92,
        "SLG / 黑帮经营 / 联盟战争",
        "黑帮；城市经营；家族；地盘争夺；联盟；实时战争；豪车；Crew；Godfather",
    )
    company = {
        "en": "VoyagerOne Pte. Ltd. / Phantix Games / Yotta Games",
        "cn": "VoyagerOne（Apple法律主体）/ Phantix Games（海外发行品牌）/ 上海友塔网络（Yotta Games；产品体系）",
        "confidence": "已确认",
        "basis": "Apple美国区Lookup列明VoyagerOne Pte. Ltd.为seller、Phantix Games为发行展示名；商品页客服与条款指向Phantix，Mafia City官方站使用Yotta Games域名。产品统一归入上海友塔网络产品体系。",
        "source": "https://mafia.yottagames.com/",
    }
    analysis = trend(
        "趋势：2017年上线后以黑帮城市经营、家族联盟和实时地盘战承接付费，2018年前后又因“Level 1 Crook→Boss”等级逆袭短剧形成高辨识度获量资产；关键转折：9月17日1.8.519上线Beers without Borders活动、Dionysus Garden装饰与联盟招募调整，时间上紧邻本次iOS回榜但不直接认定因果；主力素材：等级逆袭、Boss权力、豪车、Crew编制、城市地盘与联盟对抗。",
        "Apple美国区于2017年5月上架。产品本体以经营黑帮地盘、研究科技、配置Bulker/Shooter/Biker/Vehicle四类Crew、加入家族并进行实时城市战争为核心；成熟期主要依靠家族关系、跨服竞争、持续活动与高价值用户维持。外层获量则长期使用低等级角色受辱、选择后升级为Boss的短剧情景。",
        "本次首次进入项目保存的iOS美国策略畅销TOP60，位列第59名；Google同产品当前第44名。Apple本店releaseDate为2017年5月16日，早于90天窗口；因缺少2026-06-20精确基准，内部保持pending并按常规展示。",
        "Apple官方1.8.519版本于9月17日发布，新增Beers without Borders活动、Dionysus Garden地盘装饰与社交装饰套装，并调整Inventory、Island Edit、Vigilante Succession及Syndicate Recruitment。这是可确认的运营节点，但现有证据不能证明它单独造成今天回榜。",
        "等级逆袭短剧、黑帮Boss身份、豪车与地盘视觉奖励构成外层获量；商店内层展示城市经营、四类Crew、家族协作、科技树、世界地图和实时地盘战。当前判断结合Apple商品页、官方版本说明与产品站，可信度为中。",
        "观察下一工作日能否离开后五名并继续与Google同时在榜；若迅速退出，只记录为Beers without Borders更新窗口附近的榜尾回归信号。",
        game["storeUrl"],
        [
            {"label": "Mafia City官方网站", "url": "https://mafia.yottagames.com/", "type": "primary"},
            {"label": "Phantix Games官方条款", "url": "https://www.phantixgames.com/en/article/terms_of_use", "type": "company-research"},
            {"label": "Google Play美国区商品页", "url": "https://play.google.com/store/apps/details?id=com.yottagames.mafiawar&hl=en_US&gl=US", "type": "lifecycle-analysis"},
        ],
    )
    analysis = clean_analysis(analysis)
    analysis["sourceAudit"].update(
        confidence="中",
        basis="Apple本店上架日期、玩法、版本说明与商店图来自Apple Lookup/商品页；官方产品站、Phantix条款及Google同产品页用于核验发行与产品体系。",
        changeReason="首次进入项目iOS榜，补建Apple本店素材、公司归属和独立生命周期档案；仅记录1.8.519与回榜时间相邻。",
    )
    analysis["lifecycleAudit"].update(
        confidence="中",
        scope="从2017年黑帮城市SLG上线、2018年前后等级逆袭短剧传播梳理至当前家族、活动和地盘战成熟运营。",
        evidenceNote="玩法、上架时间、当前活动和发行主体有官方依据；广告演化用于解释长期素材识别度，不将单日榜位写成确定因果。",
    )
    return game, company, analysis


def build_google(rows, source_info):
    current = records(
        "data/games-20260917.json", "data/enrichment-20260917.json", "data/trends-20260917.json", "packageName"
    )
    historical = merged_records(history_specs("", GOOGLE_DATES), "packageName")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    games, companies, trends, asset_bundle = [], {}, {}, {}
    for row in rows:
        rank, package = row["rank"], row["packageName"]
        if package == "com.ProjectMoon.LimbusCompany":
            metadata = play_metadata(package)
            game, company, analysis = google_limbus_profile(row, metadata)
            asset_bundle["77_icon"] = data_uri(metadata["icon"], (256, 256))
            asset_bundle["77_store"] = data_uri(metadata["screenshot"], (720, 720))
        elif package == "com.YoStarEN.Arknights":
            metadata = play_metadata(package)
            game, company, analysis = google_arknights_profile(row, metadata)
            asset_bundle["78_icon"] = data_uri(metadata["icon"], (256, 256))
            asset_bundle["78_store"] = data_uri(metadata["screenshot"], (720, 720))
        elif package in current:
            game, company, analysis = map(deepcopy, current[package])
        elif package in historical:
            game, company, analysis = map(deepcopy, historical[package])
        elif package == "leyi.ageofspirits":
            metadata = play_metadata(package)
            game, company, analysis = age_of_spirits_profile(row, metadata)
            asset_bundle["75_icon"] = data_uri(metadata["icon"], (256, 256))
            asset_bundle["75_store"] = data_uri(metadata["screenshot"], (720, 720))
        elif package == "aliens.zombies.invasion":
            metadata = play_metadata(package)
            game, company, analysis = aliens_profile(row, metadata)
            asset_bundle["76_icon"] = data_uri(metadata["icon"], (256, 256))
            asset_bundle["76_store"] = data_uri(metadata["screenshot"], (720, 720))
        else:
            raise RuntimeError(f"Unexpected Google entrant: {row}")
        change = delta_label(old_rank.get(package), rank)
        comp = comparison(None, rank, GOOGLE_DATE, GOOGLE_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row.get("developer", game.get("developer", "")),
            store="googlePlay",
            storeUrl=row["storeUrl"],
            iconUrl=row["iconUrl"],
            screenshotUrl=row["screenshotUrl"],
            totalInstalls=str(row.get("downloads") or game.get("totalInstalls") or "").replace("+", " +"),
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(
            clean_analysis(analysis), "Google Play", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)

    enrichment = deepcopy(load("data/enrichment-20260917.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=GOOGLE_BASELINE,
        currentDate=GOOGLE_DATE,
        new="当前榜单日期前90天内按Google Play美国区商品页released日期上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/games-20260918.json", games)
    save("data/enrichment-20260918.json", enrichment)
    save("data/trends-20260918.json", trends)
    manifest = load("assets/manifest.json")
    manifest["date"] = GOOGLE_DATE
    if asset_bundle:
        save("assets/assets-15.json", asset_bundle)
        if "assets-15.json" not in manifest["files"]:
            manifest["files"].append("assets-15.json")
    save("assets/manifest.json", manifest)

    cross_check = audit_google(rows)
    save(
        "data/history/google-play/2026-09-18.json",
        {
            "store": "google-play",
            "country": "US",
            "category": "Games > Strategy > Top Grossing",
            "date": CAPTURE,
            "dataDate": GOOGLE_DATE,
            "sourceCapturedAt": source_info["capturedAt"],
            "sourceUrl": source_info["sourceUrl"],
            "sourceEndpoint": source_info["sourceEndpoint"],
            "sourceMethod": source_info["sourceMethod"],
            "freshnessNote": "Google Play不公开该榜单的Last updated标签；以北京时间直连抓取时间记录新鲜度。",
            "crossCheck": cross_check,
            "rankings": [
                {
                    "rank": game["rank"],
                    "packageName": game["packageName"],
                    "gameName": game["gameName"],
                    "sourceUrl": game["storeUrl"],
                }
                for game in games
            ],
        },
    )
    return games, cross_check


def build_ios(rows, source_url, source_updated):
    current = records(
        "data/ios-games-20260917.json",
        "data/ios-enrichment-20260917.json",
        "data/ios-trends-20260917.json",
        "appId",
    )
    historical = merged_records(history_specs("ios-", IOS_DATES), "appId")
    old_rank = {product_id: value[0]["rank"] for product_id, value in current.items()}
    games, companies, trends, asset_bundle = [], {}, {}, {}
    for row in rows:
        rank, app_id = row["rank"], row["appId"]
        if app_id == "6444112366":
            metadata = lookup([app_id])[app_id]
            game, company, analysis = ios_limbus_profile(row, metadata)
            asset_bundle["91_icon"] = data_uri(game["iconUrl"], (256, 256))
            asset_bundle["91_store"] = data_uri(game["screenshotUrl"], (720, 720))
        elif app_id == "1235569398":
            metadata = lookup([app_id])[app_id]
            game, company, analysis = ios_mafia_city_profile(row, metadata)
            asset_bundle["92_icon"] = data_uri(game["iconUrl"], (256, 256))
            asset_bundle["92_store"] = data_uri(game["screenshotUrl"], (720, 720))
        elif app_id in current:
            game, company, analysis = map(deepcopy, current[app_id])
        elif app_id in historical:
            game, company, analysis = map(deepcopy, historical[app_id])
        elif app_id == "1464872022":
            metadata = lookup([app_id])[app_id]
            game, company, analysis = ios_arknights_profile(row, metadata)
            asset_bundle["90_icon"] = data_uri(game["iconUrl"], (256, 256))
            asset_bundle["90_store"] = data_uri(game["screenshotUrl"], (720, 720))
        else:
            raise RuntimeError(f"Unexpected iOS entrant: {row}")
        change = delta_label(old_rank.get(app_id), rank)
        comp = comparison(None, rank, IOS_DATE, IOS_BASELINE, True, game.get("releaseDateIso"))
        game.update(
            rank=rank,
            gameName=row["gameName"],
            developer=row["developer"],
            store="ios",
            storeUrl=f"https://apps.apple.com/us/app/id{app_id}",
            dailyChange=change,
            comparison90d=comp,
        )
        analysis = refresh_daily_rank_path(
            clean_analysis(analysis), "iOS", rank, change, comp["status"], game.get("releaseDateIso", "")
        )
        companies[str(rank)] = company
        trends[str(rank)] = analysis
        games.append(game)

    enrichment = deepcopy(load("data/ios-enrichment-20260917.json"))
    enrichment["productCompaniesByRank"] = companies
    enrichment["comparisonPolicy"].update(
        baselineDate=IOS_BASELINE,
        currentDate=IOS_DATE,
        new="当前榜单日期前90天内按Apple Lookup releaseDate上架，且当前进入TOP60。",
        surge="上架早于90天窗口、精确基准日已在同口径TOP60，且baselineRank-currentRank>5。",
        normal="不满足新品或飙升条件；缺少精确基准的较老产品内部保留pending，页面按常规展示。",
        pending="上架早于窗口但缺少精确同口径90天基准，不做代理推断。",
    )
    save("data/ios-games-20260918.json", games)
    save("data/ios-enrichment-20260918.json", enrichment)
    save("data/ios-trends-20260918.json", trends)
    manifest = load("assets/ios-manifest.json")
    manifest["date"] = IOS_DATE
    if asset_bundle:
        save("assets/ios-assets-22.json", asset_bundle)
        if "ios-assets-22.json" not in manifest["files"]:
            manifest["files"].append("ios-assets-22.json")
    save("assets/ios-manifest.json", manifest)

    source_date = datetime.fromisoformat(source_updated.replace("Z", "+00:00")).astimezone(
        ZoneInfo("Asia/Shanghai")
    ).date().isoformat()
    save(
        "data/history/ios/2026-09-18.json",
        {
            "store": "ios",
            "country": "US",
            "device": "iPhone",
            "category": "Games > Strategy > Top Grossing",
            "date": source_date,
            "dataDate": source_date,
            "sourceUpdated": source_updated,
            "sourceUrl": source_url,
            "rankings": [
                {
                    "rank": game["rank"],
                    "appId": game["appId"],
                    "gameName": game["gameName"],
                    "sourceUrl": game["storeUrl"],
                }
                for game in games
            ],
        },
    )
    return games, source_date


def main():
    google_source = fetch_top_grossing_strategy()
    ios_url, ios_updated, ios_rows = parse_ios()
    ios_source_date = datetime.fromisoformat(ios_updated.replace("Z", "+00:00")).astimezone(
        ZoneInfo("Asia/Shanghai")
    ).date().isoformat()
    if google_source["dataDate"] != GOOGLE_DATE:
        raise RuntimeError(f"Google capture date is {google_source['dataDate']}, expected {GOOGLE_DATE}")
    if ios_source_date != IOS_DATE:
        raise RuntimeError(f"Apple source is still dated {ios_source_date}; keep the previous valid iOS snapshot")
    if len(google_source["rows"]) != 60 or len({row["packageName"] for row in google_source["rows"]}) != 60:
        raise RuntimeError("Google direct source is not a complete unique TOP60")
    if len(ios_rows) != 60 or len({row["appId"] for row in ios_rows}) != 60:
        raise RuntimeError("Apple RSS is not a complete unique TOP60")
    google, audit = build_google(google_source["rows"], google_source)
    ios, _ = build_ios(ios_rows, ios_url, ios_updated)
    print("Google", google_source["capturedAt"], [(g["rank"], g["gameName"]) for g in google if g["rank"] in (1, 25, 60)])
    print("AppBrain audit", audit)
    print("iOS", ios_updated, [(g["rank"], g["gameName"]) for g in ios if g["rank"] in (1, 25, 60)])


if __name__ == "__main__":
    main()
