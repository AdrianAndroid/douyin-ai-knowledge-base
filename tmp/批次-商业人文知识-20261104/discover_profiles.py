#!/usr/bin/env python3
import datetime as dt
import json
import re
import subprocess
import time
from pathlib import Path
from urllib.parse import quote

BATCH = Path(__file__).resolve().parent
ROWS_FILE = BATCH / "批次作者清单.json"
PAGE = "eaf754f4-67ce-4969-ba63-93fc2f976356"


def orca(args, timeout=60):
    cp = subprocess.run(["orca", *args], text=True, capture_output=True, timeout=timeout)
    if cp.returncode:
        raise RuntimeError((cp.stderr or cp.stdout).strip())
    data = json.loads(cp.stdout)
    if not data.get("ok"):
        raise RuntimeError(json.dumps(data, ensure_ascii=False))
    return data.get("result", {})


def eval_js(expression, timeout=60):
    value = orca(["eval", "--page", PAGE, "--expression", expression, "--json"], timeout).get("result")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def navigate(url):
    return eval_js(f"location.assign({json.dumps(url, ensure_ascii=False)}); 'navigating'")


def wait_state(kind, author, timeout=45):
    last = {}
    for _ in range(timeout):
        time.sleep(1)
        try:
            if kind == "search":
                last = eval_js(r'''
JSON.stringify({url:location.href,text:(document.body?.innerText||'').slice(0,12000),users:Array.from(document.querySelectorAll('a[href*="/user/"]')).map(a=>({href:a.href,text:(a.innerText||'').trim()})).filter(x=>x.text)})
''')
                if last.get("users"):
                    return last
            else:
                last = eval_js(r'''
JSON.stringify({url:location.href,name:(document.querySelector('h1')?.innerText||'').trim(),text:(document.body?.innerText||'').slice(0,7000),followed:Array.from(document.querySelectorAll('button')).some(b=>b.innerText.trim()==='已关注')})
''')
                if last.get("name"):
                    return last
        except Exception as exc:
            last = {"error": str(exc)}
    return last


def norm(text):
    return re.sub(r"\s+", "", text or "").casefold()


def write_json(path, data):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def main():
    rows = json.loads(ROWS_FILE.read_text(encoding="utf-8"))
    results = []
    for row in rows:
        author = row["author"]
        expected_id = row["douyin_id"]
        tmp = Path(row["tmp"])
        print(f"SEARCH {author}", flush=True)
        try:
            navigate("https://www.douyin.com/search/" + quote(author) + "?type=user")
            time.sleep(6)
            search = wait_state("search", author)
            candidates = []
            for user in search.get("users", []):
                match = re.search(r"/user/([^/?]+)", user.get("href", ""))
                if not match:
                    continue
                lines = [x.strip() for x in user.get("text", "").splitlines() if x.strip()]
                if not lines:
                    continue
                candidate = {
                    "name": lines[0], "sec_uid": match.group(1), "text": user.get("text", ""),
                    "followed": "已关注" in lines,
                    "name_match": norm(lines[0]) == norm(author),
                    "id_match": expected_id == "未知" or expected_id in user.get("text", ""),
                }
                if candidate["name_match"] or candidate["id_match"]:
                    candidates.append(candidate)
            eligible = [x for x in candidates if x["followed"] and x["name_match"] and x["id_match"]]
            write_json(tmp / "搜索账号核对.json", {
                "author": author, "expected_douyin_id": expected_id,
                "searched_at": dt.datetime.now().isoformat(timespec="seconds"),
                "eligible_count": len(eligible), "candidates": candidates,
            })
            if len(eligible) != 1:
                raise RuntimeError(f"followed exact account count={len(eligible)}")
            chosen = eligible[0]
            profile = "https://www.douyin.com/user/" + chosen["sec_uid"] + "?from_tab_name=main"
            navigate(profile)
            time.sleep(5)
            state = wait_state("profile", author)
            body = state.get("text", "")
            id_match = re.search(r"抖音号[：:]\s*([^\n\s]+)", body)
            actual_id = id_match.group(1) if id_match else ""
            work_match = re.search(r"(?:^|\n)作品\s*\n(\d+)(?:\n|$)", body)
            works = int(work_match.group(1)) if work_match else 0
            verified = (norm(state.get("name")) == norm(author) and state.get("followed")
                        and actual_id and (expected_id == "未知" or actual_id == expected_id))
            account = {
                "author": author, "profile_name": state.get("name"), "douyin_id": actual_id,
                "expected_douyin_id": expected_id, "sec_uid": chosen["sec_uid"],
                "profile_work_count": works, "followed": bool(state.get("followed")),
                "verified": bool(verified), "profile_url": profile,
                "verified_at": dt.datetime.now().isoformat(timespec="seconds"),
            }
            write_json(tmp / "账号核对.json", account)
            result = {**row, **account, "status": "ready" if verified else "review"}
            if not verified:
                result["error"] = "profile verification mismatch"
            print(f"PROFILE {author} id={actual_id} works={works} verified={verified}", flush=True)
        except Exception as exc:
            result = {**row, "status": "review", "error": str(exc)}
            print(f"REVIEW {author} {exc}", flush=True)
        results.append(result)
        write_json(BATCH / "主页核对结果.json", results)
    print("DISCOVERY_DONE", flush=True)


if __name__ == "__main__":
    main()
