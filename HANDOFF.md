# Complete portal implementation handoff

Updated 2026-10-23, Asia/Taipei.

Canonical workspace: /home/andy/projects/hko-signal8 (Ubuntu WSL); Git inside WSL. One checkout, repository AndyZHENG0715/HKOSignal8TransparencyPortal. Production https://hko-signal8.pages.dev/ was verified live for the initial chart site; PRs #1 and #2 merged. Main at implementation start:417f94a.

## Current work

Branch feat/complete-portal integrates a complete seven-page bilingual website into the existing Pages deployment. No changes to the two other HKO repositories. Website source is website/; generated data committed. Pages build remains sh scripts/build_site.sh, output dist, main production. No Python in CI. New schema /data/events-v2 is separate from legacy prototype JSON. The original chart and source/raw archives are preserved.

User requested complete website and data supplementation, then reminded the coordinator to orchestrate. Parent owns integration/browser/final acceptance. Independent data_audit agent recovered official missing data and reviewed provenance; website_review agent performed read-only code/contract checks. Parent reviewed and corrected reported mobile header, footer contrast, comparison axis, CDN fallback and heatmap interaction issues.

## Data acceptance

Original Ma-on and Nalgae source dates do not overlap their warning envelopes; Koinu, Saola, Ragasa had incomplete tails. Official DATA.GOV.HK historical monthly archives were recovered for all five, exact CSV bytes preserved in recovered-data ZIPs with URL/retrieval/version/hash manifests. Original folders untouched. Regeneration uses embedded observation times, not revision filenames, and latest archived revision per reference station/time. Ragasa has 394 conflicting reference cells across revisions; independent first-versus-latest analysis preserves first onset02:20 and confirmation02:40 on Sep24. Malformed rows retained in raw downloads, skipped defensively; nulls remain unknown.

The new pipeline checks cadence and complete eight-station network within inherited warning metadata. Continuous ten-minute grid only; missing network data/gaps break sustained/pattern runs. Warning metadata provenance remains inherited rather than universally independently verified. Complete-network requirement and three-sample convention are project rules, not official HKO policy. No casualty causation or blanket judgment of HKO decisions is presented.

## Verification and delivery

Seven Python regression/integrity tests passed during implementation. These cover minute/hour gap rejection, third-sample confirmation, missing-station run breaks, two-sample lull, summary/detail agreement, and every downloadable raw-file hash. Browser acceptance and public preview checks are recorded in subsequent closeout updates. Production should stay on prior version until the completed PR is reviewed/merged; do not call a local build a deployment.

README is rewritten to current serving/build/data paths and attribution. Recovery evidence is in recovered-data/*-manifest.json and README. Main data generator scripts/build_portal_data.py is standard library and reproducible offline. A website code review found no concrete user-controlled HTML injection; IDs are allowlisted and strings escaped. Future TCM phase2a should not distract from completing this portal upgrade first.
