#!/usr/bin/env python3
import importlib.util
import json
import sys
import time

SCRIPT = "/Volumes/wd/ai-learn/tmp/jianghushuo-姜胡说/jiang_hushuo_extract.py"
PROFILE = ("https://www.douyin.com/user/MS4wLjABAAAAxaSHyjKQyfWHKjIS1mYbpxxEQZpT8ogl_eyks2M_Twc"
           "?from_tab_name=main&modal_id=")
spec = importlib.util.spec_from_file_location("extract", SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def load_rows():
    rows = []
    for line in m.PROGRESS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            pass
    return rows


def pending_ids(all_ids):
    latest = {row["id"]: row for row in load_rows()}
    return [video_id for video_id in all_ids
            if latest.get(video_id, {}).get("status") not in {"saved", "no_ai"}]


all_ids = json.loads((m.TMP_OUT / "主页作品ID.json").read_text(encoding="utf-8"))
pending = pending_ids(all_ids)
(m.TMP_OUT / "待补提作品.json").write_text(
    json.dumps(pending, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"RETRY_START pending={len(pending)}", flush=True)

for video_id in pending:
    for attempt in range(2):
        print(f"RETRY id={video_id} attempt={attempt+1}", flush=True)
        try:
            m.orca(["goto", "--page", m.PAGE, "--url", PROFILE + video_id, "--json"])
            m.orca(["wait", "--page", m.PAGE, "--load", "load", "--json"])
            time.sleep(1.5)
            sys.argv = [SCRIPT, "--limit", "1"]
            m.main()
        except Exception as exc:
            print(f"RETRY_EXCEPTION id={video_id} {exc}", flush=True)
        latest = {row["id"]: row for row in load_rows()}
        status = latest.get(video_id, {}).get("status")
        if status in {"saved", "no_ai"}:
            print(f"RETRY_OK id={video_id} status={status}", flush=True)
            break
        time.sleep(2)
    else:
        print(f"RETRY_FAILED id={video_id}", flush=True)

remaining = pending_ids(all_ids)
(m.TMP_OUT / "待补提作品.json").write_text(
    json.dumps(remaining, ensure_ascii=False, indent=2), encoding="utf-8")
rows = load_rows()
m.write_summary(rows, False, f"主页视频补提完成，剩余 {len(remaining)} 个待处理")
print(f"RETRY_DONE remaining={len(remaining)} ids={' '.join(remaining)}", flush=True)
