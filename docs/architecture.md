# Architecture — android-security-lab

How the static tools are built and why they stay tiny.

## Layering

```
┌──────────── 3 static CLIs ───────────────────────────────┐
│  analyze.py     scan.py       decompile.py               │
│  (inventory)   (heuristics)    (unpack/decompile)        │
└──────┬─────────────┬──────────────┬───────────────────────┘
       │             │              │
       ├─ stdlib zip ┤              └─ jadx/apktool (opt) / zip+strings
       └─ androguard (optional, deep manifest)
```

Every module is a **single file with a `main()`** and no shared runtime —
they only share the *convention* that each takes an APK path. This keeps the
whole lab installable in one `pip install -r requirements.txt`. Note the
deliberate isolation: `analyze` may pull androguard, `scan`/`decompile`
never do.

## `analyze.py` — inventory

- `_archive_info` / `_find_cert` / `_sha256` are pure stdlib (zipfile for the
  APK archive; hashlib for integrity).
- `_androguard_analysis` is a soft dependency: it's imported *inside* the
  function, so a missing androguard results in a clean, explanatory `note`
  field instead of an importError at startup.
- `analyze_apk()` merges a safe stdlib report with the optional deep pass and
  returns one structured dict — `render_text` (tables/etc.) or `--json`.

## `scan.py` — the `RULES` table

The whole scanner is a list of tuples:

```python
RULES = [
    (regex, severity, label, reason_advice),
    ...
]
```

Scanning an APK is: read the dex into one blob → `re.search` every pattern →
sort by severity → summarize per-severity counts. Adding a check is *one tuple*
and nothing else — that's the intended extension point. Exit code is 1 when
any `high`/`critical` lands, so it drops into CI.

## `decompile.py` — tool selection, then graceful

- `which_decompiler()` returns the first of `jadx`/`apktool`/`enjar` on PATH;
  you can force one with `--tool`.
- With a tool: run it as a subprocess (timeout 60s, capture stderr).
- Without: `_unbundle()` copies every zip entry to the output dir and appends
  all dex-as-string-blob entries to `strings.txt`. A zip-slip guard rejects
  entries that resolve outside the target.
- Output default is `<apk-stem>.src`.

## Design principles

1. **Stdlib-first.** The tools work with zero deps; deep features are gated
   behind optional imports (androguard) or optional binaries (jadx/apktool).
2. **One dict in, one dict out.** All three return JSON-able dicts, so
   `--json` and programmatic embedding are free.
3. **Findings are feedback, not verdicts.** `scan` labels *patterns* a human
   should look at — never a certainty.
4. **Safe by default.** `decompile`'s unbundle refuses bad paths; samples are
   synthetic, never a collected real APK.

## Extension map

- New scan check → one line in `scan.RULES`.
- New manifest surface → an entry in `analyze`'s (androguard) dict.
- New decompiler → add to `TOOLS` + a template string.
- New Frida script → `frida_scripts/*.js` (see `frida_scripts/README.md`).