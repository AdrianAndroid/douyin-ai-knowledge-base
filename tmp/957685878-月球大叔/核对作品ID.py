#!/usr/bin/env python3
import importlib.util
import json
import os
import time

SCRIPT = "/Volumes/wd/ai-learn/tmp/957685878-月球大叔/yueqiu_dashu_extract.py"
spec = importlib.util.spec_from_file_location("extract", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.PAGE = os.environ.get("ORCA_PAGE", m.PAGE)

INIT_JS = r'''
document.querySelectorAll('video').forEach(v => { v.autoplay = false; v.pause(); });
window.__yqAllIds = new Set();
window.__yqCollect = () => {
  const lists = Array.from(document.querySelectorAll('.route-scroll-container ul'))
    .filter(u => u.querySelector('a[href*="/video/"],a[href*="/note/"]'))
    .sort((a, b) =>
      b.querySelectorAll('a[href*="/video/"],a[href*="/note/"]').length -
      a.querySelectorAll('a[href*="/video/"],a[href*="/note/"]').length);
  const scope = lists.length ? [lists[0]] : [];
  scope.forEach(root => {
    root.querySelectorAll('a[href*="/video/"],a[href*="/note/"]').forEach(a => {
      const match = a.href.match(/\/(?:video|note)\/(\d+)/);
      if (match) window.__yqAllIds.add(match[1]);
    });
  });
  return window.__yqAllIds.size;
};
'ready'
'''

SCROLL_JS = r'''
(() => {
  document.querySelectorAll('video').forEach(v => v.pause());
  const sc = document.querySelector('.route-scroll-container');
  if (sc) sc.scrollTop = sc.scrollHeight;
  return JSON.stringify({count: window.__yqCollect(),
    height: sc ? sc.scrollHeight : 0, top: sc ? sc.scrollTop : 0});
})()
'''

profile = m.eval_js(r'''
JSON.stringify({
  url: location.href,
  text: (document.querySelector('h1')?.innerText || '').trim(),
  hasDouyinId: document.body.innerText.includes('957685878')
})
''')
if profile.get("text") != "月球大叔" or not profile.get("hasDouyinId"):
    raise RuntimeError(f"not on the expected author profile: {profile}")

m.eval_js(INIT_JS)
stable = 0
last = (-1, -1)
for i in range(160):
    s = m.eval_js(SCROLL_JS)
    current = (s.get("count", 0), s.get("height", 0))
    stable = stable + 1 if current == last else 0
    last = current
    print(f"scroll={i+1} count={current[0]} height={current[1]} stable={stable}", flush=True)
    if (current[0] >= 233 and stable >= 3) or stable >= 12:
        break
    time.sleep(1.2)

ids = m.eval_js("JSON.stringify(Array.from(window.__yqAllIds))")
(m.TMP_OUT / "主页作品ID.json").write_text(
    json.dumps(ids, ensure_ascii=False, indent=2), encoding="utf-8")

latest = {}
if m.PROGRESS.exists():
    for line in m.PROGRESS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            latest[row["id"]] = row
        except (json.JSONDecodeError, KeyError):
            pass
completed = {video_id for video_id, row in latest.items()
             if row.get("status") in {"saved", "no_ai"}}
missing = [video_id for video_id in ids if video_id not in completed]
(m.TMP_OUT / "待补提作品.json").write_text(
    json.dumps(missing, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"TOTAL profile={len(ids)} completed={len(completed & set(ids))} pending={len(missing)}", flush=True)
print("PENDING " + " ".join(missing), flush=True)
