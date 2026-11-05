# Research workflow

See the [method notes](../.agents/skills/dna-research/references/method.md) for research design and the [analysis notes](../.agents/skills/dna-research/references/analysis.md) for the official rDNA bridge. Human review is required for all statements used in analysis. There is no automated import into DNA in this version. The synthetic example is for format validation, not results.

## Optional actor normalization

Create a JSON object mapping exact recorded names to researcher-approved names. Run `python3 scripts/dna_tool.py normalize-actors statements.csv --mapping aliases.json --output reviewed-copy.csv` from the skill directory. Review the new file against its sources and keep the original. This tool does not infer identities.

The manifest command hashes local files and records a researcher-declared status. It does not verify human approval or DNA execution. See the [reporting notes](../.agents/skills/dna-research/references/report.md).
