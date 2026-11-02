#!/usr/bin/env python3
"""Build a small local icon bundle for the daily market brief product cards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from audit_store_icons import data_uri, fetch


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_assets(repo: Path, manifest_path: str) -> dict[str, str]:
    manifest_file = repo / manifest_path
    manifest = load_json(manifest_file)
    assets: dict[str, str] = {}
    for filename in manifest["files"]:
        assets.update(load_json(manifest_file.parent / filename))
    return assets


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--brief", required=True, help="Daily market brief JSON path")
    parser.add_argument("--output", required=True, help="Output icon bundle JSON path")
    parser.add_argument(
        "--google-override-bundle",
        action="append",
        default=[],
        help="Only emit Google products whose asset keys occur in these override bundles",
    )
    parser.add_argument("--refresh-from-store-urls", action="store_true", help="Rebuild every card icon from its product-specific store URL")
    parser.add_argument("--keys-per-file", type=int, default=0, help="Split output into numbered files with at most this many icons")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    brief = load_json(repo / args.brief)
    store_config = {
        "googlePlay": ("packageName", "assets/manifest.json"),
        "ios": ("appId", "assets/ios-manifest.json"),
    }
    output: dict[str, str] = {}
    google_overrides: dict[str, str] = {}
    for override_path in args.google_override_bundle:
        google_overrides.update(load_json(repo / override_path))

    for store_key, (id_field, manifest_path) in store_config.items():
        ranking_paths = [brief["rankingSources"][store_key]]
        previous_path = brief.get("previousRankingSources", {}).get(store_key)
        if previous_path:
            ranking_paths.append(previous_path)
        games_by_id = {}
        for ranking_path in ranking_paths:
            for game in load_json(repo / ranking_path):
                games_by_id.setdefault(str(game[id_field]), game)
        assets = load_assets(repo, manifest_path)
        for product in brief["rankingDynamics"][store_key]["products"]:
            product_id = str(product["productId"])
            game = games_by_id.get(product_id)
            if game is None:
                raise SystemExit(f"Missing {store_key} product in ranking data: {product_id}")
            asset_key = f"{int(game['assetRank']):02d}_icon"
            if args.refresh_from_store_urls:
                icon = data_uri(fetch(game["iconUrl"]))
            elif google_overrides:
                if store_key != "googlePlay" or asset_key not in google_overrides:
                    continue
                icon = google_overrides.get(asset_key)
            else:
                icon = assets.get(asset_key)
            if not icon:
                raise SystemExit(f"Missing icon asset {asset_key} for {product_id}")
            output[product["iconKey"]] = icon

    output_path = Path(args.output)
    output_paths = []
    if args.keys_per_file > 0 and len(output) > args.keys_per_file:
        items = list(output.items())
        for index in range(0, len(items), args.keys_per_file):
            part_number = index // args.keys_per_file + 1
            part_path = output_path.with_name(f"{output_path.stem}-{part_number:02d}{output_path.suffix}")
            save_path = repo / part_path
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with save_path.open("w", encoding="utf-8") as handle:
                json.dump(dict(items[index:index + args.keys_per_file]), handle, ensure_ascii=False, separators=(",", ":"))
                handle.write("\n")
            output_paths.append(part_path)
    else:
        save_path = repo / output_path
        save_path.parent.mkdir(parents=True, exist_ok=True)
        with save_path.open("w", encoding="utf-8") as handle:
            json.dump(output, handle, ensure_ascii=False, separators=(",", ":"))
            handle.write("\n")
        output_paths.append(output_path)

    print(f"Wrote {len(output)} local icons to {', '.join(map(str, output_paths))}")


if __name__ == "__main__":
    main()
