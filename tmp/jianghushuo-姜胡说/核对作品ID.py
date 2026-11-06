#!/usr/bin/env python3
import importlib.util
import json
import time

SCRIPT = "/Volumes/wd/ai-learn/tmp/jianghushuo-姜胡说/jiang_hushuo_extract.py"
spec = importlib.util.spec_from_file_location("extract", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

SCROLL_JS = r'''
(() => {
  const sc = document.querySelector('.route-scroll-container');
  if (sc) sc.scrollTop = sc.scrollHeight;
  return JSON.stringify({count: window.__jhCollect(),
    height: sc ? sc.scrollHeight : 0, top: sc ? sc.scrollTop : 0});
})()
'''

stable = 0
last = (-1, -1)
for i in range(120):
    s = m.eval_js(SCROLL_JS)
    current = (s.get("count", 0), s.get("height", 0))
    stable = stable + 1 if current == last else 0
    last = current
    print(f"scroll={i+1} count={current[0]} height={current[1]} stable={stable}", flush=True)
    if (current[0] >= 720 and stable >= 3) or stable >= 12:
        break
    time.sleep(1.2)

ids = m.eval_js("JSON.stringify(Array.from(window.__jhAllIds))")
(m.TMP_OUT / "主页作品ID.json").write_text(
    json.dumps(ids, ensure_ascii=False, indent=2), encoding="utf-8")

latest = {}
if m.PROGRESS.exists():
    for line in m.PROGRESS.read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            latest[row["id"]] = row
completed = {video_id for video_id, row in latest.items()
             if row.get("status") in {"saved", "no_ai"}}
missing = [video_id for video_id in ids if video_id not in completed]
(m.TMP_OUT / "待补提作品.json").write_text(
    json.dumps(missing, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"TOTAL profile={len(ids)} completed={len(completed & set(ids))} pending={len(missing)}", flush=True)
print("PENDING " + " ".join(missing), flush=True)
