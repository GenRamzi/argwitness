"""Public API. A breaking witness always passes OLD and fails NEW validation."""

from .contracts import catalog, calls, canonical, digest, errors, InputError
from .generate import Search, shrink


def _counterexample(old, new, value):
    return isinstance(value, dict) and not errors(old, value) and bool(errors(new, value))


def _witness(old, new, value, source, show_values):
    small = shrink(value, lambda x: _counterexample(old, new, x))
    result = {"source": source, "oldValid": True, "newValid": False,
              "violations": errors(new, small), "argumentsIncluded": show_values}
    if show_values:
        result["arguments"] = small
    return result


def compare(before, after, observations=(), *, limit=512, show_values=False):
    if isinstance(limit, bool) or not isinstance(limit, int) or not 16 <= limit <= 4096:
        raise InputError("Candidate limit must be 16..4096")
    old, new = catalog(before), catalog(after)
    observed = calls(observations)
    findings = []
    baseline_invalid = 0
    for index, call in enumerate(observed):
        if call["tool"] not in old or errors(old[call["tool"]]["inputSchema"], call["arguments"]):
            baseline_invalid += 1
            findings.append({"tool": call["tool"], "status": "review", "code": "AW005",
                             "callIndex": index, "reason": "Observed call is invalid against baseline"})
    for name in sorted(set(old) | set(new)):
        if name not in old:
            findings.append({"tool": name, "status": "added", "code": "AW006", "reason": "Tool added"})
            continue
        if name not in new:
            findings.append({"tool": name, "status": "breaking", "code": "AW001", "reason": "Tool removed"})
            continue
        a, b = old[name]["inputSchema"], new[name]["inputSchema"]
        if canonical(old[name]["metadata"]) != canonical(new[name]["metadata"]):
            findings.append({"tool": name, "status": "review", "code": "AW004",
                             "reason": "Tool metadata changed; routing or behavior may differ"})
        if canonical(a) == canonical(b):
            findings.append({"tool": name, "status": "unchanged", "code": "AW000",
                             "reason": "Input schema unchanged"})
            continue
        found = None
        tested = 0
        for call in observed:
            if call["tool"] == name and _counterexample(a, b, call["arguments"]):
                found = _witness(a, b, call["arguments"], "observed", show_values)
                break
        if found is None:
            for candidate in Search(a, b, limit).candidates(a, b):
                tested += 1
                if _counterexample(a, b, candidate):
                    found = _witness(a, b, candidate, "generated", show_values)
                    break
        if found is not None:
            findings.append({"tool": name, "status": "breaking", "code": "AW002",
                             "reason": "Concrete call accepted before and rejected after",
                             "candidatesTested": tested, "witness": found})
        else:
            findings.append({"tool": name, "status": "review", "code": "AW003",
                             "reason": "Schema changed; bounded search found no counterexample. Compatibility is unknown.",
                             "candidatesTested": tested})
    statuses = {f["status"] for f in findings}
    status = next((s for s in ("breaking", "review", "added") if s in statuses), "unchanged")
    return {"schema": "argwitness.report/v1", "version": "0.1.0", "status": status,
            "baselineDigest": digest(old), "candidateDigest": digest(new),
            "observations": len(observed), "baselineInvalidCalls": baseline_invalid,
            "searchLimit": limit, "findings": findings}


def replay(document, observations, *, show_values=False):
    tools = catalog(document)
    results = []
    for index, call in enumerate(calls(observations)):
        exists = call["tool"] in tools
        violations = errors(tools[call["tool"]]["inputSchema"], call["arguments"]) if exists else []
        item = {"index": index, "tool": call["tool"], "status": "valid" if exists and not violations else "invalid",
                "violations": violations, "reason": "Schema validation" if exists else "Unknown tool"}
        if show_values:
            item["arguments"] = call["arguments"]
        results.append(item)
    return {"schema": "argwitness.replay/v1", "status": "invalid" if any(r["status"] == "invalid" for r in results) else "valid",
            "catalogDigest": digest(tools), "calls": results}


def verify_witness(before, after, witness):
    old, new = catalog(before), catalog(after)
    call = calls([witness])[0]
    name = call["tool"]
    if name not in old or name not in new:
        raise InputError("Witness verification requires the tool in both catalogs")
    confirmed = _counterexample(old[name]["inputSchema"], new[name]["inputSchema"], call["arguments"])
    return {"schema": "argwitness.verification/v1", "tool": name,
            "status": "confirmed" if confirmed else "unconfirmed",
            "baselineDigest": digest(old), "candidateDigest": digest(new)}
