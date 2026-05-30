# LLM Wiki — Pattern Reference

The wiki pattern: LLM incrementally builds and maintains a persistent knowledge base via `index.md` (catalog) + `log.md` (chronology). Knowledge compiles once, not re-derived on every query.

## In This Repo

- **AGENTS.md** = the schema (core principles, workflow, rules)
- **Pro-Labs/index.md** = catalog of all machines (solved + unsolved), technique pages
- **Pro-Labs/log.md** = chronological action log with per-machine chains, bugs fixed, lessons
- **Category wiki** = per-category `index.md` + `log.md` at `Crypto/`, `Web/`, etc.

## Operations

1. **Ingest** (after solving a machine): document the solve → update `index.md` catalog → append `log.md` entry with chain + bugs + lessons → update `AGENTS.md` patterns table
2. **Query** (before starting a machine): read `index.md` for known patterns → read `log.md` for relevant solved chains → read matching `patterns.md` for attack sequence
3. **Compact** (per AGENTS.md compaction rule): when context exceeds 2 challenges or 50 calls, move technique details to `log.md`, concepts to `index.md`, update anchored summary
4. **Companion files** (`tools.md`, `platforms.md`, `patterns.md`, `strategy.md`): read on demand, never auto-loaded. These are the expanded reference layer.

## Key Insight

The wiki is the **compiled knowledge** — keeps getting richer. Every solve adds to it. Every query reads from it. No re-discovery.
