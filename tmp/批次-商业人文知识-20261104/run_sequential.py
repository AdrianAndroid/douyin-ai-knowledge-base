#!/usr/bin/env python3
import datetime as dt
import json
import subprocess
from pathlib import Path

BATCH = Path(__file__).resolve().parent
QUEUE = BATCH / "顺序执行清单.json"
STATUS = BATCH / "顺序执行状态.json"


def write_status(data):
    temp = STATUS.with_suffix(".json.tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(STATUS)


def main():
    rows = json.loads(QUEUE.read_text(encoding="utf-8"))
    for index, row in enumerate(rows, 1):
        if row.get("status") in {"completed", "skipped"}:
            continue
        tmp = Path(row["tmp"])
        row["status"] = "running"
        row["started_at"] = dt.datetime.now().isoformat(timespec="seconds")
        write_status({"current_index": index, "total_authors": len(rows),
                      "current_author": row["author"], "authors": rows})
        print(f"START {index}/{len(rows)} {row['author']} works={row['profile_work_count']}", flush=True)
        with (tmp / "提取日志.txt").open("a", encoding="utf-8") as log:
            cp = subprocess.run(["python3", "-I", "-u", str(tmp / "extract_author.py")],
                                stdout=log, stderr=subprocess.STDOUT)
        row["exit_code"] = cp.returncode
        row["finished_at"] = dt.datetime.now().isoformat(timespec="seconds")
        row["status"] = "completed" if cp.returncode == 0 else "needs_retry"
        write_status({"current_index": index, "total_authors": len(rows),
                      "current_author": row["author"], "authors": rows})
        print(f"END {row['author']} code={cp.returncode}", flush=True)
        QUEUE.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
        if cp.returncode:
            print("STOPPED_FOR_RETRY", flush=True)
            raise SystemExit(cp.returncode)
    print("ALL_AUTHORS_COMPLETED", flush=True)


if __name__ == "__main__":
    main()
