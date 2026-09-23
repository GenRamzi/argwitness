import unittest

from argwitness.contracts import InputError, catalog, normalize


def obj(properties=None, required=None, **kw):
    return {"type": "object", "properties": properties or {}, "required": required or [], **kw}


class McpdescTests(unittest.TestCase):
    def test_single_protocol(self):
        document = {
            "mcpdesc": "0.7.0",
            "info": {"name": "demo", "version": "1.0.0", "protocolVersion": "2025-06-18"},
            "tools": [{"name": "search", "inputSchema": obj({"query": {"type": "string"}}, ["query"])}],
        }
        self.assertIn("search", catalog(document))
        self.assertIn("search", catalog(document, protocol_version="2025-06-18"))

    def test_multi_protocol_requires_selection(self):
        document = {
            "mcpdesc": "0.8.0",
            "protocolVersions": ["2025-11-25", "2026-07-28"],
            "tools": [
                {"name": "run_job", "description": "legacy",
                 "protocolVersions": ["2025-11-25"], "inputSchema": obj()},
                {"name": "run_job", "description": "modern",
                 "protocolVersions": ["2026-07-28"], "inputSchema": obj()},
            ],
        }
        with self.assertRaises(InputError):
            catalog(document)

    def test_protocol_selection(self):
        document = {
            "mcpdesc": "0.8.0",
            "protocolVersions": ["2025-11-25", "2026-07-28"],
            "tools": [
                {"name": "run_job", "description": "legacy",
                 "protocolVersions": ["2025-11-25"], "inputSchema": obj()},
                {"name": "run_job", "description": "modern",
                 "protocolVersions": ["2026-07-28"], "inputSchema": obj()},
            ],
        }
        selected = catalog(document, protocol_version="2026-07-28")
        self.assertEqual(selected["run_job"]["metadata"]["description"], "modern")
        normalized = normalize(document, protocol_version="2025-11-25")
        self.assertEqual(normalized["tools"][0]["description"], "legacy")

    def test_non_mcpdesc_rejects_protocol_option(self):
        with self.assertRaises(InputError):
            catalog({"tools": [{"name": "x", "inputSchema": obj()}]}, protocol_version="2026-07-28")


if __name__ == "__main__":
    unittest.main()
