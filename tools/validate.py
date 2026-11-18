"""Run named local checks and write a fresh, inspectable evidence directory."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import platform
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quoteledger.core import analyze, canonical, digest
from tools.corpus import authored, generated


def fingerprints():
    out = {}
    for folder in ("quoteledger", "tests", "tools", "fixtures", "examples"):
        for p in sorted((ROOT / folder).rglob("*")):
            if p.is_file() and "__pycache__" not in p.parts and p.suffix != ".pyc":
                out[p.relative_to(ROOT).as_posix()] = digest(p.read_bytes())
    return out


class RecordedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.outcomes = []

    def addSuccess(self, test):
        super().addSuccess(test)
        self.outcomes.append({"test": test.id(), "outcome": "pass"})

    def addFailure(self, test, error):
        super().addFailure(test, error)
        self.outcomes.append({"test": test.id(), "outcome": "fail"})

    def addError(self, test, error):
        super().addError(test, error)
        self.outcomes.append({"test": test.id(), "outcome": "error"})

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.outcomes.append({"test": test.id(), "outcome": "skip", "reason": reason})

    def addSubTest(self, test, subtest, error):
        super().addSubTest(test, subtest, error)
        if error is not None:
            self.outcomes.append({"test": test.id(), "outcome": "subtest_failure",
                                  "subtest": str(subtest)})


def check_cases(cases):
    rows = []
    for case in cases:
        observations = {k: v.encode("utf-8") for k, v in case["snapshots_utf8"].items()}
        report = analyze(case["packet"], observations, require="primary_quote")
        row = report["claims"][0]
        observed = {"basis": row["observed_basis"],
                    "codes": [f["code"] for f in row["findings"]],
                    "policy_met": report["policy_met"]}
        rows.append({"case_id": case["id"], "matched": observed == case["expected"],
                     "semantic_negative": case["semantic_negative"],
                     "expected": case["expected"], "observed": observed, "report": report})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--allow-windows-symlink-skip", action="store_true",
        help="Allow only the recorded Windows symlink privilege skip.",
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    start = datetime.now(timezone.utc).isoformat()
    before = fingerprints()
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"))
    with (args.output / "unittest.log").open("x", encoding="utf-8") as log:
        result = unittest.TextTestRunner(
            stream=log, verbosity=2, resultclass=RecordedResult).run(suite)
    families, fixture_matches = {}, {}
    for name, factory in (("authored", authored), ("generated", generated)):
        raw = (ROOT / "fixtures" / (name + ".json")).read_bytes()
        supplied = json.loads(raw)["cases"]
        fixture_matches[name] = canonical(supplied) == canonical(factory())
        rows = check_cases(supplied)
        families[name] = {"total": len(rows), "matched": sum(r["matched"] for r in rows)}
        (args.output / (name + "-outcomes.json")).write_bytes(canonical(rows))
    after = fingerprints()
    allowed_skip = (
        "test_cli.IOTests.test_source_symlink_refused",
        "Windows account cannot create symlinks (WinError 1314)",
    )
    skipped = [(test.id(), reason) for test, reason in result.skipped]
    skips_ok = not skipped or (
        args.allow_windows_symlink_skip and sys.platform == "win32"
        and skipped == [allowed_skip]
    )
    passed = (result.wasSuccessful() and skips_ok and before == after and
              all(fixture_matches.values()) and
              all(r["total"] == r["matched"] for r in families.values()))
    receipt = {
        "schema": "quoteledger.validation.v1", "started_utc": start,
        "ended_utc": datetime.now(timezone.utc).isoformat(),
        "environment": {"python": platform.python_version(), "implementation": platform.python_implementation(),
                        "system": platform.system(), "machine": platform.machine()},
        "unit": {"run": result.testsRun,
                 "passed": sum(r["outcome"] == "pass" for r in result.outcomes),
                 "failures": len(result.failures), "errors": len(result.errors),
                 "skipped": len(result.skipped), "outcomes": result.outcomes},
        "families": families, "fixture_regeneration_matches": fixture_matches,
        "skip_policy": {"windows_symlink_exception_requested": args.allow_windows_symlink_skip,
                        "accepted": skips_ok},
        "tracked_inputs_unchanged": before == after,
        "tracked_sha256_before": before, "tracked_sha256_after": after,
        "passed": passed,
        "limits": "Local synthetic implementation checks; not semantic accuracy or authenticated execution.",
    }
    (args.output / "validation.json").write_bytes(canonical(receipt))
    print(json.dumps({"passed": passed, "unit": receipt["unit"]["run"],
                      "skipped": receipt["unit"]["skipped"], **families}))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
