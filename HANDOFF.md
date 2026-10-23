# HKO Signal 8 deployment handoff

Checked: 2026-10-23, Asia/Taipei.

## Current status

Phase 1 public deployment acceptance passed. Live URL: https://hko-signal8.pages.dev/

Andy created Cloudflare Pages after deployment PR #1 was merged into `main` (`19d6a56`). A failed initial build used pre-merge commit `306dfcc`; the public deployment now serves the prepared page and assets. GitHub Website is set to the verified live URL. A documentation-only follow-up updates README and this handoff; no runtime code or dataset changes.

TCM phase 2a is eligible to start after this phase 1 closeout; no TCM work has been started by this coordinator.

## Workspace and architecture

Canonical workspace: `/home/andy/projects/hko-signal8` in Ubuntu WSL; Git runs inside WSL. Repository: `AndyZHENG0715/HKOSignal8TransparencyPortal`. No competing checkout created.

Static HTML/JavaScript with Chart.js via jsDelivr, no request-time backend, functions, DB, or API server. Source page: `prototypes/charts.html`. Offline Python pipeline `scripts/build_event_data.py` generates committed `data/index.json` and `data/events/*.json` from raw CSV/Markdown. Data remains a historical 2022–2025 snapshot; there is no automatic refresh.

Pages settings: project `hko-signal8`, production `main`, preset None, repository root, build `sh scripts/build_site.sh`, output `dist`, no environment variables or dependency installation. Build copies only the page, committed JSON, favicon and share PNG; it excludes raw CSVs and reports. No Python pipeline in CI, Wrangler, Worker or paid setup. Optional scheduled data updates remain unimplemented.

## Accepted changes

Minimal public packaging script and Linux line endings; homepage entry; project explanation and historical-data limitation; title/description/OG PNG/favicon; project-specific observational-check labels; requested footer and repo link; mobile grid/select fixes and dedicated chart containers; bundled date adapter pinned to 3.0.0. Dataset and algorithm preserved.

## Verification evidence

- Local WSL packaging and diff whitespace checks passed before PR #1.
- Live anonymous checks from WSL curl: 16 HTTP 200 routes covering `/`, `/prototypes/charts.html`, favicon, share PNG, index and all 11 event JSONs. All 12 live JSON files byte-identical to repository source.
- Live browser: five populated chart canvases, 11 event options, Ragasa switching works; 390×844 viewport has scroll width 375px with no horizontal overflow. No warning/error console logs observed.
- Local ignored evidence: `.tmp/live-http-checks.json` and `.tmp/live-mobile-390.png`. Screenshot inspected; chart canvas sizes 310×320 on mobile. PNG share asset matches packaged 1200×630 image.
- Windows/WSL Python urllib received HTTP 403, while WSL curl and normal browser succeeded. This is a client-specific observation, not a login requirement; successful anonymous checks used curl without credentials/cookies.
- GitHub Website update returned the expected live URL.

## Source provenance and attribution

Architecture: README, scripts/README, scripts/build_event_data.py, prototypes/charts.html and committed data. `prototypes/poster.html` identifies GCAP3226, December 2025 and Zheng Zian among authors; the group report link file lists the team including Zheng Zian. Git authors include ZHENG Zian. These support contribution, not exclusive authorship. Footer follows Andy's requested wording; source team attribution is preserved.

Cloudflare static HTML guidance checked on 2026-10-23: https://developers.cloudflare.com/pages/framework-guides/deploy-anything/

## GitHub artifacts and remaining actions

PR #1: https://github.com/AndyZHENG0715/HKOSignal8TransparencyPortal/pull/1 — merged by Andy. Implementation `464a7e1`, handoff `c333b51`, merge `19d6a56`. PR was assigned to AndyZHENG0715. GitHub rejected self-review request with HTTP 422 because Andy is also the PR author.

Follow-up documentation branch: `docs/live-deployment`. Merge the documentation PR to bring the verified URL and final status into main. Public site is already live; this documentation merge is not required for serving. Future runtime edits should go through a branch/PR to main. No further Cloudflare setup is needed for the accepted deployment.
