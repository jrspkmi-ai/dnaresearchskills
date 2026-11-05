# Troubleshooting

- Missing means not found in the limited search, not definitely absent. Provide a local path to DNA manually.
- `rJava` load failure can indicate an incompatible Java/R architecture or configuration. Consult the respective official documentation.
- Documents location is uncertain: choose a path explicitly with `init --root`.
- GraphML parse success checks a limited XML structure, not correctness of edge semantics or successful visualization.
- If the R bridge fails, stop and retain the error privately after removing secrets. Check upstream `help("dna_network", package="rDNA")` and versions. The bridge is not yet end-to-end tested.
