# Schema support and limits

## Validation semantics

ArgWitness uses `jsonschema.Draft202012Validator`. The default dialect is Draft
2020-12; an explicit different `$schema` is an input error. Tool arguments must be
objects, even if a permissive schema would also accept scalar values.

Supported schema keywords:

- Objects: `properties`, `patternProperties`, `additionalProperties`,
  `unevaluatedProperties`, `propertyNames`, `required`, `dependentRequired`,
  `dependentSchemas`, `minProperties`, `maxProperties`.
- Arrays: `items`, `prefixItems`, `contains`, `minContains`, `maxContains`,
  `unevaluatedItems`, `uniqueItems`, `minItems`, `maxItems`.
- Scalars: `type`, `enum`, `const`, `minimum`, `maximum`, `exclusiveMinimum`,
  `exclusiveMaximum`, `multipleOf`, `minLength`, `maxLength`, `pattern`.
- Logic: `allOf`, `anyOf`, `oneOf`, `not`, `if`, `then`, `else`.
- References: `$defs` and local JSON Pointer `$ref` values such as `#/$defs/Item`.
- Annotations: `title`, `description`, `default`, `examples`, `$comment`,
  `deprecated`, `readOnly`, `writeOnly`, and `format`.

`format` is **annotation-only**: `format: email` does not reject a non-email string.
Defaults do not fill missing arguments; examples do not constrain validity.
Unknown keywords are rejected rather than silently ignored. `$id`, `$anchor`,
dynamic references, external references, percent-encoded reference fragments, and
legacy `definitions`/`dependencies` are currently unsupported. Boolean subschemas
are accepted. This is not a complete MCP or provider request validator.

Only schema positions are walked as schemas: a `$ref` key inside `default`, `enum`,
or `examples` is ordinary instance data. JSON duplicates, NaN, Infinity, and
non-UTF-8 files are rejected. Mappings are compared using canonical JSON so
Python's `False == 0` does not hide a contract change.

## Generation is narrower than validation

The generator combines schema defaults/examples/enums, scalar boundaries, required
and optional object shapes, nested property variants, array lengths/items, and
candidate hints from logical branches and local refs. Every emitted witness is
validated against both original schemas; candidate-generation heuristics cannot
turn an invalid OLD argument into a breaking witness.

Generated search is bounded to 512 candidates per tool by default (`--limit`
16..4096), recursion depth 8, 64 properties per object, generated string lengths
up to 128 and array lengths up to 64, and 20,000 recursive candidate calls. There
is no Cartesian-product completeness guarantee. The shrinker tries up to 128
changes and does not claim global minimality. Observed calls can supply values
outside those generation limits.

Input files are capped at 4 MiB each; catalogs at 256 tools, observations at 5,000
calls, and schema traversal depth at 32. There is no hard CPU deadline. Complex
regexes and recursive references require external resource limits for untrusted
data. Evaluation failures are input errors, never compatibility approval.

Unchanged schemas are not searched. A changed schema with no found witness always
requires review, including harmless widening or annotation-only changes inside
the input schema. Tool removal is a structural break, not an argument witness.

## Source references

- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/json-schema-core)
- [Object validation](https://json-schema.org/understanding-json-schema/reference/object)
- [python-jsonschema](https://python-jsonschema.readthedocs.io/)
- [MCP tools specification](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)
