# PROJECT_MAP: where things are, and when to open them

Read this when you need to FIND something, not at every session start. Pointers only: what a file is for and when to
open it. Facts live in the files it points to. Rules are in `CLAUDE.md`; current state in `STATUS.md`.
Missing rows: `python scripts/mapcheck.py`.

## How to read cheaply
- Find before you read: grep a word in the file this map points to, then read only that line range.
- Newest-first logs (`docs/DECISIONS.md`, `docs/CHANGELOG.md`): read the top ~60 lines or grep. Never whole.
- Every source file starts with a header comment: read it, then grep.
- Heavy commands: `python scripts/cached.py -- <command>`, then grep the cache file.
- Never open: `build/`, `.cache/`, `node_modules/`, `backups/`, generated data.
- Added, moved or removed a file? Fix its row here in the same turn.

## Top level
| path | what | open when |
|---|---|---|
| `CLAUDE.md` | Rules: safety, git, memory on paper | auto-loaded |
| `STATUS.md` | Current state, 40 lines max | start of a task that is not self-contained |
| `src/` | Application code (one row per subfolder below) | code changes |
| `docs/DECISIONS.md` | Decision log, newest first | before re-deciding anything |

## src/
| path | what | open when |
|---|---|---|
| `src/example/` | ... | ... |
