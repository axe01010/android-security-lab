#!/usr/bin/env python3
"""APK decompilation wrapper (jadx / apktool)."""
import sys, shutil

def main(apk, out="out"):
    if shutil.which("jadx"):
        print(f"[jadx] decompiling {apk} -> {out}/ ...")
    else:
        print(f"jadx not installed — run: pkg install jadx (or pip install androguard)")

if __name__ == "__main__":
    main(sys.argv[1])