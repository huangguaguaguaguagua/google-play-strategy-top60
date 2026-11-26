#!/usr/bin/env python3
"""Offline integrity checks for the reviewed 2026-11-26 dual-store release."""

from pathlib import Path


source_path = Path(__file__).with_name("validate_snapshot_20261125.py")
source = source_path.read_text(encoding="utf-8")
source = source.replace('2026-11-25", "20261125", "20261124', '2026-11-26", "20261126", "20261125')
source = source.replace("2026-08-27.json", "2026-08-28.json")
source = source.replace("2026-11-25T09:42:13+08:00", "2026-11-26T09:09:17+08:00")
source = source.replace("reviewed 2026-11-25", "reviewed 2026-11-26")
namespace = {"__file__": __file__, "__name__": "__main__"}
exec(compile(source, __file__, "exec"), namespace)
