#!/usr/bin/env python3
import datetime as dt
import json
import os
import re
import subprocess
import time
from collections import Counter
from pathlib import Path

TMP = Path(__file__).resolve().parent
CONFIG = json.loads((TMP / "配置.json").read_text(encoding="utf-8"))
AUTHOR = CONFIG["author"]
DOUYIN_ID = CONFIG["douyin_id"]
SEC_UID = CONFIG["sec_uid"]
PAGE = CONFIG["page"]
EXPECTED_COUNT = CONFIG["profile_work_count"]
OUT = Path(CONFIG["output"])
PROFILE = f"https://www.douyin.com/user/{SEC_UID}?from_tab_name=main"
PROGRESS = TMP / "提取进度.jsonl"
SUMMARY = TMP / "提取状态.json"
IDS_FILE = TMP / "主页作品ID.json"
PENDING_FILE = TMP / "待补提作品.json"
CURRENT_YEAR = 2026

STATE_JS = r'''
(() => {
  window.__batchPause = true;
  if (!window.__batchPlayBlocker) {
    window.__batchPlayBlocker = e => {
      if (window.__batchPause && e.target instanceof HTMLVideoElement) {
        e.target.autoplay = false;
        e.target.pause();
      }
    };
    document.addEventListener('play', window.__batchPlayBlocker, true);
  }
  document.querySelectorAll('video').forEach(v => {v.autoplay = false; v.pause()});
  const id = (location.href.match(/[?&]modal_id=(\d+)/) || [])[1] || '';
  const out = {id, url: location.href, slide: false, author: '', title: '', date: '',
    tags: [], ai: '', hasAiButton: false, aiClicked: false, aiFailed: false,
    coauthorVerified: false,
    paused: Array.from(document.querySelectorAll('video')).every(v => v.paused)};
  if (!id) return JSON.stringify(out);
  const slide = document.querySelector('.sliderVideo.video_' + id);
  if (!slide) return JSON.stringify(out);
  out.slide = true;
  const slideLines = (slide.innerText || '').split('\n').map(t => t.trim());
  const coauthorIndex = slideLines.indexOf('2人共创');
  out.coauthorVerified = coauthorIndex >= 0 &&
    slideLines.slice(coauthorIndex + 1, coauthorIndex + 5).includes(__EXPECTED_AUTHOR__);
  const account = slide.querySelector('.account');
  out.author = account ? account.innerText.trim() : '';
  const titleEl = slide.querySelector('.video-info-detail .title');
  if (titleEl) {
    const first = titleEl.firstElementChild;
    out.title = ((first && first.innerText) || titleEl.innerText || '')
      .trim().split('\n')[0].trim();
    out.tags = Array.from(new Set(Array.from(titleEl.querySelectorAll('a'))
      .map(a => a.textContent.trim()).filter(t => t.startsWith('#'))));
  }
  const dm = out.author.match(
    /(?:20\d{2}年)?\d{1,2}月\d{1,2}日|昨天|今天|\d+(?:天|周|小时|分钟)前/
  );
  out.date = dm ? dm[0] : '';
  const buttons = Array.from(slide.querySelectorAll('[class*=ai-douyin-entry]')).filter(e => {
    const r = e.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight;
  });
  out.hasAiButton = buttons.length > 0;
  const candidates = Array.from(slide.querySelectorAll('div,section,article,p')).filter(e => {
    const r = e.getBoundingClientRect();
    const t = (e.innerText || '').trim();
    return r.width >= 150 && r.height > 0 && r.bottom > 0 && r.top < innerHeight &&
      t.includes('以上内容由AI生成');
  }).map(e => (e.innerText || '').trim()).filter(t => t.length > 20 &&
    !['抱歉，这个问题未找到相关结果', '抱歉，您的问题我无法识别'].some(f => t.includes(f)));
  candidates.sort((a, b) => a.length - b.length);
  if (candidates.length) out.ai = candidates[0];
  if (!out.ai) {
    const chapterCandidates = Array.from(slide.querySelectorAll('div,section,article')).filter(e => {
      const r = e.getBoundingClientRect();
      const t = (e.innerText || '').trim();
      return r.height > 0 && r.bottom > 0 && r.top < innerHeight &&
        t.includes('章节要点') && t.includes('内容由AI生成');
    }).map(e => {
      const t = (e.innerText || '').trim();
      return t.slice(t.indexOf('章节要点')).replace(/\s*内容由AI生成\s*$/, '').trim();
    }).filter(t => t.length > 50);
    chapterCandidates.sort((a, b) => a.length - b.length);
    if (chapterCandidates.length) out.ai = chapterCandidates[0];
  }
  out.aiFailed = !out.ai && ['很抱歉，我还在努力学习中', '抱歉，这个问题未找到相关结果',
    '抱歉，您的问题我无法识别'].some(t => (slide.innerText || '').includes(t));
  if (!out.ai && buttons.length && window.__batchAiClickedFor !== id) {
    buttons[0].click();
    window.__batchAiClickedFor = id;
    out.aiClicked = true;
  }
  return JSON.stringify(out);
})()
'''


def orca(args, timeout=60):
    cp = subprocess.run(["orca", *args], text=True, capture_output=True, timeout=timeout)
    if cp.returncode != 0:
        raise RuntimeError((cp.stderr or cp.stdout).strip())
    data = json.loads(cp.stdout)
    if not data.get("ok"):
        raise RuntimeError(json.dumps(data, ensure_ascii=False))
    return data.get("result", {})


def eval_js(expression, timeout=60):
    result = orca(["eval", "--page", PAGE, "--expression", expression, "--json"], timeout)
    value = result.get("result")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def state():
    return eval_js(STATE_JS.replace("__EXPECTED_AUTHOR__", json.dumps(AUTHOR)))


def navigate(url):
    return eval_js(f"location.assign({json.dumps(url)}); 'navigating'")


def close_modal():
    eval_js(r'''
(() => {
  if (!/[?&]modal_id=\d+/.test(location.href)) return false;
  const event = new KeyboardEvent('keydown', {
    key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true
  });
  document.dispatchEvent(event);
  document.body.dispatchEvent(new KeyboardEvent('keydown', {
    key: 'Escape', code: 'Escape', keyCode: 27, which: 27, bubbles: true
  }));
  return true;
})()
''')
    for _ in range(15):
        time.sleep(0.5)
        if not eval_js("/[?&]modal_id=\\d+/.test(location.href)"):
            return


def parse_date(text, video_id=""):
    if video_id:
        try:
            timestamp = int(video_id) >> 32
            date = (dt.datetime.fromtimestamp(timestamp, dt.timezone.utc) +
                    dt.timedelta(hours=8)).date()
            if 2010 <= date.year <= CURRENT_YEAR + 1:
                return date.strftime("%Y-%m-%d"), date.strftime("%Y%m%d")
        except (ValueError, OverflowError, OSError):
            pass
    match = re.search(r"(?:(20\d{2})年)?(\d{1,2})月(\d{1,2})日", text or "")
    if match:
        date = dt.date(int(match.group(1) or CURRENT_YEAR),
                       int(match.group(2)), int(match.group(3)))
        return date.strftime("%Y-%m-%d"), date.strftime("%Y%m%d")
    today = dt.date.today()
    relative = re.search(r"(\d+)天前", text or "")
    if "昨天" in (text or ""):
        days = 1
    elif "今天" in (text or "") or "小时前" in (text or "") or "分钟前" in (text or ""):
        days = 0
    elif relative:
        days = int(relative.group(1))
    else:
        weeks = re.search(r"(\d+)周前", text or "")
        if not weeks:
            return "", ""
        days = int(weeks.group(1)) * 7
    date = today - dt.timedelta(days=days)
    return date.strftime("%Y-%m-%d"), date.strftime("%Y%m%d")


def safe_title(title, video_id):
    title = re.sub(r"[/#?%*:|\"<>\\\x00-\x1f]", "_", title or "").strip(" ._")
    return (title or f"未命名作品_{video_id}")[:80]


def save_markdown(s):
    date_iso, date_compact = parse_date(s["date"], s["id"])
    if not date_iso:
        raise ValueError("missing date")
    title = s["title"].strip() or f"未命名作品_{s['id']}"
    ai = re.sub(r"\s*以上内容由AI生成，仅供参考\s*$", "", s["ai"]).strip()
    ai = re.sub(r"^(?:AI\n)?TA的作品\n评论\n相关推荐\n+", "", ai).strip()
    if len(ai) < 20:
        raise ValueError("empty AI text")
    tags = " ".join(s.get("tags") or [])
    name = f"{date_compact}-{s['id']}-{safe_title(title, s['id'])}.md"
    content = (f"# {title}\n\n> 作者：{AUTHOR}\n> 抖音号：{DOUYIN_ID}\n"
               f"> 作品ID：{s['id']}\n> 创作时间：{date_iso}\n> 标签：{tags}\n\n"
               f"---\n\n{ai}\n\n---\n\n> 以上内容由AI生成，仅供参考\n")
    temp = OUT / f".{name}.{os.getpid()}.tmp"
    temp.write_text(content, encoding="utf-8")
    os.replace(temp, OUT / name)
    return name, len(ai)


def load_rows():
    rows = []
    if PROGRESS.exists():
        for line in PROGRESS.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return rows


def latest_rows(rows):
    return {row["id"]: row for row in rows if row.get("id")}


def append_progress(row):
    with PROGRESS.open("a", encoding="utf-8") as file:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")
        file.flush()


def bootstrap_existing(rows):
    latest = latest_rows(rows)
    for path in sorted(OUT.glob("*.md")):
        match = re.match(r"^(\d{8})-(\d{15,25})-.+\.md$", path.name)
        if not match or match.group(2) in latest:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        title = text.splitlines()[0].removeprefix("# ").strip()
        date_compact, video_id = match.groups()
        row = {"id": video_id, "title": title,
               "date": f"{date_compact[:4]}-{date_compact[4:6]}-{date_compact[6:]}",
               "status": "saved", "file": path.name, "existing": True}
        append_progress(row)
        rows.append(row)
        latest[video_id] = row
        print(f"EXISTING id={video_id} file={path.name}", flush=True)


def write_json(path, data):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


def completed_ids(rows):
    return {video_id for video_id, row in latest_rows(rows).items()
            if row.get("status") in {"saved", "no_ai"}}


def pending_ids(all_ids, rows):
    done = completed_ids(rows)
    return [video_id for video_id in all_ids if video_id not in done]


def write_summary(rows, all_ids, running, note=""):
    latest = latest_rows(rows)
    counts = Counter(row.get("status", "unknown") for row in latest.values())
    pending = pending_ids(all_ids, rows)
    write_json(SUMMARY, {
        "author": AUTHOR, "douyin_id": DOUYIN_ID,
        "profile_work_count": EXPECTED_COUNT, "running": running,
        "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "counts": dict(counts), "pending": len(pending), "note": note,
        "last": rows[-1] if rows else None,
    })


def collect_profile_ids(persist=True):
    navigate(PROFILE)
    profile = {}
    for _ in range(80):
        time.sleep(1)
        profile = eval_js(r'''
JSON.stringify({
  name: (document.querySelector('h1')?.innerText || '').trim(),
  works: Array.from(document.querySelectorAll('h2')).map(e => e.innerText),
  hasId: (document.body?.innerText || '').includes(%s),
  followed: Array.from(document.querySelectorAll('button')).some(b => b.innerText.trim() === '已关注')
})
''' % json.dumps(DOUYIN_ID))
        if profile.get("name") == AUTHOR and profile.get("hasId"):
            break
    if (profile.get("name") != AUTHOR or not profile.get("hasId")
            or not profile.get("followed")):
        raise RuntimeError(f"author/following verification failed: {profile}")
    write_json(TMP / "账号核对.json", {
        "author": AUTHOR, "douyin_id": DOUYIN_ID, "sec_uid": SEC_UID,
        "profile_work_count": EXPECTED_COUNT, "followed": True,
        "verified_at": dt.datetime.now().isoformat(timespec="seconds"),
    })
    eval_js(r'''
document.querySelectorAll('video').forEach(v => {v.autoplay = false; v.pause()});
window.__authorIds = new Set();
window.__collectAuthorIds = () => {
  const lists = Array.from(document.querySelectorAll('.route-scroll-container ul'))
    .filter(u => u.querySelector('a[href*="/video/"],a[href*="/note/"]'))
    .sort((a, b) =>
      b.querySelectorAll('a[href*="/video/"],a[href*="/note/"]').length -
      a.querySelectorAll('a[href*="/video/"],a[href*="/note/"]').length);
  if (lists.length) {
    lists[0].querySelectorAll('a[href*="/video/"],a[href*="/note/"]').forEach(a => {
      const match = a.href.match(/\/(?:video|note)\/(\d+)/);
      if (match) window.__authorIds.add(match[1]);
    });
  }
  return window.__authorIds.size;
};
'ready'
''')
    stable = 0
    last = (-1, -1)
    for index in range(220):
        current_state = eval_js(r'''
(() => {
  document.querySelectorAll('video').forEach(v => v.pause());
  const sc = document.querySelector('.route-scroll-container');
  if (sc) sc.scrollTop = sc.scrollHeight;
  return JSON.stringify({count: window.__collectAuthorIds(),
    height: sc ? sc.scrollHeight : 0});
})()
''')
        current = (current_state.get("count", 0), current_state.get("height", 0))
        stable = stable + 1 if current == last and current[0] > 0 else 0
        last = current
        print(f"SCROLL {index+1} count={current[0]} stable={stable}", flush=True)
        if EXPECTED_COUNT and current[0] >= EXPECTED_COUNT and stable >= 3:
            break
        if stable >= (25 if current[0] < EXPECTED_COUNT else 12):
            break
        time.sleep(1)
    ids = eval_js("JSON.stringify(Array.from(window.__authorIds))")
    if not ids:
        raise RuntimeError("no author works collected")
    if persist:
        write_json(IDS_FILE, ids)
    print(f"COLLECTED profile={EXPECTED_COUNT} actual={len(ids)} persist={persist}", flush=True)
    return ids


def process_one(video_id):
    close_modal()
    clicked = eval_js(r'''
(() => {
  const id = %s;
  const links = Array.from(document.querySelectorAll(
    '.route-scroll-container a[href*="/video/"],.route-scroll-container a[href*="/note/"]'
  ));
  const anchor = links.find(a => {
    const match = a.href.match(/\/(?:video|note)\/(\d+)/);
    return match && match[1] === id;
  });
  if (!anchor) return false;
  anchor.click();
  return true;
})()
''' % json.dumps(video_id))
    if not clicked:
        print(f"FALLBACK_NAV id={video_id}", flush=True)
        navigate(PROFILE + "&modal_id=" + video_id)
    time.sleep(1)
    started = time.time()
    while True:
        elapsed = time.time() - started
        try:
            s = state()
        except Exception:
            if elapsed > 150:
                raise
            time.sleep(1)
            continue
        if s.get("id") != video_id:
            if elapsed > 150:
                raise RuntimeError(f"modal mismatch: expected {video_id}, got {s.get('id')}")
            time.sleep(1)
            continue
        if not s.get("slide"):
            if elapsed > 150:
                raise RuntimeError("slide not found")
            time.sleep(1)
            continue
        author = s.get("author", "")
        if author and AUTHOR not in author and not s.get("coauthorVerified"):
            raise RuntimeError(f"wrong author: {author}")
        if s.get("ai") and s.get("date"):
            try:
                name, ai_len = save_markdown(s)
            except ValueError as exc:
                if str(exc) == "empty AI text" and elapsed <= 150:
                    time.sleep(1)
                    continue
                raise
            row = {"id": video_id, "title": s.get("title", ""),
                   "date": parse_date(s["date"], video_id)[0], "status": "saved",
                   "file": name, "ai_len": ai_len}
            if s.get("coauthorVerified"):
                row["note"] = "本作者主页共创作品；页面明确列出本作者为共创者"
            return row
        no_ai_ready = not s.get("hasAiButton") or (s.get("aiFailed") and elapsed > 60)
        if elapsed > 15 and no_ai_ready and author:
            return {"id": video_id, "title": s.get("title", ""),
                    "date": parse_date(s.get("date", ""), video_id)[0], "status": "no_ai",
                    "note": "AI面板返回失败提示" if s.get("aiFailed") else "无AI入口"}
        if elapsed > 150:
            raise RuntimeError("AI text or metadata timeout")
        time.sleep(1)


def validate(all_ids, rows):
    latest = latest_rows(rows)
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
            "author": AUTHOR in text,
            "douyin_id": DOUYIN_ID in text,
            "matching_id": video_id in text,
            "date": f"{date_compact[:4]}-{date_compact[4:6]}-{date_compact[6:]}" in text,
            "ai_marker": "以上内容由AI生成，仅供参考" in text,
            "substantial_text": len(text) > 100,
        }
        failed = [name for name, ok in checks.items() if not ok]
        if failed:
            invalid.append({"file": path.name, "error": ",".join(failed)})
    duplicates = sorted(video_id for video_id, count in Counter(ids).items() if count > 1)
    file_ids = set(ids)
    no_ai_ids = {video_id for video_id, row in latest.items() if row.get("status") == "no_ai"}
    pending = sorted(set(all_ids) - file_ids - no_ai_ids)
    extra = sorted((file_ids | no_ai_ids) - set(all_ids))
    validation = {
        "author": AUTHOR, "douyin_id": DOUYIN_ID,
        "validated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "markdown_files": len(files), "unique_video_ids": len(file_ids),
        "duplicate_ids": duplicates, "invalid_files": invalid,
        "profile_listed_items": len(all_ids), "no_ai": len(no_ai_ids),
        "listed_pending": pending, "processed_not_in_profile_list": extra,
    }
    write_json(TMP / "文案校验.json", validation)
    report = {
        "author": AUTHOR, "douyin_id": DOUYIN_ID, "sec_uid": SEC_UID,
        "profile_work_count": EXPECTED_COUNT, "accessible_author_items": len(all_ids),
        "running": False, "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "counts": {"saved": len(file_ids), "no_ai": len(no_ai_ids),
                   "error": len(pending)},
        "validation": {"markdown_files": len(files), "unique_video_ids": len(file_ids),
                       "invalid_files": len(invalid), "duplicate_ids": len(duplicates),
                       "processed_not_in_profile_list": len(extra)},
        "coverage_note": (f"主页显示作品{EXPECTED_COUNT}；实际展开并核对{len(all_ids)}个本作者作品。"
                          f"保存{len(file_ids)}个AI文案，{len(no_ai_ids)}个无AI总结，待补提{len(pending)}个。"),
    }
    write_json(TMP / "提取完成报告.json", report)
    return validation


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    bootstrap_existing(rows)
    if IDS_FILE.exists():
        all_ids = json.loads(IDS_FILE.read_text(encoding="utf-8"))
        print(f"RESUME_IDS count={len(all_ids)}", flush=True)
    else:
        all_ids = collect_profile_ids()
    write_summary(rows, all_ids, True)
    for attempt in range(1, 4):
        pending = pending_ids(all_ids, rows)
        write_json(PENDING_FILE, pending)
        print(f"ROUND {attempt} pending={len(pending)}", flush=True)
        if not pending:
            break
        for video_id in pending:
            latest = latest_rows(rows)
            if latest.get(video_id, {}).get("status") in {"saved", "no_ai"}:
                continue
            existing_files = sorted(OUT.glob(f"*-{video_id}-*.md"))
            if existing_files:
                row = {"id": video_id, "status": "saved",
                       "file": existing_files[0].name, "existing": True}
                append_progress(row)
                rows.append(row)
                print(f"SKIP_FILE id={video_id}", flush=True)
                write_summary(rows, all_ids, True)
                continue
            try:
                row = process_one(video_id)
            except Exception as exc:
                if "browser_tab_not_found" in str(exc):
                    write_summary(rows, all_ids, False, "内置浏览器标签页失效，已停止；修复页面后可从断点续提")
                    raise
                row = {"id": video_id, "status": "error", "error": str(exc)}
                print(f"ERROR id={video_id} {exc}", flush=True)
                time.sleep(1)
            append_progress(row)
            rows.append(row)
            print(f"{row['status'].upper()} id={video_id} title={row.get('title', '')}", flush=True)
            write_summary(rows, all_ids, True)
    pending = pending_ids(all_ids, rows)
    write_json(PENDING_FILE, pending)
    write_summary(rows, all_ids, False, f"处理结束，待补提{len(pending)}个")
    validation = validate(all_ids, rows)
    print("VALIDATION " + json.dumps(validation, ensure_ascii=False), flush=True)
    print(f"DONE pending={len(pending)}", flush=True)
    if pending or validation["invalid_files"] or validation["duplicate_ids"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
