# QuoteLedger

By Aaron Michael Weis (ΩNeiron™) · https://orcid.org/0009-0002-1906-148X · Version 0.1.0

A reference at the end of a sentence can make unfinished research look finished. The paper might be real. The quoted sentence might be real too. Neither fact tells us whether someone opened the right version, read beyond the abstract or checked that the passage supports the conclusion.

QuoteLedger gives that unfinished work a place to live. A research lead stays a lead until its record contains more. You can retain a text snapshot, locate the passage you intend to quote and check that the recorded bytes and exact passage still match. If a human reviews the claim, that judgment is tied to the claim and source records they inspected.

Imagine a fictional report that says eight specimens took twelve minutes in one trial. Turning that into “the method always finishes every job in twelve minutes” changes the meaning. QuoteLedger can show that the quotation is intact and the review is current. It cannot make that leap in meaning valid. The package includes this deliberately wrong example so that a successful check is never confused with proof.

The useful distinction is between a link, an exact local quotation, a source declared primary and full text, and a completed review. Those are different records, not increasing confidence scores. An abstract can remain useful without being mislabeled as a full-text check. A changed claim can keep its source while losing the applicability of an old review.

The small Python tool runs locally without a model or network connection. Its CSV intake preserves original bytes and extra columns rather than throwing away context. It can prepare pending review records and produce JSON or a readable report. It does not rewrite the original packet, fetch papers or approve research on your behalf.

The accompanying working paper explains the contract and its limits. The recorded release passed 67 unit tests, matched 20 authored cases and 64 generated checks, and passed ten packaging checks. These are synthetic implementation checks, not a measurement of better real-world citations.

The goal is modest and practical: make it easier to see what has actually been checked and what still deserves a person's attention. The structured companion keeps the detailed records available without making this introduction read like a database.

[PROSE / DAG companion](dag/index.html)

© 2026 Oneiron Holdings LLC. Owner-review release candidate; public software, document/data and model-training terms have not been selected.

Aaron Michael Weis supplied direction, requirements and attribution. OpenAI's assistant through Notion AI assisted implementation, testing, packaging and writing. Human author review remains distinct.
