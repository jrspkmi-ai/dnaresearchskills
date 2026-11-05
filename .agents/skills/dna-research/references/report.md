# Reporting and provenance

Use the report template and record software and versions, database snapshot checksum, input identifiers, codebook version, researcher's review, parameters, dates, command or script identity without secrets, outputs with SHA-256 hashes and limitations. Store sensitive identifiers in the private workspace. Suggested statuses describe separate stages: `AI_CANDIDATE`, `HUMAN_VALIDATED`, `DNA_EXECUTED`, `EXTERNALLY_COMPUTED`, `VISUALIZED`. They are not interchangeable; a human-entered status is a claim, not cryptographic proof. Record actual evidence for each status. Never infer execution from a filename or an XML file passing structural validation. Visualized requires a documented actual visualization.

Create a minimal local hash ledger without storing input paths or contents:

```sh
python3 scripts/dna_tool.py manifest --file /private/path/network.graphml --status DNA_EXECUTED --output /private/path/manifest.json
```

A user declares the status. The script does not establish that DNA ran. The output is not overwritten. Add study metadata to a separate private report; do not put secrets in it.
