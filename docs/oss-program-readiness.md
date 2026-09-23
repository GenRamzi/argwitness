# OSS support-program readiness

Checked against official pages on 2026-09-23. This is a project readiness record,
not a submitted application or an eligibility certification.

## Claude for Open Source

The current maintainer routes include: 500 dependent repositories, 100 dependent
packages, 200,000 aggregate monthly package downloads, recognized foundation/language
maintainer status, 100 merged PRs to others' public repositories in 12 months,
20 external contributors with merged PRs in 12 months, or OpenSSF criticality
score at least 0.4. These are alternatives, not requirements to satisfy together.
There is also a discretionary ecosystem-impact route requiring meaningful dependence.

General requirements include eligible age/residency, a GitHub account at least two
years old and in good standing, public OSS activity within 90 days, an OSI-approved
license, and specified Anthropic affiliation exclusions. Account and personal
requirements need owner confirmation; this project cannot establish them.

The terms prohibit fabricated or artificially inflated metrics and reserve selection
discretion. Creating a new MIT repository does not satisfy impact thresholds.

Sources: [program](https://claude.com/contact-sales/claude-for-oss),
[terms](https://www.anthropic.com/claude-for-oss-terms).

## Codex for Open Source

The form requests a public GitHub profile/repository, primary/core maintainer role,
and an explanation of project usage or importance (maximum 500 characters). The
official criteria emphasize meaningful usage, adoption, ecosystem importance, and
ongoing maintenance. No fixed star threshold is stated on the checked form.

API credits and Codex Security are additional options with separate considerations.
The form asks for the ChatGPT-associated email and, for credits, an OpenAI
organization ID and a use explanation. Accurate information is required and
selection is discretionary.

Sources: [form](https://openai.com/form/codex-for-oss/),
[terms](https://learn.chatgpt.com/docs/codex-for-oss-terms).

## Status of this new project

| Evidence | Status at creation |
| --- | --- |
| Working implementation and reproducible demo | Implemented; see validation record |
| OSI-approved license | MIT included |
| Maintainer documentation and contribution path | Included |
| Public repository and recent public contribution | Published at https://github.com/GenRamzi/argwitness |
| Registry release | `argwitness==0.1.0` published to PyPI on 2026-09-23 via GitHub OIDC trusted publishing |
| Independent users/dependents/downloads | Not established |
| External contributors | Not established |
| Criticality score | Not measured; no claim |
| Personal/account eligibility | Not fully verified |
| Application submission or acceptance | Not performed or claimed |

## Honest draft language

**Repository significance (under 500 characters):**

> ArgWitness is an early-stage MIT-licensed tool that finds concrete JSON arguments
> accepted by an old AI tool schema and rejected by a new one. It imports saved MCP,
> OpenAI, and Anthropic tool definitions and validates captured calls offline. It
> helps maintainers reproduce contract breaks without API costs or tool side effects.
> Independent adoption is not yet established.

**Proposed use of support:**

> I would use the tools to investigate real schema-compatibility reports, expand
> regression fixtures, review contributions, improve bounded counterexample search,
> and maintain releases. I would evaluate model-assisted repair suggestions against
> deterministic schema validation rather than treating generated claims as proof.

These drafts do not establish qualifying impact. Registry publication is now verified; before applying, confirm the actual applicant identity and account details and include genuine downstream use if it exists. Do not count
tests, self-owned demos, or generated activity as independent adoption.
