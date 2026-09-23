import copy
import itertools
import json
import unittest

from argwitness import compare, replay, verify_witness
from argwitness.contracts import InputError, catalog, calls, errors, normalize, parse_json


def tool(schema, name="search", **extra):
    return {"tools": [{"name": name, "inputSchema": schema, **extra}]}


def obj(properties=None, required=None, **kw):
    return {"type": "object", "properties": properties or {}, "required": required or [], **kw}


class WitnessTests(unittest.TestCase):
    def witness(self, a, b, observations=()):
        report = compare(tool(a), tool(b), observations, show_values=True)
        findings = [f for f in report["findings"] if f["code"] == "AW002"]
        self.assertTrue(findings, report)
        value = findings[0]["witness"]["arguments"]
        self.assertEqual(errors(a, value), [])
        self.assertTrue(errors(b, value))
        return findings[0]["witness"]

    def test_required_field_added(self):
        self.witness(obj({"query": {"type": "string"}}), obj({"query": {"type": "string"}}, ["query"]))

    def test_enum_narrowed(self):
        self.witness(obj({"mode": {"enum": ["fast", "full"]}}, ["mode"]),
                     obj({"mode": {"enum": ["fast"]}}, ["mode"]))

    def test_numeric_boundary(self):
        self.witness(obj({"limit": {"type": "integer", "minimum": 1, "maximum": 100}}, ["limit"]),
                     obj({"limit": {"type": "integer", "minimum": 1, "maximum": 20}}, ["limit"]))

    def test_exclusive_boundary(self):
        self.witness(obj({"x": {"type": "number", "minimum": 0}}, ["x"]),
                     obj({"x": {"type": "number", "exclusiveMinimum": 0}}, ["x"]))

    def test_number_to_integer(self):
        self.witness(obj({"x": {"type": "number"}}, ["x"]), obj({"x": {"type": "integer"}}, ["x"]))

    def test_bool_not_integer_and_python_equality(self):
        self.witness(obj({"x": {"enum": [False]}}, ["x"]), obj({"x": {"enum": [0]}}, ["x"]))

    def test_additional_properties_tightened(self):
        self.witness(obj(), obj(additionalProperties=False))

    def test_removed_optional_property_from_closed_object(self):
        self.witness(obj({"q": {"type": "string"}}, additionalProperties=False), obj(additionalProperties=False))

    def test_nested_required(self):
        self.witness(obj({"address": obj({"city": {"type": "string"}})}, ["address"]),
                     obj({"address": obj({"city": {"type": "string"}}, ["city"])}, ["address"]))

    def test_array_length(self):
        self.witness(obj({"ids": {"type": "array", "items": {"type": "integer"}, "maxItems": 5}}, ["ids"]),
                     obj({"ids": {"type": "array", "items": {"type": "integer"}, "maxItems": 1}}, ["ids"]))

    def test_string_length(self):
        self.witness(obj({"x": {"type": "string", "minLength": 1}}, ["x"]),
                     obj({"x": {"type": "string", "minLength": 3}}, ["x"]))

    def test_local_ref(self):
        a = obj({"x": {"$ref": "#/$defs/limit"}}, ["x"], **{"$defs": {"limit": {"type": "integer", "maximum": 10}}})
        b = copy.deepcopy(a)
        b["$defs"]["limit"]["maximum"] = 5
        self.witness(a, b)

    def test_observed_pattern(self):
        a = obj({"id": {"type": "string", "pattern": "^[A-Z]{4}$"}}, ["id"])
        b = obj({"id": {"type": "string", "pattern": "^[A-Z]{5}$"}}, ["id"])
        witness = self.witness(a, b, [{"tool": "search", "arguments": {"id": "ABCD"}}])
        self.assertEqual(witness["source"], "observed")

    def test_shrink_drops_irrelevant_fields(self):
        a, b = obj(), obj({"x": {"type": "integer"}})
        w = self.witness(a, b, [{"tool": "search", "arguments": {"x": "bad", "unrelated": "secret"}}])
        self.assertEqual(list(w["arguments"]), ["x"])

    def test_unknown_is_not_compatible(self):
        r = compare(tool(obj({"x": {"type": "integer"}}, ["x"])), tool(obj({"x": {"type": "number"}}, ["x"])))
        self.assertEqual(r["status"], "review")
        self.assertTrue(any(f["code"] == "AW003" for f in r["findings"]))

    def test_unchanged(self):
        a = tool(obj({"a": {"type": "string"}}))
        self.assertEqual(compare(a, a)["status"], "unchanged")

    def test_metadata_review(self):
        self.assertEqual(compare(tool(obj(), description="read"), tool(obj(), description="write"))["status"], "review")

    def test_removed(self):
        self.assertEqual(compare(tool(obj()), {"tools": []})["status"], "breaking")

    def test_added(self):
        self.assertEqual(compare({"tools": []}, tool(obj()))["status"], "added")

    def test_invalid_baseline_observation(self):
        a = tool(obj({"x": {"type": "integer"}}, ["x"]))
        r = compare(a, a, [{"tool": "search", "arguments": {"x": "bad"}}])
        self.assertEqual(r["baselineInvalidCalls"], 1)
        self.assertEqual(r["status"], "review")

    def test_private_values_not_in_report(self):
        a, b = tool(obj()), tool(obj({"token": {"type": "integer"}}))
        r = compare(a, b, [{"tool": "search", "arguments": {"token": "TOP_SECRET_VALUE"}}])
        self.assertNotIn("TOP_SECRET_VALUE", json.dumps(r))
        self.assertNotIn('"arguments":', json.dumps(r))

    def test_deterministic(self):
        a, b = tool(obj()), tool(obj(required=["x"]))
        self.assertEqual(compare(a, b), compare(a, b))

    def test_verify_rechecks_not_trusts_claims(self):
        a, b = tool(obj()), tool(obj(required=["x"]))
        self.assertEqual(verify_witness(a, b, {"tool": "search", "arguments": {}})["status"], "confirmed")
        self.assertEqual(verify_witness(a, b, {"tool": "search", "arguments": {"x": 1}})["status"], "unconfirmed")

    def test_soundness_cross_product(self):
        # Independent validation of every emitted witness over 144 schema pairs.
        variants = [{"type": "integer"}, {"type": "number"}, {"type": "string"},
                    {"type": "boolean"}, {"type": "null"}, {"enum": [0, 1]},
                    {"enum": [False, True]}, {"type": "integer", "minimum": 3},
                    {"type": "string", "minLength": 2}, {"const": "abc"},
                    {"type": "array", "items": {"type": "integer"}},
                    {"anyOf": [{"type": "string"}, {"type": "number"}]}]
        from jsonschema import Draft202012Validator
        for x, y in itertools.product(variants, repeat=2):
            a, b = obj({"x": x}, ["x"]), obj({"x": y}, ["x"])
            for f in compare(tool(a), tool(b), show_values=True)["findings"]:
                if "witness" in f:
                    v = f["witness"]["arguments"]
                    self.assertTrue(Draft202012Validator(a).is_valid(v))
                    self.assertFalse(Draft202012Validator(b).is_valid(v))


class InputTests(unittest.TestCase):
    def test_mcp_jsonrpc(self):
        self.assertIn("search", catalog({"jsonrpc": "2.0", "id": 1, "result": tool(obj())}))

    def test_mcp_contracts_snapshot(self):
        snapshot = {
            "snapshotVersion": "1.0.0",
            "server": {"name": "demo"},
            "tools": {
                "search": {
                    "description": "Search",
                    "inputSchema": obj({"limit": {"type": "integer", "maximum": 100}}, ["limit"]),
                }
            },
        }
        self.assertIn("search", catalog(snapshot))
        normalized = normalize(snapshot)
        self.assertEqual(normalized["tools"][0]["name"], "search")
        self.assertEqual(normalized["tools"][0]["description"], "Search")

    def test_mcp_contracts_snapshot_breaking_witness(self):
        before = {
            "snapshotVersion": "1.0.0",
            "tools": {
                "search": {
                    "inputSchema": obj({"limit": {"type": "integer", "maximum": 100}}, ["limit"])
                }
            },
        }
        after = copy.deepcopy(before)
        after["tools"]["search"]["inputSchema"]["properties"]["limit"]["maximum"] = 20
        report = compare(before, after, show_values=True)
        self.assertEqual(report["status"], "breaking")
        finding = next(f for f in report["findings"] if "witness" in f)
        self.assertEqual(finding["tool"], "search")
        self.assertEqual(finding["witness"]["arguments"]["limit"], 100)

    def test_mcp_contracts_snapshot_name_conflict(self):
        with self.assertRaises(InputError):
            catalog({
                "snapshotVersion": "1.0.0",
                "tools": {"search": {"name": "other", "inputSchema": obj()}},
            })

    def test_chat_completions(self):
        self.assertIn("search", catalog([{"type": "function", "function": {"name": "search", "parameters": obj()}}]))

    def test_responses(self):
        self.assertIn("search", catalog([{"type": "function", "name": "search", "parameters": obj(), "strict": True}]))

    def test_anthropic(self):
        self.assertIn("search", catalog([{"name": "search", "input_schema": obj()}]))

    def test_normalize_idempotent(self):
        a = [{"type": "function", "function": {"name": "search", "parameters": obj()}}]
        self.assertEqual(normalize(a), normalize(normalize(a)))

    def test_call_formats(self):
        records = [{"method": "tools/call", "params": {"name": "search", "arguments": {}}},
                   {"type": "function", "function": {"name": "search", "arguments": "{}"}},
                   {"type": "function_call", "name": "search", "arguments": "{}"},
                   {"type": "tool_use", "name": "search", "input": {}}]
        self.assertEqual(calls(records), [{"tool": "search", "arguments": {}}] * 4)

    def test_missing_args_rejected(self):
        with self.assertRaises(InputError):
            calls([{"name": "search"}])

    def test_duplicate_names(self):
        with self.assertRaises(InputError):
            catalog({"tools": tool(obj())["tools"] * 2})

    def test_remote_ref_blocked_before_network(self):
        with self.assertRaises(InputError):
            catalog(tool({"$ref": "https://example.com/schema"}))

    def test_nested_remote_ref_blocked(self):
        with self.assertRaises(InputError):
            catalog(tool(obj({"x": {"$ref": "https://example.com/private"}})))

    def test_ref_like_data_is_data(self):
        catalog(tool(obj(default={"$ref": "https://example.com/data"})))

    def test_unknown_keyword(self):
        with self.assertRaises(InputError):
            catalog(tool({"type": "object", "maxLenght": 2}))

    def test_legacy_draft_rejected(self):
        with self.assertRaises(InputError):
            catalog(tool({"$schema": "http://json-schema.org/draft-07/schema#"}))

    def test_duplicate_json_keys(self):
        with self.assertRaises(InputError):
            parse_json('{"a":1,"a":2}')

    def test_non_finite_json(self):
        with self.assertRaises(InputError):
            parse_json('{"a":NaN}')

    def test_malformed_schema(self):
        with self.assertRaises(InputError):
            catalog(tool({"type": "object", "required": "x"}))

    def test_replay_never_invokes_tools(self):
        r = replay(tool(obj()), [{"tool": "search", "arguments": {"shell": "do not execute"}},
                                {"tool": "missing", "arguments": {}}])
        self.assertEqual([x["status"] for x in r["calls"]], ["valid", "invalid"])
        self.assertNotIn("do not execute", json.dumps(r))

    def test_format_annotation_only(self):
        # Draft 2020-12 format is annotation-only in this release, explicitly documented.
        self.assertEqual(errors(obj({"x": {"type": "string", "format": "email"}}), {"x": "not-email"}), [])


if __name__ == "__main__":
    unittest.main()
