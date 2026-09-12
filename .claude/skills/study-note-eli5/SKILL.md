---
name: study-note-eli5
description: "Use when a Korean lecture note and its companion quiz must become a complete visual study guide that teaches enough to solve every in-scope source question."
---

# Study Note ELI5

This Claude Code entrypoint uses the repository's shared implementation so
Claude and Codex cannot drift.

**REQUIRED:** Read and follow the
[shared canonical instructions](../../../.agents/skills/study-note-eli5/SKILL.md)
completely before acting. Resolve every relative script, asset, and reference
path from that canonical skill directory.

When building or validating a guide, also read the
[coverage contract](../../../.agents/skills/study-note-eli5/references/coverage-contract.md).
Run the canonical scripts in its scripts directory; do not create a separate
Claude copy.

An ordinary invocation requires the complete gate. A draft or selected
question subset does not satisfy the request. Partial delivery is available
only when the user explicitly requests a subset and the canonical partial
contract is followed.
