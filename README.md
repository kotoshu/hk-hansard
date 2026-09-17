# hk-hansard

The **Chinese Official Record of Proceedings** (立法會會議過程正式紀錄) of the
Hong Kong Legislative Council — the large **formal-register zh-Hant-HK**
corpus source for the kotoshu spellchecker's Hong Kong variant model
(`zh-Hant-HK`; see `models-fasttext-onnx/docs/cjk-typo-corpus-research.md`).

## Why this repo exists

Kotoshu is splitting Chinese into three variant models (zh-Hans-CN,
zh-Hant-TW, zh-Hant-HK) because the regions differ by vocabulary, not just
script (HK 軟件 vs TW 軟體). No open formal-HK corpus exists today
(verified 2026-09-16 across HuggingFace and arXiv), but the LegCo Chinese
Hansard is large, authoritative, and scrapable — the English twin is already
mirrored at `Swithord/hong-kong-legco-transcript` (813k speeches, 1985-2025);
this repo is the Chinese counterpart.

## Status: THE CORPUS IS IN (2026-09-17)

**1,343 meetings scraped and extracted — June 1999 through July 2026,
~503 million characters of formal Traditional Chinese** (the LegCo
Official Record), distributed in this repo as
`data/text/{legco-year}-{stem}.txt` with the full provenance manifest
(`data/manifest.json`: per-meeting date, source URL, PDF sha256, byte
and character counts). Known gaps: 3 meetings scraped but not yet
manifest-reconciled; 1 corrupt PDF quarantined (`data/failed.txt`).

- URL archaeology for every verified era: `docs/URL-PATTERNS.md`.
- Scraper (rate-limited, resumable, checksummed): `scripts/`.
- **Content license: DISTRIBUTION APPROVED by owner 2026-09-17**
  (`LICENSE-VERIFICATION.md`), with attribution to the Hong Kong
  Legislative Council Official Record on every derived use.

## Layout

- `scripts/scrape_hansard_zh.py` — URL generation (verified era first),
  rate-limited download, PDF→text extraction with the de-spacing cleanup,
  checksum + manifest.
- `docs/URL-PATTERNS.md` — per-era URL discovery log.
- `LICENSE-VERIFICATION.md` — the license determination state.

## Credit

The English URL archaeology is
[Swithord/hong-kong-legco-transcript](https://github.com/Swithord/hong-kong-legco-transcript);
this repo adapts it for the Chinese records. Source content: the Hong Kong
Legislative Council Official Record.
