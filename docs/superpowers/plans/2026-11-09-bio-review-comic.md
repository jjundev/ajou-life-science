# Bio review comic implementation plan

> Execution: implement directly in this chat. The user approved all recommended design decisions and implementation on 2026-11-09. No second approval, commits, or publication of course comics is requested.

**Goal:** Add a discoverable repository skill that adapts each learning/review/summary topic in a saved biology note into a reviewed 4–8-panel comic HTML.

**Architecture:** A standard-library Python CLI extracts source evidence and scaffolds a storyboard, prepares prompts for the built-in image tool, registers local raster outputs, validates evidence/asset/review fingerprints, builds a preview, and publishes a versioned local artifact. The existing note template remains the authority for tokens and navigation. Separate source, contract, and rendering modules keep those responsibilities bounded.

**Spec:** Approved design in this chat (2026-11-09). Include learning, review, and whole-note summaries; exclude hero, future lesson preview, and resource links. Biology-structure-led illustrations, HTML dialogue, original-note same-tab links. Skill implementation only; no real 15-page comic batch in this change.

**Constraints:** 4–8 panels per included topic; source HTML is authoritative; no original-note edits; no quiz/video/audio/PDF; no shape stand-ins for final illustration; never claim a held page complete; preserve previous published versions; use existing note theme, panels, pager, and a separate comic read-state key. UTF-8 paths must resolve NFC/NFD consistently. No runtime Python dependencies.

## Tasks

### Task 1: Source inventory and storyboard contract
- [x] Write/run failing behavioral tests for date/path ambiguity, NFC paths, source topic order, classification, evidence, source drift, panel ranges, complete coverage, and supplemental scope.
- [x] Implement `comic_source.py`, `comic_contract.py` and CLI extraction/check commands.
- [x] Run tests and extract the actual 1105 note: 17 rows, 15 included.

### Task 2: Images, rendering, and local publication
- [x] Write/run failing tests for prompt/asset invalidation, missing/corrupt images, partial results, HTML escaping, original links, stale reviews, backup preservation, and publication without browser evidence.
- [x] Implement image registration, deterministic prompts/fingerprints, derived template and comic CSS, preview rendering, review reports, and versioned publication.
- [x] Exercise light/dark, desktop/mobile, navigation, summaries, separate read state, and links in Playwright with explicit test-only raster fixtures.

### Task 3: Skill and independent application test
- [x] Use the observed baseline (it added a quiz and altered cover behavior outside scope) to write a concise positive workflow and explicit output contract.
- [x] Add storyboard/schema/image/review references and discovery metadata; add the existing Claude skill alias convention.
- [x] Run a fresh read-only application scenario with the skill; correct demonstrated gaps.
- [x] Run quick_validate, all new tests and the repository test command. Report unrelated failures distinctly.

## Review focus

- A changed original or missing source must invalidate build/publication, including already-held pages.
- Unchanged artwork may be reused only when its prompt and content hash match; changed text must invalidate semantic review.
- All source topics and evidence blocks must have an explicit disposition, with no silent exclusions.
- Partial outputs must preserve topic positions and make unfinished pages visible; publication can never label these complete.
- The copied template's theme can be shared, but note reading progress cannot be shared.

## Verification record

- Baseline application test: correctly found 15/17 pages but proposed unrequested recall questions/answers and unnecessary cover/pager changes. New skill will state the exact artifact shape and preserve the existing shell.
- Final verification and known existing suite failures: `docs/superpowers/reviews/2026-11-09-bio-review-comic.md`.
