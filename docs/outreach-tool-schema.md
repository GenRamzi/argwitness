# tool-schema outreach

Preferred upstream channel: GitHub Discussions, per `slegarraga/tool-schema/.github/ISSUE_TEMPLATE/config.yml`.

## Discussion title

Interop idea: regression witnesses for provider tool-schema changes

## Discussion body

Hi Sebastian — I maintain ArgWitness, a deterministic tool that compares old/new AI tool schemas and, when it can establish one, returns a concrete argument object that was valid before and invalid after.

I added a pinned interoperability CI check against `slegarraga/tool-schema`. The workflow checks out tool-schema commit `56ca752ca2a4d25af17b542259fc75b69aceaba8`, builds it from source, and uses its real `toTool` implementation to generate OpenAI, Anthropic, and MCP envelopes from the same schema migration (`limit.maximum: 100 -> 20`).

ArgWitness then independently validates the generated before/after envelopes and requires a concrete old-valid/new-invalid witness for all three provider outputs. The CI is merged here:

https://github.com/GenRamzi/argwitness/pull/14

ArgWitness v0.2.0 is published here:

https://pypi.org/project/argwitness/0.2.0/

The intent is complementary: tool-schema handles provider-valid transformation/linting; ArgWitness handles regression evidence between two saved versions. No runtime dependency or change to tool-schema is required.

Would a small interoperability/CI recipe be useful in tool-schema's docs, or would you prefer this remain entirely external? If useful, I can prepare a minimal docs contribution around the workflow above.
