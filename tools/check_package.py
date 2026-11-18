"""Exercise an explicit built zipapp outside the source tree; create a new receipt."""
from pathlib import Path
import argparse
from datetime import datetime, timezone
import json
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from quoteledger.core import canonical, digest
from tools.build_zipapp import archive


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise SystemExit("Choose a new receipt path.")
    app = args.app.resolve(strict=True)
    checked_files = [app, ROOT / "examples/primary-quote.json",
                     ROOT / "examples/lead-link.json", ROOT / "examples/false-but-consistent.json",
                     ROOT / "examples/snapshots/report-a.txt", ROOT / "examples/research-leads.csv",
                     ROOT / "examples/quote.txt"]
    before = {p.name: digest(p.read_bytes()) for p in checked_files}
    checks = []
    def check(name, passed):
        checks.append({"check": name, "passed": bool(passed)})
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    with tempfile.TemporaryDirectory(prefix="quoteledger-package-") as tmp:
        folder = Path(tmp)
        def run(*tokens):
            return subprocess.run([sys.executable, "-I", str(app), *map(str, tokens)],
                                  cwd=folder, env=env, capture_output=True, text=True, timeout=20)
        a = run("audit", ROOT / "examples/primary-quote.json", "--root", ROOT / "examples/snapshots",
                "--require", "primary_quote", "--output", folder / "pass.json")
        check("standalone_primary_quote", a.returncode == 0 and json.loads((folder / "pass.json").read_bytes())["policy_met"])
        b = run("audit", ROOT / "examples/lead-link.json", "--require", "primary_quote", "--output", folder / "lead.json")
        check("lead_not_promoted", b.returncode == 1 and not json.loads((folder / "lead.json").read_bytes())["policy_met"])
        c = run("audit", ROOT / "examples/false-but-consistent.json", "--root", ROOT / "examples/snapshots",
                "--require", "primary_reviewed", "--output", folder / "negative.json")
        check("semantic_boundary_remains_visible", c.returncode == 0)
        original = (folder / "pass.json").read_bytes()
        d = run("audit", ROOT / "examples/primary-quote.json", "--output", folder / "pass.json")
        check("existing_report_refused_and_preserved", d.returncode == 2 and (folder / "pass.json").read_bytes() == original)
        e = run("intake-csv", ROOT / "examples/research-leads.csv", "--output", folder / "intake")
        check("csv_bytes_preserved", e.returncode == 0 and
              (folder / "intake/source-import.csv").read_bytes() == (ROOT / "examples/research-leads.csv").read_bytes())
        f = run("plan", ROOT / "examples/primary-quote.json", "--output", folder / "plan.json")
        check("plan_has_no_approvals", f.returncode == 0 and
              all(not r["review"]["completed"] for r in json.loads((folder / "plan.json").read_bytes())["reviews"]))
        g = run("locate", ROOT / "examples/snapshots/report-a.txt", "--quote-file", ROOT / "examples/quote.txt",
                "--output", folder / "locations.json")
        locations = json.loads((folder / "locations.json").read_bytes()) if g.returncode == 0 else {}
        check("exact_quote_location", g.returncode == 0 and len(locations["matches"]) == 1 and not locations["selection_made"])
        h = run("capture", ROOT / "examples/snapshots/report-a.txt", "--source-id", "capture-a",
                "--title", "Synthetic capture", "--path", "report-a.txt", "--output", folder / "capture.json")
        descriptor = json.loads((folder / "capture.json").read_bytes()) if h.returncode == 0 else {}
        check("capture_does_not_assign_primary", h.returncode == 0 and descriptor["kind"] == descriptor["extent"] == "unknown")
    check("byte_identical_zipapp_rebuild", archive() == app.read_bytes())
    check("checked_inputs_unchanged", before == {p.name: digest(p.read_bytes()) for p in checked_files})
    receipt = {"schema": "quoteledger.packaging.v1", "recorded_utc": datetime.now(timezone.utc).isoformat(),
               "checks": checks, "passed": all(c["passed"] for c in checks),
               "artifacts_sha256": before,
               "limits": "Local consistency checks, not independent validation or a portability guarantee."}
    with args.output.open("xb") as out:
        out.write(canonical(receipt))
    print(json.dumps({"passed": receipt["passed"], "checks": len(checks)}))
    return 0 if receipt["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())