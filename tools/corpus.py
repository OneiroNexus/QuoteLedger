"""All text and reviews in this corpus are fictional, explicit test fixtures."""
import copy

from quoteledger.core import digest, review_binding

RAW = ("SYNTHETIC REPORT — not a real study.\n"
       "In trial A, 8 fictional specimens required 12 minutes.\n"
       "The result does not establish performance in other settings.\n").encode()
QUOTE = "In trial A, 8 fictional specimens required 12 minutes."


def base(kind="primary", extent="full_text"):
    start = RAW.decode().index(QUOTE)
    source = {"id": "source-a", "title": "Synthetic report A",
              "url": "https://example.org/synthetic-report-a",
              "kind": kind, "extent": extent, "path": "report-a.txt", "sha256": digest(RAW)}
    claim = {"id": "claim-a", "text": "Trial A required 12 minutes for 8 fictional specimens.",
             "declared_basis": "primary_quote",
             "citations": [{"source_id": "source-a", "start": start, "end": start + len(QUOTE), "quote": QUOTE}],
             "review": None}
    return {"schema": "quoteledger.packet.v1", "sources": [source], "claims": [claim]}, {"source-a": RAW}


def completed(packet, decision="supports"):
    claim = packet["claims"][0]
    claim["review"] = {"completed": True, "decision": decision,
                       "reviewer": "FICTIONAL FIXTURE REVIEWER",
                       "rationale": "Synthetic test assertion, not a real-person review.",
                       "binding": review_binding(claim, {s["id"]: s for s in packet["sources"]})}


def case(name):
    p, obs = base()
    claim, source = p["claims"][0], p["sources"][0]
    expected = {"basis": "primary_quote", "codes": [], "policy_met": True}
    if name == "lead-link":
        source.update(path=None, sha256=None, kind="unknown", extent="unknown")
        claim.update(declared_basis="lead")
        claim["citations"] = [{"source_id": source["id"], "start": None, "end": None, "quote": None}]
        obs = {}
        expected.update(basis="lead", policy_met=False)
    elif name == "no-citation":
        claim.update(citations=[], declared_basis="lead")
        expected.update(basis="lead", policy_met=False)
    elif name == "primary-quote":
        pass
    elif name in ("secondary-quote", "abstract-quote", "synthesis-quote"):
        if name == "secondary-quote":
            source["kind"] = "secondary"
        elif name == "abstract-quote":
            source["extent"] = "abstract"
        else:
            source.update(kind="synthesis", extent="summary")
        claim["declared_basis"] = "local_quote"
        expected.update(basis="local_quote", policy_met=False)
    elif name == "changed-snapshot":
        obs["source-a"] += b"Changed after capture.\n"
        expected.update(basis="lead", codes=["SNAPSHOT_MISMATCH", "DECLARED_BASIS_NOT_MET"], policy_met=False)
    elif name == "wrong-offset":
        claim["citations"][0]["start"] += 1
        expected.update(basis="lead", codes=["SPAN_MISMATCH", "DECLARED_BASIS_NOT_MET"], policy_met=False)
    elif name == "wrong-quote":
        claim["citations"][0]["quote"] = QUOTE.replace("12", "21")
        expected.update(basis="lead", codes=["SPAN_MISMATCH", "DECLARED_BASIS_NOT_MET"], policy_met=False)
    elif name == "unread-snapshot":
        obs = {}
        expected.update(basis="lead", codes=["SNAPSHOT_NOT_READ", "DECLARED_BASIS_NOT_MET"], policy_met=False)
    elif name == "undeclared-snapshot":
        source.update(path=None, sha256=None)
        obs = {}
        expected.update(basis="lead", codes=["NO_SNAPSHOT_DECLARED", "DECLARED_BASIS_NOT_MET"], policy_met=False)
    elif name == "abstract-overclaimed":
        source["extent"] = "abstract"
        expected.update(basis="local_quote", codes=["DECLARED_BASIS_NOT_MET"], policy_met=False)
    elif name == "reviewed-primary":
        claim["declared_basis"] = "primary_reviewed"
        completed(p)
        expected["basis"] = "primary_reviewed"
    elif name == "reviewed-secondary":
        source["kind"] = "secondary"
        claim["declared_basis"] = "primary_reviewed"
        completed(p)
        expected.update(basis="local_quote", codes=["DECLARED_BASIS_NOT_MET"], policy_met=False)
    elif name == "stale-review":
        completed(p)
        claim["text"] += " A changed scope."
        expected.update(codes=["STALE_REVIEW"], policy_met=False)
    elif name == "contradictory-review":
        completed(p, "contradicts")
        expected.update(codes=["REVIEWER_CONTRADICTS"], policy_met=False)
    elif name == "uncertain-review":
        completed(p, "uncertain")
        expected.update(codes=["REVIEWER_UNCERTAIN"], policy_met=False)
    elif name == "false-but-consistent":
        claim["text"] = "The method always finishes every real-world job in 12 minutes."
        claim["declared_basis"] = "primary_reviewed"
        completed(p)
        expected["basis"] = "primary_reviewed"
    elif name == "one-broken-citation":
        extra = copy.deepcopy(claim["citations"][0])
        extra["quote"] = extra["quote"].replace("8", "9")
        claim["citations"].append(extra)
        expected.update(codes=["SPAN_MISMATCH"], policy_met=False)
    elif name == "pending-review":
        claim["review"] = {"completed": False, "decision": "uncertain",
                           "reviewer": "", "rationale": "",
                           "binding": review_binding(claim, {source["id"]: source})}
    else:
        raise ValueError(name)
    return {"id": name, "synthetic": True,
            "semantic_negative": name == "false-but-consistent",
            "packet": p, "snapshots_utf8": {k: v.decode() for k, v in obs.items()},
            "expected": expected}


NAMES = ("lead-link", "no-citation", "primary-quote", "secondary-quote", "abstract-quote",
         "synthesis-quote", "changed-snapshot", "wrong-offset", "wrong-quote",
         "unread-snapshot", "undeclared-snapshot", "abstract-overclaimed",
         "reviewed-primary", "reviewed-secondary", "stale-review", "contradictory-review",
         "uncertain-review", "false-but-consistent", "one-broken-citation", "pending-review")


def authored():
    return [case(name) for name in NAMES]


def generated():
    out = []
    for variant in range(16):
        for family in ("identity", "source-change", "claim-change", "quote-change"):
            p, obs = base()
            p["claims"][0]["text"] += f" Synthetic variant {variant}."
            completed(p)
            expected = {"basis": "primary_reviewed", "codes": [], "policy_met": True}
            if family == "source-change":
                obs["source-a"] += f" Variant {variant} changed bytes.".encode()
                expected.update(basis="lead", codes=["SNAPSHOT_MISMATCH", "DECLARED_BASIS_NOT_MET"], policy_met=False)
            elif family == "claim-change":
                p["claims"][0]["text"] += " Changed after review."
                expected.update(basis="primary_quote", codes=["STALE_REVIEW"], policy_met=False)
            elif family == "quote-change":
                p["claims"][0]["citations"][0]["quote"] += "!"
                expected.update(basis="lead", codes=["SPAN_MISMATCH", "STALE_REVIEW", "DECLARED_BASIS_NOT_MET"], policy_met=False)
            out.append({"id": f"{family}-{variant}", "synthetic": True, "semantic_negative": False,
                        "packet": p, "snapshots_utf8": {k: v.decode() for k, v in obs.items()},
                        "expected": expected})
    return out