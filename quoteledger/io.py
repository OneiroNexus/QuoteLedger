"""Bounded local files; trusted root/ancestors required. No network access."""
import html
import json
import os
from pathlib import Path
import stat

from .core import InputError, safe_path


def read_bytes(path, limit):
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "rb") as stream:
        if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
            raise InputError("NOT_REGULAR_FILE")
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise InputError("INPUT_LIMIT")
    return raw


def load_json(path):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise InputError("DUPLICATE_JSON_KEY")
            result[key] = value
        return result
    def bad_constant(_):
        raise InputError("NONFINITE_JSON")
    raw = read_bytes(path, 4 * 1024 * 1024)
    return json.loads(raw.decode("utf-8"), object_pairs_hook=unique,
                      parse_constant=bad_constant), raw


def observe(sources, root):
    base = Path(root).resolve(strict=True)
    if not base.is_dir():
        raise InputError("ROOT_DIRECTORY")
    output, total = {}, 0
    for sid, source in sources.items():
        if source["path"] is None:
            continue
        path = base
        for part in safe_path(source["path"]):
            path = path / part
            if path.is_symlink():
                raise InputError("SNAPSHOT_SYMLINK")
        raw = read_bytes(path, min(4 * 1024 * 1024, 16 * 1024 * 1024 - total))
        total += len(raw)
        output[sid] = raw
    return output


def write_new(path, raw):
    with Path(path).open("xb") as stream:
        stream.write(raw)


def html_report(report):
    escape = html.escape
    rows = []
    for row in report["claims"]:
        codes = ", ".join(f["code"] for f in row["findings"]) or "No checked inconsistency"
        label = row.get("claim_text", row["claim_id"])
        rows.append("<tr>" + "".join("<td>" + escape(str(x)) + "</td>" for x in
                    (label, row["declared_basis"], row["observed_basis"], codes)) + "</tr>")
    return ("""<!doctype html><html lang="en"><meta charset="utf-8"><title>QuoteLedger report</title>
<style>body{font:17px/1.55 system-ui;margin:40px;color:#263b34}table{border-collapse:collapse;width:100%}
th,td{text-align:left;vertical-align:top;border-bottom:1px solid #ccd8d0;padding:10px}th{background:#eef5f0}</style>
<h1>QuoteLedger — citation inspection</h1><p>""" +
            escape(report["result"]) + " · Required basis: " + escape(report["require"]) +
            " · Policy met: " + str(report["policy_met"]) +
            "</p><p>Exact local quotation is not proof of meaning. Source type and review are supplied assertions.</p>"
            "<table><tr><th>Claim</th><th>Declared basis</th><th>Observed basis</th><th>Findings</th></tr>" +
            "".join(rows) + "</table></html>").encode()