# 0910 Study Note ELI5 pilot source review

Status: rejected partial regression fixture. This is source evidence for the
next audited guide, not a completed guide or a semantic approval. The v2
validator must reject its 6-question coverage against the 52-question source
scope and its broad metadata blocks.

## Inputs and scope

Read the current 0910 note and quiz HTML, the linked 0908 review material,
and every page of the original 1강 and 2강 question PDFs at 150 dpi. The
source audit records fingerprints, normalized question text, option lists,
printed keys, and page locations in the plan workspace report
.superpowers/sdd/2026-09-10-study-note-eli5/pilot-source-audit.md.

## Question reclassification

Track 52 source-qualified IDs: 29 included, 6 review, and 17 deferred.
The original current quiz set treated 2강:13 as an included plant/animal
metabolism question. The supplied PDF instead has a displaced photosynthesis
reaction-equation image strongly associated with 2강:13, while the plant/
animal question is 2강:18. Keep 2강:13 deferred with a visible source-layout
caution; do not delete it or duplicate 2강:18.

## Source conflicts to disclose in a guide

- 2강:1 prints ATP but its unqualified heat option is also physically true.
- 2강:7 uses an unsafe generalization about vitamins being not degraded.
- 2강:20 prints 32 ATP; label it as this source's convention, not a
  universal yield.
- 2강:23, 2강:29, and 2강:38 are source short-answer prompts. Any generated
  choices must be marked as practice.
- 2강:25 prints NADH but CoQ is also an electron carrier; retain the
  ambiguity and evidence.
- 2강:14 depends on an enzyme/lactose figure; redraw its factual mechanism
  or supply an accurate text alternative before asking it.

## Current validation

The source-inventory, HTML-contract, CLI/review-gate, and template test suite
passes 14 tests. Existing source-note tests pass 40 tests. A browser security
policy blocked opening the local template in the available browser surface, so
desktop/mobile/print visual review remains pending and cannot be marked pass.

## Remaining pilot work

Create 0910-eli5-audited.html and its coverage JSON only after transcribing
all 52 source-qualified question statuses and building fact mappings for every
nonblank range of 0910.md. Do not use the current generated 0910.html choices
as an authoritative substitute for PDF wording.
