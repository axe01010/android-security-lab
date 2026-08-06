#!/usr/bin/env python3
"""Static APK analysis."""
import sys, zipfile

def main(apk):
    z = zipfile.ZipFile(apk)
    names = z.namelist()
    print(f"entries: {len(names)}")
    print("classes.dex:", "classes.dex" in names)
    print("AndroidManifest.xml:", "AndroidManifest.xml" in names)
    print("resources.arsc:", "resources.arsc" in names)

if __name__ == "__main__":
    main(sys.argv[1])