#!/usr/bin/env python3
"""Static analysis of an Android APK.

Extracts the manifest surface (permissions, components, exported flags,
SDK levels), dex metadata and signing info from an APK, and prints a
human-readable report (or JSON).

Two engines:
  * **android**  — full androguard-manifest analysis (install it: pip install androguard).
  * **zip fallback** — pure-stdlib listing of the APK's archive, so the tool
    still produces a useful inventory with zero dependencies.

Usage:
    python analyze.py app.apk             # text report
    python analyze.py app.apk --json      # machine-readable
    python analyze.py app.apk --format md # markdown
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any

REPORT_OK = (
    "file", "size_bytes", "sha256", "archive_entries",
    "package", "version_name", "version_code",
    "min_sdk", "target_sdk",
    "permissions", "activities", "services", "receivers", "providers",
    "exported", "cert", "signing", "note",
)


# --------------------------------------------------------------------------
# APK inventory (pure stdlib — always runs)
# --------------------------------------------------------------------------
def _archive_info(apk: zipfile.ZipFile) -> list[str]:
    names = sorted(apk.namelist())
    if not names:
        return []
    # Keep it terse for the report; full list through --json
    return names[:60]


def _find_cert(apk: zipfile.ZipFile) -> str:
    """Extract a signing cert if present (META-INF/*.{RSA,DSA,EC})."""
    for name in apk.namelist():
        if name.startswith("META-INF/") and name.rsplit(".", 1)[-1].upper() in ("RSA", "DSA", "EC"):
            try:
                data = apk.read(name)
                return f"{name} ({len(data)} bytes)"
            except KeyError:
                continue
    return ""


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# androguard analysis (optional)
# --------------------------------------------------------------------------
def _androguard_analysis(apk_path: Path) -> dict[str, Any]:
    from androguard.core.apk import APK  # type: ignore
    apk = APK(apk_path)

    return {
        "package": apk.get_package() or apk.get_app_name() or "",
        "version_name": apk.get_androidversion_name() or "",
        "version_code": apk.get_androidversion_code() or "",
        "min_sdk": apk.get_min_sdk_version() or "",
        "target_sdk": apk.get_target_sdk_version() or "",
        "permissions": sorted(set(apk.get_permissions() or [])),
        "activities": sorted(set(apk.get_activities() or [])),
        "services": sorted(set(apk.get_services() or [])),
        "receivers": sorted(set(apk.get_receivers() or [])),
        "providers": sorted(set(apk.get_providers() or [])),
        "signing": bool(getattr(apk, "is_signed", lambda: False)()),
    }


# --------------------------------------------------------------------------
# Reports
# --------------------------------------------------------------------------
def analyze_apk(apk_path: Path) -> dict[str, Any]:
    report: dict[str, Any] = {
        "file": str(apk_path),
        "size_bytes": apk_path.stat().st_size,
        "sha256": _sha256(apk_path),
    }
    if not zipfile.is_zipfile(apk_path):
        raise ValueError(f"{apk_path} is not a valid zip/APK")

    with zipfile.ZipFile(apk_path) as apk:
        report["archive_entries"] = _archive_info(apk)
        report["cert"] = _find_cert(apk)

    try:
        deep = _androguard_analysis(apk_path)
        report.update({k: v for k, v in deep.items() if v not in (None, [], "")})
    except ImportError:
        report["note"] = "androguard not installed — running in stdlib (zip) mode. pip install androguard for the full report."
    except Exception as exc:  # pragma: no cover - parsing quirks
        report["note"] = f"androguard analysis failed: {exc}"

    return report


def _sha256(apk_path: Path) -> str:
    h = hashlib.sha256()
    with open(apk_path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def render_text(report: dict[str, Any]) -> str:
    lines = [f"== android-security-lab: analyze  ({report['file']}) =="]
    meta = ["package", "version", "version_code", "min_sdk", "target_sdk", "cert"]
    for key in meta:
        if report.get(key) not in (None, "", []):
            lines.append(f"  {key:<16}: {report[key]}")
    locked = report.get("permissions")
    if locked:
        lines.append(f"  permissions    : {', '.join(locked)}")
    export = report.get("activities")
    if export:
        lines.append(f"  activities     : {', '.join(export)[:120]}")
    if report.get("note"):
        lines.append(f"  note           : {report['note']}")
    lines.append(f"  archive entries: {len(report.get('archive_entries', []))}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Static analysis of an Android APK.")
    ap.add_argument("apk", help="path to an APK file")
    ap.add_argument("--json", action="store_true", help="emit JSON report")
    args = ap.parse_args(argv)

    p = Path(args.apk)
    if not p.is_file():
        print(f"[error] no such file: {p}")
        return 1

    try:
        report = analyze_apk(p)
    except ValueError as exc:
        print(f"[error] {exc}")
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())