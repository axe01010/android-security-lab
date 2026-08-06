#!/usr/bin/env python3
"""Build a tiny but realistic-ish sample APK for the static tools.

Deterministic(fixture) — the dex bytes contain strings that the `scan` rules
will flag (camera, cleartext, debuggable, an embedded password). Useful for
CI/demo without a real APK.

Usage: python examples/make_sample_apk.py [--out samples/sample.apk]
"""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

# A minimum dex-like blob + manifest hint — enough for stdlib string scanning.
DEX_BLOB = (
    "dex\n035\\0\\0\\0"
    "android.permission.INTERNET "
    "android.permission.CAMERA "
    "android.permission.READ_SMS "
    "android:exported=\"true\" "
    "usesCleartextTraffic=\"true\" "
    "android:debuggable=\"true\" "
    "Runtime.getRuntime().exec(\"sh\") "
    "password=\"hunter2\" "
    "SecretKeySpec(AES)"
).encode("utf-8")


def build(out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w") as z:
        z.writestr("AndroidManifest.xml",
                   b'<manifest package="com.example.lab"/>'
                   b'<!-- synthetic sample for android-security-lab -->')
        z.writestr("classes.dex", DEX_BLOB)
        z.writestr("resources.arsc", b"\x02\x00res")
        z.writestr("META-INF/CERT.RSA", b"\x30\x82\x01")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", default="samples/sample.apk")
    args = ap.parse_args(argv)
    path = build(Path(args.out))
    print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())