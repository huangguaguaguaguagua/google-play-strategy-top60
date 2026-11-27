#!/usr/bin/env python3
"""Build the Beijing 2026-11-27 dual-store snapshots from official sources."""

import daily_update_20261126 as prior
from daily_update_20260820 import comparison, data_uri


updater = prior.updater
editorial = prior.editorial
editorial.DATE = "2026-11-27"
editorial.STAMP = "20261127"
editorial.PREV = "20261126"
editorial.BASELINE = "2026-08-29"
updater.CAPTURE = updater.GOOGLE_DATE = updater.IOS_DATE = "2026-11-27"
updater.STAMP = "20261127"
updater.PREVIOUS_STAMP = "20261126"
updater.GOOGLE_BASELINE = updater.IOS_BASELINE = "2026-08-29"
updater.GOOGLE_DATES = ("20261126",) + updater.GOOGLE_DATES
updater.IOS_DATES = ("20261126",) + updater.IOS_DATES


# 2026-08-29 was a Saturday and the project has no same-scope snapshot for
# that exact day.  An empty in-memory baseline lets the normal builders run
# without creating a fake historical file.  Release-date-new products remain
# visible as new; older products stay pending internally and render as regular.
_load = updater.load


def load_with_missing_weekend_baseline(path):
    if path in (
        "data/history/google-play/2026-08-29.json",
        "data/history/ios/2026-08-29.json",
    ):
        return {"rankings": []}
    return _load(path)


def pending_comparison(_baseline_rank, rank, release_date, _store_label):
    return comparison(None, rank, "2026-11-27", "2026-08-29", True, release_date)


def pending_status_text(game, store_label, basis):
    comp = game["comparison90d"]
    if comp["status"] == "new":
        return f"按{basis}{game.get('releaseDateIso','')}计算，归类为近三个月新上榜。"
    return (
        f"上架早于90天窗口；缺少2026-08-29{store_label}同口径完整TOP60基准，"
        "内部保留pending并按常规在榜展示。"
    )


updater.load = load_with_missing_weekend_baseline
editorial.comparison_for = pending_comparison
editorial.status_text = pending_status_text


def finalize_audits_and_policy():
    for prefix in ("", "ios-"):
        trends_path = f"data/{prefix}trends-20261127.json"
        trends = _load(trends_path)
        for trend in trends.values():
            for key in ("sourceAudit", "lifecycleAudit"):
                audit = trend.get(key, {})
                audit["reviewedAt"] = "2026-11-27"
                if key == "sourceAudit":
                    audit["changeReason"] = "按11月27日官方榜单复核当前名次、相邻快照变化与商店元数据；单日位移仅作待验证信号。"
        updater.save(trends_path, trends)

        enrichment_path = f"data/{prefix}enrichment-20261127.json"
        enrichment = _load(enrichment_path)
        enrichment["comparisonPolicy"].update(
            baselineDate="2026-08-29",
            currentDate="2026-11-27",
            baselineAvailable=False,
            pending="缺少2026-08-29精确同口径完整TOP60基准；上架更早的产品内部保留pending，页面按常规展示。",
        )
        updater.save(enrichment_path, enrichment)

    # Refresh the dated, product-specific turning points for today's most
    # material movements instead of carrying a stale generic explanation.
    for path in ("data/trends-20261127.json", "data/ios-trends-20261127.json"):
        games_path = path.replace("trends", "games")
        games = _load(games_path)
        trends = _load(path)
        by_name = {game["gameName"]: trends[str(game["rank"])] for game in games}
        if "Limbus Company" in by_name:
            trend = by_name["Limbus Company"]
            trend["sections"]["turningPoints"] = (
                "Project Moon于11月26日发布1.120.0定期更新，随后确认已知问题及热修时间；"
                "它与本次双端同时进入同窗，但没有公开收入或归因数据证明更新直接造成榜位变化。"
            )
            trend["summary"] = trend["summary"].split("；关键转折：", 1)[0] + (
                "；关键转折：11月26日1.120.0更新与本次双端同时进榜同窗，先记为待验证信号，不直接归因；"
                "主力素材：暗黑都市、人格抽取、技能拼点、章节Boss与剧情演出。"
            )
        if "The Battle Cats" in by_name:
            trend = by_name["The Battle Cats"]
            trend["sections"]["turningPoints"] = (
                "PONOS宣布PAC-MAN联动于11月26日开启，联动角色与限定关卡为可核验节点；"
                "本次回榜与活动同窗，只能作为活动峰值候选，需后续快照确认。"
            )
            trend["summary"] = (
                "趋势：2014年靠极简横版出兵和荒诞猫咪美术形成长尾，持续用新形态、关卡和联动回流；"
                "关键转折：PAC-MAN联动11月26日开启，本期iOS回榜#42，暂记活动峰值候选；"
                "主力素材：怪猫进化、PAC-MAN限定角色、巨大敌人、低成本反差与联动关卡。"
            )
        updater.save(path, trends)


def ensure_assets(games_path, manifest_path, filename):
    manifest = _load(manifest_path)
    assets = {}
    for bundle in manifest["files"]:
        assets.update(_load("assets/" + bundle))
    additions = {}
    for game in _load(games_path):
        for suffix, url, size in (
            ("icon", game.get("rankIconUrl") or game.get("iconUrl"), (256, 256)),
            ("store", game.get("screenshotUrl"), (720, 960)),
        ):
            key = f"{int(game['assetRank']):02d}_{suffix}"
            if key not in assets:
                additions[key] = data_uri(url, size)
    if additions:
        updater.save("assets/" + filename, additions)
        manifest["files"].append(filename)
    manifest["date"] = "2026-11-27"
    updater.save(manifest_path, manifest)


def refresh_entry_assets(games_path, previous_path, id_key, manifest_path, filename):
    previous_ids = {str(game[id_key]) for game in _load(previous_path)}
    additions = {}
    for game in _load(games_path):
        if str(game[id_key]) in previous_ids:
            continue
        rank = int(game["assetRank"])
        additions[f"{rank:02d}_icon"] = data_uri(game.get("rankIconUrl") or game.get("iconUrl"), (256, 256))
        additions[f"{rank:02d}_store"] = data_uri(game["screenshotUrl"], (720, 960))
    if additions:
        updater.save("assets/" + filename, additions)
        manifest = _load(manifest_path)
        if filename not in manifest["files"]:
            manifest["files"].append(filename)
        updater.save(manifest_path, manifest)


if __name__ == "__main__":
    updater.main()
    ensure_assets("data/games-20261127.json", "assets/manifest.json", "google-assets-refresh-20261127.json")
    ensure_assets("data/ios-games-20261127.json", "assets/ios-manifest.json", "ios-assets-refresh-20261127.json")
    refresh_entry_assets("data/games-20261127.json", "data/games-20261126.json", "packageName", "assets/manifest.json", "google-entry-assets-20261127.json")
    refresh_entry_assets("data/ios-games-20261127.json", "data/ios-games-20261126.json", "appId", "assets/ios-manifest.json", "ios-entry-assets-20261127.json")
    finalize_audits_and_policy()
