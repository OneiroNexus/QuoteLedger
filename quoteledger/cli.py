"""Local citation audit, source capture, quote location and configurable CSV intake."""
from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path
import sys

from .core import (BASES, EXTENTS, KINDS, InputError, analyze, canonical, digest,
                   identifier, plans, safe_path, validate)
from .io import html_report, load_json, observe, read_bytes, write_new


def intake(raw, claim_column, title_column, url_column):
    reader = csv.DictReader(io.StringIO(raw.decode("utf-8-sig"), newline=""))
    headers = reader.fieldnames
    if (not headers or len(headers) > 200 or len(headers) != len(set(headers)) or
            not {claim_column, title_column, url_column} <= set(headers)):
        raise InputError("CSV_HEADERS")
    rows = []
    for row in reader:
        rows.append(row)
        if len(rows) > 1000:
            raise InputError("CSV_ROWS")
    if not 1 <= len(rows) <= 1000 or any(None in row or any(v is None for v in row.values()) for row in rows):
        raise InputError("CSV_ROWS")
    sources, claims = [], []
    for i, row in enumerate(rows, 1):
        sid = f"source-{i:04}"
        sources.append({"id": sid, "title": row[title_column],
                        "url": row[url_column] or None, "kind": "unknown", "extent": "unknown",
                        "path": None, "sha256": None})
        claims.append({"id": f"claim-{i:04}", "text": row[claim_column],
                       "declared_basis": "lead", "review": None,
                       "citations": [{"source_id": sid, "start": None, "end": None, "quote": None}]})
    packet = {"schema": "quoteledger.packet.v1", "sources": sources, "claims": claims}
    validate(packet)
    return packet, {"schema": "quoteledger.import.v1", "input_sha256": digest(raw),
                    "columns": headers, "mapping": {"claim": claim_column, "title": title_column, "url": url_column},
                    "rows": rows, "note": "All rows imported as leads; no source or claim was verified."}


def locate(raw, quoted):
    source, quote = raw.decode("utf-8"), quoted.decode("utf-8")
    if not quote.strip():
        raise InputError("EMPTY_QUOTE")
    spans, start = [], 0
    while len(spans) < 2000:
        offset = source.find(quote, start)
        if offset < 0:
            break
        spans.append({"start": offset, "end": offset + len(quote), "quote": quote})
        start = offset + 1
    return {"schema": "quoteledger.locations.v1", "snapshot_sha256": digest(raw),
            "offset_unit": "Unicode code points, half-open, no normalization",
            "matches": spans, "additional_matches": source.find(quote, start) >= 0,
            "selection_made": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    audit = subs.add_parser("audit")
    audit.add_argument("packet")
    audit.add_argument("--root")
    audit.add_argument("--require", choices=BASES, default="lead")
    audit.add_argument("--include-text", action="store_true")
    audit.add_argument("--format", choices=("json", "html"), default="json")
    audit.add_argument("--output", required=True)
    plan = subs.add_parser("plan")
    plan.add_argument("packet"); plan.add_argument("--output", required=True)
    loc = subs.add_parser("locate")
    loc.add_argument("source"); loc.add_argument("--quote-file", required=True)
    loc.add_argument("--output", required=True)
    capture = subs.add_parser("capture")
    capture.add_argument("source"); capture.add_argument("--source-id", required=True)
    capture.add_argument("--title", required=True); capture.add_argument("--url")
    capture.add_argument("--kind", choices=KINDS, default="unknown")
    capture.add_argument("--extent", choices=EXTENTS, default="unknown")
    capture.add_argument("--path", required=True); capture.add_argument("--output", required=True)
    imp = subs.add_parser("intake-csv")
    imp.add_argument("csv"); imp.add_argument("--claim-column", default="claim")
    imp.add_argument("--title-column", default="title"); imp.add_argument("--url-column", default="url")
    imp.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command in ("audit", "plan"):
            packet, raw = load_json(args.packet)
            sources = validate(packet)
            if args.command == "plan":
                write_new(args.output, canonical(plans(packet)))
            else:
                observations = observe(sources, args.root) if args.root else {}
                report = analyze(packet, observations, require=args.require,
                                 include_text=args.include_text)
                report["input_file_sha256"] = digest(raw)
                write_new(args.output, canonical(report) if args.format == "json" else html_report(report))
                print(json.dumps({"result": report["result"], "policy_met": report["policy_met"]}))
                return 0 if report["policy_met"] else 1
        elif args.command == "locate":
            raw = read_bytes(args.source, 4 * 1024 * 1024)
            quote = read_bytes(args.quote_file, 64000)
            write_new(args.output, canonical(locate(raw, quote)))
        elif args.command == "capture":
            raw = read_bytes(args.source, 4 * 1024 * 1024)
            raw.decode("utf-8")
            identifier(args.source_id); safe_path(args.path)
            source = {"id": args.source_id, "title": args.title, "url": args.url,
                      "kind": args.kind, "extent": args.extent,
                      "path": args.path, "sha256": digest(raw)}
            validate({"schema": "quoteledger.packet.v1", "sources": [source], "claims": []})
            write_new(args.output, canonical(source))
        else:
            raw = read_bytes(args.csv, 4 * 1024 * 1024)
            packet, log = intake(raw, args.claim_column, args.title_column, args.url_column)
            root = Path(args.output)
            root.mkdir(parents=True, exist_ok=False)
            for name, data in {"source-import.csv": raw, "packet.json": canonical(packet),
                               "import-map.json": canonical(log)}.items():
                write_new(root / name, data)
        print(json.dumps({"created": args.command, "publication_performed": False}))
        return 0
    except (InputError, OSError, ValueError, TypeError, KeyError, RecursionError, OverflowError, csv.Error) as error:
        code = str(error) if isinstance(error, InputError) else "INPUT_OR_OUTPUT_ERROR"
        sys.stderr.write(json.dumps({"result": "INPUT_ERROR", "code": code}) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())