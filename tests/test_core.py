import copy
import unittest

from quoteledger.core import InputError, analyze, digest, plans, review_binding, validate
from tools.corpus import base, completed, authored, generated


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.p, self.obs = base()

    def mutate_error(self, fn):
        fn(self.p)
        with self.assertRaises(InputError):
            analyze(self.p, self.obs)

    def test_primary_quote(self):
        self.assertTrue(analyze(self.p, self.obs, require="primary_quote")["policy_met"])

    def test_no_mutation(self):
        before = copy.deepcopy((self.p, self.obs))
        analyze(self.p, self.obs)
        self.assertEqual(before, (self.p, self.obs))

    def test_deterministic(self):
        self.assertEqual(analyze(self.p, self.obs), analyze(self.p, self.obs))

    def test_unknown_packet_field(self):
        self.mutate_error(lambda p: p.update(secret="no"))

    def test_unknown_source_field(self):
        self.mutate_error(lambda p: p["sources"][0].update(command="no"))

    def test_unknown_claim_field(self):
        self.mutate_error(lambda p: p["claims"][0].update(command="no"))

    def test_duplicate_source(self):
        self.mutate_error(lambda p: p["sources"].append(copy.deepcopy(p["sources"][0])))

    def test_duplicate_claim(self):
        self.mutate_error(lambda p: p["claims"].append(copy.deepcopy(p["claims"][0])))

    def test_unknown_source_reference(self):
        self.mutate_error(lambda p: p["claims"][0]["citations"][0].update(source_id="missing"))

    def test_duplicate_citation(self):
        self.mutate_error(lambda p: p["claims"][0]["citations"].append(copy.deepcopy(p["claims"][0]["citations"][0])))

    def test_invalid_id(self):
        self.mutate_error(lambda p: p["sources"][0].update(id="../outside"))

    def test_invalid_source_kind(self):
        self.mutate_error(lambda p: p["sources"][0].update(kind=[]))

    def test_invalid_extent(self):
        self.mutate_error(lambda p: p["sources"][0].update(extent="verified"))

    def test_path_traversal(self):
        self.mutate_error(lambda p: p["sources"][0].update(path="../outside.txt"))

    def test_absolute_path(self):
        self.mutate_error(lambda p: p["sources"][0].update(path="/outside.txt"))

    def test_windows_path(self):
        self.mutate_error(lambda p: p["sources"][0].update(path="C:\\outside.txt"))

    def test_partial_snapshot(self):
        self.mutate_error(lambda p: p["sources"][0].update(sha256=None))

    def test_bad_digest(self):
        self.mutate_error(lambda p: p["sources"][0].update(sha256="a"*8))

    def test_unsafe_url(self):
        self.mutate_error(lambda p: p["sources"][0].update(url="javascript:alert(1)"))

    def test_credentials_url(self):
        self.mutate_error(lambda p: p["sources"][0].update(url="https://name:password@example.org"))

    def test_empty_claim(self):
        self.mutate_error(lambda p: p["claims"][0].update(text=" "))

    def test_invalid_unicode(self):
        self.mutate_error(lambda p: p["claims"][0].update(text="\ud800"))

    def test_boolean_offset(self):
        self.mutate_error(lambda p: p["claims"][0]["citations"][0].update(start=False))

    def test_negative_offset(self):
        self.mutate_error(lambda p: p["claims"][0]["citations"][0].update(start=-1))

    def test_partial_span(self):
        self.mutate_error(lambda p: p["claims"][0]["citations"][0].update(quote=None))

    def test_invalid_basis(self):
        self.mutate_error(lambda p: p["claims"][0].update(declared_basis="proven"))

    def test_review_plan_is_pending(self):
        plan = plans(self.p)["reviews"][0]["review"]
        self.assertFalse(plan["completed"])
        self.assertEqual(plan["decision"], "uncertain")
        self.assertEqual(plan["reviewer"], "")

    def test_missing_review_fields(self):
        self.mutate_error(lambda p: p["claims"][0].update(review={}))

    def test_nonboolean_review(self):
        completed(self.p)
        self.mutate_error(lambda p: p["claims"][0]["review"].update(completed="yes"))

    def test_completed_review_needs_reviewer(self):
        completed(self.p)
        self.mutate_error(lambda p: p["claims"][0]["review"].update(reviewer=""))

    def test_completed_review_needs_rationale(self):
        completed(self.p)
        self.mutate_error(lambda p: p["claims"][0]["review"].update(rationale=""))

    def test_review_binds_source_metadata(self):
        completed(self.p)
        self.p["sources"][0]["title"] += " changed"
        codes = [f["code"] for f in analyze(self.p, self.obs)["claims"][0]["findings"]]
        self.assertIn("STALE_REVIEW", codes)

    def test_binding_ignores_only_review(self):
        sources = validate(self.p); c = self.p["claims"][0]
        before = review_binding(c, sources)
        completed(self.p)
        self.assertEqual(before, review_binding(c, sources))

    def test_observation_unknown_id(self):
        with self.assertRaises(InputError):
            analyze(self.p, {"missing": b""})

    def test_observation_not_bytes(self):
        with self.assertRaises(InputError):
            analyze(self.p, {"source-a": "text"})

    def test_snapshot_invalid_utf8(self):
        self.obs["source-a"] = b"\xff"
        self.p["sources"][0]["sha256"] = digest(b"\xff")
        codes = [f["code"] for f in analyze(self.p, self.obs)["claims"][0]["findings"]]
        self.assertIn("SNAPSHOT_NOT_UTF8", codes)

    def test_empty_packet_not_success(self):
        r = analyze({"schema":"quoteledger.packet.v1","sources":[],"claims":[]})
        self.assertEqual(r["result"], "NO_CLAIMS")
        self.assertFalse(r["policy_met"])

    def test_default_report_omits_claim_text(self):
        self.assertNotIn("claim_text", analyze(self.p, self.obs)["claims"][0])

    def test_explicit_text_option(self):
        self.assertEqual(analyze(self.p, self.obs, include_text=True)["claims"][0]["claim_text"], self.p["claims"][0]["text"])

    def test_source_identity_not_a_truth_checker(self):
        from tools.corpus import case
        c = case("false-but-consistent")
        r = analyze(c["packet"], {k:v.encode() for k,v in c["snapshots_utf8"].items()}, require="primary_reviewed")
        self.assertTrue(r["policy_met"])

    def test_all_authored_expectations(self):
        for case in authored():
            with self.subTest(case=case["id"]):
                self.check_case(case)

    def test_all_generated_expectations(self):
        for case in generated():
            with self.subTest(case=case["id"]):
                self.check_case(case)

    def check_case(self, case):
        r = analyze(case["packet"], {k:v.encode() for k,v in case["snapshots_utf8"].items()}, require="primary_quote")
        row = r["claims"][0]
        self.assertEqual(row["observed_basis"], case["expected"]["basis"])
        self.assertEqual(sorted(f["code"] for f in row["findings"]), sorted(case["expected"]["codes"]))
        self.assertEqual(r["policy_met"], case["expected"]["policy_met"])