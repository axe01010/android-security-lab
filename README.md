# 🔒 Android Security Lab

<p align="center">
  <img src="https://img.shields.io/badge/Android-Security-red?style=for-the-badge&logo=hackthebox&logoColor=white" />
  <img src="https://img.shields.io/badge/Pentesting-000000?style=for-the-badge" />
</p>

> **Android security research toolkit.** APK analysis, pentesting, and threat detection.

## ✨ Features

- 📦 APK decompilation and analysis
- 🔍 Static and dynamic analysis
- 🛡️ Vulnerability scanning
- 📊 Malware detection
- 🔐 Certificate pinning bypass
- 📱 Frida scripts collection

## 🚀 Quick Start

```bash
git clone https://github.com/axe01010/android-security-lab.git
cd android-security-lab

# Analyze an APK
python analyze.py /path/to/app.apk

# Start dynamic analysis
python dynamic.py --package com.example.app

# Run vulnerability scan
python scan.py /path/to/app.apk
```

## 🛠️ Tools Included

| Tool | Purpose |
|------|---------|
| `analyze.py` | Static APK analysis |
| `dynamic.py` | Dynamic instrumentation |
| `scan.py` | Vulnerability scanning |
| `decompile.py` | APK decompilation |
| `frida_scripts/` | Frida hooking scripts |

## 📁 Structure

```
android-security-lab/
├── analyze.py            # Static analysis
├── dynamic.py            # Dynamic analysis
├── scan.py               # Vulnerability scan
├── decompile.py          # Decompiler
├── frida_scripts/        # Frida hooks
├── signatures/           # Malware signatures
├── samples/              # Test APKs
├── docs/
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). New tools and signatures welcome.

## 📜 License

MIT
