#!/usr/bin/env python3
"""Compare all current official icons with local static assets."""

import base64
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
import json
from pathlib import Path
from urllib.request import Request, urlopen

from PIL import Image, ImageChops, ImageStat


ROOT = Path(__file__).resolve().parents[1]
DATE, STAMP = "2026-11-20", "20261120"


def load(path): return json.loads((ROOT/path).read_text(encoding="utf-8"))


def local_assets(manifest_path):
    result = {}
    for name in load(manifest_path)["files"]: result.update(load("assets/"+name))
    return result


def dhash(data):
    image = Image.open(BytesIO(data)).convert("L").resize((17,16), Image.Resampling.LANCZOS)
    pixels = list(image.getdata())
    value = 0
    for y in range(16):
        for x in range(16): value = (value << 1) | (pixels[y*17+x] > pixels[y*17+x+1])
    return value


def normalized_rmse(left, right):
    a=Image.open(BytesIO(left)).convert("RGB").resize((128,128),Image.Resampling.LANCZOS)
    b=Image.open(BytesIO(right)).convert("RGB").resize((128,128),Image.Resampling.LANCZOS)
    return max(ImageStat.Stat(ImageChops.difference(a,b)).rms)


def bytes_from_data_uri(value): return base64.b64decode(value.split(",",1)[1])


def audit_one(store, game, assets):
    key=f"{int(game['assetRank']):02d}_icon"
    local=assets.get(key,"")
    if not str(local).startswith("data:image/"): return {"rank":game["rank"],"gameName":game["gameName"],"id":game.get("packageName") or game.get("appId"),"status":"missing-local","distance":None}
    request=Request(game["rankIconUrl"],headers={"User-Agent":"Mozilla/5.0","Referer":game["storeUrl"]})
    with urlopen(request,timeout=8) as response: remote=response.read()
    local_bytes=bytes_from_data_uri(local)
    distance=(dhash(local_bytes) ^ dhash(remote)).bit_count()
    rmse=normalized_rmse(local_bytes,remote)
    return {"rank":game["rank"],"gameName":game["gameName"],"id":game.get("packageName") or game.get("appId"),"assetKey":key,"status":"match" if distance<=18 or rmse<=12 else "review","distance":distance,"normalizedRmse":round(rmse,3),"officialUrl":game["rankIconUrl"]}


def run(store, games_path, manifest_path, output):
    games=load(games_path); assets=local_assets(manifest_path); results=[]
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures={pool.submit(audit_one,store,g,assets):g for g in games}
        for future in as_completed(futures):
            game=futures[future]
            try: results.append(future.result())
            except Exception as error: results.append({"rank":game["rank"],"gameName":game["gameName"],"id":game.get("packageName") or game.get("appId"),"status":"network-error","distance":None,"error":str(error)})
    results.sort(key=lambda x:x["rank"])
    report={"date":DATE,"store":store,"method":"Current official icon versus local data-URI asset: accept 256-bit difference-hash distance<=18 or normalized RGB RMSE<=12","rowCount":len(games),"matched":sum(x["status"]=="match" for x in results),"review":sum(x["status"]=="review" for x in results),"networkErrors":sum(x["status"]=="network-error" for x in results),"missingLocal":sum(x["status"]=="missing-local" for x in results),"results":results}
    (ROOT/output).write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(output,report["matched"],report["review"],report["networkErrors"],report["missingLocal"])


run("googlePlay",f"data/games-{STAMP}.json","assets/manifest.json",f"data/icon-audit-google-{DATE}.json")
run("ios",f"data/ios-games-{STAMP}.json","assets/ios-manifest.json",f"data/icon-audit-ios-{DATE}.json")
