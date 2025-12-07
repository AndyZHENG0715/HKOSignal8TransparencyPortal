## CSV → JSON Builder

`scripts/build_event_data.py` turns the raw 10-minute wind CSVs into the JSON payloads that power the portal.

### Prerequisites
- Python 3.10+ (only standard library modules are used).
- Project structure intact (`typhoon_data/` contains event folders + metadata markdown files).

### How to run
```bash
python scripts/build_event_data.py
```

Optional flags:
- `--typhoon-dir typhoon_data` – override raw data location.
- `--output-dir data` – override where JSON is written (`data/index.json`, `data/events/<event>.json`).

### Adding a new event
1. **Drop CSVs** into a new folder under `typhoon_data/`. The folder name just needs to begin with the storm's English name (e.g. `Nova 20251010` → event id `nova`).
2. **Update metadata**:
   - Append a row to `typhoon_data/time_of_signal_8.md` with the official T8/T10 timings.
   - Append casualty/property data (if available) to `typhoon_data/casualty_and_lost_of_signal_8.md`.
3. **Run the script** again. It will detect the new directory automatically, recompute tiers, and rewrite the JSON files deterministically.

### Key assumptions
- Only the 8 HKO reference stations are considered (`Cheung Chau`, `Chek Lap Kok`, `Kai Tak`, `Lau Fau Shan`, `Sai Kung`, `Sha Tin`, `Ta Kwu Ling`, `Tsing Yi`).
- All timestamps are treated as Hong Kong Time (UTC+8).
- Tier thresholds come directly from the PRD (≥4 stations ≥63 km/h; Tier 1 requires ≥3 consecutive intervals, Tier 2 requires wind-lull-wind when Tier 1 fails).

If the metadata tables stay up to date, rerunning the script is the only step needed to keep the portal data current.
