#!/usr/bin/env python3
"""Build a small local icon bundle for the daily market brief product cards."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


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
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[1]
    brief = load_json(repo / args.brief)
    store_config = {
        "googlePlay": ("packageName", "assets/manifest.json"),
        "ios": ("appId", "assets/ios-manifest.json"),
    }
    output: dict[str, str] = {}

    for store_key, (id_field, manifest_path) in store_config.items():
        games = load_json(repo / brief["rankingSources"][store_key])
        games_by_id = {str(game[id_field]): game for game in games}
        assets = load_assets(repo, manifest_path)
        for product in brief["rankingDynamics"][store_key]["products"]:
            product_id = str(product["productId"])
            game = games_by_id.get(product_id)
            if game is None:
                raise SystemExit(f"Missing {store_key} product in ranking data: {product_id}")
            asset_key = f"{int(game['assetRank']):02d}_icon"
            icon = assets.get(asset_key)
            if not icon:
                raise SystemExit(f"Missing icon asset {asset_key} for {product_id}")
            output[product["iconKey"]] = icon

    output_path = repo / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(output, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")

    print(f"Wrote {len(output)} local icons to {output_path.relative_to(repo)}")


if __name__ == "__main__":
    main()
