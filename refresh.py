"""Refresh authorized HTTPS JSON/CSV feeds. Missing feeds are not fabricated."""
import csv, datetime as dt, io, json, os
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen
ROOT=Path(__file__).parent
TODAY=dt.datetime.now(dt.timezone.utc).date()
def fetch(url,token):
    parsed=urlparse(url)
    if parsed.scheme!="https" or not parsed.netloc: raise ValueError("HTTPS URL required")
    headers={"User-Agent":"2JUICY-Radar/0.2 (authorized feed client)","Accept":"application/json,text/csv"}
    if token: headers["Authorization"]="Bearer "+token
    with urlopen(Request(url,headers=headers),timeout=25) as response:
        ctype=response.headers.get("Content-Type","")
        raw=response.read(3000001)
    if len(raw)>3000000: raise ValueError("Feed too large")
    body=raw.decode("utf-8-sig")
    if "csv" in ctype or parsed.path.lower().endswith(".csv"): return list(csv.DictReader(io.StringIO(body)))
    result=json.loads(body)
    return result.get("tracks",result.get("data")) if isinstance(result,dict) else result
def previous(key,days):
    directory=ROOT/"history"/key
    target=(TODAY-dt.timedelta(days=days)).isoformat()
    if not directory.exists(): return None
    candidates=sorted(p for p in directory.glob("????-??-??.json") if p.stem<=target)
    if not candidates:return None
    rows=json.loads(candidates[-1].read_text())["tracks"]
    return {str(t.get("track_id") or (t["artist"]+"|"+t["title"]).casefold()):t["rank"] for t in rows}
def run():
    updated=0
    for key in ("tiktok","dubstep","house","global"):
        url=os.getenv(f"RADAR_{key.upper()}_URL","").strip()
        if not url:
            print(f"{key}: not connected");continue
        try:
            rows=fetch(url,os.getenv(f"RADAR_{key.upper()}_TOKEN"))
            if not isinstance(rows,list) or not rows:raise ValueError("No track list")
            clean=[]; ranks=set()
            for i,row in enumerate(rows,1):
                if not isinstance(row,dict):raise ValueError("Track is not an object")
                title=str(row.get("title","")).strip();artist=str(row.get("artist","")).strip()
                rank=int(row.get("rank") or i)
                if not title or not artist or rank<1 or rank in ranks:raise ValueError("Invalid title/artist/rank")
                ranks.add(rank)
                item={"rank":rank,"title":title,"artist":artist}
                for field in ("track_id","preview_url","bpm","fit_score","points_14d"):
                    if row.get(field) is not None:item[field]=row[field]
                clean.append(item)
            clean.sort(key=lambda x:x["rank"])
            for days in (7,30):
                old=previous(key,days)
                if old is None:continue
                for t in clean:
                    ident=str(t.get("track_id") or (t["artist"]+"|"+t["title"]).casefold())
                    if ident in old:t[f"rank_change_{days}d"]=old[ident]-t["rank"]
            result={"source":urlparse(url).hostname,"captured_at":dt.datetime.now(dt.timezone.utc).isoformat(),"chart_type":"Source-provided ranking (verify chart methodology)","tracks":clean}
            archive=ROOT/"history"/key;archive.mkdir(parents=True,exist_ok=True)
            (archive/f"{TODAY.isoformat()}.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
            out=ROOT/"data";out.mkdir(exist_ok=True)
            (out/f"{key}.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
            print(f"{key}: {len(clean)} tracks saved");updated+=1
        except Exception as exc:print(f"{key}: {type(exc).__name__}: {exc}; previous snapshot retained")
    print(f"Updated {updated}/4 feeds")
if __name__=="__main__":run()
