# lean-context

**Start coding-agent sessions at half the context.** A Claude Code skill, two small scripts and three templates
for keeping agent sessions cheap on large, multi-repo projects. No presets: everything here came from trial and error
on a real project.

## Result
Measured on [RBR-RTX](https://github.com/penkaty/RBR-RTX): a workspace with 5 repositories (C++ proxy, a Vulkan
runtime fork, a Python asset pipeline, a reverse-engineering knowledge base, ~300 docs and tools), built over
several weeks of long daily sessions on a single Pro plan.

| | Context at session start |
|---|---|
| Before: default setup in the desktop app | 55,000 – 75,000 tokens |
| After: this setup, in the CLI / editor extension | 20,000 – 45,000 tokens (depends on the first prompt) |
| **Change** | **about 50% less at the midpoint (40–64% across the range)** |

That saving is paid on every session, and long tasks spread over a week mean dozens of sessions. Part of it comes from
leaving the desktop app's own integrations behind (fewer tools loaded), part from the habits below.
Measure your own: note the context size at the start of a fresh session before and after each change.

## The ideas in one screen
1. **Index the library.** A `PROJECT_MAP.md` with one row per file or folder: what it is and *when to open it*.
   Pointers only, never facts, so it cannot go stale. The agent finds anything in one or two steps instead of
   "climbing ladders" through folders.
2. **The map checks itself.** `scripts/mapcheck.py` lists files missing from the map and rows that point to nothing;
   install it as a commit hook.
3. **Tool diet.** Every tool and MCP server definition is loaded into every session. Deny what the project never uses.
4. **Find before you read.** Header comments in every file, grep, then read a line range. Newest-first logs are read
   from the top.
5. **Expensive output goes to disk.** `scripts/cached.py -- <command>` keeps the full output in a file and shows the
   agent only the path and the first lines.
6. **Tiny always-loaded context.** Rules file a few KB; status file at most 40 lines, rewritten each session end.
7. **Never learn the same thing twice.** A small knowledge base with a find step, updated in the same turn.

## Install
Copy the folder into your project's `.claude/skills/lean-context/` (or your user skills folder). Then ask the agent:
*"Use the lean-context skill to audit this project."* It follows the checklist at the end of `SKILL.md`.

```
python .claude/skills/lean-context/scripts/mapcheck.py                 # check the map
python .claude/skills/lean-context/scripts/mapcheck.py --install-hook  # warn on every commit
python .claude/skills/lean-context/scripts/cached.py -- git log --stat # cache a heavy command
```
Python 3.8+, standard library only, works on Windows, Linux and macOS.

## Files
| File | What |
|---|---|
| `SKILL.md` | The skill: principles, session habits, audit checklist |
| `scripts/mapcheck.py` | Map completeness check and commit hook |
| `scripts/cached.py` | Cache a command's output on disk, print only the head |
| `templates/PROJECT_MAP.md` | Map skeleton with a "how to read cheaply" block |
| `templates/STATUS.md` | 40-line status file |
| `templates/settings.local.example.json` | Deny list for unused tools and bulky folders |

## Author
Franciszek Godrecki ([penkaty](https://github.com/penkaty)). Built while making RBR-RTX with Claude Code.
