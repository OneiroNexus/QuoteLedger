"""Pure record inspection. A matching quote is not a true or entailed claim."""
from __future__ import annotations

import hashlib
import json
import re
from urllib.parse import urlsplit

BASES = ("lead", "local_quote", "primary_quote", "primary_reviewed")
KINDS = ("primary", "secondary", "synthesis", "unknown")
EXTENTS = ("full_text", "abstract", "snippet", "summary", "unknown")
ID = re.compile(r"[A-Za-z][A-Za-z0-9_.:-]{0,79}\Z")
HEX = re.compile(r"[0-9a-f]{64}\Z")


class InputError(ValueError):
    pass


def canonical(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def keys(value, fields, code):
    if type(value) is not dict or set(value) != set(fields):
        raise InputError(code)


def text(value, maximum=10000, blank=False):
    if type(value) is not str or len(value) > maximum or (not blank and not value.strip()):
        raise InputError("TEXT")
    try:
        value.encode("utf-8")
    except UnicodeError:
        raise InputError("UNICODE") from None


def identifier(value):
    if type(value) is not str or not ID.fullmatch(value):
        raise InputError("IDENTIFIER")


def safe_path(value):
    if type(value) is not str or len(value) > 500:
        raise InputError("SNAPSHOT_PATH")
    parts = value.split("/")
    if len(parts) > 12 or any(p in ("", ".", "..") or
                            not re.fullmatch(r"[A-Za-z0-9_.-]+", p) for p in parts):
        raise InputError("SNAPSHOT_PATH")
    return parts


def validate(packet):
    keys(packet, {"schema", "sources", "claims"}, "PACKET_FIELDS")
    if packet["schema"] != "quoteledger.packet.v1":
        raise InputError("SCHEMA")
    for field in ("sources", "claims"):
        if type(packet[field]) is not list or len(packet[field]) > 1000:
            raise InputError("RECORD_LIMIT")
    sources = {}
    for row in packet["sources"]:
        keys(row, {"id", "title", "url", "kind", "extent", "path", "sha256"}, "SOURCE_FIELDS")
        identifier(row["id"])
        if row["id"] in sources:
            raise InputError("DUPLICATE_SOURCE")
        text(row["title"], 2000)
        if row["kind"] not in KINDS or row["extent"] not in EXTENTS:
            raise InputError("SOURCE_ENUM")
        if row["url"] is not None:
            text(row["url"], 2000)
            u = urlsplit(row["url"])
            if (u.scheme not in ("http", "https") or not u.netloc or u.username or
                    u.password or any(c.isspace() for c in row["url"])):
                raise InputError("SOURCE_URL")
        if (row["path"] is None) != (row["sha256"] is None):
            raise InputError("PARTIAL_SNAPSHOT")
        if row["path"] is not None:
            safe_path(row["path"])
            if type(row["sha256"]) is not str or not HEX.fullmatch(row["sha256"]):
                raise InputError("SOURCE_DIGEST")
        sources[row["id"]] = row
    seen = set()
    total = 0
    for claim in packet["claims"]:
        keys(claim, {"id", "text", "declared_basis", "citations", "review"}, "CLAIM_FIELDS")
        identifier(claim["id"])
        if claim["id"] in seen:
            raise InputError("DUPLICATE_CLAIM")
        seen.add(claim["id"])
        text(claim["text"])
        if claim["declared_basis"] not in BASES:
            raise InputError("BASIS")
        if type(claim["citations"]) is not list or len(claim["citations"]) > 100:
            raise InputError("CITATION_LIMIT")
        total += len(claim["citations"])
        unique = set()
        for cite in claim["citations"]:
            keys(cite, {"source_id", "start", "end", "quote"}, "CITATION_FIELDS")
            identifier(cite["source_id"])
            if cite["source_id"] not in sources:
                raise InputError("UNKNOWN_SOURCE")
            if cite["quote"] is None:
                if cite["start"] is not None or cite["end"] is not None:
                    raise InputError("PARTIAL_SPAN")
            else:
                text(cite["quote"], 64000)
                if (type(cite["start"]) is not int or type(cite["end"]) is not int or
                        not 0 <= cite["start"] < cite["end"] <= 4 * 1024 * 1024):
                    raise InputError("SPAN_RANGE")
            signature = canonical(cite)
            if signature in unique:
                raise InputError("DUPLICATE_CITATION")
            unique.add(signature)
        review = claim["review"]
        if review is not None:
            keys(review, {"completed", "decision", "reviewer", "rationale", "binding"}, "REVIEW_FIELDS")
            if type(review["completed"]) is not bool:
                raise InputError("REVIEW_BOOLEAN")
            if review["decision"] not in ("supports", "contradicts", "uncertain"):
                raise InputError("REVIEW_DECISION")
            text(review["reviewer"], 1000, blank=not review["completed"])
            text(review["rationale"], 4000, blank=not review["completed"])
            if type(review["binding"]) is not str or not HEX.fullmatch(review["binding"]):
                raise InputError("REVIEW_BINDING_FORMAT")
    if total > 10000:
        raise InputError("TOTAL_CITATION_LIMIT")
    return sources


def review_binding(claim, sources):
    body = {k: v for k, v in claim.items() if k != "review"}
    cited = sorted({c["source_id"] for c in claim["citations"]})
    return digest(b"QuoteLedger.Claim.v1\0" + canonical(
        {"claim": body, "sources": [sources[sid] for sid in cited]}))


def plans(packet):
    sources = validate(packet)
    return {"schema": "quoteledger.pending-reviews.v1", "reviews": [
        {"claim_id": c["id"],
         "review": {"completed": False, "decision": "uncertain",
                    "reviewer": "", "rationale": "",
                    "binding": review_binding(c, sources)}}
        for c in packet["claims"]
    ]}


def analyze(packet, observations=None, *, require="lead", include_text=False):
    sources = validate(packet)
    if require not in BASES or type(include_text) is not bool:
        raise InputError("POLICY")
    if observations is None:
        observations = {}
    if type(observations) is not dict or not set(observations) <= set(sources):
        raise InputError("OBSERVATION_IDS")
    if any(type(raw) is not bytes or len(raw) > 4 * 1024 * 1024
           for raw in observations.values()) or sum(map(len, observations.values())) > 16 * 1024 * 1024:
        raise InputError("OBSERVATION_LIMIT")
    source_states = {}
    decoded = {}
    for sid, source in sources.items():
        if source["sha256"] is None:
            state = "NO_SNAPSHOT_DECLARED"
        elif sid not in observations:
            state = "SNAPSHOT_NOT_READ"
        elif digest(observations[sid]) != source["sha256"]:
            state = "SNAPSHOT_MISMATCH"
        else:
            try:
                decoded[sid] = observations[sid].decode("utf-8")
                state = "SNAPSHOT_MATCHED"
            except UnicodeError:
                state = "SNAPSHOT_NOT_UTF8"
        source_states[sid] = state
    rows = []
    for claim in packet["claims"]:
        findings, citations = [], []
        achieved = 0
        for i, cite in enumerate(claim["citations"]):
            source = sources[cite["source_id"]]
            state = source_states[source["id"]]
            result = "LINK_ONLY"
            if cite["quote"] is not None:
                if state != "SNAPSHOT_MATCHED":
                    result = state
                    findings.append({"code": state, "citation": i})
                elif (cite["end"] > len(decoded[source["id"]]) or
                      decoded[source["id"]][cite["start"]:cite["end"]] != cite["quote"]):
                    result = "SPAN_MISMATCH"
                    findings.append({"code": result, "citation": i})
                else:
                    result = "EXACT_LOCAL_QUOTE"
                    achieved = max(achieved, 2 if source["kind"] == "primary"
                                   and source["extent"] == "full_text" else 1)
            citations.append({"source_id": source["id"], "result": result,
                              "declared_source_kind": source["kind"],
                              "declared_extent": source["extent"]})
        review_state = "NOT_REVIEWED"
        review = claim["review"]
        if review is not None:
            if review["binding"] != review_binding(claim, sources):
                review_state = "STALE_REVIEW"
                findings.append({"code": review_state})
            elif not review["completed"]:
                review_state = "PENDING_REVIEW"
            else:
                review_state = "REVIEWER_" + review["decision"].upper()
                if review["decision"] == "supports" and achieved == 2:
                    achieved = 3
                elif review["decision"] != "supports":
                    findings.append({"code": review_state})
        if BASES.index(claim["declared_basis"]) > achieved:
            findings.append({"code": "DECLARED_BASIS_NOT_MET"})
        row = {"claim_id": claim["id"], "declared_basis": claim["declared_basis"],
               "observed_basis": BASES[achieved], "review_state": review_state,
               "citations": citations, "findings": findings,
               "policy_met": achieved >= BASES.index(require) and not findings}
        if include_text:
            row["claim_text"] = claim["text"]
        rows.append(row)
    count = len(rows)
    return {
        "schema": "quoteledger.report.v1", "version": "0.1.0",
        "packet_sha256": digest(b"QuoteLedger.Packet.v1\0" + canonical(packet)),
        "result": ("NO_CLAIMS" if not count else "ATTENTION_REQUIRED"
                   if any(r["findings"] for r in rows) else "CONSISTENT_RECORDS"),
        "require": require, "policy_met": bool(count) and all(r["policy_met"] for r in rows),
        "counts": {"declared_claims": count,
                   "claims_with_findings": sum(bool(r["findings"]) for r in rows),
                   "exact_quote_claims": sum(BASES.index(r["observed_basis"]) >= 1 for r in rows),
                   "primary_quote_claims": sum(BASES.index(r["observed_basis"]) >= 2 for r in rows),
                   "reviewed_primary_claims": sum(r["observed_basis"] == "primary_reviewed" for r in rows)},
        "sources": [{"source_id": sid, "snapshot_state": state}
                    for sid, state in sorted(source_states.items())],
        "claims": rows,
        "limits": ["Source role and extent are supplied labels, not authenticated.",
                   "Exact quotes do not establish truth or entailment.",
                   "Reviews are editable assertions, not signatures.",
                   "Coverage concerns supplied claims, not every claim in an article.",
                   "No web fetching, model invocation or publication is performed."],
    }