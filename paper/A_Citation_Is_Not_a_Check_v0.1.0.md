# A Citation Is Not a Check
## Evidence Depth and Snapshot-Bound Quotations for AI Research

**Aaron Michael Weis (ΩNeiron™)**

ORCID: [0009-0002-1906-148X](https://orcid.org/0009-0002-1906-148X)

**Working methods paper · QuoteLedger v0.1.0 · Prepared 17 November 2026 (America/Denver)**

### Abstract

An AI-assisted research note may contain a plausible claim, a real-looking citation and an exact quotation while leaving several questions unresolved: was the cited work opened, was full text available, did the retained bytes change, and does the passage actually support the claim? Collapsing these questions into a single “verified” label makes a research trail difficult to inspect. This paper presents QuoteLedger, a small local tool that separates a research lead, an exact local quotation, a quotation from a source declared primary and full text, and an explicit human review bound to that claim's records.

The implementation imports configurable CSV rows without promoting them beyond leads or discarding unused fields. It compares full snapshot fingerprints and literal Unicode-code-point spans, records source-role and extent declarations, and exposes stale review bindings. It does not retrieve sources, authenticate source labels or determine semantic entailment. A deliberately unsupported universal claim can receive the strongest record label when its fictional reviewer approves it; that negative case is part of the contract.

In the recorded environment, 67 unit tests passed. Twenty authored synthetic cases and 64 deterministic generated checks matched their expected behavior; ten packaging checks passed. These are overlapping local implementation checks, not a citation-accuracy study, hallucination-reduction result or independent validation.

The accompanying publication separates a readable article from a visibly linked PROSE/DAG companion. Questions, answers and explicit attribution relationships live in that companion and derive from the same work record. The contribution is an inspectable evidence-depth contract, runnable local reference tool and reproducible record-level checks.

> Working principle: preserve the useful lead, but do not silently promote the lead into a source check—or the source check into proof of the claim.

### Keywords

Retrieval-augmented generation; citation reliability; research evidence; quotation provenance; source inspection; human review; reproducible software.

### Authorship and assistance

The author supplied the direction, requirements and attribution. OpenAI's assistant through Notion AI assisted implementation, test construction, packaging and writing. Human author review remains distinct. This is a working methods paper, not a peer-reviewed publication or degree thesis.

<!-- PAGE -->

## 1. The problem: several checks hiding behind one citation

Consider a researcher who exports an AI-generated literature table. One row summarizes an abstract; another was assembled from a secondary account; a third points to a paper the researcher has read in full. If all three become sentences with references, their different evidence states can disappear from the working record. A reader sees citations, but the author may no longer know which passages were actually checked.

Three different mistakes can follow. A source may be misidentified. The right source may be attached to the wrong statement. Or a real quotation may be used to support a conclusion broader than the passage warrants. A fourth problem concerns time: a review of yesterday's claim may be copied onto today's revised wording or changed snapshot.

QuoteLedger addresses a narrow part of this workflow. It makes supplied evidence states and exact retained text inspectable. It does not replace bibliographic resolution, critical reading or semantic support assessment. Keeping those responsibilities separate is more useful than producing a stronger-looking badge.

### Related work and positioning

CiteFix studies citation correction after RAG generation. Its methods compare factual points with retrieved documents using lexical, semantic and model-based approaches. This is close to the practical problem of attaching the right source to a statement. QuoteLedger does not choose or repair citations and does not reproduce CiteFix's experiments.[^https://aclanthology.org/2025.acl-industry.23.pdf]

Ponnuraj's study of retrieval jitter distinguishes document overlap from continuity of exact evidence spans. That distinction motivates recording more than a document identifier. QuoteLedger uses a full raw-text snapshot hash and exact span comparison; its contract is not the same as that study's normalized-span measurement, and neither literal identity measure alone establishes semantic equivalence.[^https://aclanthology.org/2026.evaleval-1.35.pdf]

CiteTracer addresses bibliographic citation hallucination through source retrieval, field comparison and additional handling of ambiguous cases. QuoteLedger neither determines whether a citation exists nor classifies a paper as genuine or fabricated. A locally consistent packet may still contain a fabricated source. These tools therefore operate at different inspection boundaries.[^https://arxiv.org/html/2605.08583v3]

These works show an active research problem, not an empty field awaiting its first solution. The present contribution is a bounded workflow contract rather than a claim to have invented citation validation, checksums or human review.

### Research questions

- **RQ1:** Can imported research rows retain their original information without being silently upgraded to checked primary evidence?
- **RQ2:** Can a local implementation distinguish exact snapshot/span identity, declared source extent and a current review record?
- **RQ3:** Can implementation checks expose both record failures and the limit that an internally consistent approval may still be wrong?

No comparative user study, live research-service integration or evaluation of generated answers is reported.

<!-- PAGE -->

## 2. An evidence-basis contract

A packet contains sources and claims. A source names an identifier, supplied title and URL, role, inspected extent, optional relative snapshot path and optional SHA-256. A claim names its text, declared basis, citations and optional review. Each citation either points to a source as a lead or supplies a literal quotation with a half-open offset range.

The parser rejects unknown fields, duplicate JSON keys, duplicate identifiers, malformed digests, unknown references and invalid values. It does not infer missing relationships. Supplied URLs are retained as labels and are never fetched.

### Four labels, not four confidence scores

| Observed basis | Required record condition |
| --- | --- |
| `lead` | A supplied assertion. Its citation may be link-only or absent; no source read is implied. |
| `local_quote` | At least one quotation exactly matches an observed UTF-8 snapshot whose complete byte fingerprint matches the declaration. |
| `primary_quote` | A matching quotation whose source is additionally declared `primary` and `full_text`. Those classifications are not authenticated. |
| `primary_reviewed` | The preceding condition plus a current, completed review declaring support for the claim. |

The ordering describes required record conditions. It is not a probability scale or a judgment of study quality. A source labeled primary can be fake; an exact quotation can be irrelevant; a completed review can be wrong.

One matching citation can establish a claim's observed basis. Other attached quotations are still inspected and their failures remain findings. Link-only citations are not automatically checked because another citation is valid. Every citation's result remains visible.

### Formal inspection rule

For source s, let B(s) be the supplied byte snapshot and h(s) its declared fingerprint. A quotation q with offsets a and b matches only if SHA-256(B(s)) equals h(s), strict UTF-8 decoding succeeds, the bounds lie within the decoded string, and that string's slice [a:b] equals q literally.

Offsets count Unicode code points, not bytes, UTF-16 units, grapheme clusters or PDF positions. Line endings, whitespace and Unicode spelling remain significant. Python's ordinarily permissive slice truncation is not accepted as a valid out-of-range quote: the endpoint must be within the observed text.

The snapshot may be text extracted from a PDF. Its hash identifies that text snapshot, not the original PDF, publisher or extraction completeness. Original files and extraction details belong in an accompanying research record.

### Import without upgrading

CSV intake requires mapped claim, title and URL columns. Every row begins at `lead`, with unknown source role and extent, no snapshot and no invented review. Exact original CSV bytes, all rows, all columns and the selected mapping are retained. The adapter does not assume that a research service's citation field certifies a primary-source read.

<!-- PAGE -->

## 3. Snapshot binding, review and results

The core receives a packet and optional byte observations and performs no filesystem or network I/O. The command-line adapter can read declared snapshots under an explicit local root. A metadata-only invocation never implies that source bytes were read.

### What a review binds

A review has a separate completion boolean, a support/contradiction/uncertainty decision, reviewer label, rationale and fingerprint. A generated plan contains only pending records. Completion requires a nonblank label and rationale; it does not authenticate either.

The fingerprint covers all fields of the claim except the review itself, together with its cited source records sorted by source identifier. A distinct `QuoteLedger.Claim.v1` domain prefix and zero byte precede the deterministic project JSON encoding. Changing claim wording, citations, declared basis or cited source metadata makes the old binding stale.

The encoding uses sorted object keys, compact separators, UTF-8, preserved array order and a trailing line feed. Unicode is not normalized. This is not a claim of RFC 8785 conformance. Unrelated claims and unused sources are outside an individual claim binding. The report separately fingerprints the complete structured packet; the CLI additionally reports the raw input-file hash.

Review fields are outside their own binding to avoid circularity. They remain editable. Someone can invent a reviewer, change the decision or recompute a digest. The mechanism helps expose stale reuse; it is not a signature, a trusted timestamp or an authenticity detector.

### A visible policy rather than a hidden interpretation

| Result | Meaning |
| --- | --- |
| `NO_CLAIMS` | No supplied claim; the policy is not met. |
| `ATTENTION_REQUIRED` | At least one checked record, quotation or review inconsistency remains. |
| `CONSISTENT_RECORDS` | A nonempty claim set contains no checked inconsistency. A stronger evidence-basis policy may still be unmet. |

The requested policy is separate from the result. For example, a correctly labeled abstract quotation can be consistent while failing a requirement for primary full-text quotations. A completed “contradicts” or “uncertain” review remains a finding. Pending review does not count as completed support.

The default audit policy requires only `lead`; exit zero under that default must not be interpreted as primary verification. With `--require primary_quote` or `--require primary_reviewed`, every claim must reach the requested basis without findings. Exit one reports an unmet policy; exit two reports invalid or unavailable input/output.

> A reproducible check should say what it checked. “The bytes and span match” is a useful statement without being renamed “the claim is true.”

<!-- PAGE -->

## 4. Cases that make the boundary concrete

### A research lead remains useful

The included CSV contains two explicitly fictional research leads and extra scope/note columns. Intake retains the original bytes and all fields but produces no source-read claim. An audit requiring primary quotation does not pass. The importer has not rejected the research; it has preserved the work still to do.

This distinction is useful for literature tables, exploratory notebooks and AI-assisted search. Uncertainty can remain an actionable queue rather than being concealed by a citation marker.

### An abstract is not a full-text inspection

Two fixtures contain the same matching quotation. One declares the source primary/full text; the other declares an abstract. The former can reach `primary_quote`; the latter reaches only `local_quote`. Claiming primary full-text evidence for the abstract produces a declared-basis finding.

This comparison tests label handling, not the program's ability to identify an abstract. If the operator falsely labels the abstract full text, the software cannot discover the false label from these records alone.

### A changed source or changed claim invalidates different things

Adding one line to a retained snapshot changes its full-file hash, even if the quoted passage itself is still present. The old snapshot declaration therefore fails. This conservatively binds the quotation to the precise retained text rather than just the recurring sentence.

Changing the claim while retaining source bytes produces a different failure: the quotation may still match, but an old review binding becomes stale. A fresh source match must not silently carry forward a review of a different proposition.

### A wrong assertion can still be internally consistent

The synthetic source says:

```text
In trial A, 8 fictional specimens required 12 minutes.
```

The negative fixture claims:

```text
The method always finishes every real-world job in 12 minutes.
```

A fictional reviewer supplies a current “supports” decision. The quote and snapshot match, the role/extent labels satisfy the contract, and the review binding is current. The observed basis becomes `primary_reviewed`, although the universal claim is unsupported.

> This accepted negative example is not a truth-detection success. It demonstrates that a mechanically consistent research trail can record a bad judgment.

The fixture is explicitly marked synthetic and semantically negative. No real person is represented as having approved it.

<!-- PAGE -->

## 5. Evaluation and observed results

The evaluation used only included synthetic records and exact expected outcomes. No private research exports, real participant data or research-service accounts were used. Implementation and test construction were AI-assisted, so the results are not independent validation.

### Recorded environment

The reference run used **CPython 3.13.15 on Linux x86_64**. Its local receipt began at `2026-11-18T02:54:59.123537+00:00` and ended at `2026-11-18T02:54:59.822172+00:00`. These are recorded system times, not externally attested timestamps. Other Python versions and platforms remain intended compatibility targets.

| Check family | Observed result |
| --- | --- |
| Unit tests | 67 passed; no failures, errors or skips. |
| Authored synthetic cases | 20 matched the expected basis, findings and requested-policy result. |
| Generated checks | 64 matched the expected basis, findings and requested-policy result. |
| Packaging checks | 10 passed, including isolated standalone execution and byte-identical zipapp rebuilding. |

The authored cases include link-only and absent citations, primary/secondary/synthesis roles, abstract-only material, unread or changed snapshots, incorrect spans, stale reviews, contrary reviews, pending review, an additional broken citation and the false-but-consistent negative case.

The generated set has sixteen deterministic variants in each of four families: unchanged records, changed source bytes, a changed claim after review, and a changed quotation after review. These variants are correlated regression exercises, not independently sampled research tasks.

The unit suite also checks strict schemas, duplicate fields, bounded paths, Unicode code-point offsets, exact line endings, out-of-range spans, CSV preservation, HTML escaping, no-overwrite behavior and refusal of observed source symlinks.

### Reproduction evidence

The receipts retain individual unit outcomes, every authored/generated result, environment details and tracked source/fixture fingerprints before and after validation. The tracked files remained unchanged during the run. Fixture regeneration matched the included frozen corpus.

The standalone zipapp ran outside the source directory with Python isolation enabled. Checks exercised both successful quotation inspection and the nonzero policy result for a lead. CSV bytes, pending review state and existing outputs were preserved. A rebuilt app matched the original app bytes. These are local consistency checks, not an independent security audit.

Some unit tests re-exercise the authored and generated corpus. The totals must not be added into an accuracy rate. The work does not measure reduced hallucinations, better citations, faster reviewing, real-world reliability or general source-authentication performance.

<!-- PAGE -->

## 6. Human-first publication and practical use

QuoteLedger fits between a research intake and a publication or context handoff. It can be used to preserve a literature-table export, inspect retained passages, distinguish abstracts from declared full-text reads, and identify reviews that no longer bind a revised claim.

It is not a RAG engine, automated reviewer or replacement for reading a paper. An application could adapt its reports to a review queue, but no live research-service integration or automatic publication gate is implemented here.

### One work, two readable surfaces

The accompanying article introduces the problem naturally. It does not ask a human reader to navigate a pile of identity tokens or repeated question variants. A clearly linked PROSE/DAG companion carries the explicit work facts, author relationship, claims, evidence references, glossary and supplied questions and answers.

Questions and answers are explicit graph nodes, connected by an `answers` relation; questions connect to the work with an `about` relation. The graph also connects claims to the work and supplied evidence records to the claims they concern. The chosen directions form a DAG for this local representation. General citation networks are not claimed to be acyclic.

The human article, structured files and citation formats derive from the same supplied record. Q&A is explanatory content, not independent evidence, and no supporting relation is inferred merely because an answer sounds confident. The companion is visible to readers; it is not a contradictory crawler-only page.

The private publication generator is not part of this freebie's source release. Its generated work record and output checksums are included, so the publication facts and relationships remain inspectable without disclosing the private generator.

### Threat boundary and privacy

Supplied text is data. The core does not call a model, run source code, follow URLs or write inputs. The CLI reads bounded snapshots and creates only new outputs. It limits packet files to 4 MiB, individual source reads to 4 MiB and aggregate source bytes to 16 MiB. These are defensive bounds, not measured denial-of-service resistance.

The file adapter rejects observed symlinks below an explicit root and requires regular files. It is not complete protection against hostile concurrent filesystem actors or parent-path replacement. The host, resolved root and its ancestors must be trusted. Files are not monitored after inspection.

Default reports omit source paths, titles, URLs, full quotations and reviewer prose. IDs, fingerprints and findings can still reveal information. CSV intake logs intentionally retain all original columns, which may contain sensitive material. A report or import folder is not automatically safe to publish.

Interrupted output can leave an incomplete new file. Shell redirection is outside the no-overwrite behavior. Original source files, evidence rights and author approval remain operational responsibilities.

<!-- PAGE -->

## 7. Reproduction, next study and conclusion

From the source folder:

```text
python -m unittest discover -s tests -v
python tools/validate.py --output new-validation
python tools/build_zipapp.py --output new-quoteledger.pyz
```

The README documents the packaging check and command-line workflow. Validation creates a fresh output directory rather than overwriting a prior receipt. The source tool and standalone app use Python's standard library; optional PDF rendering uses ReportLab and local fonts.

### What a stronger next study would require

A useful follow-up would use consented research tasks with independently labeled source identity, extent, quote location and claim support. It should measure review effort, unsupported claims retained, correct claims unnecessarily blocked, stale approvals caught and missing research rows. A comparison should distinguish mere link checking, exact-snapshot checking, semantic citation verification and human review, rather than combining them into one score.

This release does not contain that study. It establishes a reproducible local baseline and states where its record contract stops.

### Conclusion

QuoteLedger makes a narrow promise: a research lead need not be discarded, but it should not silently acquire evidence it does not have. Exact snapshots, explicit source-extent declarations and current review records answer different questions. Keeping them separate makes research easier to inspect without pretending that a matching quotation proves a conclusion.

### Selected references

[1] Maheshwari, Harsh; Tenneti, Srikanth; Nakkiran, Alwarappan. **CiteFix: Enhancing RAG Accuracy Through Post-Processing Citation Correction.** ACL 2025 Industry Track, pp. 310–317. [Primary paper](https://aclanthology.org/2025.acl-industry.23.pdf).

[2] Ponnuraj, Punitha. **Document Overlap Is Not Evidence Continuity: Measuring Retrieval Jitter in Citation-Based RAG Evaluation.** EvalEval 2026, pp. 221–226. [Primary paper](https://aclanthology.org/2026.evaleval-1.35.pdf).

[3] Li, Mingzhe; Lin, Zhiqiang; Ma, Shiqing. **Source or It Didn't Happen: A Multi-Agent Framework for Citation Hallucination Detection.** arXiv:2605.08583v3, 2026. [Primary manuscript](https://arxiv.org/html/2605.08583v3).

These sources were inspected for the cited scope distinctions. Their experiments were not reproduced. This is not a systematic literature review or a novelty determination.

### Associated project records and release state

R1. Weis, Aaron Michael. **QuoteLedger**, v0.1.0. Source, command-line tool, record contract and examples. Repository and DOI remain unassigned.

R2. `evidence/reference-run/validation.json`, individual outcome files and `evidence/packaging.json`. Local observations, not independent attestations.

R3. `publication/dag/source-record.json`, graph, Q&A and publication checksums. Generated factual companion to the readable article.

The owner must approve the release and choose effective software, paper/data and training terms. No license grant, public repository, archive deposit or model-ingestion event is asserted by this paper.