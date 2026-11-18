# QuoteLedger v0.1 — record contract

## Input and identity

The CLI accepts strict UTF-8 JSON, at most 4 MiB. Duplicate JSON fields,
nonfinite numbers, unknown fields, duplicate IDs, unknown source references and
malformed values are rejected, not repaired.

The packet has exactly `schema`, `sources`, `claims`. The schema literal is
`quoteledger.packet.v1`. There can be at most 1,000 sources and 1,000 claims;
each claim has at most 100 citations, with at most 10,000 citations total.

IDs match `[A-Za-z][A-Za-z0-9_.:-]{0,79}`. Source IDs and claim IDs have separate
namespaces. Array order is preserved. No Unicode or line-ending normalization
is applied.

## Sources

Each source has exactly:

| Field | Contract |
| --- | --- |
| `id` | Unique source identifier. |
| `title` | Supplied, nonblank title, at most 2,000 characters. |
| `url` | `null` or an HTTP(S) URL without credentials or whitespace. Never fetched or verified. |
| `kind` | `primary`, `secondary`, `synthesis` or `unknown`. Supplied classification. |
| `extent` | `full_text`, `abstract`, `snippet`, `summary` or `unknown`. Supplied classification. |
| `path` | `null` or a restricted relative snapshot path. |
| `sha256` | `null` or 64 lower-case hexadecimal characters for exact snapshot bytes. |

Path and digest must either both be present or both be absent. Paths have at
most 12 slash-separated components from ASCII letters, digits, `_`, `-`, `.`;
empty, dot and dot-dot components are rejected. Absolute paths, backslashes and
drive prefixes are not accepted. This restriction is not a sandbox.

A snapshot is retained **text**, not necessarily original PDF bytes. If text
was extracted from a PDF, preserve the PDF and extraction details separately.
A hash of extracted text does not identify the original PDF, its publisher or
the completeness of extraction.

## Claims and quotations

Each claim has exactly `id`, `text`, `declared_basis`, `citations`, `review`.
Text is nonblank and at most 10,000 characters. Basis is one of `lead`,
`local_quote`, `primary_quote`, `primary_reviewed`.

A citation has exactly `source_id`, `start`, `end`, `quote`.
For a link-only citation, the last three values are all `null`. Otherwise the
quote is nonblank (at most 64,000 characters) and offsets are integers, not
booleans. The range is half-open: `snapshot[start:end]`.

Offsets count **Unicode code points in the strictly decoded UTF-8 text**, not
UTF-8 bytes, display cells, UTF-16 units, grapheme clusters or PDF positions.
`0 <= start < end <= len(decoded_snapshot)` must hold to match. The declared
upper bound is additionally limited to 4 MiB. Exact comparison includes spaces
and line endings. Duplicate identical citation records within a claim are
rejected.

The full observed snapshot must match its SHA-256 before any quote is credited.
A match does not determine whether that quotation supports the claim.

## Reviews

`review` is `null` or has exactly `completed`, `decision`, `reviewer`,
`rationale`, `binding`. `completed` is a boolean. `decision` is `supports`,
`contradicts` or `uncertain`. Completed reviews require a nonblank reviewer
label (up to 1,000 characters) and rationale (up to 4,000). Pending reviews may
leave those empty. There is no authentication or reviewer-time field.

The binding is:

```text
SHA256(b"QuoteLedger.Claim.v1\x00" + encode({
  "claim": all claim fields except "review",
  "sources": cited source records sorted by source ID
}))
```

In this display `\x00` means one zero byte.
`encode` is UTF-8 JSON with sorted object keys, compact separators, no nonfinite
numbers and one trailing LF. Array order and Unicode spelling remain intact.
This is a documented project encoding, not a claim of RFC 8785 conformance.

Changing the claim, citations, declared basis or cited source metadata makes an
old review stale. Unrelated claims and unused sources are not part of a claim's
review binding. The entire report packet fingerprint separately uses
`QuoteLedger.Packet.v1` plus a zero byte and the entire structured packet.
The CLI also reports the raw input-file SHA-256.

Review fields themselves are outside the claim binding. Anyone able to edit
the records can invent a review or recompute a binding. No human identity,
authentic execution, trusted time or legal approval is established.

## Decision rules

1. Every claim begins at `lead`, even if no citation has been supplied.
2. A matched snapshot plus exact span raises the observed basis to at least
   `local_quote`.
3. One such citation with declared `primary` and `full_text` raises it to
   `primary_quote`. No role or extent is inferred.
4. A nonstale, completed, `supports` review raises that to `primary_reviewed`.
5. Every nonmatching attached quoted citation remains a finding; a valid
   citation does not conceal another broken citation.
6. A stale review, a completed contrary/uncertain review, or a declared basis
   higher than observed creates a finding.

This is a maximum **record basis**, not a tally of independent supporting
studies. A single matching quote can provide the level; additional link-only
citations are not automatically checked. The report lists each citation.
Coverage is only over claims supplied in the packet, not a paper's unlisted
claims.

`policy_met` requires at least one claim, every claim at or above the requested
basis, and no findings. A pending review is not by itself a finding. A pending
review cannot meet `primary_reviewed`.

Results:

- `NO_CLAIMS`: empty claim set, policy not met.
- `ATTENTION_REQUIRED`: at least one checked inconsistency.
- `CONSISTENT_RECORDS`: nonempty claim set without a checked inconsistency.

`CONSISTENT_RECORDS` can still fail a stronger required-basis policy. Inspect
both fields. It can also describe false claims: consistency is not truth.

## Byte observations and filesystem boundary

The core takes a packet and an optional mapping of known source IDs to byte
snapshots; it performs no filesystem or network operations. Observations are
limited to 4 MiB per source and 16 MiB aggregate.

The CLI reads only declared snapshot paths under an explicit root, rejects
observed symlink components below that root and requires regular files.
`O_NOFOLLOW` is used where available. The resolved root and its ancestors must
be trusted. These checks are not atomic protection against all path races;
read bytes are snapshots, and files can change after inspection.

Missing declared snapshot files produce an input error in the file adapter,
not a successful audit. Without `--root`, no snapshots are read: requested
quotations produce `SNAPSHOT_NOT_READ`.