# HKO Signal 8 Transparency Portal

**Live site:** https://hko-signal8.pages.dev/

The complete multi-page upgrade is prepared on `feat/complete-portal`. Until that PR merges, the production URL may still show the original chart page.

Explore 11 historical Hong Kong typhoons (2022–2025): event timelines, station heatmaps, side-by-side comparisons, bilingual explanations, data quality and downloadable evidence. This is a GCAP3226 student project, not an official HKO warning service or a certification of warning decisions.

## Build and host

Cloudflare Pages Git integration; production branch `main`, framework None, repository root, build command `sh scripts/build_site.sh`, output `dist`, no environment variables. No Worker, request-time backend, database, npm installation or Python processing is needed in CI. The build packages committed output in `website/`, assets, and the legacy chart route.

```sh
sh scripts/build_site.sh
python3 -m http.server 8000 --directory dist
```

Open http://localhost:8000/. The prototype remains at `/prototypes/charts.html` with its original data contract; it is historical output and does not use the newly recovered data. The new website uses `/data/summary.json` and `/data/events-v2/*.json`.

## Data regeneration and tests

Run locally, deliberately; Python 3 standard library only:

```sh
python3 scripts/build_portal_data.py
python3 scripts/test_portal_data.py
sh scripts/build_site.sh
```

- `data/event-metadata.json`: frozen warning metadata inherited from repository records at `417f94a`. Individual warning records have not all been independently reverified. The envelope includes higher signals where present, not only time at Signal 8.
- `typhoon_data/`: original course archive, retained unchanged.
- `recovered-data/`: exact official DATA.GOV.HK historical CSV versions packaged as per-event ZIP inputs, with retrieval URLs/times and SHA-256 manifests. Recovered Ma-on, Nalgae, Koinu, Saola and Ragasa replace those events' incomplete or misdated source folders for the new pipeline. The original folders are retained for provenance.
- `website/data/`: generated summary, event timelines, quality diagnostics, source hashes, recovery manifests and metadata copy.
- `website/downloads/`: generated timeline CSV and byte-preserving source CSV ZIP for every event.
- `website/`: seven public pages and bilingual shared UI; base visual styles adapted from `hko-signal8-validation` at `5c6dae859542b56f086fc55399ae1146d694a2e5`.

Observation timestamps come from CSV `Date time`, never the archive download/version filename. Only ten-minute embedded observation grid samples are used. Latest archived filename revision wins for each timestamp/station, including nulls. Conflicting revisions are counted and all original versions remain in downloadable ZIPs. Missing/malformed observations are not fabricated. Rebuilding from committed inputs needs no network access.

## Interpretation

The project checks for at least four reference stations at ≥63 km/h at exactly ten-minute sample spacing inside the inherited warning envelope. A sustained run requires three consecutive complete-network samples. A reappearance pattern requires two complete-network below-threshold samples between qualifying observations. Missing network readings or timestamp gaps break the sequence. Events with no complete-network overlap receive an insufficient-data state, separate from unverified observations.

Three ten-minute mean samples are a project convention, not HKO's definition of a 30-minute requirement. Onset is the first sample in a sustained run; confirmation is its third sample. Ragasa onset and confirmation lead times are therefore 720 and 740 minutes respectively. Nonverification is not proof that a warning was unnecessary. Observations do not reconstruct forecast judgment or establish casualty/safety causation.

Historical data is not automatically updated. Scheduled refresh is an optional future feature and is not enabled.

## Sources and attribution

- [HKO reference for issuing No.3 and No.8 signals](https://www.hko.gov.hk/en/informtc/tcsignal3_ref.htm), checked 23 October 2026.
- [HKO warnings database](https://www.hko.gov.hk/en/wxinfo/climat/warndb/warndb1.shtml).
- [DATA.GOV.HK historical archive API](https://data.gov.hk/en/help/api-spec); exact recovery URLs, version times and hashes are committed in `recovered-data/*-manifest.json`.
- [Original multi-page project](https://github.com/AndyZHENG0715/hko-signal8-validation).
- Team recorded in the original project report: Chen Man Ching, Hong Kam Yin, Hui Man Hei, Kung Tsz Lok, Zheng Zian. Course/date attribution follows the committed poster. Team contribution is not exclusive authorship.

Public footer: GCAP3226 course project, December 2025. Built by Zian Zheng

MIT license: see LICENSE. HKO data remains attributed to its source; the project does not claim ownership of observations.
