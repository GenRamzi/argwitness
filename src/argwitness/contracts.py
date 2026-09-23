"""Strict input normalization. Nothing in a catalog is executed or fetched."""

import hashlib
import json
import math
import re
from pathlib import Path

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError
from referencing import Registry
from referencing.exceptions import NoSuchResource


class InputError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def _pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InputError("Duplicate JSON object key")
        result[key] = value
    return result


def parse_json(text):
    def invalid_constant(_):
        raise InputError("Non-finite numbers are not JSON")
    def finite_float(text):
        number = float(text)
        if not math.isfinite(number):
            raise InputError("Non-finite numbers are not JSON")
        return number
    try:
        return json.loads(text, object_pairs_hook=_pairs, parse_constant=invalid_constant, parse_float=finite_float)
    except (ValueError, RecursionError) as exc:
        raise InputError("Invalid JSON (duplicate keys and non-finite numbers are rejected)") from exc


def read_json(path):
    return parse_json(read_text(path))


def read_text(path):
    with Path(path).open("rb") as stream:
        data = stream.read(4 * 1024 * 1024 + 1)
    if len(data) > 4 * 1024 * 1024:
        raise InputError("Input exceeds 4 MiB")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InputError("Expected UTF-8") from exc


SCHEMA_MAPS = {"properties", "patternProperties", "$defs", "dependentSchemas"}
SCHEMA_ARRAYS = {"allOf", "anyOf", "oneOf", "prefixItems"}
SCHEMA_SINGLE = {"additionalProperties", "unevaluatedProperties", "propertyNames", "items",
                 "contains", "unevaluatedItems", "not", "if", "then", "else"}
SUPPORTED = SCHEMA_MAPS | SCHEMA_ARRAYS | SCHEMA_SINGLE | {
    "$schema", "$ref", "type", "enum", "const", "required", "dependentRequired",
    "minProperties", "maxProperties", "minItems", "maxItems", "uniqueItems",
    "minContains", "maxContains", "minLength", "maxLength", "pattern", "format",
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf",
    "title", "description", "default", "examples", "$comment", "deprecated",
    "readOnly", "writeOnly",
}
DIALECT = "https://json-schema.org/draft/2020-12/schema"


def schema_nodes(schema, depth=0):
    if depth > 32:
        raise InputError("Schema nesting exceeds 32 levels")
    if isinstance(schema, bool):
        return
    if not isinstance(schema, dict):
        raise InputError("A schema must be an object or boolean")
    yield schema
    for key in SCHEMA_MAPS & schema.keys():
        if not isinstance(schema[key], dict):
            raise InputError("Invalid schema map")
        for child in schema[key].values():
            yield from schema_nodes(child, depth + 1)
    for key in SCHEMA_ARRAYS & schema.keys():
        if not isinstance(schema[key], list):
            raise InputError("Invalid schema array")
        for child in schema[key]:
            yield from schema_nodes(child, depth + 1)
    for key in SCHEMA_SINGLE & schema.keys():
        yield from schema_nodes(schema[key], depth + 1)


def local_ref(root, ref):
    if ref == "#":
        return root
    if not isinstance(ref, str) or not ref.startswith("#/") or "%" in ref:
        raise InputError("Only local JSON Pointer refs (#/$defs/...) are supported")
    if re.search(r"~(?![01])", ref):
        raise InputError("Invalid JSON Pointer escape")
    node = root
    try:
        for part in ref[2:].split("/"):
            part = part.replace("~1", "/").replace("~0", "~")
            node = node[int(part)] if isinstance(node, list) else node[part]
    except (KeyError, IndexError, ValueError, TypeError) as exc:
        raise InputError("Unresolved local JSON Pointer") from exc
    if not isinstance(node, (dict, bool)):
        raise InputError("Reference target is not a schema")
    return node


def check_schema(schema):
    try:
        Draft202012Validator.check_schema(schema)
    except (SchemaError, RecursionError) as exc:
        raise InputError("Invalid Draft 2020-12 schema") from exc
    nodes = list(schema_nodes(schema))
    for node in nodes:
        if set(node) - SUPPORTED:
            raise InputError("Unsupported schema keyword; see docs/schema-support.md")
        if "$schema" in node and node["$schema"].rstrip("#") != DIALECT:
            raise InputError("Only JSON Schema Draft 2020-12 is supported")
        if "$ref" in node:
            target = local_ref(schema, node["$ref"])
            # Ref targets in data annotations are intentionally unsupported.
            if isinstance(target, dict) and not any(target is candidate for candidate in nodes):
                raise InputError("Reference must target a schema position")
    return schema


def no_remote(uri):
    raise NoSuchResource(ref=uri)


def validator(schema):
    return Draft202012Validator(schema, registry=Registry(retrieve=no_remote))


def errors(schema, value):
    try:
        # No raw error messages: they can contain private argument or enum values.
        result = []
        for error in validator(schema).iter_errors(value):
            result.append({"keyword": error.validator,
                           "instancePath": list(error.absolute_path),
                           "schemaPath": list(error.absolute_schema_path)})
            if len(result) >= 10:
                break
        return result
    except Exception as exc:
        if isinstance(exc, InputError):
            raise
        raise InputError("Schema evaluation failed; recursive or unsupported reference") from exc


def _mcp_contracts_snapshot_tools(document):
    """Convert an mcp-contracts v1-style snapshot tool map into a tool array."""
    tools = document.get("tools")
    if not isinstance(tools, dict):
        raise InputError("mcp-contracts snapshot requires a tools object")
    if len(tools) > 256:
        raise InputError("Expected at most 256 tools")
    result = []
    for name, raw in tools.items():
        if not isinstance(name, str) or not name or len(name) > 256:
            raise InputError("mcp-contracts tool keys must be non-empty strings")
        if not isinstance(raw, dict):
            raise InputError("mcp-contracts tool entry must be an object")
        if "name" in raw and raw["name"] != name:
            raise InputError("mcp-contracts tool key conflicts with embedded name")
        entry = dict(raw)
        entry["name"] = name
        result.append(entry)
    return result


def catalog(document):
    """Accept saved MCP/OpenAI/Anthropic catalogs and mcp-contracts snapshots."""
    if isinstance(document, dict):
        if "result" in document:
            document = document["result"]
        if isinstance(document, dict):
            if document.get("nextCursor"):
                raise InputError("Incomplete MCP catalog: combine every tools/list page and remove nextCursor")
            if "snapshotVersion" in document:
                document = _mcp_contracts_snapshot_tools(document)
            else:
                document = document.get("tools")
    if not isinstance(document, list) or len(document) > 256:
        raise InputError("Expected a tool array or {tools: [...]} (maximum 256)")
    normalized = {}
    for tool in document:
        if not isinstance(tool, dict):
            raise InputError("Tool entry must be an object")
        entry = tool.get("function", tool)
        if not isinstance(entry, dict):
            raise InputError("Invalid function tool")
        if "type" in tool and tool["type"] != "function":
            raise InputError("Built-in provider tools are not supported")
        name = entry.get("name")
        if not isinstance(name, str) or not name or len(name) > 256:
            raise InputError("Tool name must be a non-empty string (maximum 256 characters)")
        if name in normalized:
            raise InputError("Duplicate tool name; namespace tools from different servers first")
        keys = [k for k in ("inputSchema", "input_schema", "parameters") if k in entry]
        if len(keys) != 1:
            raise InputError("Each tool must have exactly one inputSchema, input_schema, or parameters")
        schema = check_schema(entry[keys[0]])
        # Preserve provider metadata for review, including strict and annotations.
        metadata = {k: v for k, v in entry.items() if k not in {"name", *keys}}
        if entry is not tool:
            metadata["_wrapper"] = {k: v for k, v in tool.items() if k != "function"}
        normalized[name] = {"name": name, "inputSchema": schema, "metadata": metadata}
    return normalized


def normalize(document):
    return {"tools": [{"name": tool["name"], "inputSchema": tool["inputSchema"], **tool["metadata"]}
                      for _, tool in sorted(catalog(document).items())]}


def calls(records):
    result = []
    for record in records:
        if not isinstance(record, dict):
            raise InputError("Each call must be an object")
        if record.get("method") == "tools/call":
            record = record.get("params", {})
        elif "function" in record:
            record = record["function"]
        if not isinstance(record, dict):
            raise InputError("Invalid call envelope")
        name = record.get("tool", record.get("name"))
        if not isinstance(name, str) or not name:
            raise InputError("Each call requires a tool/name")
        key = "input" if record.get("type") == "tool_use" else "arguments"
        if key not in record:
            raise InputError("Missing call arguments")
        arguments = record[key]
        if isinstance(arguments, str):
            arguments = parse_json(arguments)
        if not isinstance(arguments, dict):
            raise InputError("Tool arguments must be a JSON object")
        result.append({"tool": name, "arguments": arguments})
        if len(result) > 5000:
            raise InputError("Maximum 5000 calls per comparison")
    return result
