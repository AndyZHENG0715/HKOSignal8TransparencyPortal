# HKO Signal 8 Transparency Portal

**Live website:** https://hko-signal8.pages.dev/ — anonymous public access verified on 23 October 2026.

### Deploy this snapshot on Cloudflare Pages

In **Workers & Pages → Create application → Pages → Import an existing Git repository**, select `AndyZHENG0715/HKOSignal8TransparencyPortal`.

- Project name: `hko-signal8`.
- Production branch: `main` (deployment PR #1 is merged).
- Framework preset: **None**.
- Root directory: leave blank (repository root).
- Build command: `sh scripts/build_site.sh`.
- Build output directory: `dist`.
- Environment variables: none.

This is a static HTML/JavaScript site with **no request-time backend, database, or API server**. The build copies `prototypes/charts.html` to `dist/index.html`, retains `/prototypes/charts.html`, and packages the committed `data/index.json`, `data/events/*.json`, favicon, and share image. Source reports and raw CSVs are not copied to the public bundle. No npm install, Python processing, or Wrangler configuration is required for deployment.

The data is a historical 2022–2025 snapshot, not a live feed. Run `python scripts/build_event_data.py` locally only when intentionally updating source data, review its changes, then commit the resulting JSON. A scheduled rebuild is an optional future enhancement, not enabled here.

Local deployment preview (from Ubuntu WSL):

```sh
sh scripts/build_site.sh
python3 -m http.server 8000 --directory dist
```

Open `http://localhost:8000/`. Python here is only a convenient local file server, not a production requirement. Existing source preview at `/prototypes/charts.html` also remains available when serving the repository root.

The share image is available at `https://hko-signal8.pages.dev/assets/social-preview.png`. The live homepage, legacy chart route, favicon, share image, and all 12 JSON files returned anonymous HTTP 200 during verification. All five charts loaded, event switching worked, and the 390px mobile view had no horizontal overflow or observed console warnings/errors. The repository Website field links to the public site.

Build guidance: [Cloudflare static HTML documentation](https://developers.cloudflare.com/pages/framework-guides/deploy-anything/).

---

A public-facing bilingual (English & Traditional Chinese) web portal that independently verifies Hong Kong Observatory's Tropical Cyclone Warning Signal No. 8 issuance against actual observed wind data.

**Project Goal:** Compare official T8 signal issuance with real wind observations to classify each typhoon event into one of three tiers, measuring early-warning effectiveness and public safety impact.

---

## Overview

The Hong Kong Observatory issues Tropical Cyclone Warning Signal No. 8 when sustained gale-force winds (≥63 km/h) are recorded across the reference network. This portal uses a **3-tier classification system** to evaluate whether each signal was issued responsibly—providing sufficient early warning for public preparation while avoiding unnecessary disruptions.

### Key Questions This Portal Answers

- **Was the T8 signal justified?** (Tier 1/2 = observed sustained gales; Tier 3 = unverified by wind data)
- **How much advance notice did people have?** (Early warning minutes between official issuance and actual gales)
- **What was the real-world impact?** (Casualties, property damage, and correlation with early-warning lead time)

---

## Data & Methodology

### Raw Data Source
- **Hong Kong Observatory 10-minute mean wind observations** from 8 reference anemometer stations across Hong Kong
- **Timeframe:** 2022–2025 (11 typhoon events)
- **Reference Network (HKO official):**
  - Cheung Chau (長洲)
  - Chek Lap Kok (赤鱲角)
  - Kai Tak (啟德)
  - Lau Fau Shan (流浮山)
  - Sai Kung (西貢)
  - Sha Tin (沙田)
  - Ta Kwu Ling (打鼓嶺)
  - Tsing Yi (青衣)

### 3-Tier Classification System

| Tier | Condition | Indicator |
|------|-----------|-----------|
| **Tier 1** | ≥4 stations ≥63 km/h for ≥3 consecutive 10-min intervals (~30 min) | 🟢 Sustained T8 Wind Speed Verified |
| **Tier 2** | Wind-lull-wind pattern (gales → drop → gales re-emerge) | ⚠️ Reappear T8 Wind Speed Verified |
| **Tier 3** | Neither Tier 1 persistence nor Tier 2 pattern detected | ❓ Unverified |
| **No Signal** | No official T8 issued | ➖ Not Applicable |

**Key Insight:** Tier 1 & 2 demonstrate that HKO's "expected to persist" criterion was met by observation data. Tier 3 signals require HKO to provide public explanation.

---

## Project Structure

```
HKOSignal8TransparencyPortal/
├── README.md                          # This file
├── HKO Signal 8 Transparency Portal PRD.md  # Full specification
├── data/
│   ├── index.json                    # Summary of all 11 events
│   └── events/                       # Per-event detailed payloads
│       ├── chaba.json
│       ├── koinu.json
│       ├── ma-on.json
│       ├── nalgae.json
│       ├── ragasa.json
│       ├── saola.json
│       ├── talim.json
│       ├── tapah.json
│       ├── toraji.json
│       ├── wipha.json
│       └── yagi.json
├── scripts/
│   ├── build_event_data.py           # CSV → JSON pipeline
│   └── README.md                     # Usage instructions
├── prototypes/
│   ├── charts.html                   # Chart visualizations
│   ├── poster.html                   # Project poster (HTML)
│   ├── QR Code to GitHub Repo.png    # QR code for easy repo access
│   └── README.md                     # Chart documentation
├── typhoon_data/
│   ├── time_of_signal_8.md           # Official signal timings (metadata)
│   ├── casualty_and_lost_of_signal_8.md  # Casualty & property data
│   └── <Event>/                      # Raw HKO CSV files per typhoon
│       └── *.csv                     # 10-minute wind observations
├── Group Project Report & Poster/
│   └── Group Project Report & Poster.txt  # Links to report & poster
└── assets/                            # Images, logos, etc.
```

---

## Getting Started

### Prerequisites
- **Python 3.10+** (only standard library modules used)
- **Modern web browser** (ES6+ support, no IE11)
- **Static HTTP server** (for local preview)

### Quick Start

1. **Clone or download this repository**
   ```bash
   git clone <repo-url>
   cd HKOSignal8TransparencyPortal
   ```

2. **Generate JSON data from raw CSVs** (if updating events)
   ```bash
   python scripts/build_event_data.py
   ```

3. **Preview the portal locally**
   ```bash
   # Option 1: Python
   python -m http.server 8000

   # Option 2: Node
   npx serve
   ```

4. **Open in browser**
   - Charts: `http://localhost:8000/prototypes/charts.html`

### Data Pipeline

```
Raw CSV Files (typhoon_data/EVENT/*.csv)
         ↓
   build_event_data.py (Python script)
         ↓
Generated JSON (data/index.json + data/events/*.json)
         ↓
   Web Portal & Charts
```

---

## Adding a New Typhoon Event

1. **Collect raw CSVs** from HKO and place them in a new folder under `typhoon_data/`
   - Folder naming convention: `<EventName>_<Date>` (e.g., `Nova_20251010`)
   - CSV format: `yyyymmdd-hhmm-latest_10min_wind.csv`

2. **Update metadata files:**
   - Add official T8/T10 signal timings to `typhoon_data/time_of_signal_8.md`
   - Add casualty & property loss data (if available) to `typhoon_data/casualty_and_lost_of_signal_8.md`

3. **Regenerate data**
   ```bash
   python scripts/build_event_data.py
   ```
   - Script auto-detects new event folder
   - Computes tiers deterministically
   - Outputs updated `data/index.json` and `data/events/<event>.json`

4. **Verify results** in the portal

---

## Current Events (11 Typhoons)

| Event | Year | Severity | Tier | Early Warning | Casualties | Notes |
|-------|------|----------|------|---------------|-----------|-------|
| Chaba | 2022 | T8 | Tier 3 | — | 3 injured | Unverified |
| Ma-on | 2022 | T8 | Tier 3 | — | 2 injured | Unverified |
| Nalgae | 2022 | T8 | Tier 3 | — | 3 injured | Unverified |
| Talim | 2023 | T8 | Tier 3 | — | 9 injured | Unverified |
| Saola | 2023 | T10 | Tier 2 | 1,060 min | 86 injured | Reappear pattern verified |
| Koinu | 2023 | T8 | Tier 3 | — | 29 injured | Unverified |
| Yagi | 2024 | T8 | Tier 3 | — | 9 injured | Unverified |
| Toraji | 2024 | T8 | Tier 3 | — | 1 injured | Unverified |
| Wipha | 2025 | T10 | Tier 3 | — | TBD | Unverified |
| Tapah | 2025 | T8 | Tier 3 | — | TBD | Unverified |
| Ragasa | 2025 | T10 | Tier 1 | 720 min | TBD | Sustained verified |

---

## Portal Features (Planned/In Progress)

### Pages
- **Homepage** – Key metrics, event cards (tier-based colors), bilingual toggle
- **Event Detail** – Per-event timeline, station statistics, FAQ
- **Comparison Tool** – Multi-event analysis, side-by-side metrics
- **Methodology** – Tier definitions, HKO vs algorithm comparison, educational FAQs

### Charts
1. **Tier Compliance Pie** – Share of verified (Tier 1+2) vs unverified (Tier 3) signals
2. **Early Warning Lead/Lag Bar** – Minutes between official issuance and observed gales
3. **Casualty/Property Scatter** – Correlation between early warning and real-world impact
4. **Event Timeline Heatmap** – 10-min timeline × 8 stations, color-coded by wind speed
5. **Per-Event Interactive Timeline** – Station counts with T8 threshold reference line

### Design
- **Bilingual UI** (English & Traditional Chinese 繁體中文)
- **Mobile-first responsive** (breakpoint ~768px)
- **Accessible color palette** – Clear distinction between tier indicators
- **Interactive charts** – Chart.js 4.x, responsive, touch-friendly on mobile

---

## Technical Stack

- **Frontend:** Vanilla HTML5/CSS3 + JavaScript (ES6+)
- **Charts:** Chart.js 4.x (via CDN)
- **Data Format:** JSON (pre-generated, no backend API)
- **Data Processing:** Python 3.10+ (standard library only)
- **Deployment:** Static site (GitHub Pages compatible)
- **Browser Support:** Modern browsers (no IE11)

---

## Bilingual Support

Translations use a centralized JSON dictionary (`i18n/`) with language-specific keys. Components toggle between English and Traditional Chinese via a language selector.

Example:
```html
<h2 data-key="timelineComparison">Timeline Comparison</h2>
```

Both keys are resolved at render time based on the active language context.

---

## Success Criteria

✅ Display all 11 typhoon events with automated tier classification (no hardcoding)
✅ Calculate early warning time (Official start → Algorithm detection)
✅ Bilingual interface with seamless language toggle
✅ Interactive per-event timeline charts
✅ Multi-event comparison tool
✅ Tier-based visual distinction (colors, icons, borders)
✅ Reference network strictly adheres to 8 HKO stations
✅ Neutral educational framing (no subjective judgments)

---

## Key Design Principles

1. **Public-Facing:** No jargon—assumes audience has no meteorology background
2. **Neutral Tone:** Use "Tier 1/2/3" classification rather than "appropriate/inappropriate"
3. **Transparent:** Explain both benefits (early warning saves lives) and costs (unnecessary signals cause economic loss)
4. **Data-Driven:** All claims backed by actual HKO observation records
5. **Maintenance-Free:** Once CSV/metadata are updated, one script run regenerates all JSON

---

## Project History

- **Project Goal:** Evaluate transparency of HKO Signal 8 issuance
- **Initiative:** Group project for Hong Kong Baptist University
- **Data Span:** 11 typhoon events (2022–2025)
- **Status:** Data collection & analysis complete; portal UI in development

---

## Contributing & Issues

### Reporting a Bug
Please check the raw CSV files and metadata markdown files for accuracy. If a calculation or chart rendering is incorrect, please file a detailed issue with:
- Event name and date
- Expected vs actual tier/early-warning minutes
- Screenshot or error log

### Adding Events
Follow the **"Adding a New Typhoon Event"** section above.

### Updating Visualizations
Chart prototypes are in `prototypes/charts.html`. Modify chart types, colors, or labels there and test locally before committing.

---

## License

This project is licensed under the **MIT License** – see [LICENSE](LICENSE) file for details.

MIT License is permissive and free for educational, research, and commercial use. You are free to use, modify, and distribute this project with minimal restrictions.

---

## Acknowledgments

- **Data Source:** Hong Kong Observatory (HKO) 10-minute mean wind observations
- **Reference Standard:** HKO Tropical Cyclone Warning System (effective 2007–present)
- **Project Sponsor:** Hong Kong Baptist University

---

## Contact & Questions

For questions about the methodology, data accuracy, or to request new features:
- See `HKO Signal 8 Transparency Portal PRD.md` for full specification
- Review `scripts/README.md` for data pipeline details
- Check `prototypes/README.md` for chart documentation

---

**Last Updated:** December 2025
