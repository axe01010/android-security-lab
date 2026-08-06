# Frida mastery — android-security-lab

This repo ships 13 Frida hooks. Here's how to pick and use them, plus how
traffic and pitfalls differ from the CLI.

## Prerequirements

- A rooted device (or a debuggable app) with `frida-server` running.
  - Build matching arch: `adb shell getprop ro.product.cpu.abi`.
  - `frida-server` (same ABI) + `adb forward tcp:27042 tcp:27042` if needed.
- Host `pip install frida-tools` to get the `frida` CLI.

## Loading, spawn vs attach

```bash
# Attach to a running app (fast, but misses early logic)
frida -U com.example.app -l scripts/network-log.js

# Spawn-and-hook before anything runs (necessary for pinning/frida-detectors)
frida -U -f com.example.app -l scripts/universal-ssl.js --no-pause
```

Always prefer `--no-pause` spawn for the papers.

## The scripts, in order of attack

### Phase 1 — reach into TLS
1. `cert-pinning.js` — neutralize OkHttp `CertificatePinner` only.
2. `universal-ssl.js` — the big hammer: replace the TLS TrustManager +
   Conscrypt re-trust + OkHttp pins in one shot.

### Phase 2 — dodge the app's defensive gates
3. `root-bypass.js` — block `Runtime.exec("su")`/`ProcessBuilder`, flip
   known root-check booleans.
4. `frida-bypass.js` — preempt `/proc/self/maps`-based tools + 
   `Debug.isDebuggerConnected`.
5. `anti-debug.js` — spoof `myPid`, swallow `Debug` sampling, log `dlopen`.

### Phase 3 — watch it move
6. `network-log.js` — URL + method for OkHttp/URL connections, no MITM.
7. `sqlite-sieve.js` — SQLite `SELECT`/`execSQL`/`rawQuery`.
8. `shared-prefs.js` — SharedPreferences writes.
9. `crypto-log.js` — `Cipher.init` + `MessageDigest` outcomes.
10. `intent-dumper.js` / `stack-tracer.js` — what launches & why.

### Phase 4 — the secrets
11. `dump-keys.js` — SecretKeySpec/KeyStore entry/Base64 outputs.
12. `log-dex.js` — enumerate loaded `.dex` for reversing the compiled app.

## Practical snippet: dump a SharedPreferences secret

```bash
frida -U -f com.example.app -l scripts/shared-prefs.js --no-pause | tee prefs.log
# trigger the app to write (login/refresh); watch console for [prefs]
```

## Keep-mistakes list

- Don't attach on an app that reads its DEX at startup before `--no-pause`
  —  hooks land too late. spawn when tests.
- `universal-ssl.js` is a sledgehammer; on a production build prefer
  `cert-pinning.js` (smaller footprint).
- Frida-detectors can run before JS even attaches its first hook; that's what
  `frida-bypass.js` is *for*, but expect to iterate.

## Ethics reminder

Use these only against apps you own or have permission to test. They strip
protections on purpose — that's the lab's entire point, and the target must be
yours.