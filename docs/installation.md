# Installation & usage — android-security-lab

Static pass, dynamic pass, CI, and a sample workflow.

## 1. Install

```bash
git clone https://github.com/axe01010/android-security-lab.git
cd android-security-lab

# stdlib tools work with NOTHING installed. For deeper analyze:
pip install -r requirements.txt       # androguard (optional)

# optional: full decompile (jadx via pkg/brew/apt)
#   Termux: pkg install jadx
#   apt:    apt install jadx ; or  pipx install jadx
```

## 2. Static analysis

```bash
# inventory — package/permissions/sdk/cert/SHA-256 (stdlib mode shown below)
python analyze.py app.apk
python analyze.py app.apk --json          # machine-readable

# security scan (heuristics + advice)
python scan.py app.apk
python scan.py app.apk --min-severity medium --json

# unpack / decompile
python decompile.py app.apk               # jadx → apktool → stdlib
python decompile.py app.apk -o /tmp/out
```

For a demo with no real APK:

```bash
python examples/make_sample_apk.py       # builds samples/sample.apk
python examples/run_full_pass.py --sample
```

## 3. CI gate (`scan`)

`scan.py` returns exit 1 if it sees `high` or `critical`. So:

```yaml
# .github/workflows/smoke-scan.yml (sketch)
- run: pip install androguard
- run: python3 -m py_compile scan.py analyze.py decompile.py
- run: for apk in "$(find samples -name '*.apk')"; do
        python3 scan.py "$apk" --min-severity medium || exit 1;
      done
```

## 4. Dynamic analysis (Frida)

```bash
# build frida-server for the device arch, push & run on the target
adb push frida-server /data/local/tmp/  && adb shell "/data/local/tmp/frida-server &"

# bypass SSL pinning for your own app
frida -U -f com.example.app -l frida_scripts/universal-ssl.js --no-pause

# log SQL it runs
frida -U com.example.app -l frida_scripts/sqlite-sieve.js
```

Every hook is indexed and described in [frida_scripts/README.md](frida_scripts/README.md);
see also [docs/frida-guide](docs/frida-guide.md).

## 5. Full pass workflow

```bash
./examples/run_full_pass.py <apk>         # analyze → scan → decompile
# exit code = 0 if no high/critical, else 1 (a CI gate)
```

## Troubleshooting

| Symptom | Fix |
| ------- | --- |
| `analyze` prints "stdlib (zip) mode" | fine — `pip install androguard` for the deep manifest. |
| `scan` finds nothing | it's heuristic; run `--min-severity info --json` to see all matches. |
| `decompile` says "stdlib unpack" | get `jadx` on PATH for real code output. |
| frida hook does nothing | use `--no-pause` at spawn; check `frida-server` is running & same arch. |

## Contributing

Follow the extension map in [docs/architecture](docs/architecture.md);
keep a real rename test with `examples/`. Open a PR — thanks!