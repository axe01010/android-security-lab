<p align="center">
  <img src="https://github.com/axe01010/android-security-lab/raw/main/assets/banner.png" alt="android-security-lab" width="100%" />
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/axe01010/android-security-lab?style=for-the-badge&color=DC2626&logo=github" />
  <img src="https://img.shields.io/github/forks/axe01010/android-security-lab?style=for-the-badge&color=111827&logo=github" />
  <img src="https://img.shields.io/github/license/axe01010/android-security-lab?style=for-the-badge&color=DC2626" />
  <img src="https://img.shields.io/github/last-commit/axe01010/android-security-lab?style=for-the-badge&color=111827" />
</p>

# 🛡️ android-security-lab

Static + dynamic tooling for Android APK analysis.

`analyze.py · scan.py · decompile.py · frida_scripts/`

[Quickstart](#quickstart) · [Tools](#tools) · [Frida scripts](frida_scripts/README.md) ·
[Architecture](docs/architecture.md) · [License](#license)

> ⚠️ **Ethics first.** Use only against apps you own, or that you have explicit
> permission to assess. These tools disable protections on purpose — the
> four-square is yours alone to push.

---

## What it is

A small, dependency-light lab for **your own** APK analysis:

- **Static** — inventory an APK (`analyze`), scan its security surface
  (`scan`), and unpack/decompile it (`decompile`).
- **Dynamic** — 13 ready-to-load Frida scripts (SSL pinning bypass, root /
  Frida-detection evasion, network / SQLite / SharedPreferences / key logging,
  intent and stack tracing).

Every piece is a single-file, stdlib-first module (only `analyze` *optionally*
uses androguard for a deep manifest pass) — so the lab runs on Termux and in
CI with zero heavyweight setup.

## Quickstart

```bash
# 1) python deps
pip install -r requirements.txt       # adds optional androguard

# 2) static pass
python3 analyze.py   app.apk           # package · sdk · permissions · cert · SHA-256
python3 scan.py      app.apk           # heuristic findings w/ severity
python3 decompile.py app.apk           # jadx/apktool, else stdlib unpack

# 3) dynamic pass (frida-server on the device)
frida -U -f com.example.app -l frida_scripts/universal-ssl.js --no-pause
```

`scan.py` exits non-zero on any `high`/`critical` finding — easy to wire into a
CI gate.

## Tools

| Command | Engine | What you get |
| ------- | ------ | ------------ |
| `analyze.py <apk>` | androguard (optional)/stdlib | package, sdk, permissions, components, cert, archive inventory, SHA-256; `--json` |
| `scan.py <apk>` | stdlib heuristics | severity-tagged findings + advice; `--json`, `--min-severity` |
| `decompile.py <apk>` | jadx / apktool → stdlib | `.src/` unpack + `strings.txt` (dex) on fallback |
| `frida_scripts/*.js` | Frida | per-file dynamic hooks (index in the folder README) |

## Try it offline

```bash
python3 examples/make_sample_apk.py        # → samples/sample.apk
python3 examples/run_full_pass.py samples/sample.apk
```

No device or real APK needed for the static tools.

## Use cases

- **Pre-release self-review** — a fast manifest/scan/CI checkpoint on your own
  build.
- **CI gate** — `scan.py` fails on high/critical.
- **Reversing something you own** — automated static pass + Frida hooks to
  understand components and traffic.
- **Learning** — small, readable hooks for OkHttp, SQLite, SharedPreferences,
  crypto.

## FAQ

| Q | A |
| - | - |
| Is Android SDK required? | No — everything is stdlib-based by default. |
| Is `scan.py` a vuln scanner? | It flags *patterns* worth a human eye (weak crypto, cleartext, exported, exec). It is a triage helper, not a CVE finder. |
| Does `decompile` need jadx? | It uses jadx/apktool if installed; otherwise falls back to zip unpacking + dex strings. |
| Works on Termux? | Yes (stdlib-only). `analyze` goes deepest if you `pip install androguard`. |

## Contributing

Add rules to the `RULES` table in `scan.py`, manifest surface to `analyze.py`,
and hooks as `frida_scripts/*.js` (list entries in `frida_scripts/README.md`).
Keep modules stdlib-first unless a real dependency earns its keep. See
[CONTRIBUTING](docs/usage.md#contributing).

## License

MIT — see [LICENSE](LICENSE).

---
<p align="center">
  <b>Part of the <a href="https://github.com/axe01010/axe01010">Free On-Device AI DevKit</a> stack</b><br>
</p>
<p align="center">
  <a href="https://github.com/axe01010/android-ai-agent">android-ai-agent</a> ·
  <a href="https://github.com/axe01010/on-device-llm-mobile">on-device-llm-mobile</a> ·
  <a href="https://github.com/axe01010/mcp-server-hub">mcp-server-hub</a> ·
  <a href="https://github.com/axe01010/termux-toolkit">termux-toolkit</a> ·
  <a href="https://github.com/axe01010/android-security-lab">android-security-lab</a>
</p>
<p align="center"><sub>README built for the <b>Free On-Device AI DevKit</b> — private AI that runs entirely on a phone.</sub></p>
