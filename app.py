import json
from pathlib import Path
from urllib.parse import quote_plus
import streamlit as st
import pandas as pd

ROOT = Path(__file__).parent
st.set_page_config(page_title="2JUICY Trend Radar", page_icon="💦", layout="wide")
st.title("💦 2JUICY Trend Radar")
st.caption("Four discovery feeds · Dated snapshots · No invented rankings")
charts = [
    ("TikTok • Vibe Fit", "tiktok", "https://ads.tiktok.com/business/creativecenter/inspiration/popular/music/pc/en"),
    ("Beatport • Dubstep", "dubstep", "https://www.beatport.com/genre/dubstep/18/top-100"),
    ("Beatport • House", "house", "https://www.beatport.com/genre/house/5/top-100"),
    ("Beatport • Global Top 100", "global", "https://www.beatport.com/top-100"),
]
for tab, (name, key, url) in zip(st.tabs([x[0] for x in charts]), charts):
    with tab:
        path = ROOT / "data" / f"{key}.json"
        if not path.exists():
            st.warning("No verified automated snapshot available. Data source not connected.")
            st.link_button("Open source chart", url)
            continue
        try:
            payload = json.loads(path.read_text())
            rows = payload.get("tracks", [])
            st.caption(f"Source: {payload.get('source','unknown')} · Updated: {payload.get('captured_at','unknown')} · {payload.get('chart_type','')}")
            if not rows:
                st.warning("No tracks in this snapshot.")
                continue
            df = pd.DataFrame(rows)
            query = st.text_input("Search tracks or artists", key=f"q_{key}")
            if query:
                df = df[df.astype(str).apply(lambda col: col.str.contains(query, case=False, regex=False)).any(axis=1)]
            for _, track in df.iterrows():
                artist, title = str(track.get("artist", "")), str(track.get("title", ""))
                with st.container(border=True):
                    left, middle, right = st.columns([1, 7, 2])
                    left.markdown(f"**#{track.get('rank','—')}**")
                    middle.markdown(f"**{title}**  \\n{artist}")
                    preview = track.get("preview_url") or "https://www.youtube.com/results?search_query=" + quote_plus(artist + " " + title)
                    right.link_button("▶ Listen" if track.get("preview_url") else "▶ Search audio", preview)
                    metrics = [f"{label}: {track[field]}" for label, field in [("7d rank Δ", "rank_change_7d"), ("30d rank Δ", "rank_change_30d"), ("BPM", "bpm"), ("Fit", "fit_score"), ("14d points", "points_14d")] if field in track and pd.notna(track[field])]
                    if metrics:
                        st.caption(" · ".join(metrics))
            st.download_button("Export CSV", df.to_csv(index=False).encode(), file_name=f"2juicy_{key}.csv")
        except Exception as exc:
            st.error(f"Snapshot could not be displayed: {exc}")
st.divider()
st.info("Daily automation requires authorized machine-readable feeds. YouTube search links are not verified recordings. BeatStats points must not be presented as Beatport daily sales ranks.")
