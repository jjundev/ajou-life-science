# Coverage contract v2

The guide has three independently checked records:

1. question-scope lock: the complete source-derived question universe;
2. coverage JSON: atomic facts, process dimensions, and HTML mappings;
3. review evidence: fact checks, question solvability checks, reverse audit,
   visual audit, and disclosed source conflicts.

## Question-scope lock

The lock is built in two phases into the same file.

- Phase 1, before authoring: build_question_scope.py without audits. Its
  source hash, base questions, evidenced status overrides, and final IDs and
  statuses are immutable inputs. A status override never deletes an ID.
- Phase 2, after the fact inventory: build_guide.py merges one audit per
  active question. The audit holds requirements, which are fact IDs, and fact
  IDs exist only after the inventory. Audits cannot change id, status,
  source_locator, reason, or override fields.

Every active question must be audited before complete validation. Its final
scope record contains:

- id and included or review status;
- original format: multiple_choice (with option_count) or short_answer;
- grading: single, ambiguous, or rubric;
- requirements: atomic fact IDs needed to solve it;
- source_evidence with source_path, page, and a short quote;
- audit_status: confirmed.

Deferred questions have a concrete reason and later prerequisite. They have no
answer card. Draft validation may expose missing audit fields; complete
validation rejects them.

## Coverage JSON

Schema version 2 contains inventory, inventory_sha256, mappings, review, and
delivery_mode. delivery_mode is complete unless the user explicitly requested
a partial artifact.

Every nonblank source unit is classified. Metadata is restricted to titles,
provenance, navigation, separators, and table syntax. Summary rows, review
bullets, warnings, mnemonics, quantities, explanations, and question mappings
cannot be hidden as metadata.

A supplement or review block may be external: it has no start/end and does
not cover note lines. Every fact in it must cite a non-note source (reference
or quiz), and the block needs a reason. Use it for facts that a question
needs but the note never states. Teaching, boundary, metadata, and
question_map blocks always cover note lines.

Facts are independently checkable claims. Each has id, block_id, statement,
kind, qualifiers, concept_id, scope, and evidence. Kinds are definition,
structure, process_step, quantity, direction, condition, exception, and
contrast. A process_step additionally has dimensions with nonempty location,
input, and output. Direction, accounting, carrier, and boundary are added when
the source or a question requires them.

Each active question repeats the scope-locked format, grading, and requirements
without changes. answerability contains teaching_target_ids. Multiple-choice
questions contain option_diagnostics; short-answer questions contain a rubric.
Diagram-dependent questions declare diagram_required and figure_target_ids.
Ambiguous questions contain a visible source-conflict element.

Mappings connect every fact to visible teaching text. A solution, hidden
element, script, style, or template cannot satisfy a teaching requirement.

## Guide data module

build_guide.py imports `eli5-src/MMDD/guide.py`; sibling modules may be
imported from it. The module defines:

- META: note, output_stem, title, quiz_sources ({"2강": {source_id, path,
  label}}), groups ([(group, heading)]), header_html (may use {inc} {rev}
  {deferred} {total}), scope_notes_html, footer. Optional: overrides,
  prior_notes, routine_html, delivery_mode.
- SOURCES, CONCEPTS ([(id, title, prerequisites)]), BLOCKS ([(id, start, end,
  kind, reason, question_ids)], with start/end None for an external block),
  FACTS (guide_kit.F), QUESTIONS (guide_kit.Q), DEFERRED ({id: (reason,
  later prerequisite, fact IDs)}), SECTIONS (the overview first), and BOUNDARY.

The builder derives mappings from `id="…" data-facts="…"` attributes. It
fails on an untaught or unknown fact, a quote missing from its note block, an
option diagnosis gap, an ambiguous item without also_accept or a conflict, and
a figure id missing from the HTML. Rebuilding unchanged data reproduces the
same bytes, so the recorded review stays valid.

## Review and delivery

Complete review is bound to current source, scope, inventory, and artifact
hashes. fact_checks cover every fact. question_checks cover every active
question and record teaching_target_ids, used_external_knowledge=false,
option_or_rubric_check, and evidence. A reviewer who did not write the
solutions answers from the blind copy made by make_blind_copy.py, never from
the full artifact. Source/reverse/desktop/mobile/print audits must pass. A
scientifically unresolved but pedagogically handled item uses grading=ambiguous
and a visible disclosed conflict.

Draft output says that it is not a complete study guide. Partial delivery is
allowed only when the user explicitly asks for a subset, the artifact filename
contains partial, coverage says delivery_mode=partial, and the validator
receives allow-partial. A partial artifact can never pass complete validation.
