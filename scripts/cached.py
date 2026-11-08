#!/usr/bin/env python3
"""cached: run an expensive command once, keep its full output on disk, print only the head.

Agents pay for every line of tool output that enters the conversation. Wrap heavy commands (decompilers,
linters over the whole tree, long log queries, big git logs) so the full result lands in a file and the agent
sees the path, the size and the first lines. It then greps the file for what it needs.

Usage:
  python cached.py -- git log --stat              # first run: executes, caches, prints head
  python cached.py -- git log --stat              # second run: served from cache
  python cached.py --head 40 --force -- make lint # refresh and show 40 lines
  python cached.py --ttl 3600 -- curl -s URL      # cache expires after an hour

Cache folder: .cache/cmd/ in the current directory (override with --dir). Standard library only.
"""
import argparse, hashlib, os, re, subprocess, sys, time

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--head", type=int, default=15)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--ttl", type=int, default=0, help="seconds; 0 = never expires")
    ap.add_argument("--dir", default=os.path.join(".cache", "cmd"))
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()
    cmd = a.cmd[1:] if a.cmd and a.cmd[0] == "--" else a.cmd
    if not cmd:
        ap.error("give a command after --")
    key = hashlib.sha1(("\0".join(cmd) + "\0" + os.getcwd()).encode()).hexdigest()[:10]
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", " ".join(cmd))[:50].strip("_")
    os.makedirs(a.dir, exist_ok=True)
    path = os.path.join(a.dir, f"{slug}-{key}.txt")
    fresh = os.path.exists(path) and (a.ttl == 0 or time.time() - os.path.getmtime(path) < a.ttl)
    if a.force or not fresh:
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
        with open(path, "w", encoding="utf8") as f:
            f.write(r.stdout)
            if r.stderr: f.write("\n--- stderr ---\n" + r.stderr)
        state = f"ran (exit {r.returncode})"
    else:
        state = "from cache"
    lines = open(path, encoding="utf8", errors="replace").read().splitlines()
    print(f"{state}: {path} ({len(lines)} lines). Grep this file; do not print it whole.")
    for l in lines[: a.head]: print(l)
    if len(lines) > a.head: print(f"... {len(lines) - a.head} more lines in the file")
    return 0

if __name__ == "__main__":
    sys.exit(main())
