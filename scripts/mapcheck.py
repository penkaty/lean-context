#!/usr/bin/env python3
"""mapcheck: keep PROJECT_MAP.md honest.

Lists every file in the project (git ls-files, or a directory walk outside git) and checks that each one is
covered by the map: its own path, or one of its parent folders, appears in `backticks` somewhere in the map.
Also lists map entries that point to paths which no longer exist.

Usage:
  python mapcheck.py                      # map = PROJECT_MAP.md in the current folder
  python mapcheck.py --map docs/MAP.md --warn
  python mapcheck.py --install-hook       # run it on every commit (warns, never blocks)

Ignore files with a .mapignore next to the map: one glob per line (fnmatch), e.g. `tests/*` or `*.png`.
Exit code: 1 when something is missing or stale (0 with --warn). Standard library only.
"""
import argparse, fnmatch, os, re, subprocess, sys

def project_files(root):
    try:
        out = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True, check=True).stdout
        return [l.strip() for l in out.splitlines() if l.strip()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        files = []
        for d, dirs, names in os.walk(root):
            dirs[:] = [x for x in dirs if not x.startswith(".")]
            files += [os.path.relpath(os.path.join(d, n), root).replace(os.sep, "/") for n in names]
        return files

def map_paths(map_text):
    paths = set()
    for m in re.findall(r"`([^`\s]+)`", map_text):
        p = m.strip().lstrip("./").rstrip("/")
        if p and not p.startswith("-") and ("/" in m or "." in p):
            paths.add(p)
    return paths

def covered(path, entries):
    parts = path.split("/")
    return any("/".join(parts[:i]) in entries for i in range(1, len(parts) + 1))

def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--map", default="PROJECT_MAP.md")
    ap.add_argument("--root", default=".")
    ap.add_argument("--warn", action="store_true", help="report but exit 0")
    ap.add_argument("--install-hook", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    if a.install_hook:
        hook = os.path.join(root, ".git", "hooks", "pre-commit")
        with open(hook, "a", encoding="utf8") as f:
            f.write(f'\npython "{os.path.abspath(__file__)}" --map "{a.map}" --warn\n')
        os.chmod(hook, 0o755)
        print("pre-commit hook added:", hook); return 0
    map_file = os.path.join(root, a.map)
    text = open(map_file, encoding="utf8").read()
    entries = map_paths(text)
    ignore_file = os.path.join(os.path.dirname(map_file), ".mapignore")
    ignores = [l.strip() for l in open(ignore_file, encoding="utf8")] if os.path.exists(ignore_file) else []
    ignores = [g for g in ignores if g and not g.startswith("#")]
    files = [f for f in project_files(root) if not any(fnmatch.fnmatch(f, g) for g in ignores)]
    map_rel = os.path.relpath(map_file, root).replace(os.sep, "/")
    own = {map_rel, os.path.relpath(ignore_file, root).replace(os.sep, "/")}
    missing = [f for f in files if f not in own and not f.startswith(".cache/") and not covered(f, entries)]
    stale = sorted(p for p in entries if not os.path.exists(os.path.join(root, p)) and not any(c in p for c in "*?<"))
    for f in missing: print("missing from map:", f)
    for p in stale: print("map points to nothing:", p)
    print(f"mapcheck: {len(files)} files, {len(entries)} map entries, {len(missing)} missing, {len(stale)} stale")
    return 0 if a.warn or not (missing or stale) else 1

if __name__ == "__main__":
    sys.exit(main())
