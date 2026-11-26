#!/usr/bin/env python3
"""Audit the 2026-11-26 official icons against local static assets."""

from pathlib import Path


source_path = Path(__file__).with_name("audit_icons_20261125.py")
source = source_path.read_text(encoding="utf-8")
source = source.replace('2026-11-25", "20261125', '2026-11-26", "20261126')
source = source.rsplit('\nrun("googlePlay"', 1)[0]
namespace = {"__file__": __file__, "__name__": "audit_helpers"}
exec(compile(source, __file__, "exec"), namespace)
namespace["run"]("googlePlay", "data/games-20261126.json", "assets/manifest.json", "data/icon-audit-google-2026-11-26.json")
namespace["run"]("ios", "data/ios-games-20261126.json", "assets/ios-manifest.json", "data/icon-audit-ios-2026-11-26.json")
