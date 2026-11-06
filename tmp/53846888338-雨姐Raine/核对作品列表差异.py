#!/usr/bin/env python3
import importlib.util
import json
import time
from pathlib import Path

TMP = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("extract", TMP / "extract_author.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
m.PAGE = "3eb064bf-b8d8-43eb-98cf-a355818f8fb6"

last = (-1, -1)
stable = 0
for index in range(100):
    time.sleep(1)
    state = m.eval_js(r'''
(() => {
  document.querySelectorAll('video').forEach(v => {v.autoplay = false; v.pause()});
  const sc = document.querySelector('.route-scroll-container');
  if (sc) sc.scrollTop = sc.scrollHeight;
  const count = document.querySelectorAll(
    '.route-scroll-container ul a[href*="/video/"],.route-scroll-container ul a[href*="/note/"]'
  ).length;
  return JSON.stringify({count, height: sc ? sc.scrollHeight : 0});
})()
''')
    current = (state.get("count", 0), state.get("height", 0))
    stable = stable + 1 if current == last else 0
    last = current
    print(f"scroll={index+1} count={current[0]} stable={stable}", flush=True)
    if stable >= 12:
        break

result = m.eval_js(r'''
JSON.stringify({
  lists: Array.from(document.querySelectorAll('.route-scroll-container ul')).map((u, i) => ({
    index: i,
    ids: Array.from(new Set(Array.from(u.querySelectorAll('a[href*="/video/"],a[href*="/note/"]'))
      .map(a => (a.href.match(/\/(?:video|note)\/(\d+)/) || [])[1]).filter(Boolean)))
  })).filter(x => x.ids.length),
  allIds: Array.from(new Set(Array.from(document.querySelectorAll(
    '.route-scroll-container a[href*="/video/"],.route-scroll-container a[href*="/note/"]'
  )).map(a => (a.href.match(/\/(?:video|note)\/(\d+)/) || [])[1]).filter(Boolean)))
})
''')
(TMP / "主页列表容器核对.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"list_counts": [len(x["ids"]) for x in result["lists"]],
                  "all_ids": len(result["allIds"])}, ensure_ascii=False), flush=True)
