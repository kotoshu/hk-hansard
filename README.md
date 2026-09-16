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

## Status

- URL pattern for the Chinese records VERIFIED for the yr98-99/yr99-00 era
  (same stem as the English files, `/english/` → `/chinese/`, final part
  letter → `c`). Per-era table: `docs/URL-PATTERNS.md`.
- Sample verified: `000627fc.pdf` (2000-06-27 meeting) — formal Traditional
  Chinese, HK parliamentary register, ~1.9 MB; extraction quirks documented
  in the scraper.
- **Content license: PENDING** (`LICENSE-VERIFICATION.md`). This repo hosts
  the scraper, the URL archaeology, and packaging tooling. No bulk Hansard
  text is committed until the license determination clears (owner call).

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
