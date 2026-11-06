#!/usr/bin/env python3
import importlib.util
import json
import time

SCRIPT = "/Volumes/wd/ai-learn/tmp/957685878-月球大叔/yueqiu_dashu_extract_worker2.py"
TARGET = "7539380141366349099"
spec = importlib.util.spec_from_file_location("extract", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

for attempt in range(100):
    result = m.eval_js(r'''
(() => {
  document.querySelectorAll('video').forEach(v => {v.autoplay = false; v.pause()});
  const a = document.querySelector('a[href*="/video/7539380141366349099"]');
  if (a) {
    a.scrollIntoView({block: 'center'});
    a.click();
    return JSON.stringify({clicked: true, href: a.href});
  }
  const sc = document.querySelector('.route-scroll-container');
  if (sc) sc.scrollTop = sc.scrollHeight;
  return JSON.stringify({clicked: false,
    count: document.querySelectorAll('a[href*="/video/"],a[href*="/note/"]').length,
    height: sc ? sc.scrollHeight : 0});
})()
''')
    print(json.dumps(result, ensure_ascii=False), flush=True)
    if result.get("clicked"):
        break
    time.sleep(1)
else:
    raise RuntimeError(f"target not found: {TARGET}")

time.sleep(2)
state = m.state()
print("OPENED " + json.dumps(state, ensure_ascii=False), flush=True)
if state.get("id") != TARGET or "月球大叔" not in state.get("author", ""):
    raise RuntimeError(f"wrong modal: {state}")
