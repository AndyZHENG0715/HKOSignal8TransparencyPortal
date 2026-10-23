#!/usr/bin/env python3
"""Rebuild the public portal from committed raw HKO CSVs. No network or third-party dependencies."""
import csv, hashlib, io, json, zipfile, math
from collections import Counter
from datetime import datetime
from pathlib import Path
import build_event_data as legacy
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'website'

def runs(rows):
    result=[]; current=[]
    for r in rows:
        if current and (r['time']-current[-1]['time']).total_seconds()!=600:
            result.append(current); current=[]
        if r['count']>=4 and r['valid']==8:
            current.append(r)
        elif current:
            result.append(current); current=[]
    if current: result.append(current)
    return result

def classify(rows):
    windows=runs(rows)
    sustained=[w for w in windows if len(w)>=3]
    if sustained: return 1,sustained[0][0]['timestamp'],sustained[0][2]['timestamp'],sustained
    # A reappearance pattern requires a continuous 10-minute sequence and >=2 below-threshold samples.
    seen=False; lull=0; previous=None
    for r in rows:
        if previous is not None and (r['time']-previous).total_seconds()!=600: seen=False; lull=0
        previous=r['time']
        if r['valid']!=8: seen=False; lull=0; continue
        if r['count']>=4:
            if seen and lull>=2: return 2,None,None,[]
            seen=True; lull=0
        elif seen: lull+=1
    return 3,None,None,[]

def write(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes((json.dumps(data,ensure_ascii=False,indent=2)+'\n').encode())

def source_files(event_id,folder):
    recovered=ROOT/'recovered-data'/f'{event_id}.zip'
    if recovered.exists():
        with zipfile.ZipFile(recovered) as z:
            return [(name,z.read(name)) for name in sorted(z.namelist())],recovered.relative_to(ROOT).as_posix()
    return [(p.relative_to(ROOT).as_posix(),p.read_bytes()) for p in sorted(folder.glob('*.csv'))],None

def load_rows(files):
    cells={}; values={}; invalid=0
    for name,raw in files:
        for row in csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))):
            if None in row or any(row.get(k) is None for k in ['Date time','Automatic Weather Station','10-Minute Mean Speed(km/hour)']):
                invalid+=1;continue
            station=(row.get('Automatic Weather Station') or '').strip()
            if station not in legacy.STATION_BY_CSV: continue
            stamp=(row.get('Date time') or '').strip()
            try: time=datetime.strptime(stamp,'%Y%m%d%H%M').replace(tzinfo=legacy.HKT)
            except ValueError: invalid+=1;continue
            value=(row.get('10-Minute Mean Speed(km/hour)') or '').strip()
            try: mean=float(value); mean=mean if math.isfinite(mean) and mean>=0 else None
            except ValueError: mean=None
            values.setdefault((stamp,station),set()).add(mean)
            cells.setdefault(time,{})[station]=mean
    rows=[];excluded=0
    for time,cell in sorted(cells.items()):
        # Retain only embedded observation times on a declared 10-minute grid.
        if time.minute%10: excluded+=1;continue
        winds=[cell.get(s['csvName']) for s in legacy.REFERENCE_STATIONS]
        rows.append({'timestamp':time.isoformat(timespec='minutes'),'time':time,'winds':winds,
                     'count':sum(w is not None and w>=63 for w in winds),'valid':sum(w is not None for w in winds)})
    return rows,{'conflictingReferenceCells':sum(len(v)>1 for v in values.values()),'malformedReferenceRows':invalid,'offGridSamplesExcluded':excluded}

def main():
    (OUT/'data').mkdir(parents=True,exist_ok=True)
    (OUT/'data/event-metadata.json').write_bytes((ROOT/'data/event-metadata.json').read_bytes())
    folders=legacy.discover_event_directories(ROOT/'typhoon_data')
    events=[]; provenance=[]
    for m in json.loads((ROOT/'data/event-metadata.json').read_text()):
        folder=folders[m['id']]; source,source_archive=source_files(m['id'],folder); rows,parse_quality=load_rows(source)
        start=datetime.fromisoformat(m['officialSignal8Start']); end=datetime.fromisoformat(m['officialSignal8End'])
        window=[r for r in rows if start<=r['time']<=end]
        tier,onset,confirmation,sustained=classify(window)
        if not any(r['valid']==8 for r in window): tier=0
        gaps=sum((b['time']-a['time']).total_seconds()!=600 for a,b in zip(window,window[1:]))
        sustained_set={r['timestamp'] for w in sustained for r in w}
        event={'metadata':m,'tier':tier,'onset':onset,'confirmation':confirmation,
               'leadToOnsetMinutes':int((datetime.fromisoformat(onset)-start).total_seconds()/60) if onset else None,
               'leadToConfirmationMinutes':int((datetime.fromisoformat(confirmation)-start).total_seconds()/60) if confirmation else None,
               'sourceArchive':source_archive,'revisionPolicy':'Latest archived file version in filename order per embedded timestamp and station; all source versions preserved.',
               'quality':{**parse_quality,'totalSamples':len(rows),'windowSamples':len(window),'completeNetworkSamples':sum(r['valid']==8 for r in window),
                          'gaps':gaps,'firstSample':rows[0]['timestamp'],'lastSample':rows[-1]['timestamp'],
                          'windowFirstSample':window[0]['timestamp'] if window else None,'windowLastSample':window[-1]['timestamp'] if window else None,
                          'startsBeforeWarning':rows[0]['time']<=start,'endsAfterWarning':rows[-1]['time']>=end},
               'sustainedSampleMinutes':sum(len(w)*10 for w in sustained),
               'stations':[{'id':s['stationId'],'nameEn':s['nameEn'],'nameZh':s['nameZh']} for s in legacy.REFERENCE_STATIONS],
               'timeline':[{'timestamp':r['timestamp'],'count':r['count'],'valid':r['valid'],'winds':r['winds'],
                            'inWindow':start<=r['time']<=end,'sustained':r['timestamp'] in sustained_set} for r in rows]}
        files=[{'path':name,'sha256':hashlib.sha256(raw).hexdigest()} for name,raw in source]
        provenance.append({'id':m['id'],'sourceArchive':source_archive,'sourceFiles':files})
        if source_archive:
            (OUT/'data'/f"{m['id']}-recovery-manifest.json").write_bytes((ROOT/'recovered-data'/f"{m['id']}-manifest.json").read_bytes())
        write(OUT/'data/events-v2'/f"{m['id']}.json",event)
        stream=io.StringIO(newline=''); writer=csv.writer(stream,lineterminator='\n')
        writer.writerow(['timestamp_hkt','stations_ge_63','valid_stations','within_warning_envelope','sustained_run',*[s['nameEn']+'_kmh' for s in event['stations']]])
        for r in event['timeline']: writer.writerow([r['timestamp'],r['count'],r['valid'],r['inWindow'],r['sustained'],*r['winds']])
        (OUT/'downloads'/f"{m['id']}-timeline.csv").write_bytes(stream.getvalue().encode())
        source_map=dict(source)
        with zipfile.ZipFile(OUT/'downloads'/f"{m['id']}-raw.zip",'w',compression=zipfile.ZIP_DEFLATED) as z:
            for f in files:
                zi=zipfile.ZipInfo(f['path'],(2025,12,1,0,0,0)); zi.compress_type=zipfile.ZIP_DEFLATED
                z.writestr(zi,source_map[f['path']])
        events.append({k:v for k,v in event.items() if k not in ['timeline','stations']})
        print(m['id'],parse_quality, 'tier',tier,'samples',len(rows),'lead onset/confirmation',event['leadToOnsetMinutes'],event['leadToConfirmationMinutes'])
    events.sort(key=lambda e:e['metadata']['officialSignal8Start'])
    write(OUT/'data/summary.json',{'schemaVersion':1,'snapshot':'2022–2025','method':'10-minute cadence, complete 8-station network, official warning envelope; >=3 consecutive qualifying samples for Tier 1; >=2 below-threshold samples for Tier 2 lull. Not an audit of official decision correctness.','events':events})
    write(OUT/'data/provenance.json',{'rawDataSource':'https://data.weather.gov.hk/weatherAPI/hko_data/regional-weather/latest_10min_wind.csv','metadataSource':'data/event-metadata.json inherited from repository data at 417f94a; not all warning records independently reverified','events':provenance})
if __name__=='__main__': main()
