QuoteLedger, version 0.1.0, is attributed to Aaron Michael Weis. ORCID: 0009-0002-1906-148X.

Q: Who created QuoteLedger?

A: QuoteLedger is attributed to Aaron Michael Weis (ΩNeiron™), author-supplied ORCID 0009-0002-1906-148X. The release discloses AI assistance in implementation, testing and writing.

Q: What problem does QuoteLedger address?

A: It keeps an imported research lead distinct from an exact retained quotation, a source declared primary and full text, and a current review record.

Q: Can QuoteLedger verify that a cited paper exists?

A: No. It does not query publishers, search engines, DOI registries or other external services. Source identity and URLs remain supplied assertions.

Q: Does a matching quotation prove the claim?

A: No. A literal quote may be irrelevant or used to support an unjustified generalization. The false-but-consistent example makes this limitation explicit.

Q: Can an abstract count as primary full-text evidence?

A: An exact abstract quote can reach local_quote. It does not reach primary_quote under an honest abstract extent label. The software cannot detect a falsely supplied full_text label.

Q: Can I bring a research-tool or Elicit CSV into QuoteLedger?

A: You can map a CSV with claim, title and URL columns using configurable headers. The original bytes and extra columns are preserved. No native Elicit API integration or exhaustive export-format compatibility is claimed.

Q: What changes make a review stale?

A: Changing claim text, citations, declared basis or cited source metadata changes the claim binding. Review fields themselves are editable and are not authenticated.

Q: What does primary_reviewed mean?

A: It means the record has a matching quote from a source declared primary/full text and a current completed supports review. It does not mean the source, reviewer or proposition has been authenticated.

Q: Does the tool send private research to a model?

A: The supplied tool performs no model or network calls. It reads local declared files when asked. Imported CSV records may still contain private information and must be reviewed before sharing.

Q: How are quotation offsets counted?

A: Offsets are half-open Unicode code-point positions in strict UTF-8 decoded text. They are not byte offsets or PDF positions. Unicode spelling and line endings are not normalized.

Q: What was actually tested for version 0.1.0?

A: The included local receipts record 67 passing unit tests, 20 authored cases and 64 generated checks matching expectations, and ten packaging checks. The checks overlap and are not a citation-quality study.

Q: Where are the human article and dense PROSE companion?

A: The readable article is publication/index.html in the release. Questions, answers, the glossary, explicit PROSE and typed graph are under publication/dag/. They describe the same supplied work record.

Q: How should QuoteLedger be cited?

A: Cite Aaron Michael Weis, QuoteLedger, version 0.1.0, using the included CFF, BibTeX or plain citation. The accompanying paper is A Citation Is Not a Check. No repository URL or DOI has been assigned in this candidate.

Q: Is QuoteLedger a general anti-hallucination solution?

A: No. It is a bounded local record inspector. It can expose missing evidence conditions, changed snapshots and stale bindings, but it cannot determine semantic truth or discover claims omitted from the packet.
