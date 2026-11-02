#!/usr/bin/env python3
"""Compare current store icon URLs with the local static icon bundles.

The ranking page addresses icons by the stable ``assetRank`` field.  Daily
ranking refreshes update ``iconUrl`` metadata, but an existing product may
change its store icon without receiving a new local asset.  This audit catches
that drift and can write a small, last-loaded override bundle containing only
the mismatches.
"""

from __future__ import annotations

import argparse
import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import io
import json
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parents[1]
STORE_DEFAULTS = {
    "google": ("assets/manifest.json", "data/games-{stamp}.json", "packageName"),
    "ios": ("assets/ios-manifest.json", "data/ios-games-{stamp}.json", "appId"),
}


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")


def load_assets(manifest_path: Path) -> dict[str, str]:
    manifest = load_json(manifest_path)
    assets: dict[str, str] = {}
    for filename in manifest["files"]:
        assets.update(load_json(manifest_path.parent / filename))
    return assets


def decode_data_uri(uri: str) -> bytes:
    header, encoded = uri.split(",", 1)
    if ";base64" not in header:
        raise ValueError("local asset is not a base64 data URI")
    return base64.b64decode(encoded)


def fetch(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "Mozilla/5.0 icon-audit/1.0"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def normalized_image(raw: bytes, size: tuple[int, int] = (64, 64)) -> Image.Image:
    with Image.open(io.BytesIO(raw)) as image:
        if image.mode == "P" and "transparency" in image.info:
            image = image.convert("RGBA")
        return image.convert("RGB").resize(size, Image.Resampling.LANCZOS)


def mean_absolute_error(left: bytes, right: bytes) -> float:
    difference = ImageChops.difference(normalized_image(left), normalized_image(right))
    channel_means = ImageStat.Stat(difference).mean
    return sum(channel_means) / len(channel_means)


def data_uri(raw: bytes) -> str:
    with Image.open(io.BytesIO(raw)) as image:
        if image.mode == "P" and "transparency" in image.info:
            image = image.convert("RGBA")
        converted = image.convert("RGB")
        converted.thumbnail((256, 256), Image.Resampling.LANCZOS)
        output = io.BytesIO()
        converted.save(output, "WEBP", quality=76, method=6)
    return "data:image/webp;base64," + base64.b64encode(output.getvalue()).decode()


def audit_one(game: dict, assets: dict[str, str], id_field: str) -> tuple[dict, str]:
    asset_key = f"{int(game['assetRank']):02d}_icon"
    if asset_key not in assets:
        raise KeyError(f"missing local asset {asset_key}")
    official = fetch(game["iconUrl"])
    score = mean_absolute_error(decode_data_uri(assets[asset_key]), official)
    result = {
        "rank": game["rank"],
        "productId": str(game[id_field]),
        "gameName": game["gameName"],
        "assetRank": game["assetRank"],
        "assetKey": asset_key,
        "meanAbsoluteError": round(score, 3),
        "officialUrl": game["iconUrl"],
    }
    return result, data_uri(official)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", choices=STORE_DEFAULTS, required=True)
    parser.add_argument("--data", help="Ranking JSON path; defaults to the current checked-in snapshot")
    parser.add_argument("--manifest", help="Static asset manifest path")
    parser.add_argument("--threshold", type=float, default=8.0, help="Mean RGB error above which an icon is stale")
    parser.add_argument("--output", help="Write mismatched icons as a last-loaded override bundle")
    parser.add_argument("--keys-per-file", type=int, default=0, help="Split an override into numbered files with at most this many keys")
    parser.add_argument("--report", help="Write a machine-readable audit report")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    default_manifest, data_pattern, id_field = STORE_DEFAULTS[args.store]
    manifest_path = ROOT / (args.manifest or default_manifest)
    manifest = load_json(manifest_path)
    stamp = str(manifest["date"]).replace("-", "")
    data_path = ROOT / (args.data or data_pattern.format(stamp=stamp))
    games = load_json(data_path)
    if len(games) != 60:
        raise SystemExit(f"expected 60 rows in {data_path.relative_to(ROOT)}, found {len(games)}")
    if len({str(game[id_field]) for game in games}) != 60:
        raise SystemExit(f"duplicate {id_field} values in {data_path.relative_to(ROOT)}")

    assets = load_assets(manifest_path)
    rows: list[dict] = []
    encoded_by_key: dict[str, str] = {}
    failures: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(audit_one, game, assets, id_field): game for game in games}
        for future in as_completed(futures):
            game = futures[future]
            try:
                row, encoded = future.result()
                rows.append(row)
                encoded_by_key[row["assetKey"]] = encoded
            except Exception as error:  # Keep the complete audit visible instead of silently skipping.
                failures.append({
                    "rank": game["rank"],
                    "productId": str(game[id_field]),
                    "gameName": game["gameName"],
                    "error": str(error),
                })

    rows.sort(key=lambda row: row["rank"])
    mismatches = [row for row in rows if row["meanAbsoluteError"] > args.threshold]
    override = {row["assetKey"]: encoded_by_key[row["assetKey"]] for row in mismatches}
    output_bundles: list[str] = []
    if args.output:
        output_path = Path(args.output)
        if args.keys_per_file > 0 and len(override) > args.keys_per_file:
            items = list(override.items())
            for index in range(0, len(items), args.keys_per_file):
                part_number = index // args.keys_per_file + 1
                part_path = output_path.with_name(f"{output_path.stem}-{part_number:02d}{output_path.suffix}")
                save_json(ROOT / part_path, dict(items[index:index + args.keys_per_file]))
                output_bundles.append(str(part_path))
        else:
            save_json(ROOT / output_path, override)
            output_bundles.append(str(output_path))

    report = {
        "store": args.store,
        "checkedAt": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(timespec="seconds"),
        "rankingFile": str(data_path.relative_to(ROOT)),
        "manifestFile": str(manifest_path.relative_to(ROOT)),
        "thresholdMeanAbsoluteError": args.threshold,
        "checkedCount": len(rows),
        "mismatchCount": len(mismatches),
        "failureCount": len(failures),
        "action": "override-written" if args.output else "audit-only",
        "outputBundles": output_bundles,
        "mismatches": mismatches,
        "failures": failures,
    }

    if args.report:
        save_json(ROOT / args.report, report)

    print(json.dumps(report, ensure_ascii=False, indent=2))
    if failures:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
