#!/usr/bin/env python3
import argparse
import datetime as dt
import json
import os
import re
import subprocess
import time
from pathlib import Path

PAGE = "39fbe6c0-4c62-4eed-9d1d-c1d1472bd110"
OUT = Path("/Volumes/wd/ai-learn/抖音关注/957685878-月球大叔")
TMP_OUT = Path("/Volumes/wd/ai-learn/tmp/957685878-月球大叔")
PROGRESS = TMP_OUT / "提取进度.jsonl"
SUMMARY = TMP_OUT / "提取状态.json"
CURRENT_YEAR = 2026

STATE_JS = r'''
(() => {
  window.__jhPause = true;
  if (!window.__jhPlayBlocker) {
    window.__jhPlayBlocker = e => {
      if (window.__jhPause && e.target instanceof HTMLVideoElement) {
        e.target.autoplay = false;
        e.target.pause();
      }
    };
    document.addEventListener('play', window.__jhPlayBlocker, true);
  }
  document.querySelectorAll('video').forEach(v => { v.autoplay = false; v.pause(); });
  const id = (location.href.match(/[?&]modal_id=(\d+)/) || [])[1] || '';
  const out = {id, url: location.href, slide: false, author: '', title: '', date: '',
               tags: [], ai: '', hasAiButton: false, aiClicked: false,
               paused: Array.from(document.querySelectorAll('video')).every(v => v.paused)};
  if (!id) return JSON.stringify(out);
  const slide = document.querySelector('.sliderVideo.video_' + id);
  if (!slide) return JSON.stringify(out);
  out.slide = true;
  const account = slide.querySelector('.account');
  out.author = account ? account.innerText.trim() : '';
  const titleEl = slide.querySelector('.video-info-detail .title');
  if (titleEl) {
    const first = titleEl.firstElementChild;
    out.title = ((first && first.innerText) || titleEl.innerText || '').trim().split('\n')[0].trim();
    out.tags = Array.from(new Set(Array.from(titleEl.querySelectorAll('a'))
      .map(a => a.textContent.trim()).filter(t => t.startsWith('#'))));
  }
  const dm = out.author.match(/(?:20\d{2}年)?\d{1,2}月\d{1,2}日|昨天|今天|\d+(?:天|周|小时|分钟)前/);
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
  }).map(e => (e.innerText || '').trim()).filter(t => t.length > 20);
  candidates.sort((a, b) => a.length - b.length);
  if (candidates.length) out.ai = candidates[0];
  if (!out.ai && buttons.length && window.__jhAiClickedFor !== id) {
    buttons[0].click();
    window.__jhAiClickedFor = id;
    out.aiClicked = true;
  }
  return JSON.stringify(out);
})()
'''

CURRENT_ID_JS = "((location.href.match(/[?&]modal_id=(\\d+)/)||[])[1]||'')"


def orca(args, timeout=40):
    cp = subprocess.run(["orca", *args], text=True, capture_output=True, timeout=timeout)
    if cp.returncode != 0:
        raise RuntimeError((cp.stderr or cp.stdout).strip())
    data = json.loads(cp.stdout)
    if not data.get("ok"):
        raise RuntimeError(json.dumps(data, ensure_ascii=False))
    return data.get("result", {})


def eval_js(expression, timeout=40):
    result = orca(["eval", "--page", PAGE, "--expression", expression, "--json"], timeout)
    value = result.get("result")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def state():
    return eval_js(STATE_JS)


def parse_date(text, video_id=""):
    # Douyin aweme IDs carry the creation timestamp in their high bits.
    # This also handles relative labels such as “2天前” without guessing.
    if video_id:
        try:
            timestamp = int(video_id) >> 32
            date = (dt.datetime.fromtimestamp(timestamp, dt.timezone.utc) +
                    dt.timedelta(hours=8)).date()
            if 2010 <= date.year <= CURRENT_YEAR + 1:
                return date.strftime("%Y-%m-%d"), date.strftime("%Y%m%d")
        except (ValueError, OverflowError, OSError):
            pass
    m = re.search(r"(?:(20\d{2})年)?(\d{1,2})月(\d{1,2})日", text or "")
    if m:
        year = int(m.group(1) or CURRENT_YEAR)
        date = dt.date(year, int(m.group(2)), int(m.group(3)))
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
    content = (f"# {title}\n\n"
               f"> 作者：月球大叔\n"
               f"> 抖音号：957685878\n"
               f"> 作品ID：{s['id']}\n"
               f"> 创作时间：{date_iso}\n"
               f"> 标签：{tags}\n\n"
               f"---\n\n{ai}\n\n---\n\n"
               f"> 以上内容由AI生成，仅供参考\n")
    path = OUT / name
    path.write_text(content, encoding="utf-8")
    return name, len(ai)


def append_progress(row):
    with PROGRESS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
        f.flush()


def load_seen():
    seen = set()
    if PROGRESS.exists():
        for line in PROGRESS.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
                if row.get("status") in {"saved", "no_ai"}:
                    seen.add(row["id"])
            except (json.JSONDecodeError, KeyError):
                pass
    for path in OUT.glob("*.md"):
        m = re.search(r"-(\d{15,25})-", path.name)
        if m:
            seen.add(m.group(1))
    return seen


def write_summary(rows, running, note=""):
    counts = {}
    for row in rows:
        counts[row.get("status", "unknown")] = counts.get(row.get("status", "unknown"), 0) + 1
    tmp = SUMMARY.with_suffix(".tmp")
    tmp.write_text(json.dumps({
        "author": "月球大叔", "douyin_id": "957685878", "profile_work_count": 233,
        "running": running, "updated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "counts": counts, "note": note,
        "last": rows[-1] if rows else None,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, SUMMARY)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="new items to process; 0 means all")
    ap.add_argument("--max-items", type=int, default=250)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    TMP_OUT.mkdir(parents=True, exist_ok=True)
    seen = load_seen()
    rows = []
    if PROGRESS.exists():
        for line in PROGRESS.read_text(encoding="utf-8").splitlines():
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    processed = 0
    steps = 0
    last_id = ""
    started = time.time()
    print(f"START seen={len(seen)} output={OUT}", flush=True)

    while steps < args.max_items:
        steps += 1
        try:
            s = state()
        except Exception as e:
            print(f"STATE_ERROR {e}", flush=True)
            time.sleep(2)
            continue
        video_id = s.get("id", "")
        if not video_id:
            time.sleep(1)
            continue
        if video_id in seen:
            print(f"RESUME_SKIP {video_id}", flush=True)
        else:
            item_start = time.time()
            clicked_retry = False
            while True:
                if not s.get("slide"):
                    if time.time() - item_start > 25:
                        raise RuntimeError(f"slide not found for {video_id}")
                    time.sleep(0.8)
                    s = state()
                    continue
                author = s.get("author", "")
                if author and "月球大叔" not in author:
                    raise RuntimeError(f"wrong author for {video_id}: {author}")
                if s.get("ai") and s.get("date"):
                    name, ai_len = save_markdown(s)
                    row = {"id": video_id, "title": s["title"], "date": parse_date(s["date"], s["id"])[0],
                           "status": "saved", "file": name, "ai_len": ai_len}
                    append_progress(row)
                    rows.append(row)
                    seen.add(video_id)
                    processed += 1
                    print(f"SAVED {processed} id={video_id} chars={ai_len} file={name}", flush=True)
                    break
                elapsed = time.time() - item_start
                if elapsed > 8 and not s.get("hasAiButton") and author:
                    row = {"id": video_id, "title": s.get("title", ""),
                           "date": parse_date(s.get("date", ""), video_id)[0], "status": "no_ai"}
                    append_progress(row)
                    rows.append(row)
                    seen.add(video_id)
                    processed += 1
                    print(f"NO_AI {processed} id={video_id} title={s.get('title','')}", flush=True)
                    break
                if elapsed > 16 and not clicked_retry:
                    eval_js("window.__jhAiClickedFor=''; 'retry-ai'")
                    clicked_retry = True
                if elapsed > 30:
                    row = {"id": video_id, "title": s.get("title", ""),
                           "date": parse_date(s.get("date", ""), video_id)[0], "status": "error",
                           "error": "AI text or metadata timeout"}
                    append_progress(row)
                    rows.append(row)
                    seen.add(video_id)
                    processed += 1
                    print(f"ERROR {processed} id={video_id} AI text or metadata timeout", flush=True)
                    break
                time.sleep(1)
                s = state()
            write_summary(rows, True)

        if args.limit and processed >= args.limit:
            write_summary(rows, False, f"limit {args.limit} reached")
            print(f"DONE limit={args.limit} elapsed={time.time()-started:.1f}s", flush=True)
            return

        old_id = video_id
        changed = False
        for attempt in range(3):
            orca(["keypress", "--page", PAGE, "--key", "ArrowDown", "--json"])
            wait_start = time.time()
            while time.time() - wait_start < 5:
                time.sleep(0.6)
                try:
                    new_id = eval_js(CURRENT_ID_JS)
                    state()  # Pause the new short video immediately.
                except Exception:
                    continue
                if new_id and new_id != old_id:
                    changed = True
                    break
            if changed:
                break
            print(f"ARROW_RETRY id={old_id} attempt={attempt+1}", flush=True)
        if not changed:
            write_summary(rows, False, f"no next video after {old_id}")
            print(f"DONE end_of_queue id={old_id} elapsed={time.time()-started:.1f}s", flush=True)
            return
        last_id = old_id

    write_summary(rows, False, f"max items {args.max_items} reached")
    print(f"DONE max_items={args.max_items}", flush=True)


if __name__ == "__main__":
    main()
