#!/usr/bin/env python3
"""Fetch the live US Strategy top-grossing chart directly from Google Play.

Google Play's web category page loads chart tabs through its own PlayStoreUi
batch endpoint.  This module requests the ``topgrossing`` / ``GAME_STRATEGY``
cluster, validates a complete TOP60, and returns the small metadata subset used
by the daily updater.  It does not depend on AppBrain or another chart vendor.
"""

import json
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo


PUBLIC_SOURCE_URL = "https://play.google.com/store/apps/category/GAME_STRATEGY?hl=en_US&gl=US"
RPC_URL = (
    "https://play.google.com/_/PlayStoreUi/data/batchexecute"
    "?rpcids=vyAe2"
    "&source-path=%2Fstore%2Fapps%2Fcategory%2FGAME_STRATEGY"
    "&hl=en_US&gl=US&rt=c"
)
CHART_METHOD = "Google Play PlayStoreUi / vyAe2 / topgrossing / GAME_STRATEGY / US"


def _path(value, *indexes, default=""):
    try:
        for index in indexes:
            value = value[index]
        return value
    except (IndexError, KeyError, TypeError):
        return default


def _request_body(limit):
    # The first four cluster options are the minimum fields accepted by vyAe2:
    # page size, full-record flag, continuation token, and requested app fields.
    cluster_options = [
        [8, [20, limit]],
        True,
        None,
        [64, 1, 195, 71, 8, 72, 9, 10, 11, 139, 12, 16, 145, 148, 150,
         151, 152, 27, 30, 31, 96, 32, 34, 163, 100, 165, 104, 169, 108,
         110, 113, 55, 56, 57, 122],
    ]
    rpc_arguments = [[None, cluster_options, [2, "topgrossing", "GAME_STRATEGY"]]]
    envelope = [[["vyAe2", json.dumps(rpc_arguments, separators=(",", ":")), None, "generic"]]]
    return urlencode({"f.req": json.dumps(envelope, separators=(",", ":"))}).encode()


def _decode_response(raw):
    text = raw.decode("utf-8")
    frames = None
    for line in text.splitlines():
        if line.startswith("[["):
            frames = json.loads(line)
            break
    if not frames:
        raise RuntimeError("Google Play returned no vyAe2 response frame")
    for frame in frames:
        if len(frame) >= 3 and frame[0] == "wrb.fr" and frame[1] == "vyAe2":
            return json.loads(frame[2])
    raise RuntimeError("Google Play response did not contain the expected vyAe2 payload")


def _parse_apps(payload, limit):
    app_nodes = _path(payload, 0, 1, 0, 28, 0, default=[])
    rows = []
    for rank, node in enumerate(app_nodes[:limit], 1):
        package = _path(node, 0, 0, 0)
        name = _path(node, 0, 3)
        if not package or not name:
            raise RuntimeError(f"Google Play row {rank} is missing package or title")
        screenshots = []
        for image_node in _path(node, 0, 2, default=[]):
            image_url = _path(image_node, 3, 2)
            if image_url and image_url not in screenshots:
                screenshots.append(image_url)
        rows.append({
            "rank": rank,
            "packageName": package,
            "gameName": name,
            "developer": _path(node, 0, 14),
            "iconUrl": _path(node, 0, 1, 3, 2),
            "screenshotUrl": screenshots[0] if screenshots else "",
            "downloads": _path(node, 0, 15),
            "storeUrl": f"https://play.google.com/store/apps/details?id={package}&hl=en_US&gl=US",
        })
    expected_ranks = list(range(1, limit + 1))
    if len(rows) != limit or [row["rank"] for row in rows] != expected_ranks:
        raise RuntimeError(f"Google Play returned {len(rows)} rows; expected {limit}")
    packages = [row["packageName"] for row in rows]
    if len(set(packages)) != limit:
        raise RuntimeError("Google Play TOP60 contains duplicate package names")
    return rows


def fetch_top_grossing_strategy(limit=60, timeout=60):
    if not 1 <= limit <= 100:
        raise ValueError("limit must be between 1 and 100")
    request = Request(
        RPC_URL,
        data=_request_body(limit),
        headers={
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "User-Agent": "Mozilla/5.0 (compatible; StrategyChartUpdater/2.0)",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": PUBLIC_SOURCE_URL,
        },
    )
    with urlopen(request, timeout=timeout) as response:
        payload = _decode_response(response.read())
    captured_at = datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds")
    return {
        "sourceUrl": PUBLIC_SOURCE_URL,
        "sourceEndpoint": RPC_URL,
        "sourceMethod": CHART_METHOD,
        "capturedAt": captured_at,
        "dataDate": captured_at[:10],
        "rows": _parse_apps(payload, limit),
    }


def main():
    result = fetch_top_grossing_strategy()
    print(result["capturedAt"], result["sourceMethod"])
    for index in (0, 24, 59):
        row = result["rows"][index]
        print(f'#{row["rank"]}\t{row["gameName"]}\t{row["packageName"]}')


if __name__ == "__main__":
    main()
