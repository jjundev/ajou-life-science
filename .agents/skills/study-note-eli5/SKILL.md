---
name: study-note-eli5
description: "Use when a Korean lecture note and its companion quiz should become a beginner-friendly, exam-ready visual HTML study guide, especially when the user asks to understand a note well enough to solve its problems or requests an ELI5/picture-book explanation."
---

# Study Note ELI5

Create a complete visual lesson from a study note so a beginner can solve the note's associated questions without guessing.

## Workflow

1. **Locate inputs.** Identify the target note and any companion quiz, answer sheet, transcript, PDF, or referenced earlier note. Read the target note completely. Read the companion quiz when it exists; never infer choices or answers from the note alone.
   - Completion criterion: record the target path, companion paths, stated lecture range, and every question number in scope.

2. **Build the coverage map.** Extract every heading, table, diagram/code block, warning, mnemonic, review section, question mapping, and out-of-scope boundary. Group facts into a small concept sequence that follows the note.
   - Completion criterion: every source section appears in the planned outline, including review material and explicit “not yet taught” material.

3. **Translate, do not dilute.** For each concept, give an everyday analogy first, then the accurate biological explanation, then the exam distinction or trap. Preserve exact relationships, quantities, directions, exceptions, and terminology.
   - Prefer analogies such as city/apartment, factory/post office, blueprint/copy, and energy currency.
   - State “not all,” “only when,” and other conditions explicitly; never turn a conditional fact into a universal one.
   - Keep DNA/RNA, ribosome/lysosome, bilayer/double membrane, chromatin/chromosome, and prokaryote/eukaryote contrasts side by side.

4. **Produce the artifact.** Create a self-contained UTF-8 HTML file next to the note, normally \`<stem>-eli5.html\`. Start from [assets/base-template.html](assets/base-template.html) or preserve its visual language.
   - Use inline CSS and inline SVG/ASCII diagrams; do not require a network connection or external CDN.
   - Include: a one-screen concept map, chronological/mechanistic flows, comparison cards, memorization rules, a “scope boundary” card, and a question-by-question answer-reasoning section.
   - Keep the Korean copy concise per card, but include enough detail to cover the source note. Make the layout responsive and printable.

5. **Reconcile questions.** For every in-scope question, show the correct choice or answer, the reason, and the tempting wrong interpretation. If the source quiz conflicts with the note or scientific logic, preserve the conflict explicitly and label the likely key/printing error. For out-of-scope questions, say what future lesson is needed rather than inventing an answer.
   - Completion criterion: the artifact contains one question card per in-scope question and no unmarked answer-key conflict.

6. **Verify before handoff.** Run:
   \`python .claude/skills/study-note-eli5/scripts/verify_guide.py <artifact> --questions <comma-separated-question-numbers>\`
   Fix all reported omissions. Then inspect the generated file for obvious broken markup and report the artifact's absolute path.
   - Completion criterion: the validator exits 0, the expected question count matches, and the final response links the artifact.

## Output contract

Return a short Korean summary and a direct local-file link. Mention the generated filename, the covered question numbers, any answer-key correction, and any intentionally deferred questions. Do not claim completeness until verification passes.

