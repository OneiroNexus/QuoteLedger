# Synthetic examples

Every claim, source and reviewer in these fixtures is fictional. The only URL
is an example.org placeholder, not a research source.

For most packets, run `audit` with `--root examples/snapshots` and inspect the
required policy. `primary-quote.json` and `reviewed-primary.json` illustrate
record conditions; `false-but-consistent.json` deliberately demonstrates a
wrong assertion that those conditions cannot reject.

`unread-snapshot.json` demonstrates missing observation when run **without**
`--root`. `changed-snapshot.json` requires a changed copy of the snapshot to
exercise that failure; the canonical `examples/snapshots/report-a.txt` is kept
unchanged. The exact changed observations are included in
`fixtures/authored.json`, which the validation runner reads directly.

The corpus, not the filename alone, defines each case's complete packet,
observed bytes and expected outcome. See `evidence/reference-run/` for every
recorded result. No example review is a real person's approval.
