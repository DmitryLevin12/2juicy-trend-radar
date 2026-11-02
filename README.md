# 💦 2JUICY Trend Radar

Four tabs: TikTok Vibe Fit, Beatport Dubstep, Beatport House, Beatport Global Top 100.

## Dashboard
Deploy with Streamlit Community Cloud: https://share.streamlit.io/ . Choose this repository, branch `main`, entry point `app.py`. For a private repository, ensure Streamlit has GitHub authorization. Alternatively run `pip install -r requirements.txt && streamlit run app.py`.

## Daily automation
GitHub Actions workflow `.github/workflows/daily.yml` runs at 13:17 UTC daily and can also be run manually via Actions > Daily radar refresh > Run workflow. It requires **authorized machine-readable data feeds**. Add GitHub Actions repository secrets named `RADAR_TIKTOK_URL`, `RADAR_DUBSTEP_URL`, `RADAR_HOUSE_URL`, `RADAR_GLOBAL_URL` with permitted HTTPS JSON/CSV feed URLs. Optional corresponding `RADAR_<KEY>_TOKEN` secrets add bearer authentication. Never commit credentials.

JSON format: `[{"title":"Song","artist":"Artist","rank":1,"track_id":"stable-id","preview_url":"https://..."}]` or `{"tracks":[...]}`. CSV requires title,artist; optional rank,track_id,preview_url,bpm,fit_score,points_14d. Feed semantics must be verified before presenting charts as Beatport daily sales ranks.

Snapshots live in `data/<key>.json` and `history/<key>/<YYYY-MM-DD>.json`. Historical rank changes appear after at least 7 or 30 days of snapshots; no invented backfill. TikTok creation growth is **not** inferred from chart rank changes.

## Current status
Application and daily GitHub Action committed. No feeds have been authenticated/validated, and the hosted Streamlit app has not been deployed. An Action run without secrets reports disconnected feeds and saves no fake data. BeatStats 14-day points are not the same as Beatport daily Top 100. Verify terms and permission before automated collection.
