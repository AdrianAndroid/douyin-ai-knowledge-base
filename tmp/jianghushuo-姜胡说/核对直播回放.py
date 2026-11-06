#!/usr/bin/env python3
import importlib.util
import json
import time

SCRIPT = "/Volumes/wd/ai-learn/tmp/jianghushuo-姜胡说/jiang_hushuo_extract.py"
spec = importlib.util.spec_from_file_location("extract", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.PAGE = "0b125026-0675-433a-bebc-027332f7429f"

m.eval_js(r'''
document.querySelectorAll('video').forEach(v => {v.autoplay = false; v.pause()});
window.__vsIds = new Set();
window.__vsCollect = () => {
  document.querySelectorAll('a[href*="/vsdetail/"]').forEach(a => {
    const match = a.href.match(/vsdetail\/(\d+)/);
    if (match) window.__vsIds.add(match[1]);
  });
  return window.__vsIds.size;
};
'ready'
''')

last = (-1, -1)
stable = 0
for i in range(80):
    s = m.eval_js(r'''
(() => {
  document.querySelectorAll('video').forEach(v => v.pause());
  const sc = document.querySelector('.route-scroll-container');
  if (sc) sc.scrollTop = sc.scrollHeight;
  return JSON.stringify({count: window.__vsCollect(),
    height: sc ? sc.scrollHeight : 0});
})()
''')
    current = (s.get("count", 0), s.get("height", 0))
    stable = stable + 1 if current == last else 0
    last = current
    print(f"scroll={i+1} count={current[0]} height={current[1]} stable={stable}", flush=True)
    if stable >= 8:
        break
    time.sleep(1)

ids = m.eval_js("JSON.stringify(Array.from(window.__vsIds))")
(m.TMP_OUT / "直播回放ID.json").write_text(
    json.dumps(ids, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"LIVE_REPLAY_COUNT {len(ids)}", flush=True)
