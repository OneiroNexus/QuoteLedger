# Limits and threat boundary

1. **Not a hallucination detector.** Exact quotation does not establish truth,
   semantic support, relevance, generalizability or complete coverage.
2. **Supplied source labels.** Primary/full-text labels and URLs are assertions.
   A fabricated local source can match its hash. Citation existence, metadata
   identity, source quality and licensing are not verified.
3. **Self-reported review.** A false, current review can pass. There is no
   signature, authenticated reviewer, trusted time or immutable ledger.
4. **Explicit claims only.** Unlisted claims in prose cannot be discovered by
   this packet inspector. A claim with no citation can remain a lead.
5. **Text snapshots only.** PDF extraction, OCR, tables, equations, section
   context and publisher version recovery are not implemented. Save extraction
   details separately. A quote may match multiple locations.
6. **Literal matching.** Line endings and Unicode spelling remain significant.
   A harmless formatting change can invalidate an old binding. No semantic or
   normalization equivalence is inferred.
7. **Metadata-only is not a read.** Without a supplied observation or `--root`,
   no source bytes are inspected. Link-only citations remain unverified even
   when another citation raises the claim's observed basis.
8. **Local filesystem trust.** The adapter rejects observed symlinks below an
   explicit root and reads regular files, but is not hardened against every
   parent-path race or hostile host. No continuous monitoring occurs.
9. **Output failure.** Interrupted writes can leave partial new files. Stdout
   delivery may fail. Shell redirection can truncate a file before the program
   starts and is outside the no-overwrite behavior.
10. **Privacy.** Import logs preserve all CSV columns, which may contain private
    material. Reports still expose identifiers, counts and fingerprints even
    when claim text is omitted. No secret detector or anonymizer is included.
11. **Bounded, not security-certified.** Packet and snapshot limits are defensive
    bounds, not measured denial-of-service resistance. CSV parsing also inherits
    the Python CSV field-size limit. See [REVIEW_STATUS](REVIEW_STATUS.md) for
    tested environments and the Windows symlink coverage gap.
12. **No external integration.** There is no Elicit API, online DOI resolver,
    crawler, LLM, database writeback or publication API.

The `false-but-consistent` fixture is intentionally accepted under the record
contract. It is essential evidence of this tool's limitation, not an example
to approve in real research.
