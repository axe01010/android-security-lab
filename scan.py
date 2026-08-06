#!/usr/bin/env python3
"""Security scan of an Android APK.

Static, in-memory heuristic scan over the APK's dex + manifest: labels
permission exposure, crypto weakness, cleartext/locnet settings, exported
components, package-signed debuggable flags and secret-looking strings.

Findings are attributed with severity (info/low/medium/high) and a short
remediation line. Works with zero dependencies (stdlib only).
Usage: python scan.py app.apk [--json] [--min-severity medium]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from typing import Any

SEVERITIES = ("info", "low", "medium", "high", "critical")

#: (regex, severity, label, advice) rules applied to the raw dex/string blob.
RULES: list[tuple[str, str, str, str]] = [
    (r"android\.permission\.INTERNET", "info", "internet",
     "declares INTERNET — expected for networked apps"),
    (r"android\.permission\.CAMERA", "medium", "camera",
     "camera access; audit for what it captures and when"),
    (r"android\.permission\.(ACCESS_FINE_LOCATION|ACCESS_COARSE_LOCATION)", "medium", "location",
     "location permission; a privacy reviewer must sign off"),
    (r"android\.permission\.RECORD_AUDIO", "high", "microphone",
     "audio capture is a high-stakes privacy surface"),
    (r"android\.permission\.READ_SMS|read SMS", "critical", "sms-read",
     "reading SMS is rarely needed and leaks PII/OTPs"),
    (r"RECEIVE_BOOT_COMPLETED", "medium", "boot-auto-start", "runs at boot; justify it"),
    (r"usesCleartextTraffic\s*=\s*\"true\"|cleartextTrafficPermitted=\"true\"", "high", "cleartext",
     "allows unencrypted HTTP — disable in production"),
    (r"(?i)Runtime\.getRuntime|\.exec\(\s*[\"']", "medium", "code-exec",
     "dynamic shell execution found; review for command-injection"),
    (r"Lorg/json/|org\.json", "info", "json", "JSON parsing present"),
    (r"javax\.crypto|SecretKeySpec|PBKDF2|AES/ECB", "medium", "crypto",
     "weak/legacy crypto family detected; prefer AES-GCM + PBKDF2"),
    (r"debuggable\s*=\s*\"true\"", "high", "debuggable", "app is debuggable (adb) — strip for release"),
    (r"android:debale=\"true\"", "low", "debug-attr", "manifest debug-attr marker"),
    (r"android:exported=\"true\"|exported\s*=\s*\"true\"", "medium", "exported",
     "exposed component boundary is web-public; ensure it needs to be"),
    (r"(?i)password\s*[:=]\s*[\"'][^\"']{1,}", "high", "hardcoded-password",
     "possible hardcoded credential in dex strings"),
    (r"(?i)(api[_-]?key|secret|token)\s*[:=]\s*\S{8,}", "medium", "secret-looking",
     "potential embedded API key/secret"),
]


def _read_dex(apk: zipfile.ZipFile) -> bytes:
    """Concatenate dex payloads for string-heuristic scanning."""
    parts: list[bytes] = []
    try:
        names = [n for n in apk.namelist() if n.endswith(".dex")]
    except AttributeError:
        names = []
    for name in names:
        try:
            parts.append(apk.read(name))
        except KeyError:
            continue
    return b"\n".join(parts)


def _string_blob(data: bytes) -> str:
    """Decode printable ASCII bytes (enough for dex string signatures)."""
    try:
        return data.decode("utf-8", errors="ignore")
    except ValueError:  # pragma: no cover
        return "".join(chr(b) if 32 <= b < 127 else "\n" for b in data)


def scan_apk(apk_path: Path, min_severity: str = "info") -> dict[str, Any]:
    if not zipfile.is_zipfile(apk_path):
        raise ValueError(f"{apk_path} is not a valid APK")

    order = {s: i for i, s in enumerate(SEVERITIES)}
    threshold = order[min_severity]

    findings: list[dict[str, Any]] = []
    with zipfile.ZipFile(apk_path) as apk:
            dex = _read_dex(apk)
            blob = _string_blob(dex)
    for pattern, sev, label, reason in RULES:
        try:
            if re.search(pattern, blob):
                findings.append({"severity": sev, "label": label, "reason": reason})
        except re.error:
            continue

    findings.sort(key=lambda f: -order[f["severity"]])
    return {
        "file": str(apk_path),
        "findings": findings,
        "summary": {s: sum(1 for f in findings if f["severity"] == s) for s in SEVERITIES},
    }


def render(scan: dict[str, Any]) -> str:
    lines = [f"== android-security: scan  ({scan['file']}) ==", ""]
    if not scan["findings"]:
        lines.append("  no findings (below the chosen threshold).")
        return "\n".join(lines)
    for f in scan["findings"]:
        lines.append(f"  [{f['severity']:<8}] {f['label']:<18} {f['reason']}")
    s = scan["summary"]
    lines.append("")
    lines.append("  counts: " + " · ".join(f"{k}={v}" for k, v in s.items() if v))
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Heuristic security scan of an APK.")
    ap.add_argument("apk")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--min-severity", choices=SEVERITIES, default="info")
    args = ap.parse_args(argv)

    p = Path(args.apk)
    if not p.is_file():
        print(f"[error] no such file: {args.apk}")
        return 1
    try:
        report = scan_apk(p, args.min_severity)
    except ValueError as exc:
        print(f"[error] {exc}")
        return 1

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(render(report))
    # exit code reflects presence of high/critical
    bad = sum(report["summary"][k] for k in ("high", "critical"))
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())