import copy
import unittest

from quoteledger.cli import intake
from quoteledger.core import InputError, analyze, digest
from tools.corpus import base


class BoundaryTests(unittest.TestCase):
    def test_end_past_snapshot_is_not_truncated_into_a_match(self):
        packet, observations = base()
        text = observations["source-a"].decode()
        packet["claims"][0]["citations"][0].update(
            start=0, end=len(text) + 1, quote=text)
        result = analyze(packet, observations)
        self.assertEqual(result["claims"][0]["citations"][0]["result"], "SPAN_MISMATCH")

    def test_unicode_offsets_are_codepoints_not_bytes(self):
        packet, _ = base()
        raw = "🪷 abc Ω".encode()
        packet["sources"][0]["sha256"] = digest(raw)
        packet["claims"][0]["citations"][0].update(start=2, end=5, quote="abc")
        result = analyze(packet, {"source-a": raw}, require="primary_quote")
        self.assertTrue(result["policy_met"])

    def test_line_endings_remain_literal(self):
        packet, _ = base()
        raw = b"First.\r\nSecond."
        packet["sources"][0]["sha256"] = digest(raw)
        packet["claims"][0]["citations"][0].update(
            start=0, end=len(raw), quote="First.\nSecond.")
        result = analyze(packet, {"source-a": raw})
        self.assertEqual(result["claims"][0]["citations"][0]["result"], "SPAN_MISMATCH")

    def test_csv_row_bound_is_enforced(self):
        raw = ("claim,title,url\n" + "A claim,A title,\n" * 1001).encode()
        with self.assertRaises(InputError):
            intake(raw, "claim", "title", "url")