---
name: dna-research
description: Assist researchers with Discourse Network Analysis, evidence-led statement coding, DNA and rDNA environment checks, network export, and traceable reporting. Use when preparing or analyzing a discourse network with the official DNA tools.
license: MIT
metadata:
  version: "0.1.0"
  author: John R.S.P.K.M. Isa
---
# DNA Research

Use this skill for research involving Discourse Network Analysis (DNA), not molecular DNA. Base network computations on official DNA/rDNA. Do not imply endorsement by Leifeld Lab.

1. Run `python3 scripts/dna_tool.py discover` from this skill directory. Discovery is read-only, scoped to the current execution host, and does not prove another device is ready. Interpret unknowns as unknown. Reuse an existing compatible installation.
2. If software is missing, read `references/setup.md`. Explain sources and changes; obtain explicit permission before downloading, installing, modifying configuration, or elevating. The package does not automatically install dependencies. Ask the user for a custom research directory when automatic Documents resolution is uncertain.
3. Determine research question, corpus boundary, source provenance, time frame, rights, codebook, and review protocol. Read `references/method.md` for the nine-stage workflow and analytical boundaries. Keep originals intact.
4. Extract candidate statements with source IDs, evidence location, speaker, concept, qualifier and event time. Verify quoted speakers; request human review. Use `scripts/dna_tool.py validate-corpus` and `validate-statements` for structural checks. Validation is not semantic review. Never treat `AI_CANDIDATE` as verified.
5. After researchers have validated their coding, they must import or code it in the official DNA interface. This package does not automate statement import. Read `references/analysis.md` for the R bridge, limitations, and preflight. The R bridge uses `dna_network` but is not integration-tested in the release environment. Ask researchers to confirm coding and network parameters; never invent data or claim DNA ran without proof.
6. Validate produced GraphML with `scripts/dna_tool.py graphml`. Inspection is not proof that visone or Gephi executed. Record source identifiers, codebook, versions, parameters, checksums, decisions and limitations in the report template. Do not write sensitive data, passwords, local paths or raw text to public reports.

Load only references relevant to the task: [setup](references/setup.md), [method](references/method.md), [analysis](references/analysis.md), [report](references/report.md). All scripts use local data; no telemetry or automatic upload. Remote agent host and local device may be different.
