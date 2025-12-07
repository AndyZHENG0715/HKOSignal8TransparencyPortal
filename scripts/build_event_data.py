#!/usr/bin/env python3
"""
HK Signal 8 Transparency Portal - CSV → JSON builder.

Usage:
    python scripts/build_event_data.py [--typhoon-dir typhoon_data] [--output-dir data]

The script:
1. Parses the official metadata tables (`time_of_signal_8.md`, casualty table, PRD event table).
2. Scans every event folder under typhoon_data/, filters the 8 reference stations, and builds a
   fully ordered 10-minute timeline.
3. Detects Tier 1 (persistence) or Tier 2 (wind-lull-wind) behaviour, computes early-warning
   minutes, persistence windows, and highlight bullets.
4. Emits `data/index.json` plus `data/events/<eventId>.json` so the static site can stay backend-free.

Drop new CSVs, keep the metadata tables up to date, and rerun this script to refresh all JSON output.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

HKT = timezone(timedelta(hours=8))
T8_THRESHOLD_KMH = 63
MIN_REFERENCE_STATIONS = 4
MIN_PERSISTENCE_INTERVALS = 3  # 3 × 10-minute windows ≈ 30 minutes

REFERENCE_STATIONS: List[Dict[str, str]] = [
    {"stationId": "cheung-chau", "csvName": "Cheung Chau", "nameEn": "Cheung Chau", "nameZh": "長洲"},
    {"stationId": "chek-lap-kok", "csvName": "Chek Lap Kok", "nameEn": "Chek Lap Kok", "nameZh": "赤鱲角"},
    {"stationId": "kai-tak", "csvName": "Kai Tak", "nameEn": "Kai Tak", "nameZh": "啟德"},
    {"stationId": "lau-fau-shan", "csvName": "Lau Fau Shan", "nameEn": "Lau Fau Shan", "nameZh": "流浮山"},
    {"stationId": "sai-kung", "csvName": "Sai Kung", "nameEn": "Sai Kung", "nameZh": "西貢"},
    {"stationId": "sha-tin", "csvName": "Sha Tin", "nameEn": "Sha Tin", "nameZh": "沙田"},
    {"stationId": "ta-kwu-ling", "csvName": "Ta Kwu Ling", "nameEn": "Ta Kwu Ling", "nameZh": "打鼓嶺"},
    {"stationId": "tsing-yi", "csvName": "Tsing Yi", "nameEn": "Tsing Yi", "nameZh": "青衣"},
]
STATION_BY_CSV = {entry["csvName"]: entry for entry in REFERENCE_STATIONS}

SIGNAL_HEADER = [
    "Storm",
    "Year",
    "Signal 8 Issued",
    "Signal 8 Replaced/Cancelled",
    "Duration",
    "Signal 10",
    "Notes",
]
PRD_EVENT_HEADER = [
    "Event ID",
    "Name",
    "Chinese",
    "Year",
    "Date Range",
    "Official Signal 8 Start",
    "Official Signal 8 End",
    "Official Signal 10 Start",
    "Official Signal 10 End",
    "Severity",
]
CASUALTY_HEADER = [
    "Name",
    "Year",
    "Deaths",
    "Missing",
    "Injured",
    "Shipwreck (oceangoing)",
    "Destroyed Small Boats",
    "Damaged Small Boats",
]

TIER_LABELS = {
    1: "Tier 1: Sustained T8 Wind Speed Verified",
    2: "Tier 2: Reappear T8 Wind Speed Verified",
    3: "Tier 3: Unverified",
}


@dataclass
class StationReading:
    station_id: str
    name_en: str
    name_zh: str
    mean_speed: Optional[float]
    gust_speed: Optional[float]
    meets_threshold: bool


@dataclass
class IntervalReading:
    dt: datetime
    stations: List[StationReading]
    stations_meeting_threshold: int

    @property
    def timestamp(self) -> str:
        return self.dt.isoformat(timespec="minutes")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def parse_markdown_table(path: Path, expected_header: List[str]) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    header: Optional[List[str]] = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if header is None:
            if cells == expected_header:
                header = cells
            continue
        # skip separator row (---)
        if all(set(cell) <= {"", "-", ":"} for cell in cells):
            continue
        if len(cells) != len(header):
            continue
        rows.append({header[i]: cells[i] for i in range(len(header))})
    return rows


def parse_dt(value: str, fmt: str) -> datetime:
    return datetime.strptime(value, fmt).replace(tzinfo=HKT)


def parse_signal_time(value: str) -> datetime:
    return parse_dt(value, "%H:%M, %d %b %Y")


def parse_optional_signal10(row: Dict[str, str], official_start: datetime) -> Tuple[Optional[str], Optional[str]]:
    if row.get("Signal 10", "").strip().lower() != "yes":
        return None, None
    notes = row.get("Notes", "")
    full_pattern = re.compile(
        r"(\d{2}:\d{2}),\s*(\d{1,2}\s+\w+\s+\d{4})\s+to\s+(\d{2}:\d{2}),\s*(\d{1,2}\s+\w+\s+\d{4})"
    )
    match = full_pattern.search(notes)
    if match:
        start = parse_dt(f"{match.group(1)}, {match.group(2)}", "%H:%M, %d %b %Y")
        end = parse_dt(f"{match.group(3)}, {match.group(4)}", "%H:%M, %d %b %Y")
        return start.isoformat(timespec="minutes"), end.isoformat(timespec="minutes")

    def _parse_partial(time_str: str, date_str: str, reference: datetime) -> datetime:
        date_str = date_str.strip()
        if len(date_str.split()) == 2:
            date_str = f"{date_str} {reference.year}"
        dt_value = parse_dt(f"{time_str}, {date_str}", "%H:%M, %d %b %Y")
        while dt_value < reference:
            dt_value += timedelta(days=1)
        return dt_value

    range_pattern = re.compile(
        r"(\d{2}:\d{2}),\s*(\d{1,2}\s+\w+(?:\s+\d{4})?)\s+to\s+(\d{2}:\d{2}),\s*(\d{1,2}\s+\w+(?:\s+\d{4})?)"
    )
    match = range_pattern.search(notes)
    if match:
        start_dt = _parse_partial(match.group(1), match.group(2), official_start)
        end_dt = _parse_partial(match.group(3), match.group(4), start_dt)
        while end_dt <= start_dt:
            end_dt += timedelta(days=1)
        return start_dt.isoformat(timespec="minutes"), end_dt.isoformat(timespec="minutes")

    simple_pattern = re.compile(r"(\d{2}:\d{2})-(\d{2}:\d{2})")
    match = simple_pattern.search(notes)
    if not match:
        return None, None
    start_time = datetime.strptime(match.group(1), "%H:%M").time()
    end_time = datetime.strptime(match.group(2), "%H:%M").time()
    start_dt = official_start.replace(hour=start_time.hour, minute=start_time.minute)
    if start_dt < official_start:
        start_dt += timedelta(days=1)
    end_dt = start_dt.replace(hour=end_time.hour, minute=end_time.minute)
    while end_dt <= start_dt:
        end_dt += timedelta(days=1)
    return start_dt.isoformat(timespec="minutes"), end_dt.isoformat(timespec="minutes")


def split_names(value: str) -> Tuple[str, str]:
    match = re.match(r"(.+?)\s*\((.+)\)", value)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return value.strip(), ""


def build_metadata(project_root: Path) -> Dict[str, Dict[str, object]]:
    signal_rows = parse_markdown_table(project_root / "typhoon_data" / "time_of_signal_8.md", SIGNAL_HEADER)
    casualty_rows = parse_markdown_table(project_root / "typhoon_data" / "casualty_and_lost_of_signal_8.md", CASUALTY_HEADER)
    prd_rows = parse_markdown_table(project_root / "# HKO Signal 8 Transparency Portal.md", PRD_EVENT_HEADER)

    metadata: Dict[str, Dict[str, object]] = {}
    for row in signal_rows:
        name_en, name_zh = split_names(row["Storm"])
        event_id = slugify(name_en)
        issued = parse_signal_time(row["Signal 8 Issued"])
        cancelled = parse_signal_time(row["Signal 8 Replaced/Cancelled"])
        signal10_start, signal10_end = parse_optional_signal10(row, issued)
        notes = [note.strip() for note in row.get("Notes", "").split(";") if note.strip()]
        metadata[event_id] = {
            "id": event_id,
            "nameEn": name_en,
            "nameZh": name_zh,
            "year": int(row["Year"]),
            "officialSignal8Start": issued.isoformat(timespec="minutes"),
            "officialSignal8End": cancelled.isoformat(timespec="minutes"),
            "officialSignal10Start": signal10_start,
            "officialSignal10End": signal10_end,
            "notes": notes,
        }

    for row in prd_rows:
        event_id = row["Event ID"].strip()
        if not event_id:
            continue
        meta = metadata.setdefault(event_id, {"id": event_id})
        meta.setdefault("nameEn", row["Name"].strip())
        meta.setdefault("nameZh", row["Chinese"].strip())
        if row.get("Official Signal 8 Start") and row["Official Signal 8 Start"] != "-":
            meta.setdefault("officialSignal8Start", parse_dt(row["Official Signal 8 Start"], "%Y-%m-%d %H:%M").isoformat(timespec="minutes"))
        if row.get("Official Signal 8 End") and row["Official Signal 8 End"] != "-":
            meta.setdefault("officialSignal8End", parse_dt(row["Official Signal 8 End"], "%Y-%m-%d %H:%M").isoformat(timespec="minutes"))
        if row.get("Official Signal 10 Start") and row["Official Signal 10 Start"] != "-":
            meta["officialSignal10Start"] = parse_dt(row["Official Signal 10 Start"], "%Y-%m-%d %H:%M").isoformat(timespec="minutes")
        if row.get("Official Signal 10 End") and row["Official Signal 10 End"] != "-":
            meta["officialSignal10End"] = parse_dt(row["Official Signal 10 End"], "%Y-%m-%d %H:%M").isoformat(timespec="minutes")
        meta["severity"] = row.get("Severity", "").strip() or ("T10" if meta.get("officialSignal10Start") else "T8")
        meta.setdefault("year", int(row["Year"]))

    for row in casualty_rows:
        event_id = slugify(row["Name"])
        if event_id not in metadata:
            continue
        metadata[event_id]["casualty"] = {
            "deaths": int(row["Deaths"]),
            "missing": int(row["Missing"]),
            "injured": int(row["Injured"]),
        }
        metadata[event_id]["propertyLoss"] = {
            "shipwreckOceangoing": int(row["Shipwreck (oceangoing)"]),
            "destroyedSmallBoats": int(row["Destroyed Small Boats"]),
            "damagedSmallBoats": int(row["Damaged Small Boats"]),
        }

    for meta in metadata.values():
        meta.setdefault("severity", "T10" if meta.get("officialSignal10Start") else "T8")
        meta.setdefault("notes", [])
    return metadata


def discover_event_directories(typhoon_root: Path) -> Dict[str, Path]:
    event_dirs: Dict[str, Path] = {}
    for entry in typhoon_root.iterdir():
        if not entry.is_dir():
            continue
        match = re.search(r"[-A-Za-z]+", entry.name)
        if not match:
            continue
        event_id = slugify(match.group(0))
        event_dirs[event_id] = entry
    return event_dirs


def to_float(value: str) -> Optional[float]:
    value = value.strip()
    if not value or value.upper() == "N/A":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def load_station_timelines(event_dir: Path) -> List[IntervalReading]:
    timeline_data: Dict[str, Dict[str, Dict[str, Optional[float]]]] = {}
    for csv_path in sorted(event_dir.glob("*.csv")):
        with csv_path.open("r", encoding="utf-8-sig") as handle:
            reader = csv.DictReader(handle)
            timestamp_value: Optional[str] = None
            for row in reader:
                timestamp_value = row["Date time"].strip()
                station_name = row["Automatic Weather Station"].strip()
                if station_name not in STATION_BY_CSV:
                    continue
                mean_speed = to_float(row["10-Minute Mean Speed(km/hour)"])
                gust_speed = to_float(row["10-Minute Maximum Gust(km/hour)"])
                cell = timeline_data.setdefault(timestamp_value, {})
                cell[station_name] = {"mean": mean_speed, "gust": gust_speed}
            # Some files may be empty; nothing to do if timestamp_value is None
    readings: List[IntervalReading] = []
    for timestamp_key in sorted(timeline_data.keys()):
        dt = datetime.strptime(timestamp_key, "%Y%m%d%H%M").replace(tzinfo=HKT)
        stations: List[StationReading] = []
        cell = timeline_data[timestamp_key]
        for ref in REFERENCE_STATIONS:
            row = cell.get(ref["csvName"], {})
            mean_speed = row.get("mean")
            gust_speed = row.get("gust")
            meets = mean_speed is not None and mean_speed >= T8_THRESHOLD_KMH
            stations.append(
                StationReading(
                    station_id=ref["stationId"],
                    name_en=ref["nameEn"],
                    name_zh=ref["nameZh"],
                    mean_speed=mean_speed,
                    gust_speed=gust_speed,
                    meets_threshold=meets,
                )
            )
        count = sum(1 for s in stations if s.meets_threshold)
        readings.append(IntervalReading(dt=dt, stations=stations, stations_meeting_threshold=count))
    return readings


def build_persistence_windows(readings: List[IntervalReading]) -> List[Dict[str, object]]:
    windows: List[Dict[str, object]] = []
    current: Optional[Dict[str, object]] = None
    for interval in readings:
        meets = interval.stations_meeting_threshold >= MIN_REFERENCE_STATIONS
        if meets:
            if current is None:
                current = {
                    "start_dt": interval.dt,
                    "end_dt": interval.dt,
                    "intervals": 0,
                    "maxCount": interval.stations_meeting_threshold,
                }
            current["end_dt"] = interval.dt
            current["intervals"] += 1
            current["maxCount"] = max(current["maxCount"], interval.stations_meeting_threshold)
        else:
            if current:
                windows.append(current)
                current = None
    if current:
        windows.append(current)
    return windows


def convert_window(window: Dict[str, object]) -> Dict[str, object]:
    intervals = int(window["intervals"])
    max_count = window.get("maxCount")
    return {
        "start": window["start_dt"].isoformat(timespec="minutes"),
        "end": window["end_dt"].isoformat(timespec="minutes"),
        "intervalCount": intervals,
        "minutes": intervals * 10,
        "maxStationCount": max_count,
    }


def detect_tier(readings: List[IntervalReading]) -> Dict[str, object]:
    windows = build_persistence_windows(readings)
    tier1_window = next((w for w in windows if w["intervals"] >= MIN_PERSISTENCE_INTERVALS), None)
    if tier1_window:
        return {
            "detectedTier": 1,
            "initialDetection": tier1_window["start_dt"],
            "persistenceWindows": [convert_window(w) for w in windows],
            "tier1Window": convert_window(tier1_window),
            "tier2Pattern": None,
        }

    # Tier 2 state machine
    state = "search"
    initial = lull = remerge = None
    for interval in readings:
        meets = interval.stations_meeting_threshold >= MIN_REFERENCE_STATIONS
        if state == "search":
            if meets:
                initial = {"start_dt": interval.dt, "end_dt": interval.dt, "intervals": 1}
                state = "initial"
        elif state == "initial":
            if meets:
                initial["end_dt"] = interval.dt
                initial["intervals"] += 1
            else:
                lull = {"start_dt": interval.dt, "end_dt": interval.dt, "intervals": 1}
                state = "lull"
        elif state == "lull":
            if meets:
                remerge = {"start_dt": interval.dt, "end_dt": interval.dt, "intervals": 1}
                state = "reemerge"
            else:
                lull["end_dt"] = interval.dt
                lull["intervals"] += 1
        elif state == "reemerge":
            if meets:
                remerge["end_dt"] = interval.dt
                remerge["intervals"] += 1
            else:
                break
    if state == "reemerge" and initial and lull and remerge:
        return {
            "detectedTier": 2,
            "initialDetection": initial["start_dt"],
            "persistenceWindows": [convert_window(w) for w in windows],
            "tier1Window": None,
            "tier2Pattern": {
                "initialBurst": convert_window(initial),
                "lull": convert_window(lull),
                "reemergence": convert_window(remerge),
            },
        }

    return {
        "detectedTier": 3,
        "initialDetection": None,
        "persistenceWindows": [convert_window(w) for w in windows],
        "tier1Window": None,
        "tier2Pattern": None,
    }


def minutes_delta(later: datetime, earlier: datetime) -> int:
    return int((later - earlier).total_seconds() // 60)


def summarize_peak(readings: List[IntervalReading]) -> Optional[Dict[str, object]]:
    peak = None
    for interval in readings:
        for station in interval.stations:
            if station.mean_speed is None:
                continue
            if not peak or station.mean_speed > peak["speed"]:
                peak = {
                    "stationId": station.station_id,
                    "nameEn": station.name_en,
                    "nameZh": station.name_zh,
                    "speed": station.mean_speed,
                    "timestamp": interval.timestamp,
                }
    return peak


def generate_highlights(
    tier_info: Dict[str, object],
    early_warning: Optional[int],
    peak_station: Optional[Dict[str, object]],
) -> List[str]:
    highlights: List[str] = []
    tier = tier_info["detectedTier"]
    if tier == 1 and tier_info.get("tier1Window"):
        w = tier_info["tier1Window"]
        highlights.append(
            f"Tier 1 persistence detected for {w['minutes']} min starting {w['start']} "
            f"({w['maxStationCount']}/8 stations ≥63 km/h)."
        )
    elif tier == 2 and tier_info.get("tier2Pattern"):
        pattern = tier_info["tier2Pattern"]
        highlights.append(
            "Tier 2 wind-lull-wind pattern: burst at {start}, lull until {lull_end}, "
            "reemergence at {reemerge_start}."
            .format(
                start=pattern["initialBurst"]["start"],
                lull_end=pattern["lull"]["end"],
                reemerge_start=pattern["reemergence"]["start"],
            )
        )
    else:
        highlights.append("Tier 3 (unverified): no ≥30 min persistence detected across the reference network.")

    if early_warning is not None:
        if early_warning > 0:
            highlights.append(f"HKO issued T8 {early_warning} min before sustained gales were observed.")
        elif early_warning < 0:
            highlights.append(f"Sustained gales arrived {abs(early_warning)} min before HKO's T8.")
        else:
            highlights.append("Observed persistence began at the same time as the official T8 issuance.")

    if peak_station:
        highlights.append(
            f"Peak mean wind {int(round(peak_station['speed']))} km/h at {peak_station['nameEn']} "
            f"({peak_station['timestamp']})."
        )
    return highlights


def interval_public_payload(interval: IntervalReading) -> Dict[str, object]:
    return {
        "timestamp": interval.timestamp,
        "stationsMeetingThresholdCount": interval.stations_meeting_threshold,
        "meetsTierThreshold": interval.stations_meeting_threshold >= MIN_REFERENCE_STATIONS,
        "stations": [
            {
                "stationId": s.station_id,
                "nameEn": s.name_en,
                "nameZh": s.name_zh,
                "meanSpeedKmh": s.mean_speed,
                "gustKmh": s.gust_speed,
                "meetsThreshold": s.meets_threshold,
            }
            for s in interval.stations
        ],
    }


def build_event_payload(event_meta: Dict[str, object], readings: List[IntervalReading]) -> Dict[str, object]:
    tier_info = detect_tier(readings)
    official_start = datetime.fromisoformat(event_meta["officialSignal8Start"])  # type: ignore[arg-type]
    detection_start = tier_info["initialDetection"]
    early_warning = None
    if detection_start is not None:
        early_warning = minutes_delta(detection_start, official_start)
    peak_station = summarize_peak(readings)
    highlights = generate_highlights(tier_info, early_warning, peak_station)

    tier_evaluation = {
        "detectedTier": tier_info["detectedTier"],
        "tierLabel": TIER_LABELS[tier_info["detectedTier"]],
        "initialDetection": tier_info["initialDetection"].isoformat(timespec="minutes")
        if tier_info["initialDetection"]
        else None,
        "persistenceWindows": tier_info["persistenceWindows"],
        "tier1Window": tier_info.get("tier1Window"),
        "tier2Pattern": tier_info.get("tier2Pattern"),
        "meetsFourStationPersistence": tier_info["detectedTier"] == 1,
        "stationCountSeries": [
            {
                "timestamp": interval.timestamp,
                "stationsMeetingThreshold": interval.stations_meeting_threshold,
            }
            for interval in readings
        ],
    }

    derived_metrics = {
        "earlyWarningMinutes": early_warning,
        "totalIntervals": len(readings),
        "intervalsMeetingThreshold": sum(
            1 for interval in readings if interval.stations_meeting_threshold >= MIN_REFERENCE_STATIONS
        ),
        "longestPersistenceMinutes": max(
            (window["minutes"] for window in tier_info["persistenceWindows"]), default=0
        ),
        "peakStation": peak_station,
    }

    payload = {
        "metadata": {
            "id": event_meta["id"],
            "nameEn": event_meta["nameEn"],
            "nameZh": event_meta["nameZh"],
            "year": event_meta["year"],
            "severity": event_meta["severity"],
            "officialSignal8Start": event_meta["officialSignal8Start"],
            "officialSignal8End": event_meta["officialSignal8End"],
            "officialSignal10Start": event_meta.get("officialSignal10Start"),
            "officialSignal10End": event_meta.get("officialSignal10End"),
            "notes": event_meta.get("notes", []),
            "highlights": highlights,
        },
        "stationReadings": [interval_public_payload(interval) for interval in readings],
        "tierEvaluation": tier_evaluation,
        "derivedMetrics": derived_metrics,
    }
    if event_meta.get("casualty"):
        payload["casualty"] = event_meta["casualty"]
    if event_meta.get("propertyLoss"):
        payload["propertyLoss"] = event_meta["propertyLoss"]
    payload["tier"] = tier_info["detectedTier"]
    payload["highlights"] = highlights
    payload["derivedMetrics"]["persistenceWindows"] = tier_info["persistenceWindows"]
    return payload


def write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def build_index_payload(event_payloads: Iterable[Dict[str, object]]) -> List[Dict[str, object]]:
    summaries: List[Dict[str, object]] = []
    for payload in event_payloads:
        meta = payload["metadata"]
        summaries.append(
            {
                "id": meta["id"],
                "nameEn": meta["nameEn"],
                "nameZh": meta["nameZh"],
                "year": meta["year"],
                "tier": payload["tier"],
                "tierLabel": TIER_LABELS[payload["tier"]],
                "severity": meta["severity"],
                "officialSignal8Start": meta["officialSignal8Start"],
                "officialSignal8End": meta["officialSignal8End"],
                "officialSignal10Start": meta["officialSignal10Start"],
                "officialSignal10End": meta["officialSignal10End"],
                "earlyWarningMinutes": payload["derivedMetrics"]["earlyWarningMinutes"],
                "casualty": payload.get("casualty"),
                "propertyLoss": payload.get("propertyLoss"),
                "highlights": payload["highlights"],
            }
        )
    return sorted(summaries, key=lambda row: row["officialSignal8Start"])


def main() -> None:
    parser = argparse.ArgumentParser(description="Build HK Signal 8 JSON data.")
    parser.add_argument("--typhoon-dir", default="typhoon_data", help="Where raw CSV folders live")
    parser.add_argument("--output-dir", default="data", help="Where to write the generated JSON")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parents[1]
    typhoon_root = (project_root / args.typhoon_dir).resolve()
    output_root = (project_root / args.output_dir).resolve()
    events_output_dir = output_root / "events"

    metadata = build_metadata(project_root)
    event_dirs = discover_event_directories(typhoon_root)

    generated_payloads: List[Dict[str, object]] = []
    for event_id, dir_path in sorted(event_dirs.items()):
        if event_id not in metadata:
            print(f"[warn] metadata missing for event '{event_id}', skipping.")
            continue
        print(f"[info] processing {event_id} ({dir_path.name}) ...")
        readings = load_station_timelines(dir_path)
        if not readings:
            print(f"[warn] {event_id} has no usable CSV rows, skipping.")
            continue
        payload = build_event_payload(metadata[event_id], readings)
        generated_payloads.append(payload)
        write_json(events_output_dir / f"{event_id}.json", payload)

    write_json(output_root / "index.json", build_index_payload(generated_payloads))
    print(f"[done] generated {len(generated_payloads)} event files -> {output_root}")


if __name__ == "__main__":
    main()
