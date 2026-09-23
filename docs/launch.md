# Initial adoption work

The next product milestone is useful independent feedback, not a star target.

## One-sentence description

ArgWitness finds concrete calls that break when AI tool schemas change, across
saved MCP, OpenAI, and Anthropic definitions, without executing the tools.

## Demo to share after publication

1. Run `python examples/demo.py` in a source checkout.
2. Show the OLD maximum of 100 and NEW maximum of 20.
3. Show the generated call that OLD accepts and NEW rejects.
4. Show the replay result and independent witness verification.
5. Explain that unresolved changes return review, and that this is an alpha.

## Ask early adopters for specific evidence

Invite maintainers you already have permission to contact to try one sanitized
schema migration. Ask what was useful, which witness was missed, and what they
would need to use it in CI. Do not send unsolicited bulk messages or manufacture
issues, dependents, or external contributions.

Potential contribution tasks:

- A real nested-union migration fixture with expected old/new results.
- A safe, bounded method to generate strings for common regex fragments.
- A precise diagnostics improvement for recursive schemas.
- Independently verified Windows installation and CLI instructions.

## Evidence log template

Record public integration URL, independent maintainer, date, issue resolved, and
permission to describe the result. Keep self-owned demonstrations separate.
Measure false breaking findings, missed known counterexamples, and review burden.
Publish methodology before making comparative accuracy or performance claims.

## Application timing

The OSS-program readiness document records today's gaps. A source release can
start an adoption process; it cannot create the historical usage required for
some support tracks. Recheck program terms and actual metrics before submission.
