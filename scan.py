#!/usr/bin/env python3
"""Vulnerability scanning (signature-matching stub)."""
import sys

RULES = [
    ("cleartext traffic", "usesCleartextTraffic"),
    ("debuggable", "android:debuggable"),
]

def main(apk):
    print(f"scanning {apk} for {len(RULES)} signature patterns ...")
    print("(stub) no findings")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "app.apk")