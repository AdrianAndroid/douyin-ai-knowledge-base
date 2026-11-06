#!/usr/bin/env python3
import datetime as dt
import json
import re
from collections import Counter
from pathlib import Path

OUT = Path("/Volumes/wd/ai-learn/抖音关注/957685878-月球大叔")
TMP = Path("/Volumes/wd/ai-learn/tmp/957685878-月球大叔")
PROGRESS = TMP / "提取进度.jsonl"

latest = {}
bad_progress_lines = 0
if PROGRESS.exists():
    for line in PROGRESS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
            latest[row["id"]] = row
        except (json.JSONDecodeError, KeyError):
            bad_progress_lines += 1

files = sorted(OUT.glob("*.md"))
ids = []
invalid = []
for path in files:
    match = re.match(r"^(\d{8})-(\d{15,25})-(.+)\.md$", path.name)
    if not match:
        invalid.append({"file": path.name, "error": "invalid filename"})
        continue
    date_compact, video_id, _ = match.groups()
    text = path.read_text(encoding="utf-8")
    ids.append(video_id)
    checks = {
        "author": "> 作者：月球大叔" in text,
        "douyin_id": "> 抖音号：957685878" in text,
        "matching_id": f"> 作品ID：{video_id}" in text,
        "date": f"> 创作时间：{date_compact[:4]}-{date_compact[4:6]}-{date_compact[6:]}" in text,
        "ai_marker": "以上内容由AI生成，仅供参考" in text,
        "substantial_text": len(text) > 100,
    }
    failed = [name for name, ok in checks.items() if not ok]
    if failed:
        invalid.append({"file": path.name, "error": ",".join(failed)})

duplicates = sorted(video_id for video_id, count in Counter(ids).items() if count > 1)
file_ids = set(ids)
saved_ids = {video_id for video_id, row in latest.items() if row.get("status") == "saved"}
no_ai_ids = {video_id for video_id, row in latest.items() if row.get("status") == "no_ai"}
error_ids = {video_id for video_id, row in latest.items() if row.get("status") == "error"}
profile_ids = []
profile_path = TMP / "主页作品ID.json"
if profile_path.exists():
    profile_ids = json.loads(profile_path.read_text(encoding="utf-8"))

report = {
    "author": "月球大叔",
    "douyin_id": "957685878",
    "validated_at": dt.datetime.now().isoformat(timespec="seconds"),
    "markdown_files": len(files),
    "unique_video_ids": len(file_ids),
    "duplicate_ids": duplicates,
    "invalid_files": invalid,
    "bad_progress_lines": bad_progress_lines,
    "progress": {
        "unique_items": len(latest),
        "saved": len(saved_ids),
        "no_ai": len(no_ai_ids),
        "error": len(error_ids),
        "saved_without_file": sorted(saved_ids - file_ids),
        "file_without_saved_progress": sorted(file_ids - saved_ids),
    },
    "profile": {
        "listed_items": len(profile_ids),
        "listed_saved": len(set(profile_ids) & file_ids),
        "listed_no_ai": len(set(profile_ids) & no_ai_ids),
        "listed_pending": sorted(set(profile_ids) - file_ids - no_ai_ids),
        "processed_not_in_profile_list": sorted((file_ids | no_ai_ids) - set(profile_ids)),
    },
}
(TMP / "文案校验.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)
if invalid or duplicates or saved_ids - file_ids:
    raise SystemExit(1)
