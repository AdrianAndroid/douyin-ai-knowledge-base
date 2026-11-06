#!/usr/bin/env python3
import collections
import datetime as dt
import json
import os
import re
from pathlib import Path

BATCH = Path(__file__).resolve().parent
PLAN = json.loads((BATCH / "后续45位作者提取计划.json").read_text(encoding="utf-8"))
FAILURE_MARKERS = (
    "很抱歉，我还在努力学习中",
    "抱歉，这个问题未找到相关结果",
    "抱歉，您的问题我无法识别",
)


def write_json(path, data):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


authors = []
all_file_ids = collections.defaultdict(list)
for row in PLAN["authors"]:
    if row.get("status") != "completed":
        continue
    author = row["author"]
    douyin_id = row["douyin_id"]
    tmp = Path(row["tmp"])
    output = Path(row["output"])
    listed = json.loads((tmp / "主页作品ID.json").read_text(encoding="utf-8"))
    if len(listed) != len(set(listed)):
        raise RuntimeError(f"duplicate IDs in profile list: {author}")
    progress = {}
    for line in (tmp / "提取进度.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            item = json.loads(line)
            if item.get("id"):
                progress[item["id"]] = item
    no_ai_ids = {
        video_id for video_id, item in progress.items()
        if item.get("status") == "no_ai"
    }
    files = sorted(output.glob("*.md"))
    file_ids = []
    invalid = []
    for path in files:
        match = re.match(r"^(\d{8})-(\d{15,25})-(.+)\.md$", path.name)
        if not match:
            invalid.append({"file": path.name, "error": "invalid filename"})
            continue
        date_compact, video_id, _ = match.groups()
        file_ids.append(video_id)
        all_file_ids[video_id].append({
            "author": author,
            "file": str(path),
            "in_own_profile_list": video_id in set(listed),
        })
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            invalid.append({"file": path.name, "error": f"UTF-8: {exc}"})
            continue
        lines = text.splitlines()
        checks = {
            "author_header": [line for line in lines if line.startswith("> 作者：")] == [f"> 作者：{author}"],
            "douyin_header": [line for line in lines if line.startswith("> 抖音号：")] == [f"> 抖音号：{douyin_id}"],
            "matching_id": f"> 作品ID：{video_id}" in lines,
            "matching_date": f"> 创作时间：{date_compact[:4]}-{date_compact[4:6]}-{date_compact[6:]}" in lines,
            "ai_marker": "以上内容由AI生成，仅供参考" in text,
            "substantial_text": len(text) > 100,
            "no_failure_prompt": not any(marker in text for marker in FAILURE_MARKERS),
        }
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            invalid.append({"file": path.name, "error": ",".join(failed)})
    duplicates = sorted(
        video_id for video_id, count in collections.Counter(file_ids).items()
        if count > 1
    )
    file_id_set = set(file_ids)
    listed_set = set(listed)
    missing = sorted(listed_set - file_id_set - no_ai_ids)
    extra_files = sorted(file_id_set - listed_set)
    extra_no_ai = sorted(no_ai_ids - listed_set)
    result = {
        "author": author,
        "douyin_id": douyin_id,
        "profile_displayed_works": row["profile_work_count"],
        "actual_listed_works": len(listed),
        "markdown_files": len(files),
        "unique_file_ids": len(file_id_set),
        "no_ai": len(no_ai_ids),
        "pending": len(missing),
        "duplicate_ids": duplicates,
        "invalid_files": invalid,
        "listed_pending": missing,
        "files_not_in_profile_list": extra_files,
        "no_ai_not_in_profile_list": extra_no_ai,
        "passed": not any((duplicates, invalid, missing, extra_files, extra_no_ai)),
    }
    authors.append(result)
    write_json(tmp / "独立复核.json", result)

cross_author_same_works = {
    video_id: locations for video_id, locations in all_file_ids.items()
    if len({location["author"] for location in locations}) > 1
}
report = {
    "validated_at": dt.datetime.now().isoformat(timespec="seconds"),
    "scope": "后续45位队列中当前状态为completed的作者；running、ready、needs_retry不计入",
    "completed_authors": len(authors),
    "profile_displayed_works_total": sum(row["profile_displayed_works"] for row in authors),
    "actual_listed_works_total": sum(row["actual_listed_works"] for row in authors),
    "markdown_files_total": sum(row["markdown_files"] for row in authors),
    "no_ai_total": sum(row["no_ai"] for row in authors),
    "pending_total": sum(row["pending"] for row in authors),
    "invalid_files_total": sum(len(row["invalid_files"]) for row in authors),
    "duplicate_files_total": sum(len(row["duplicate_ids"]) for row in authors),
    "cross_author_same_works": cross_author_same_works,
    "cross_author_note": "跨账号相同作品单独报告；任一文件不在对应作者主页清单时，该作者校验不会通过。",
    "all_passed": bool(authors) and all(row["passed"] for row in authors),
    "authors": authors,
}
write_json(BATCH / "后续45位已完成作者独立总校验.json", report)
print(json.dumps({key: value for key, value in report.items() if key != "authors"}, ensure_ascii=False, indent=2))
