# frida_scripts

Ready-to-use [Frida](https://frida.re) JavaScript hooks for Android dynamic
analysis. Load any of them with:

```bash
# on a USB device (frida-server running)
frida -U -f com.target.app -l <script>.js --no-pause

# or spawn from a local frida gadget
frida -U com.target.app -l scripts/cert-pinning.js
```

## Index

| Script | What it does |
| ------ | ------------ |
| `cert-pinning.js` | Neutralize `okhttp3.CertificatePinner` (classic leaked-bypass). |
| `universal-ssl.js` | Broader: replace the TLS TrustManager + Conscrypt re-trust + OkHttp pins. |
| `root-bypass.js` | Block `Runtime.exec("su")`/`ProcessBuilder` and flip root-check booleans. |
| `frida-bypass.js` | Preempt common `/proc/self/maps(libfrida)` + `Debug.isDebuggerConnected` detectors. |
| `anti-debug.js` | Spoof `Process.myPid`, swallow `Debug` sampling, log `dlopen`. |
| `network-log.js` | Log OkHttp/URL requests (URL + method) without MITM. |
| `sqlite-sieve.js` | Log every `SELECT`/`execSQL`/`rawQuery` the app runs. |
| `shared-prefs.js` | Mirror `SharedPreferences` writes to console. |
| `crypto-log.js` | Log `Cipher.init` mode/algorithm + `MessageDigest` updates. |
| `dump-keys.js` | Log `SecretKeySpec` bytes, `KeyStore` entries and Base64 outputs. |
| `log-dex.js` | Enumerate loaded `.dex`/classloaders for reverse-engineering. |
| `intent-dumper.js` | Log `startActivity`/deep links and explicit component targets. |
| `stack-tracer.js` | Dump the Java call stack on component launches. |

## Notes & ethics

- **Use only on devices/apps you own.** These scripts defeat protections;
  that's the entire point of a security lab, and only you get to press the button.
- `universal-ssl.js` and `root-bypass.js` are the "big hammer" ones — prefer
  the targeted scripts (`cert-pinning`) day to day.
- If a script logs nothing, the app may load its client separately at spawn —
  use `--no-pause` and attach at `frida-server` spawn.