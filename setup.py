#!/usr/bin/env python3
"""Packaging for android-security-lab.

Install:  pip install -e .
Provides console scripts: apk-analyze, apk-scan, apk-decompile.
"""
from setuptools import setup

setup(
    name="android-security-lab",
    version="0.1.0",
    description="Static + dynamic tooling for Android APK analysis.",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="axe01010",
    license="MIT",
    python_requires=">=3.9",
    py_modules=["analyze", "scan", "decompile"],
    install_requires=["androguard>=3.3.3"],
    entry_points={
        "console_scripts": [
            "apk-analyze=analyze:main",
            "apk-scan=scan:main",
            "apk-decompile=decompile:main",
        ],
    },
    include_package_data=True,
)