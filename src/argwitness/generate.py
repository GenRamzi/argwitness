"""Deterministic bounded search, never a proof of schema inclusion."""

import copy
import math

from .contracts import canonical, local_ref, validator


def unique(values, limit):
    seen = set()
    result = []
    for value in values:
        key = canonical(value)
        if key not in seen:
            seen.add(key)
            result.append(value)
            if len(result) >= limit:
                break
    return result


class Search:
    def __init__(self, old, new, limit=512):
        self.roots = (old, new)
        self.limit = limit
        self.fuel = 20000

    def expand(self, schema, root, depth=0):
        if not isinstance(schema, dict) or depth > 8:
            return []
        result = [schema]
        if "$ref" in schema:
            result.extend(self.expand(local_ref(root, schema["$ref"]), root, depth + 1))
        for key in ("allOf", "anyOf", "oneOf"):
            for child in schema.get(key, []):
                result.extend(self.expand(child, root, depth + 1))
        return result[:64]

    def candidates(self, old, new, depth=0):
        self.fuel -= 1
        if depth > 8 or self.fuel <= 0:
            return [None, {}, "", 0]
        groups = [self.expand(old, self.roots[0]), self.expand(new, self.roots[1])]
        schemas = groups[0] + groups[1]
        values = []
        for schema in schemas:
            values.extend(schema.get("enum", []))
            if "const" in schema:
                values.append(schema["const"])
            if "default" in schema:
                values.append(schema["default"])
            values.extend(schema.get("examples", []))
        values.extend([None, False, True, 0, 1, -1, 0.5, "", "a", "x", {}, []])
        for schema in schemas:
            for key in ("minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum", "multipleOf"):
                if key in schema:
                    n = schema[key]
                    values.extend([n, n - 1, n + 1, math.floor(n), math.ceil(n)])
                    if isinstance(n, float):
                        values.extend([math.nextafter(n, -math.inf), math.nextafter(n, math.inf)])
            for key in ("minLength", "maxLength"):
                if key in schema:
                    values.extend("a" * n for n in (schema[key] - 1, schema[key], schema[key] + 1)
                                  if 0 <= n <= 128)
        props = [{}, {}]
        required = [set(), set()]
        for index, group in enumerate(groups):
            for schema in group:
                props[index].update(schema.get("properties", {}))
                required[index].update(schema.get("required", []))
        names = sorted(set(props[0]) | set(props[1]) | required[0] | required[1])[:64]
        options = {}
        for name in names:
            before = props[0].get(name, {})
            after = props[1].get(name, {})
            samples = self.candidates(before, after, depth + 1)
            # Prefer a value accepted by the old property to make useful object seeds.
            try:
                check = validator(self.roots[0]).evolve(schema=before)
                good = [v for v in samples if check.is_valid(v)]
            except Exception:
                good = []
            options[name] = unique(good + samples, 48)
        if names:
            seeds = [
                {k: options[k][0] for k in names if k in required[0]},
                {k: options[k][0] for k in names if k in required[1]},
                {k: options[k][0] for k in names},
            ]
            for seed in seeds:
                values.append(seed)
                for name in names:
                    for value in options[name]:
                        values.append({**seed, name: value})
                    values.append({k: v for k, v in seed.items() if k != name})
                extra = "__argwitness_extra__"
                while extra in names:
                    extra += "_"
                values.append({**seed, extra: 0})
        else:
            values.append({"__argwitness_extra__": 0})
        # Array length and item-type boundaries; bounded, not exhaustive Cartesian products.
        if any(s.get("type") == "array" or "items" in s or "prefixItems" in s for s in schemas):
            item_schemas = [next((s["items"] for s in g if "items" in s), {}) for g in groups]
            items = self.candidates(*item_schemas, depth + 1)[:24]
            lengths = {0, 1, 2}
            for schema in schemas:
                for key in ("minItems", "maxItems", "minContains", "maxContains"):
                    if key in schema:
                        lengths.update((schema[key] - 1, schema[key], schema[key] + 1))
                prefix = schema.get("prefixItems", [])
                if prefix:
                    values.append([self.candidates(p, {}, depth + 1)[0] for p in prefix[:32]])
            for n in sorted(lengths):
                if 0 <= n <= 64:
                    for item in items:
                        values.append([item] * n)
                    values.append(list(range(n)))
        # Skip numeric overflow produced by boundary probes.
        values = [v for v in values if not isinstance(v, float) or math.isfinite(v)]
        return unique(values, self.limit)


def shrink(value, predicate, budget=128):
    """Try structural deletions and simpler scalars; no global minimality claim."""
    current = copy.deepcopy(value)

    def variants(node):
        if isinstance(node, dict):
            for key in sorted(node):
                yield {k: v for k, v in node.items() if k != key}
            for key in sorted(node):
                for simpler in variants(node[key]):
                    yield {**node, key: simpler}
        elif isinstance(node, list):
            for i in range(len(node)):
                yield node[:i] + node[i + 1:]
            for i, item in enumerate(node):
                for simpler in variants(item):
                    yield node[:i] + [simpler] + node[i + 1:]
        else:
            for simple in [None, False, 0, 1, "", "a"]:
                if len(canonical(simple)) < len(canonical(node)):
                    yield simple

    while budget > 0:
        improved = False
        for candidate in variants(current):
            budget -= 1
            if predicate(candidate):
                current = candidate
                improved = True
                break
            if budget <= 0:
                break
        if not improved:
            break
    return current
