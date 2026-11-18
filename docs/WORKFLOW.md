# From a useful lead to an inspectable citation

## 1. Retain the research export

Start with an authorized, non-sensitive CSV. The included CSV is fictional.
Map the correct columns; do not assume a research service's “source” field
means full text was inspected.

```sh
python -m quoteledger intake-csv research.csv --claim-column Claim --title-column Title --url-column URL --output intake-001
```

The new directory contains:

- `source-import.csv`: exact original bytes.
- `import-map.json`: original column names, all rows and fields, mapping and hash.
- `packet.json`: every imported item begins as `lead`; source kind and extent
  begin `unknown`; no quotation, snapshot or review is invented.

Unknown columns remain in the import map. The converted packet need not be the
complete research record; retain the original export too. Multiple rows may
refer to one source under separate IDs. Consolidation is an explicit later
editing task, not an automatic loss of row provenance.

## 2. Obtain and retain a source snapshot

Open the source yourself and decide whether it is the right work/version and
whether you have full text, an abstract or a secondary account. The tool does
not open URLs or parse PDFs. Retain an exact UTF-8 text snapshot in a controlled
folder. Keep the original source and extraction details separately.

```sh
python -m quoteledger capture snapshots/paper.txt --source-id source-0001 --title "The source you inspected" --kind primary --extent full_text --path paper.txt --output source-descriptor-001.json
```

Choose those labels only if your inspection justifies them. The default is
`unknown`. Capture writes a descriptor, **not a second copy of the source**.
Place that descriptor into a new version of the packet.

## 3. Locate an exact passage

Save the intended excerpt as UTF-8 in `quote.txt`, with only the intended
characters. A trailing newline is part of the requested quote if present.

```sh
python -m quoteledger locate snapshots/paper.txt --quote-file quote.txt --output locations-001.json
```

The command lists up to 2,000 exact occurrences and tells you whether more
exist. It does not choose one occurrence. Inspect surrounding context before
copying the correct offset range into a citation. A matching phrase alone may
be misleading.

## 4. Audit a new packet version

```sh
python -m quoteledger audit packet-002.json --root snapshots --require primary_quote --output audit-002.json
```

Read the findings, source state and requested policy. A statement describing a
single experiment must not silently become a universal claim. The program
does not interpret that logical difference.

## 5. Record review, if needed

First set the intended final `declared_basis` in the new packet. Then generate
a pending plan so that the binding includes that declaration.

```sh
python -m quoteledger plan packet-002.json --output pending-002.json
```

Inspect the actual source, claim, limitations and source identity. Copy a
pending review into its matching claim; supply your decision, label and
rationale. Set `completed: true` only after you finish. A completed
`contradicts` or `uncertain` review remains a finding.

Audit with `--require primary_reviewed`. Changing the claim or source metadata
after review requires a fresh review binding. Do not copy an old approval onto
a changed claim.

## 6. Publish the explanation, not a research dump

Prepare a natural article that explains the problem, example and limits.
Keep explicit attribution records, Q&As and relationship data in a clearly
linked companion. Include only evidence you are authorized to publish.
Private source exports, unpublished proposals and personal data do not belong
in the public companion by default.

The example publication in this package is entirely about QuoteLedger and its
synthetic checks. It is not an export of its author's private research pages.