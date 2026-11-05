# Installation

## Skill

Download or clone the repository. Open the repository directory in an agent that supports project-local `.agents/skills`. OpenCode supports this path. Other agents have different discovery rules; see `adapters/`. Copy the entire `dna-research` directory, including scripts, references and templates, to the documented skill directory for your client. Do not copy only SKILL.md. Confirm the client version's current documentation before installation.

## Software

This project does not bundle, download or install third-party applications. Obtain DNA/rDNA 3.1.2 from the [official release](https://github.com/leifeld-lab/dna/releases/tag/v3.1.2). DNA needs Java 11 or later. The upstream rDNA release includes a JAR and depends on rJava. R and rJava installation depends on OS and Java configuration; use upstream R and rJava guidance. For the release source package, after approving the network download and reviewing upstream instructions, the official repository documents:

```r
install.packages("https://github.com/leifeld-lab/dna/releases/download/v3.1.2/rDNA_3.1.2.tar.gz", repos = NULL, type = "source")
```

The command changes the R library and may require additional dependencies. It is not run by this skill. visone and Gephi are optional: https://visone.ethz.ch/ and https://gephi.org/ . Check their licenses separately.

## Local research project

Run commands from `.agents/skills/dna-research`. `python3 scripts/dna_tool.py discover` performs read-only checks. `python3 scripts/dna_tool.py init --root /chosen/private/DNA_Tools --project my-study` creates missing project folders without overwriting files. Supply a real writable location; do not put private research data inside the public repository. The root can be the confirmed Documents folder plus `DNA_Tools`.
