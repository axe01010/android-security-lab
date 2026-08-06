#!/usr/bin/env python3
"""One-command full static pass: analyze → scan → decompile an APK.

Usage:
    python examples/run_full_pass.py <apk-or-built>
    python examples/run_full_pass.py --sample        # build a sample first
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(tool: str, apk: Path) -> int:
    print(f"\n=== {tool}.py {apk.name} ===")
    return subprocess.call([sys.executable, str(ROOT / f"{tool}.py"), str(apk)])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("apk", nargs="?", default=None)
    ap.add_argument("--sample", action="store_true", help="build samples/sample.apk first")
    args = ap.parse_args(argv)

    if args.sample:
        subprocess.call([sys.executable, str(ROOT / "examples" / "make_sample_apk.py")])
    apk = Path(args.apk) if args.apk else ROOT / "samples" / "sample.apk"
    if not apk.is_file():
        print("no apk — build one: python examples/make_sample_apk.py")
        return 1

    rc = run("analyze", apk)
    rc |= run("scan", apk)
    rc |= run("decompile", apk)
    print(f"\n(full pass exit code: {rc})")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())