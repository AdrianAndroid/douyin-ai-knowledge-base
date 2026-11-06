#!/usr/bin/env python3
import datetime as dt
import json
import subprocess
from pathlib import Path

BATCH = Path(__file__).resolve().parent
PLAN = BATCH / "后续45位作者提取计划.json"
STATUS = BATCH / "后续45位顺序执行状态.json"


def write_json(path, data):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def write_status(index, rows):
    current = rows[index - 1] if 0 < index <= len(rows) else None
    write_json(STATUS, {
        "current_index": index,
        "total_authors": len(rows),
        "current_author": current.get("author") if current else None,
        "authors": rows,
    })


def main():
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    rows = plan["authors"]
    for index, row in enumerate(rows, 1):
        if row.get("status") in {"completed", "skipped"}:
            continue
        if row.get("status") not in {"ready", "needs_retry"}:
            write_status(index, rows)
            print(f"STOP_UNVERIFIED {index}/45 {row['author']} status={row.get('status')} error={row.get('error', '')}", flush=True)
            raise SystemExit(3)
        tmp = Path(row["tmp"])
        row["status"] = "running"
        row["started_at"] = dt.datetime.now().isoformat(timespec="seconds")
        write_json(PLAN, plan)
        write_status(index, rows)
        print(f"START {index}/45 {row['author']} works={row['profile_work_count']}", flush=True)
        with (tmp / "提取日志.txt").open("a", encoding="utf-8") as log:
            cp = subprocess.run(["python3", "-I", "-u", str(tmp / "extract_author.py")],
                                stdout=log, stderr=subprocess.STDOUT)
        row["exit_code"] = cp.returncode
        row["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
        row["status"] = "completed" if cp.returncode == 0 else "needs_retry"
        if (tmp / "提取状态.json").exists():
            state = json.loads((tmp / "提取状态.json").read_text(encoding="utf-8"))
            row["saved"] = state.get("counts", {}).get("saved", 0)
            row["no_ai"] = state.get("counts", {}).get("no_ai", 0)
            row["pending"] = state.get("pending")
        write_json(PLAN, plan)
        write_status(index, rows)
        print(f"END {row['author']} code={cp.returncode}", flush=True)
        if cp.returncode:
            print("STOPPED_FOR_RETRY", flush=True)
            raise SystemExit(cp.returncode)
    write_status(0, rows)
    print("ALL_VERIFIED_AUTHORS_COMPLETED", flush=True)


if __name__ == "__main__":
    main()
