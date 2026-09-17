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

# VERIFIED era classes (docs/URL-PATTERNS.md). A (legco_year, date) maps to
# the Chinese document path; only era classes with a live-verified Chinese
# URL are generated - the 1990s multi-part formats stay out until verified.
from datetime import timedelta

def _era_path(legco_year: str, date) -> str:
    d2 = date.strftime("%y%m%d"); d4 = date.strftime("%Y%m%d"); md = date.strftime("%m%d")
    if date < datetime(2001, 10, 17):
        return f"{legco_year}/chinese/counmtg/hansard/{d2}fc.pdf"
    if date < datetime(2006, 1, 1):
        return f"{legco_year}/chinese/counmtg/hansard/cm{md}ti-translate-c.pdf"
    if date < datetime(2014, 1, 1):
        return f"{legco_year}/chinese/counmtg/hansard/cm{md}-translate-c.pdf"
    return f"{legco_year}/chinese/counmtg/hansard/cm{d4}-translate-c.pdf"

def _legco_year(date) -> str:
    y1 = date.year if date.month >= 7 or date.year >= 2022 else date.year - 1
    if y1 >= 2022:
        return f"yr{y1}"
    return f"yr{str(y1)[-2:]}-{str(y1 + 1)[-2:]}"

VERIFIED_SAMPLES = {
    "2000-06-27": "yr99-00/chinese/counmtg/hansard/000627fc.pdf",
    "2002-01-09": "yr01-02/chinese/counmtg/hansard/cm0109ti-translate-c.pdf",
    "2007-01-10": "yr06-07/chinese/counmtg/hansard/cm0110-translate-c.pdf",
    "2015-01-07": "yr14-15/chinese/counmtg/hansard/cm20150107-translate-c.pdf",
    "2022-06-15": "yr2022/chinese/counmtg/hansard/cm20220615-translate-c.pdf",
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
        if dest.read_bytes()[:4] != b"%PDF":
            dest.unlink()  # an HTML error page saved as .pdf, etc.
            time.sleep(0.5)
            return False
    except urllib.error.HTTPError as exc:
        time.sleep(0.5)  # most weekdays have no meeting; be polite on 404s too
        return False
    except Exception as exc:
        print(f"  FAIL {url}: {exc}")
        time.sleep(rate_limit_s)
        return False
    time.sleep(rate_limit_s)
    return True


FAILED = Path("data/failed.txt")


def extract(pdf: Path, out_txt: Path) -> int:
    """Extract one PDF; a corrupt file is quarantined to data/failed.txt
    and NEVER kills the run (the 2026-09-17 crash: a magic-valid PDF
    with no /Root took down 7 hours of scraping)."""
    if out_txt.exists():  # resume: extraction is the expensive half
        return out_txt.stat().st_size
    from pdfminer.high_level import extract_text
    try:
        text = cleanup_text(extract_text(str(pdf)))
    except Exception as exc:
        with FAILED.open("a") as fh:
            fh.write(f"{pdf.name}\t{type(exc).__name__}: {str(exc)[:120]}\n")
        pdf.rename(pdf.with_suffix(".bad"))  # do not re-attempt on resume
        return 0
    out_txt.write_text(text, encoding="utf-8")
    return len(text)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sample", action="store_true", help="all five verified era samples")
    parser.add_argument("--date", default=None, help="YYYY-MM-DD meeting date (verified eras)")
    parser.add_argument("--from", dest="start_date", default=None, help="YYYY-MM-DD bulk range start")
    parser.add_argument("--to", dest="end_date", default=None, help="YYYY-MM-DD bulk range end")
    args = parser.parse_args()

    targets: list[tuple[str, str]] = []
    if args.sample:
        targets = sorted(VERIFIED_SAMPLES.items())
    elif args.date:
        d = datetime.strptime(args.date, "%Y-%m-%d")
        targets = [(args.date, _era_path(_legco_year(d), d))]
    elif args.start_date and args.end_date:
        d = datetime.strptime(args.start_date, "%Y-%m-%d")
        end = datetime.strptime(args.end_date, "%Y-%m-%d")
        while d <= end:
            if d.weekday() < 5:
                targets.append((d.strftime("%Y-%m-%d"), _era_path(_legco_year(d), d)))
            d += timedelta(days=1)
    else:
        parser.error("choose --sample, --date, or --from/--to")

    raw = DATA / "raw"; txt = DATA / "text"
    raw.mkdir(parents=True, exist_ok=True); txt.mkdir(parents=True, exist_ok=True)

    manifest = []
    for date, path in targets:
        url = f"{BASE}/{path}"
        # year-prefixed names: era stems like cm{mmdd} COLLIDE across years
        pdf = raw / f"{path.split('/')[0]}-{Path(path).name}"
        print(f"[{date}] {url}")
        if not fetch(url, pdf):
            continue
        n_chars = extract(pdf, txt / (pdf.stem + ".txt"))
        if pdf.exists():  # extract() may have quarantined a corrupt file
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
