# QuoteLedger

**A citation is a starting point. A check needs a record.**

By **Aaron Michael Weis (ΩNeiron™)**  
ORCID: https://orcid.org/0009-0002-1906-148X  
Version **0.1.0**

QuoteLedger is a small, local tool for keeping research leads, retained
quotations and human review distinct. It can import a research CSV without
throwing away unused columns, locate a quote in a retained UTF-8 text snapshot,
and report whether the claimed evidence level is present.

It is useful beside an AI research assistant or RAG workflow: a summary can
remain a useful lead without quietly becoming “primary source checked.”
Nothing is fetched, submitted, trained or published by the tool.

## Start here

- Readable introduction: [publication/index.html](publication/index.html).
- Paper: [A Citation Is Not a Check](paper/A_Citation_Is_Not_a_Check_v0.1.0.pdf).
- Dense PROSE, Q&As and graph: [publication/dag/index.html](publication/dag/index.html).
- Step-by-step use: [WORKFLOW](docs/WORKFLOW.md).
- Exact fields and decisions: [RECORD_CONTRACT](docs/RECORD_CONTRACT.md).
- Limits: [LIMITATIONS](docs/LIMITATIONS.md).
- Evidence: [validation](evidence/reference-run/validation.json) and
  [packaging checks](evidence/packaging.json).
- Verification and supported environments: [REVIEW_STATUS](docs/REVIEW_STATUS.md).

The article and DAG are preserved from the original candidate. Their publication
status and citation fields describe that historical snapshot. Use the root
`CITATION.cff` and the repository's release record for current citation details.

## Run a first example

Use Python 3.10 or newer. QuoteLedger uses the Python standard library.
See [REVIEW_STATUS](docs/REVIEW_STATUS.md) for exact tested environments.

From the source directory:

```sh
python -m quoteledger audit examples/primary-quote.json --root examples/snapshots --require primary_quote --output new-report.json
```

The example exits 0 and writes JSON with `policy_met: true` and an observed
basis of `primary_quote`. Replace the packet with `examples/lead-link.json`
and use a fresh output path to see exit 1 and `policy_met: false`.

Or run the standalone file from any working directory, with appropriate paths:

```sh
python dist/quoteledger.pyz --help
```

For a readable report, add `--format html`; use a new `.html` output path.
`--include-text` includes the claim text. Reports omit source paths, titles,
URLs, full quotations and reviewer prose, but IDs, digests and findings can
still disclose information. Inspect a report before sharing.

## Four evidence-basis labels

| Label | What the program can establish from the supplied records |
| --- | --- |
| `lead` | A tracked assertion; a citation may be a link or may be absent. No source read is implied. |
| `local_quote` | At least one exact quotation matches an observed UTF-8 snapshot with its declared full-file SHA-256. |
| `primary_quote` | The above, with the matched source **declared** primary and full text. The tool does not authenticate these labels. |
| `primary_reviewed` | The above plus a current, completed, “supports” human review record bound to this claim and its cited source metadata. |

These are record conditions, **not confidence scores or truth levels**.
A copied quote may be irrelevant; a source can be mislabeled; a reviewer can be
wrong. The deliberate `false-but-consistent` example reaches
`primary_reviewed` while making an unsupported generalization.

Use `--require primary_quote` or `--require primary_reviewed` when that is your
actual workflow requirement. The default requires only `lead`. A successful
default exit therefore does **not** mean primary verification.

## Commands

```sh
python -m quoteledger intake-csv examples/research-leads.csv --output new-intake
python -m quoteledger locate examples/snapshots/report-a.txt --quote-file examples/quote.txt --output new-locations.json
python -m quoteledger capture examples/snapshots/report-a.txt --source-id source-a --title "Retained source" --path report-a.txt --output new-source.json
python -m quoteledger plan examples/primary-quote.json --output new-pending-reviews.json
```

CSV columns default to `claim,title,url`. `--claim-column`, `--title-column`
and `--url-column` accept other header names. An Elicit or another research-tool
export can be mapped when its columns fit this contract. **This is not an Elicit
API integration or a tested importer for every Elicit export format.** The
included CSV is synthetic.

Review plans contain no approvals. Copy an appropriate pending review into the
corresponding claim only after inspecting the source; supply your own decision,
reviewer label and rationale. The software never writes back into a packet.

## Exit contract and safe use

- `0`: a new result was created and the requested audit policy was met, or a
  non-audit command completed. Not a truth certificate.
- `1`: an audit report was created, but one or more claims failed the requested
  policy, or there were no claims.
- `2`: invalid input, invalid command or unavailable input/output operation.

Output files/directories must be new. Existing inputs and outputs are not
overwritten by the commands. Interrupted writes may leave incomplete new
outputs. Shell redirection and concurrent filesystem actors are outside this
promise. Use a trusted local root; do not run the adapter against an adversarial
filesystem.

## Reproduce the included observations

```sh
python -m unittest discover -s tests -v
python tools/validate.py --output new-validation
python tools/build_zipapp.py --output new-quoteledger.pyz
python tools/check_package.py --app new-quoteledger.pyz --output new-packaging.json
```

The historical Linux run passed **67 unit tests**, matched **20 authored cases**
and **64 generated checks**, and passed **10 packaging checks**. The fresh
Windows run passed **66 tests**, with one explicitly recorded symlink skip,
matched all 84 cases, and passed all ten packaging checks. These overlap and
are synthetic implementation checks, not independent samples or a citation
accuracy estimate. The included receipts retain individual outcomes and
fingerprints. The standalone app was exercised outside the source directory.

On Windows accounts that cannot create a symlink, add
`--allow-windows-symlink-skip` to the validation command above. Strict
validation and Linux CI require every test to run.

The optional PDF renderer needs ReportLab and a supported local font pair.
It is not a runtime requirement of QuoteLedger.

## Rights and release state

See [RIGHTS](RIGHTS.md) for the status of the software, paper, and examples.

The author supplied the direction and requirements. OpenAI's assistant through
Notion AI assisted implementation, testing and writing. Human author review
remains distinct; this is not independent validation.
