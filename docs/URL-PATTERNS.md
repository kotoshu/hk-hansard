# Hansard Chinese URL patterns — discovery log

Base: `https://www.legco.gov.hk/` + `{legco_year}/chinese/counmtg/hansard/...`
(1996-97 lives under `lc_sitg/hansard/` instead of `counmtg/hansard/`).
From yr2022 the leg. year format is `yr2022` (four digits), before that
`yr{YY}-{YY}`.

| Era | English stem (Swithord) | Chinese stem | Status |
|---|---|---|---|
| 1999-06-16 .. 2001-10-16 | `{yymmdd}f{a,b}.pdf` / `{yymmdd}fe.pdf` | `{yymmdd}fc.pdf` | **VERIFIED** (2000-06-27, 1.9 MB) |
| 2001-10-17 .. 2005 | `cm{mmdd}ti-translate-e.pdf` | `cm{mmdd}ti-translate-c.pdf` | **VERIFIED** (2002-01-09, 1.5 MB) |
| 2006 .. 2013 | `cm{mmdd}-translate-e.pdf` | `cm{mmdd}-translate-c.pdf` | **VERIFIED** (2007-01-10, 1.3 MB) |
| 2014 .. 2021 | `cm{yyyymmdd}-translate-e.pdf` | `cm{yyyymmdd}-translate-c.pdf` | **VERIFIED** (2015-01-07, 2.7 MB) |
| 2022 .. now | `cm{yyyymmdd}-translate-e.pdf` | `cm{yyyymmdd}-translate-c.pdf` | **VERIFIED** (2022-06-15, 11.5 MB) |
| < 1999-06-16 | `{yymmdd}fe.htm` + date-specific `f{a-d}.htm` parts | `{yymmdd}fc.htm` variants NONE on 1997-07-16 | UNVERIFIED — multi-part special cases; see the English special-case table |
| 1996-97 (.doc) + provisional 1997 | `{yymmdd}fe.doc` / special cases | unknown | UNVERIFIED |
| < 1995 | `h{yymmdd}.pdf`, `han{ddmm}.htm` | unknown | UNVERIFIED |

Discovery method: the Chinese record shares the English stem with the
final part letter `c` (fe→fc, translate-e→translate-c). All five modern
era classes verified by direct probe on real meeting dates. Remaining
work is the 1990s multi-part formats, which need the same per-date
special-case table the English scraper carries.

Extraction quirks (pdfminer, verified samples): CJK glyphs separated by
single spaces (handled by the scraper cleanup); quadrupled runs from
overlapping text layers — single chars handled, repeated multi-char
patterns (e.g. `27272727`) partially handled; verify per era.
