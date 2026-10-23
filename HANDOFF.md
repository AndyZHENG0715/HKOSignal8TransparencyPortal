# HKO Signal 8 deployment handoff

Checked: 2026-10-23, Asia/Taipei.

## Ownership and scope

Canonical workspace: `/home/andy/projects/hko-signal8` (Ubuntu WSL). Git operations run inside WSL. Repository: `AndyZHENG0715/HKOSignal8TransparencyPortal`. Recovered from main commit `306dfcc`; no competing checkout created. Coordinator owns phase 1; TCM phase 2a waits for phase 1 completion.

Andy asked to synchronize the prepared work to GitHub so he can create Cloudflare hosting himself. Leave Pages project creation to Andy. No public deployment is verified yet. Do not label the proposed hostname live, or update the repo Website field until it is verified.

## Verified architecture and decisions

- Existing site: `prototypes/charts.html`, vanilla JS/HTML and Chart.js via jsDelivr.
- Offline pipeline: `scripts/build_event_data.py`, raw CSV/Markdown → committed JSON. No request-time backend, functions, DB, or API server found. No existing CI/build pipeline found.
- Pages Git integration is sufficient. Build `sh scripts/build_site.sh`, output `dist`, no environment variables or dependency installation. Build copies only public assets and committed JSON, with no data recomputation.
- Prepared branch: `deploy/cloudflare-pages`. Use it as production for initial setup; after PR merge switch Pages production to `main`.
- Requested project name: `hko-signal8`. Availability unverified. Share image uses that proposed hostname and needs adjustment if name differs.
- Preserve historical dataset and algorithm. UI explicitly identifies the 2022–2025 snapshot and project-specific observational checks rather than presenting them as official warning policy.

## Changes

Minimal public packaging script; Linux line endings; title/description/OG PNG/favicon; simple first-screen explanation; historical-data limitation; responsive grid and select sizing; chart containers fixing canvas distortion; bundled date adapter pinned to 3.0.0; specified footer and repo link.

## Evidence and attribution

- `README.md`, `scripts/README.md`, `scripts/build_event_data.py`, `prototypes/charts.html`, committed `data/` establish architecture and paths.
- `prototypes/poster.html` identifies GCAP3226, December 2025, and Zheng Zian among the authors; `Group Project Report & Poster/Group Project Report & Poster.md` lists the team including Zheng Zian. Git commit authors include ZHENG Zian. These support course/date and contribution, not exclusive authorship. Footer wording follows Andy's explicit request; other team attribution is preserved in source.
- Cloudflare current static HTML setup: https://developers.cloudflare.com/pages/framework-guides/deploy-anything/ (checked 2026-10-23).
- Browser verified existing Cloudflare account label `Zian.zheng0715@gmail.com`; no hosting project created.

## Checks completed

- Static packaging succeeded in WSL, producing homepage, legacy chart route, all 11 event payloads, index JSON, favicon, and 1200×630 share PNG.
- Local anonymous browser preview HTTP server, 390×844 viewport: five canvases sized correctly, no horizontal overflow, 11 events, Ragasa event selection works. No browser warning/error logs observed.
- Live deployment HTTP status/assets/console/mobile checks remain pending; local success is not deployment proof.

## Next actions

1. Andy creates the Pages Git-connected project with the exact README settings.
2. If Cloudflare needs GitHub app access, Andy grants access only to this repository.
3. Verify the assigned public URL anonymously and repeat asset, chart, console, event-selection and mobile checks.
4. Replace pending status with verified URL in README; update GitHub Website. Keep scheduled data regeneration optional.
5. Complete phase 1 acceptance before starting TCM phase 2a.
