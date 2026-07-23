---
name: zsh-memory-root-migrated-to-zsh-dir
description: zsh skill memory files consolidated into unified zsh/ directory, with migrate_layout.py to upgrade legacy projects
metadata:
  type: project
---

The zsh cross-agent memory skill changed its generated file layout to consolidate all memory files into a single `zsh/` directory (except CLAUDE.md which stays at the project root). A migration script upgrades legacy projects in place.

**Why:** Previously the skill generated `AGENT_MEMORY.md` at the project root and the rest (PROJECT_MEMORY.md, CURRENT_TASK.md, SESSION_LOG.md, DECISIONS.md, memory-archive/INDEX.md) under `skill-docs/`. This split made project directories look messy (e.g. articleReading had root AGENT_MEMORY.md + skill-docs/ + leftover docs/).

**What changed (all under `claude/zsh/zsh/`):**
- `_common.py`: `MEMORY_ROOT = "skill-docs"` → `"zsh"`
- `detect_project.py`: added `_zsh_layout()` that detects both `"zsh"` (new) and `"skill-docs"` (legacy) layouts; `has_agent_memory` now true for either
- `init_memory.py`: AGENT_MEMORY.md now generated under `zsh/`; added guard that refuses to init any project that already has zsh memory in either layout (returns `already_initialized`)
- `check_structure.py` + `validate_navigation.py`: added `_memory_root()` helper so health-check/validation resolve paths dynamically per layout (legacy = root AGENT_MEMORY.md + skill-docs/; new = everything under zsh/)
- `migrate_from_v3.py`: AGENT_MEMORY.md generation target moved under zsh/
- `git_policy.py`: exclude path `/AGENT_MEMORY.md` → `/zsh/AGENT_MEMORY.md`; note text updated
- Templates `AGENT_MEMORY.md.tmpl` (frontmatter `memory_root` + all body paths) and `zsh_memory.block.tmpl` (CLAUDE.md injected block): `skill-docs/` → `zsh/`
- `references/claude_mem_integration.md` + `session-log-format.md`: all `skill-docs/` → `zsh/`
- `SKILL.md`: all path references updated; added "迁移布局" branch (route step 6)
- **NEW** `migrate_layout.py`: upgrades legacy projects in place (see below)

**migrate_layout.py** (`scripts/migrate_layout.py`):
- Detects legacy layout via `zsh_layout == "skill-docs"`. New layout → `already_migrated`; no zsh → `not_zsh_project`.
- Moves root `AGENT_MEMORY.md` → `zsh/AGENT_MEMORY.md` and `skill-docs/*` → `zsh/*`, rewrites `skill-docs/` → `zsh/` path refs in AGENT_MEMORY.md.
- Removes now-empty `skill-docs/` tree bottom-up. Leaves `docs/` historical snapshot untouched.
- Refreshes CLAUDE.md ZSH:MEMORY block via `update_agent_entry` (template already uses zsh/ paths).
- `--dry-run` previews; `--apply` executes. Tested on articleReading: detect→`zsh`, check→ok, validate→exit 0, CLAUDE.md block updated.

**Legacy compatibility:** Existing projects keep their old layout until migrated. The skill detects both layouts via AGENT_MEMORY.md presence in either location. detect/check/validate all work on legacy projects; init refuses them to avoid duplicate zsh/ trees.

**How to apply:** When modifying zsh skill behavior, check whether the change needs to be layout-aware (resolving `_memory_root(root)` rather than assuming `MEMORY_ROOT`). See also [[zsh-skill-structure]].
