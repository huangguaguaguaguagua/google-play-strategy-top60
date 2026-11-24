#!/usr/bin/env python3
"""Build the Beijing 2026-11-24 dual-store snapshots from official sources."""

from copy import deepcopy

import daily_update_20261123 as prior
from daily_update_20260820 import data_uri


updater = prior.updater
prior.prior.prior.DATE = "2026-11-24"
prior.prior.prior.STAMP = "20261124"
prior.prior.prior.PREV = "20261123"
prior.prior.prior.BASELINE = "2026-08-26"
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-11-24"
updater.STAMP = "20261124"
updater.PREVIOUS_STAMP = "20261123"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-08-26"
updater.GOOGLE_DATES = ("20261123",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261123",) + updater.IOS_DATES


editorial = prior.prior.prior
original_source_records = editorial.source_records


def source_records(prefix, id_key):
    current, historical = original_source_records(prefix, id_key)
    if not prefix and "com.YoStarEN.MahjongSoul" not in current and "com.YoStarEN.MahjongSoul" not in historical:
        game = deepcopy(next(value[0] for value in current.values() if value[0]["packageName"] == "com.YoStarEN.Arknights"))
        game.update(
            packageName="com.YoStarEN.MahjongSoul", gameName="Mahjong Soul", developer="Yostar Limited.",
            totalInstalls="500,000 +", recentInstalls30d="", rankIconUrl="", iconUrl="", screenshotUrl="",
            storeUrl="https://play.google.com/store/apps/details?id=com.YoStarEN.MahjongSoul&hl=en_US&gl=US",
            shortDescription="Anime-style Japanese riichi mahjong with ranked, tournament and friendly matches.",
            description="以日式立直麻将为核心，提供段位赛、大会赛和友人赛；角色收集、语音、服装与牌桌装饰构成长线外观内容，移动端与网页端跨平台互通。",
            releaseDate="2019-11-26", releaseDateIso="2019-11-26", updatedDate="Jul 28, 2026",
            genre="立直麻将 / 桌游竞技 / 角色收藏",
            keywords="立直麻将；段位赛；大会赛；友人赛；跨平台；角色收藏；语音；外观",
            note="", assetRank=85,
        )
        company = {
            "en":"Yostar Limited. / YOSTAR (HONG KONG) LIMITED",
            "cn":"悠星网络 / YOSTAR（香港法律主体）",
            "confidence":"已确认",
            "basis":"Google Play列店铺发行名Yostar Limited.并在开发者信息中列YOSTAR (HONG KONG) LIMITED；产品官方主页和2019年移动端首发资料均由Yostar发布。",
            "source":"https://mahjongsoul.yo-star.com/",
        }
        sources = [
            {"label":"Google Play美国区商品页","url":game["storeUrl"],"type":"store"},
            {"label":"Mahjong Soul官方主页","url":"https://mahjongsoul.yo-star.com/","type":"primary"},
            {"label":"2019年移动端首发资料","url":"https://www.crunchyroll.com/news/latest/2019/11/26/sponsored-post-japanese-riichi-mahjong-game-mahjong-soul-launches-on-mobile-today","type":"publisher-provided"},
        ]
        trend = {
            "summary":"趋势：2019年网页端上线后，同年11月进入移动端并以日式立直麻将、段位竞技和二次元角色收藏形成跨平台长线产品；关键转折：本次进入Google Play美国策略畅销榜#58，只能记为待验证回榜信号，未发现可确认的单一活动原因；主力素材：四人牌桌、立直与和牌演出、角色语音/服装及段位赛界面。",
            "sections":{
                "development":"2019年4月先以网页端切入日式立直麻将，11月移动端上线并与网页账号跨平台互通；之后主要以段位赛、大会赛、友人赛和角色/语音/服装等外观收藏维持长期运营。",
                "rankPath":"本次位于Google Play美国策略畅销榜第58名（较前一有效快照进入/回榜#58）。产品上架早于90天窗口，按精确基准计算状态。",
                "turningPoints":"网页端到移动端跨平台是可确认的早期节点；长期版本延续竞技牌局与外观内容。当前未发现可将单日回榜归因于某一活动的可靠证据。",
                "creative":"四人日式麻将牌桌、立直/荣和演出、角色立绘与日语配音、服装和牌背等自定义外观，以及段位晋升界面。当前素材判断基于Google商品页与官方资料，可信度为中。",
                "watch":"观察未来2—3个有效快照能否持续留在TOP60；若迅速退出，只记录为榜尾回榜信号，不扩写为长期趋势。",
            },
            "sourceAudit":{"reviewedAt":"2026-11-24","status":"已复核","confidence":"中","basis":"核心玩法、跨平台和发行主体由商店及官方资料核验；素材仅有商店与官方产品证据。","changeReason":"首次进入当前历史池，按产品单独建立玩法、发行与素材记录。","evidenceNote":"未把单日回榜写成活动效果。","sources":sources},
            "lifecycleAudit":{"reviewedAt":"2026-11-24","status":"已复核","confidence":"中","scope":"从2019年网页首发、移动端跨平台到长期竞技与外观运营。","changeReason":"首次建立生命周期记录。","evidenceNote":"首发时间与跨平台信息来自官方发布资料；当前榜位来自Google Play直连。","sources":sources},
        }
        historical["com.YoStarEN.MahjongSoul"] = (game, company, trend)
    return current, historical


editorial.source_records = source_records


def finalize_audits():
    for path in ("data/trends-20261124.json", "data/ios-trends-20261124.json"):
        values = updater.load(path)
        for trend in values.values():
            for key in ("sourceAudit", "lifecycleAudit"):
                audit = trend.get(key, {})
                audit["reviewedAt"] = "2026-11-24"
                reason = str(audit.get("changeReason", ""))
                for old in ("11月23日", "11月20日"):
                    reason = reason.replace(old, "11月24日")
                audit["changeReason"] = reason
        updater.save(path, values)


def ensure_google_assets():
    manifest = updater.load("assets/manifest.json")
    assets = {}
    for filename in manifest["files"]:
        assets.update(updater.load("assets/" + filename))
    additions = {}
    for game in updater.load("data/games-20261124.json"):
        for suffix, url, size in (("icon", game.get("iconUrl"), (256, 256)), ("store", game.get("screenshotUrl"), (720, 960))):
            key = f"{int(game['assetRank']):02d}_{suffix}"
            if key not in assets:
                additions[key] = data_uri(url, size)
    if additions:
        filename = "google-assets-refresh-20261124.json"
        updater.save("assets/" + filename, additions)
        manifest["files"].append(filename)
        updater.save("assets/manifest.json", manifest)


def refresh_reviewed_assets():
    targets = (
        ("data/games-20261124.json", "assets/manifest.json", "google-icons-refresh-20261124.json", "packageName", {"com.YoStarEN.MahjongSoul"}),
        ("data/ios-games-20261124.json", "assets/ios-manifest.json", "ios-icons-refresh-20261124.json", "appId", {"6738469826"}),
    )
    for games_path, manifest_path, filename, id_key, ids in targets:
        additions = {}
        for game in updater.load(games_path):
            if str(game[id_key]) in ids:
                additions[f"{int(game['assetRank']):02d}_icon"] = data_uri(game["rankIconUrl"], (256, 256))
                if id_key == "packageName":
                    additions[f"{int(game['assetRank']):02d}_store"] = data_uri(game["screenshotUrl"], (720, 960))
        updater.save("assets/" + filename, additions)
        manifest = updater.load(manifest_path)
        if filename not in manifest["files"]:
            manifest["files"].append(filename)
        updater.save(manifest_path, manifest)


if __name__ == "__main__":
    updater.main()
    prior.prior.prior.ensure_ios_assets()
    ensure_google_assets()
    refresh_reviewed_assets()
    finalize_audits()
