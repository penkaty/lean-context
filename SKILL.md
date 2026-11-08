---
name: lean-context
description: Keep coding-agent sessions cheap on large, multi-repo projects. Use when setting up or auditing a project for Claude Code (CLAUDE.md, project map, settings, tools), when sessions start with a large context, or before long multi-day tasks.
---

# Lean context

Goal: the agent should start small, find any file in one or two steps, and never read or load what the task does
not need. Every token the agent spends finding things is a token not spent on the work.

## 1. Index the library: one project map
Create `PROJECT_MAP.md` at the project root (template in `templates/`). One row per doc, config, source folder and
tool: the path in backticks, one line on what it is, and **when to open it**.
- Pointers only, never facts (values, states, rules). Facts live in the files the map points to, so the map cannot
  go stale against them.
- Put a short "how to read cheaply" block at the top (see the template) and a never-open list for bulky folders.
- Keep it complete automatically: `python scripts/mapcheck.py --install-hook` warns on every commit when a file is
  missing from the map or a row points to nothing.
- When the agent adds, moves or removes a file, it fixes the map row in the same turn.

## 2. Keep the always-loaded context tiny
- `CLAUDE.md`: rules only (safety, git, where things are). Aim for a few KB. Point to the map; do not copy it.
- `STATUS.md` (template): current state in at most 40 lines, rewritten at the end of each session, read at the
  start only when the task is not self-contained.
- Decision log and change log are newest-first: read the top (about 60 lines) or grep. Never whole.

## 3. Find before you read
- Start every source file, config and script with a header comment saying what it is and when to use it. The agent
  reads the header, greps, then reads a line range.
- Prefer a code-graph or symbol-search tool for "where is this used" over opening files.
- Never list whole trees. Provide a tree command that skips bulk folders.

## 4. Tool diet
Every tool and MCP server definition costs context in every session, used or not.
- Deny tools the project never uses in `.claude/settings.local.json` (example in `templates/`).
- Enable only the MCP servers this project needs; prefer per-project `.mcp.json` over global ones.
- Hard-deny reads of bulky generated folders (decompiler projects, caches, build output, backups).
- Desktop-app integrations add their own tools: for long technical work a terminal or editor session
  can start much smaller.

## 5. Expensive output goes to disk
Wrap heavy commands (decompilers, whole-tree linters, big logs, API dumps) with `scripts/cached.py`: the full output
is written once to `.cache/cmd/`, the agent sees the path and the first lines, then greps the file. Re-runs are free.

## 6. Never learn the same thing twice
Keep findings in a small knowledge base with a find step (even a TSV plus grep). Rule for the agent: look it up
before researching, record what it learned in the same turn.

## 7. Session habits
- One task per session; clear between unrelated tasks; end each session by rewriting STATUS.md.
- No sub-agents or side sessions unless the user asks. When parallel work is worth it: one coordinator, at most
  two workers, each with a written brief naming the only files it may write. Cheaper models for mechanical work.
- Measure: note the context size at session start before and after each change, and keep what pays.

## Audit checklist (run on an existing project)
1. Start a fresh session and note the context size before any prompt.
2. List loaded tools and MCP servers; deny what the project does not use.
3. Check CLAUDE.md size and contents; move facts out, keep rules and pointers.
4. Create or update PROJECT_MAP.md; run mapcheck until it is clean; install the hook.
5. Add header comments to the most-opened files; add a never-open list.
6. Wrap the heaviest commands with cached.py.
7. Start a fresh session again and compare the context size.
