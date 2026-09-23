# Positioning and prior art

Research snapshot: 2026-09-23. The problem is real enough to have existing tools;
this project makes no claim of being unique, first, or better than all alternatives.

| Project | Publicly described focus | ArgWitness's chosen scope |
| --- | --- | --- |
| [mcp-contracts](https://github.com/mcp-contracts/mcp-contracts) | MCP snapshots, schema diffs, contract validation | Concrete breaking arguments and independent witness revalidation across saved provider envelopes |
| [Cisco mcptoolkit-contract](https://github.com/cisco-open/mcptoolkit-contract) | MCP description, comparison, lifecycle tooling | Small offline Python component usable within a larger contract pipeline |
| [mcpward](https://github.com/TsvetanG2/mcpward) | Black-box MCP security/contract checks | Saved-schema analysis and observed arguments, without executing a server |
| [GenRamzi/AgentProof](https://github.com/GenRamzi/AgentProof) | Verification of software-change claims and test evidence | Tool argument-contract compatibility, not software test execution |

This is a scope comparison based on published descriptions, not a feature audit
or a performance benchmark. Comparable projects may add overlapping features.
The implementation here is original and uses the established python-jsonschema
validator instead of inventing a JSON Schema dialect.

## Who might use it

- Maintainers changing MCP tool schemas across releases.
- Teams migrating function tools between provider wrappers.
- Agent framework authors maintaining tool adapters and call fixtures.
- CI maintainers who need a small input counterexample for review discussions.

## Test the demand

The first milestone is independent feedback on five real, sanitized schema
migrations. Ask whether the witness helped diagnose a break, whether a missed
witness matters, and whether `review` is clear enough. Improve those cases before
adding hosted dashboards, billing, live proxies, or broad platform claims.

Stars, downloads, and contributor counts are outcomes of useful work, not features
this repository can create by itself. No adoption, market leadership, or speed
advantage has been demonstrated at initial creation.
