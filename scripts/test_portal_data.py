#!/usr/bin/env python3
"""Regression checks for temporal classification and packaged data integrity."""
import unittest,sys,json,hashlib,zipfile
from datetime import datetime,timedelta,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_portal_data import classify,ROOT
class TemporalChecks(unittest.TestCase):
 def rows(self,minutes,counts=None,valid=None):
  base=datetime(2025,1,1,tzinfo=timezone.utc)
  return [{'time':base+timedelta(minutes=m),'timestamp':(base+timedelta(minutes=m)).isoformat(),'count':(counts or [4]*len(minutes))[i],'valid':(valid or [8]*len(minutes))[i]} for i,m in enumerate(minutes)]
 def test_confirmation_is_third_sample(self):
  rows=self.rows([0,10,20]); tier,onset,confirm,_=classify(rows)
  self.assertEqual((tier,onset,confirm),(1,rows[0]['timestamp'],rows[2]['timestamp']))
 def test_minute_or_hourly_rows_do_not_prove_persistence(self):
  for stamps in [[0,1,2],[0,60,120]]: self.assertEqual(classify(self.rows(stamps))[0],3)
 def test_missing_station_breaks_run(self): self.assertEqual(classify(self.rows([0,10,20],valid=[8,7,8]))[0],3)
 def test_pattern_requires_two_lull_samples(self):
  self.assertEqual(classify(self.rows([0,10,20,30],[4,0,0,4]))[0],2)
  self.assertEqual(classify(self.rows([0,10,20],[4,0,4]))[0],3)
 def test_gap_breaks_pattern(self): self.assertEqual(classify(self.rows([0,10,20,50],[4,0,0,4]))[0],3)
 def test_all_raw_archives_match_hash_manifest(self):
  manifest=json.loads((ROOT/'website/data/provenance.json').read_text())
  for e in manifest['events']:
   with zipfile.ZipFile(ROOT/f"website/downloads/{e['id']}-raw.zip") as archive:
    self.assertEqual(len(archive.namelist()),len(e['sourceFiles']))
    for f in e['sourceFiles']: self.assertEqual(hashlib.sha256(archive.read(f['path'])).hexdigest(),f['sha256'])
 def test_summary_and_detail_agree(self):
  summary=json.loads((ROOT/'website/data/summary.json').read_text())
  self.assertEqual(len(summary['events']),11)
  for e in summary['events']:
   detail=json.loads((ROOT/f"website/data/events-v2/{e['metadata']['id']}.json").read_text())
   self.assertEqual(detail['tier'],e['tier'])
   if not e['quality']['completeNetworkSamples']:self.assertEqual(e['tier'],0)
if __name__=='__main__':unittest.main()
