# Hansard Chinese URL patterns — discovery log

Base: `https://www.legco.gov.hk/`

| Era (leg. year) | English pattern (Swithord) | Chinese pattern | Status |
|---|---|---|---|
| yr98-99, yr99-00 | `yr{YY}-{YY}/english/counmtg/hansard/{date}f{a,b}.pdf` | `yr{YY}-{YY}/chinese/counmtg/hansard/{date}fc.pdf` | **VERIFIED** (2000-06-27: HTTP 200, 1.9 MB, Traditional verified) |
| 1996-97 (provisional) | `lc_sitg/hansard/{date}f{parts}.doc` | presumed same stem under `/chinese/` | UNVERIFIED |
| yr00-01 .. yr21-22 | per-era stems (`cm{mmdd}`, dated stems) | presumed `{...}fc` variants | UNVERIFIED |
| yr2022+ | different year format (`yr2022`) | UNVERIFIED | UNVERIFIED |

Discovery method: the English files and the Chinese files share the stem;
the Chinese record carries part suffix `c`. Verified by direct probe:

```
https://www.legco.gov.hk/yr99-00/english/counmtg/hansard/000627fa.pdf  -> 200 (English, 999 KB)
https://www.legco.gov.hk/yr99-00/chinese/counmtg/hansard/000627fc.pdf  -> 200 (Chinese, 1.9 MB)
```

Extraction quirks (pdfminer on the verified sample): CJK glyphs separated
by single spaces ("立 法 會"), quadrupled digit/phrase runs from overlapping
text layers ("2000 年年年年"). The scraper's cleanup handles both; verify
per era before trusting numbers.
