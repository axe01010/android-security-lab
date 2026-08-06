#!/usr/bin/env python3
"""Decompile / unpack an Android APK.

Prefer an installed decompiler (jadx, apktool, frida-dexdump) and fall back
to a stdlib "unpack + strings" pass when none is available. Always produces a
self-contained output directory.

Usage:
    python decompyle.py app.apk            # auto: jadx → apktool → unzip
    python decompile.py app.apk -o out/    # explicit output dir
    python decompile.py app.apk --strings-only
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path
from typing import Any

TOOLS = {
    "jadx": "-d {out} {apk}",
    "apktool": "d -f {apk} -o {out}",
    "enjar": "--enum_decimals --output_dir {out} {apk}",
}


def which_decompiler() -> str | None:
    for name in TOOLS:
        if shutil.which(name):
            return name
    return None


def _unbundle(apk: Path, out: Path) -> int:
    """Stdlib-only fallback: copy entries + strings out of the dex."""
    out.mkdir(parents=True, exist_ok=True)
    (out / "strings.txt").write_text("", encoding="utf-8")
    count = 0
    with zipfile.ZipFile(apk) as z:
        for name in z.namelist():
            target = (out / name).resolve()
            if not str(target).startswith(str(out.resolve())):  # zip-slip guard
                continue
            if name.endswith("/"):
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                if name.endswith(".dex"):
                    data = z.read(name)
                    strs = "".join(chr(b) if 32 <= b < 127 else "\n" for b in data)
                    with open(out / "strings.txt", "a", encoding="utf-8") as fh:
                        fh.write(f"--- {name} ---\n{strs}\n")
                else:
                    target.write_bytes(z.read(name))
            except (KeyError, RuntimeError):
                continue
            count += 1
    return count


def decompile(apk: Path, out: Path, tool: str | None) -> dict[str, Any]:
    out.parent.mkdir(parents=True, exist_ok=True)
    if tool is None:
        return {"method": "unbundle", "entries": _unbundle(apk, out)}
    template = TOOLS[tool]
    cmd = template.format(apk=apk, out=out).split()
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    return {"method": tool, "returncode": res.returncode,
            "stderr": (res.stderr or "")[:500]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Decompile / unpack an APK.")
    ap.add_argument("apk")
    ap.add_argument("-o", "--out", default=None, help="output directory")
    ap.add_argument("--tool", choices=list(TOOLS), default=None,
                    help="force a specific decompiler")
    args = ap.parse_args(argv)

    apk = Path(args.apk)
    if not apk.is_file():
        print(f"[error] no such file: {args.apk}")
        return 1

    tool = args.tool or which_decompiler()
    out = Path(args.out) if args.out else apk.with_suffix(".src")

    print(f"decompiling {apk} → {out}  (tool: {tool or 'stdlib unpack'})")
    result = decompile(apk, out, tool)
    if result["method"] == "unbundle" or result.get("returncode") == 0:
        print(f"[ok] wrote {out}")
    else:
        print(f"[warn] {tool} exited {result.get('returncode')}")
        print(result.get("stderr", ""))
    return int(result.get("returncode", 0) if result.get("returncode") is not None else 0)


if __name__ == "__main__":
    raise SystemExit(main())