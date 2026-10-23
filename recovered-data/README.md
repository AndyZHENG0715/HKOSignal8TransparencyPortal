# Official historical observation recovery

Downloaded via the DATA.GOV.HK historical archive API documented at https://data.gov.hk/en/help/api-spec . Each event subfolder retains unmodified English CSV bytes for archive versions recorded on requested dates, plus an API response and SHA-256 manifest. Original repository files were not changed.

The archive version time is a retrieval/revision time, not the embedded observation timestamp. For example 20220824-2009 contains 202208242000 observations. Use embedded Date time for timelines. Identical or conflicting observation duplicates can exist; never infer a new observation from filenames. Source data are provisional HKO regional observations.

Saola contains malformed archive CSV(s), named in its manifest; the consumer must skip invalid rows/files explicitly and report data gaps instead of synthesizing values. Files span named archive dates; a first archive file can contain observations from the preceding day. The parent coordinator owns filtering, integration, and duplicate conflict policy.

Ragasa recovery extended to archive dates 2025-09-23 through 2025-09-24; its combined manifest replaces the earlier September-24-only manifest. Both warning-envelope endpoints are included.
