#!/usr/bin/env python3
"""Scrape the CHINESE Official Record of Proceedings of the Hong Kong
Legislative Council - the zh-Hant-HK formal corpus source for the kotoshu
variant models (docs/cjk-typo-corpus-research.md in models-fasttext-onnx).

The English twin (github.com/Swithord/hong-kong-legco-transcript) did the
URL archaeology for the English records; the Chinese records share the stem
with part suffix 'c' (VERIFIED for yr98-99/yr99-00; see docs/URL-PATTERNS.md).

v0 scope: the verified era, extraction cleanup, manifest. The bulk scrape
runs only after LICENSE-VERIFICATION.md clears (owner call).

Usage:
  python scripts/scrape_hansard_zh.py --sample          # the verified meeting
  python scripts/scrape_hansard_zh.py --era yr99-00     # every verified date
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data"
BASE = "https://www.legco.gov.hk"

# Verified era meetings (Swithord's English table, converted to the Chinese
# part suffix). Extend per docs/URL-PATTERNS.md as eras verify.
VERIFIED: dict[str, list[tuple[str, str]]] = {
    "yr99-00": [
        ("2000-06-27", "yr99-00/chinese/counmtg/hansard/000627fc.pdf"),
        ("2000-05-24", "yr99-00/chinese/counmtg/hansard/000524fc.pdf"),
    ],
    "yr98-99": [
        ("1999-12-02", "yr98-99/chinese/counmtg/hansard/991202fc.pdf"),
    ],
}

CJK = "㐀-鿿"


def cleanup_text(raw: str) -> str:
    """The two verified PDF quirks: single spaces between CJK glyphs, and
    quadrupled runs from overlapping text layers."""
    import re
    text = re.sub(rf"([{CJK}]) ([{CJK}])", r"\1\2", raw)
    for _ in range(3):  # a spaced run needs repeated passes
        text = re.sub(rf"([{CJK}]) ([{CJK}])", r"\1\2", text)
    text = re.sub(r"(\d)\1{3,}", r"\1", text)          # 2000 -> quadrupled digits
    text = re.sub(r"([^\n\{CJK}])\1{3,}", r"\1", text)  # quadrupled phrase layers
    return text


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def fetch(url: str, dest: Path, rate_limit_s: float = 2.0) -> bool:
    if dest.exists():
        return True
    import ssl
    try:
        import certifi
        cafile = certifi.where()
    except ImportError:
        cafile = None
    ctx = ssl.create_default_context(cafile=cafile)
    # legco.gov.hk serves ONLY the leaf; the Hongkong Post intermediate is
    # fetched from the leaf's AIA and shipped beside this script.
    intermediate = Path(__file__).resolve().parent.parent / "docs" / "hongkong-post-e-cert-ssl-ca-3-17.pem"
    if intermediate.exists():
        ctx.load_verify_locations(cafile=str(intermediate))
    req = urllib.request.Request(url, headers={"User-Agent": "kotoshu-hk-hansard/0.1"})
    try:
        with urllib.request.urlopen(req, timeout=120, context=ctx) as resp, dest.open("wb") as fh:
            while chunk := resp.read(1 << 20):
                fh.write(chunk)
    except Exception as exc:
        print(f"  FAIL {url}: {exc}")
        return False
    time.sleep(rate_limit_s)
    return True


def extract(pdf: Path, out_txt: Path) -> int:
    from pdfminer.high_level import extract_text
    text = cleanup_text(extract_text(str(pdf)))
    out_txt.write_text(text, encoding="utf-8")
    return len(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sample", action="store_true")
    parser.add_argument("--era", choices=sorted(VERIFIED), default=None)
    args = parser.parse_args()

    targets: list[tuple[str, str]] = []
    if args.sample:
        targets = [VERIFIED["yr99-00"][0]]
    elif args.era:
        targets = VERIFIED[args.era]
    else:
        parser.error("choose --sample or --era {%(choices)s}" % {"choices": ",".join(VERIFIED)})

    raw = DATA / "raw"; txt = DATA / "text"
    raw.mkdir(parents=True, exist_ok=True); txt.mkdir(parents=True, exist_ok=True)

    manifest = []
    for date, path in targets:
        url = f"{BASE}/{path}"
        pdf = raw / Path(path).name
        print(f"[{date}] {url}")
        if not fetch(url, pdf):
            continue
        n_chars = extract(pdf, txt / (pdf.stem + ".txt"))
        manifest.append({
            "date": date, "url": url, "sha256": sha256_of(pdf),
            "bytes": pdf.stat().st_size, "text_chars": n_chars,
        })
    (DATA / "manifest.json").write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "records": manifest,
    }, ensure_ascii=False, indent=1) + "\n")
    for m in manifest:
        print(f"  ok {m['date']}: {m['bytes']:,}B pdf, {m['text_chars']:,} chars text")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
