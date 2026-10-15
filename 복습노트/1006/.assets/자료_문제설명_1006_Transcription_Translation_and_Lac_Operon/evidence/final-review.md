# Independent final review — 2026-10-15

Scope: read-only review against the design, implementation plan and progress.md Ruling. Only this report is written. No implementation changes and no review.json approvals. No commit/cleanup is required under the explicit Ruling.

## Verdict

Changes need revision before publication/cheatsheet READY. Critical: 0. Important: 2 open, 1 resolved on recheck. Minor: 2. New 1006 p33, new 1008 p22 and changed 1008 p14 pass the semantic checks below. Existing-card preservation passes. This is a fresh review of current inputs, not a copy of historical pass metadata.

| Pack | Original-source visual review | Content review |
|---|---|---|
| 1001 (36) | PASS for included original exam stems/options against 5강 PDF 1–5; inspected replication/structure textbook images listed below | NEEDS REVISION: p2 invents a strongest-answer criterion after acknowledging ambiguity |
| 1006 (33) | PASS for included original exam stems/options against 5강 PDF 1–5; inspected mutation/translation/RNA-processing source images | NEEDS REVISION: p11 reverses a sufficient condition; p1 cites a prior blind result without identifying it as prior |
| 1008 (22) | PASS for included original exam stems/options against 5강 PDF 2–5 and 6강 PDF 1–4; inspected regulation source images | PASS for source.json stems/options and explanation option-by-option reasoning/checks; audits need revision |

## Important findings

1. **1001 p2 — do not resolve a defective single-answer question by changing its criterion.** In `explain-1001/review-1001-Chromosome_Changes_and_DNA_Replication/explanations/p2.html`, the check says option (3) cannot be the “가장 옳은 것,” and the recall asks why (2) is nevertheless the answer. Exam 5강 PDF 1 #2 says only “옳은 것은”, not “가장 옳은 것”. DNA template T can pair with RNA A, as the explanation itself acknowledges. Retain the original/card key, but label (2) as printed/intended and the literal single-answer condition as uncertain in the check and recall too. The source-visual review confirms this is not merely a transcription issue.

2. **1006 p11 — function preservation does not establish silent mutation.** In `explain-1006/review-1006-Transcription_Translation_and_Lac_Operon/explanations/p11.html`, the check concludes “서열이 같으면 기능도 같다 … 침묵뿐이므로 답은 (2)”. Exam 5강 PDF 3 #23 provides only little change in function, not unchanged sequence. Textbook print p109 explicitly says the functional consequence of missense depends on the amino-acid change. The earlier caveat is correct, but the final inference again supplies a missing condition. State printed/intended (2), with literal classification undetermined; do not use the silent example to exclude function-preserving missense.

3. **RESOLVED ON RECHECK — All three feedback audits do not faithfully record the actual criteria/changes.** `.pack/note-feedback-audit.md` q03 copies the processing-only q01 requirement and cites lecture PDF4, while quoting DNA methylation; add the actual transcription-versus-post-transcription criterion and PDF7–8 evidence. q15 cites PDF3 alone for acetylation, whose direct evidence is PDF7 (PDF3 supports histone/packaging only). q10's quoted sentence begins with the preceding paragraph's “출처: 평행 DNA 이중가닥 실험 연구”, which misattributes the new Tm statement; extract only its actual sentence and cite its own evidence. q04 says “기존 설명 충분” although a new RNAi warn paragraph is added in 1008; either record the scoped qualification as a modification or omit truly unnecessary duplicate prose. Also quote the newly added operative sentences for q02/q03 rather than only the old introductory definition. The 17 IDs are present, but presence alone does not prove accurate closure.

## Minor findings

- 1006 p1 says “독립 재풀이도 이 읽기로 (3)을 골랐어요.” Current `work/independent-blind.md` says no valid option/condition defect, not answer (3). Remove this process claim or explicitly identify its historical provenance. The scientific distinction (formal complement ACU versus actual stop-codon tRNA absence) is already present and should remain. In p1/p8/p20 final summaries, consistently say intended/printed answer rather than allowing the disclosed defect to disappear in an unqualified “답”.
- 1001 p1 explains option (1) as if it just said DNA uses four nucleotide kinds; the actual option says “9개의 가능한 … 단지 4개”. It is still not the definition of semiconservative replication, so the answer remains (3), but acknowledge the false nine-kind premise instead of paraphrasing it into a true general fact.

## Coverage and evidence

Personally viewed all 16 supplied original exam render pages: `work/exam-4강-{1..6}.png`, `work/exam-5강-{1..5}.png`, `work/exam-6강-{1..5}.png`. Compared included original stems and all options with current source.json: 1001 p1–p20, 1006 p1–p20, 1008 p1–p9. Included originals contain no source diagram requiring a hidden cropped inference. 4강 exam pages were additionally inspected; generated genetics cards are labelled generated, not claimed verbatim 4강 originals.

Reviewed all 91 current source.json stems/options and all 91 explanation option-reasoning/check sections: 1001 p1–p36, 1006 p1–p33, 1008 p1–p22. Other than listed findings, no answer-changing mismatch identified. This is not a claim that every sentence of all seven explanation sections was individually source-verified.

Personally viewed source images `work/slides-{4,5,6,7,8,9}.png` (5장 lecture PDF pages with those numbers), `work/book-{3,8,9,16,17,18,21,22,23}.png` (5장 textbook PDF pages; printed pp94,99,100,107,108,109,112,113,114). Verified direction and primer replacement in Fig5.8, proofreading discussion on print100, translation/release-factor figures, mutation Fig5.18, regulation Fig5.21/5.22 and RNAi Fig5.23.

- **1006 p33:** substitution is explicitly in the stem. (2) nonsense→stop→early termination agrees with lecture PDF6 and textbook print109 Fig5.18c; (1) frameshift, (3) silent, (4) missense, (5) transcription-initiation failure differ from the named classification. Existing p31 tests silent; new p33 tests naming in the opposite direction and is not a duplicate of that task. Independent answer 2 agrees.
- **1008 p22:** the stem explicitly supplies the typical one-protein information condition for each X/Y. (4) incorrectly converts multiple alternative mature species into multiple structural genes per mature molecule. Lecture PDF7 lacZYA and PDF8 alternative splicing, textbook print114 agree. Independent answer 4 agrees; source originals are preserved.
- **1008 p14:** reviewed current option 1 DNA accessibility/transcription, 2 splicing/post-transcription, 3 ribosome initiation/translation, 4 ubiquitin degradation/post-translation, 5 phosphorylation/post-transcription. Only (5) is mismatched. Textbook print112 Fig5.21 plus lecture PDF7–9 support the distinctions. This explanation repair preserves the existing problem/card key.
- 1001 p20 correctly discloses the printed exam #46 key 1 versus scientifically supported answer 3; no silent original repair.
- Ambiguous originals 1001 p7/p18 and 1006 p1/p2/p8/p11/p13/p14/p20 are flagged rather than their stems rewritten. Their source defects must not be erased by unqualified conclusions (findings above). Independent blind review confirms the distinction between intended answer and literal answer. 1001 p35's primer length is explicitly marked supplemental in the explanation; p36 needs the S-phase-to-sister-chromatid bridge and is not evidence of learner mastery.

## Seventeen-item audit and preservation

Read the bank's actual 17 stems and reasoned analyses and the feedback document. q01/q06 concern precursor processing versus a mature transcript's coding scope; q03/q04/q15 concern transcription target versus existing RNA and histone accessibility; q09/q12 distinguish substitution nomenclature from frameshift. q07 remains direction-sensitive, unselected and not an established weakness. Official answers remain null and reasoned answers are not official grades. q10's Tm qualification is scientifically plausible and correctly says temperature; however lecture PDF1's hydrogen-bond counts are indirect support, not an explicit Tm source. The bank reasoning is transparently labelled non-official. Do not describe this as a directly quoted lecture claim or as derived from the parallel-DNA paper.

Ran baseline-check.py verify with current baseline.json and changes.json: **PASS protection**. Inspected the checker: existing cards are compared as complete raw article strings, widgets by ID+full script text, protected files by hash; old topic IDs and hrefs must remain. Existing cards 36/32/21 are unchanged, new cards only 1006 p33 and 1008 p22. Visible diff adds scoped note paragraphs and does not delete prior lac motivation, basal-expression supplement or interactive links. MD additionally catches up existing HTML links. Link/ID sets alone would not prove exact multiplicity, so this report does not convert that check into a duplicate-widget/browser claim.

1001 has a documented reason to change (Tm comparison and proofreading direction); conditional unchanged path therefore need not be forced. No extra 1001 practice card was added. The 17-item coverage is present, but the audit corrections above are needed before declaring final status.

## Declined-to-judge / release boundary

No browser execution by this reviewer. `work/browser.json` appeared during review; its detailed results and image layout were not inspected here. Generated SVG diagram rendering, every textbook page outside the personally viewed list, every word of explanation prose, rollback failure injection and completed publish transaction are not certified. Main executor must check browser and current-hash publication separately. No evidence that old reviews may be reused after input changes: any repair invalidates this report's affected hashes and requires rebuild/recheck/review. Persistent failure must restore the full affected pack as specified. Current verdict is NOT_READY pending findings and remaining release checks.

## Reviewed current hashes

Paths below are relative to RUN. Fragment digest uses lexically sorted `filename:SHA256\n` lines encoded UTF-8. Stage hash names the reviewed staged HTML; final published output was not substituted for it.

- 1001 stage `explain-1001/review-1001-Chromosome_Changes_and_DNA_Replication/stage/67f0c1b8ab464028816263dce92b5365/문제설명_1001_Chromosome_Changes_and_DNA_Replication.html` SHA256 `b605f86f7b40b1f041bcac23f96000a04e0f9f28fa1c11a961d912fb13d6d87a`
  Source JSON SHA256 `d3191825229bd6d604cdf43ddb0b8b8cac979a0646f9add37cba8ab581a560ad`
  Fragment aggregate SHA256 `5b55bbd40c57b11cc51ffe5a2115f6c7c622e05c3a00fe825b528c687de7b505`

<details><summary>Individual fragment hashes 1001</summary>

```text
p1.html:11eda42d2723537b88c3ab85117d5ec14b74313233a3fa881389bfe92ef19033
p10.html:24890f7f1fe99ca1a5d9a51cd1180f78f147123c5d7425a5a9fc0b35a9e6bb36
p11.html:f072068e1abc79665bf12425ccefa9d5e1eff6a09cde2565cd165db25f3a6c52
p12.html:79ef0901c867ea267688ecd187c1ffcc45d796d2357b64c7cd5e112cfaae711b
p13.html:bc6710552ee5af7cf84b25d4baad15c38fe6a6f4d16715c973c8db6a99034e6f
p14.html:818a18e198d13bc11eb9516f1386ba1347ccc262681f34b26c37d8e0865257eb
p15.html:d9328e23dfd65ae6ccb0129bb4c67fbca411f92da6108a62635b789401ad687f
p16.html:7d601859882da81614762b64ab60a4a6d8e1a1d165121339c622c4a40d8f7744
p17.html:1520306827d016fca9a1cfdfec9c5aa40802edcb59d02f87facd22b21611a745
p18.html:c7e635e79643b6dc1bc973a234e5772acdafa33f4a5d2297c5bf00624bbc32f5
p19.html:af7b7b16f476bd856d2453ad4c0ad7648013411a6e9b8afeac7ea3b30757e60c
p2.html:66f6e5129f32e2b10ebce00ba7f8e1f7514499cf693b4352f3d51032e3239502
p20.html:3489996607c76e9e1076e29d76da9cd4e2da267856b52b35d7b65f0028fffe5f
p21.html:458ffbfad8c4c88d9e5d98f5f6aa7837f00ad75d66aa6ab7619ae66368bf7dd4
p22.html:f0f34784f8da491d8973bfb54803fa485b21913bafa338c4a3457c265985f624
p23.html:5e9dac86b21fa2fb634b5b96aca95aaaa963d804cb27d331074c6aa1039247e2
p24.html:790fa23b1adaf72215ce3e19ec28f84738909bed37ed40b0d05dcaf9acdb0035
p25.html:7059e75d4270c83447ee5ce4340ab525d367f5a96c805c8dd9fcde721f5916dc
p26.html:0ffc277cbb7fd0892bc15f21e31305a570739bcb58a3dc39e8f96da42dc19fad
p27.html:ce2d311b9301069e6be39bc9540581e76d9c751c9d7818889d44def67dfbae83
p28.html:2c34344e7cc05ce8a71811178c99508e5baa70a347fff760fc758309427b5280
p29.html:07088640bd0c954fca78f41a98da3af273967a8181927b2707753843d2242f72
p3.html:5a89a3b15ff4aa31001e536152201e9e00a81ed033ce4258451b2bed7e6491b9
p30.html:49a66f0d70d76bf680c86225347887ce0e2a7e19ec91150264fd3c86d71b7fc5
p31.html:81e538e86243b0b508932211da2eebf35c1ae59b406c4dfabf87a2d44c360f02
p32.html:c5274252740b3d42056e518606e14018626a912a30f6508be82df8f22b71e85e
p33.html:d66414024527175b2833ca684c3d720e750d23a5236cf37a83d8611a1eefd573
p34.html:35923c56860cd0d86f23b149daf7be7de71ef2b64c2995564027e122cefae82b
p35.html:99219cf8d5aeb735c98ab147b483174995dcf812ac73b16bdd7d12aa4c3f4a49
p36.html:081daf7c8fe623fe7e645ec04e0055204399e516d975fd11ba012767ccd63ef0
p4.html:79fa8ae469ae46341c70f908c3b44a685b4839295bf34df2ac9c068ee5fa1bd8
p5.html:9b4a7e364d2a476217ecc4a2dd3f4aa3299a3cd0e23d6b69e45ac0433faeb1b4
p6.html:3df0ce44031de5e767ce06717e8e49fbd208f4e16727a9f858ec751474a786a6
p7.html:4486fbe841492c32a47cfa23d4949a11ff79d83027f20f7e62968170e34e98ad
p8.html:4d56c73d6e9ee0aa867315fb78b6be7336bc7fa074af0d099773fa3cdbd3a773
p9.html:a16db4cf08de6a5a7faa7e51d9990fc225405701ff9b8e2f2e675520e2691ab3
```
</details>

- 1006 stage `explain-1006/review-1006-Transcription_Translation_and_Lac_Operon/stage/e1d65c88caf74988bf444eed396a0167/문제설명_1006_Transcription_Translation_and_Lac_Operon.html` SHA256 `7c07de7c11c5f479b0c25d825db59ed2d23834dd7a70d1a4a39e5d7c98f35fb3`
  Source JSON SHA256 `586defa8bffac8ae93ffe03c8f8fe8fd4f46a22a0b3d86a8ba8308b441d521d2`
  Fragment aggregate SHA256 `5570f8e284b6a98ebdda80722bf2816c0f81fef77da57b15868a182376cebf74`

<details><summary>Individual fragment hashes 1006</summary>

```text
p1.html:08efcd931daff644edc54d00d093bdeef345643a8aa052429214ac6e051db44e
p10.html:826d42dbf66c3a66f4f8a8354ba5eea7c34a23bf28213833eba322c3eb16b9a2
p11.html:0cd9518a6a7b5125a1d7987d2232cef41a92902afee0566eabb2a8c008537681
p12.html:e3e0f5cad08e4909f9756780e6a91b0d988921249598b301ec78079063c739de
p13.html:d001ce9e89962e002fe4dc834e11f48f66df229399425a3a76afd1b732e8c247
p14.html:f7bebee533f28a6b10ea5bb206ba619d29cf949090cffb4be4cdfa05188d4ade
p15.html:f5b354cc69e324a98131d970c3c96cbe9cb463a37b04af5af5d1d42d86764809
p16.html:d4ba167f26ad31dc3450c422a13a93c2498e684a97390f6605dfb3678ae07bcc
p17.html:c810a8142d86c23bfadc91c0ba9157442ec1b39b8c1af31646598f3ab706b135
p18.html:9b943954f784503e182eba324c8ef1acf66b8d9983abf087ff715711adc50d64
p19.html:4389041f1e36fbf7817471126ceff2011aea62756612fcf710fe965083683cd8
p2.html:b32d74f8d59321ba0e46184fa93ddb2e7728ae753708e389be3614eb1163a67d
p20.html:1c6dce2e4ff04d0ceaa5b79cd6c488aefe59905b559d9018d8b4e538b293e688
p21.html:11f16846cae7c24c40cd91c99356dd1b35198c4eb54cc3fb2c0325dd09f466d5
p22.html:f1dc434916e09c858e3a48287f7f00dec0aad3201735a8094d11f5bae9de3233
p23.html:764704a2155cfdf89d8de5c4a3986827de1bd648bd14bcaae03feaa8e8c9666e
p24.html:0e99ddbcfeac46f4712afd5218645666f2584481410cd5ecb503d12d429c88f3
p25.html:3bc6c9a9eaf61360bc6e6a3f6cf9fa543974759481adbf007aa4dc74820a98a5
p26.html:84ba5bf878eb2da1a3f223656d1deda1190b6044b5ffb8300a46f7e5b12d539d
p27.html:e7bb863cda836ba26714bc5b8a5300aab36cf8b55beafd06d5b351f4591d6231
p28.html:a6ae8c4ee2b28138f9b6e1424a58b9eec16831862fd64ae095096a4eeffeb1c4
p29.html:fa44fe6f925e354930ed6166d08d081da2cb74bf1d067c57a6f71f232e2423d1
p3.html:e0bb0322ba33decfd893f0658b0a58487d0eb0c1d324dc52bef7f496e6b38097
p30.html:77a189fd2ea1c6a7f008ccea9988d591886f440af5ef69708cdaa7a1bb302c5e
p31.html:f0200667a5db401d4741fc53dc258ab7b754baebc47be7558eeda7f7e8139555
p32.html:36ba670776e265c22b705f8d301f50614fd61b7715fc1b9022e29f640ed8261a
p33.html:b5dedd7a94a2ac22de1b401cbd19dd7821106b2c924245baede71c932b9cf12c
p4.html:2e9ea3df253e7f493cd2d857615790573b6660e89a93b08814fdbf4a8ed925c2
p5.html:94488728b96d8e3fc67df747965016513ea15eaecb832f9a2edce0e017e79085
p6.html:b769e6d41aa6b9e6ff2925661145510135b0e7aed885cca3d880db6a2d28c4a9
p7.html:44a6decf8889e78d09d8fa13cf5faa5b2b06870b81eaa85b2716edd2ef61dbc4
p8.html:869d17c92588244a28f68efc1a504221b9f0fdbbbfd5e84f670a1b791beca8be
p9.html:6160912069acc60ffa54342d8dd10f9ffd6e01c34ec5b8a31e0dd67f6d942caf
```
</details>

- 1008 stage `explain-1008/review-1008-Gene_Regulation_and_DNA_Cloning/stage/2f0d1f91b7ce44f2a68735f8fab93fed/문제설명_1008_Gene_Regulation_and_DNA_Cloning.html` SHA256 `5263c0a024f9cf63e0ae04f40ab9dcbc01cd809ac3f67d356656f5b6086c951f`
  Source JSON SHA256 `f5a995d6fdad5071f76d95c5a15bf20ed537a25a05c83026ab1a674e843a76a4`
  Fragment aggregate SHA256 `e4b56eec7253a4c8eb65470da632d26358b3e2a2c525769710668a5a3bbb3929`

<details><summary>Individual fragment hashes 1008</summary>

```text
p1.html:42ddf2a43cfed9c42c2feef361d211fa9316a9c72b5e2b410a9838e322b5857a
p10.html:fe8237e0ef83aa15c78d54410faf3f834e9729ecc75aa8d41d6f366dda0163db
p11.html:f564d874c32cf9d6680991cf95e65edf743d6c0f5ffe6d5bd7302c0952faba7c
p12.html:549823ca11cfd7b96ef372a0ba20afd8cae77d9f21d15ace67f6220e1dc74095
p13.html:79c023d97624bc7c4b046254eb07b04a031fc186bfc155e52257256ad62f70d7
p14.html:b08278e4078b14f53483a50ee518f8177e6057577ec86b47ab7316416e005b47
p15.html:09f23b298980c37a68b4902b71d3a1d4efd7d2085d874907b7dba8eafc9100b6
p16.html:ef75dd60f955a82f7ad9d932f8eda3e5c6b8785a792d5dd46a7c505b37627a0b
p17.html:84de9429554cc02719571b1156803720c9babcce8e4a21c93c3ecdfbccac6710
p18.html:b2c457dc6dc764669a8ab29b365491bb6380528e7f377af152817492f86003ab
p19.html:1d6ae19508b9c3e2044f1aa9ba57653f32a9b3972e0b7f51a2744963952fc8e4
p2.html:7b5a980c4389b47496ffa85fafefda1ee3569045bf448d8f382ab6198e3abe9a
p20.html:4216b9102daf23806884eaa1421adbbe98b8a1c16bb0d8dd65eb4a5787700b9c
p21.html:5209bd0cd8aa41ea9a6fa4b711280609eca19769470dac51fe8fb52eaa3a89c4
p22.html:4e2e1be8778b0fc4e5d3536874f9a736c60c71880d85b435a0d424185c408185
p3.html:c22a9ad849860870c89d42588299fcedfee9bbbf988e56d5bcbd7e7c04ba6585
p4.html:5e39fdc7a9d0b29bc9650bd32df419c1e2458015868050c79d099ee8d5f9693c
p5.html:7f733543f7282471e8b8ce94b8bd2cedfd1bc0d3787372c50693c995479119a2
p6.html:34c660662cbb1658cb4729d0b234d39084b4e6bfcacaa17218d4222544295fda
p7.html:9f8f1551b9b1fe4e984714ec1843c6bc2932c5f5cfec02e8d61773f8413c69d9
p8.html:4ee9413b7f052420fa2d8db01a0fb94eb9e7b20a5e26ca759eafaa0c7ac5c0c8
p9.html:0f6507a41464d888489c396452bb5ef14204b2c23683e664bf371650a497b858
```
</details>


## Audit repair recheck (same review turn)

After the executor reassembled the audits, personally re-read q02/q03/q04/q10/q15 in all three final `.pack/note-feedback-audit.md` files. q03 now has the correct criterion and PDF7–8 evidence; q15 has PDF7–8; q10's quote no longer includes the parallel-DNA attribution; q04 is 本文反映 in 1008; q02/q03 quote the operative added paragraphs. Important finding 3 is resolved. Historical text above records the observed problem, not the final audit state. PE explanation findings remain open and require a separate affected-fragment review after repairs.

- `복습노트/1001/.pack/note-feedback-audit.md` SHA256 `02de9086086af1497ffc478a0e579c842252304b13bd4abb08fb1639d2b0f86b`
- `복습노트/1006/.pack/note-feedback-audit.md` SHA256 `281dbc6e4732dbda26b53b20baedf157a8000114b93005f4fb349bb93fefb6a0`
- `복습노트/1008/.pack/note-feedback-audit.md` SHA256 `0a00627aafaa65ab8112a99d8a082eb45a565afc534f6fa7c1fe3d85e921da2b`
