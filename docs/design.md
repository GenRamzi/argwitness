# Design

The question is directional: **does an argument object exist that OLD accepts and
NEW rejects?** Input compatibility requires preserving the previously accepted
domain. A single valid counterexample disproves that property.

1. Parse strict JSON and normalize provider envelopes without executing content.
2. Validate schema syntax, supported keywords, dialect, and reference policy.
3. Check supplied observations against OLD; label invalid baseline data for review.
4. Prefer an observed old-valid/new-invalid input; otherwise generate candidates.
5. Validate every candidate with the original OLD and NEW schemas.
6. Shrink a confirmed counterexample while preserving that exact predicate.
7. Emit deterministic evidence, schema paths, and normalized catalog digests.

`contracts.py` owns parsing, normalization, and validation. `generate.py` owns
bounded search and shrinking. `engine.py` owns findings, replay, and independent
verification. `cli.py` owns input/output and exit codes.

## Finding codes

| Code | Meaning |
| --- | --- |
| AW000 | Input schema unchanged |
| AW001 | Tool removed |
| AW002 | Concrete old-valid/new-invalid argument |
| AW003 | Schema changed but no counterexample found |
| AW004 | Metadata changed; semantic or routing review needed |
| AW005 | Observed call invalid in the baseline |
| AW006 | Tool added |

Top-level comparison precedence is breaking, then review, then added, then unchanged.
All findings remain in the report even when one takes precedence.

## Evidence scope

The report format `argwitness.report/v1` includes digests over normalized catalogs.
These detect which input definitions were used; they do not authenticate origin.
No clock, filesystem path, API credentials, or machine identity is collected.
Schema paths can contain user-defined names. Values are included only by explicit
request, except the separate normalization command, which prints the whole catalog.

`verify` independently evaluates one supplied witness. It does not trust a report's
claimed oldValid/newValid fields and does not validate a whole report or signature.
It needs the baseline, candidate, and `{tool, arguments}` JSON.

Schema compatibility does not establish equivalent tool behavior. A server can
silently change units, side effects, auth, or returned meanings while exposing an
identical input schema. Such questions require separate runtime and semantic tests.
