# Network analysis

Use official DNA GUI or an installed rDNA 3.1.2. This package provides `scripts/dna_bridge.R`, which calls the 3.1.2 API `dna_init`, `dna_openDatabase`, and `dna_network`. API signature checked against the upstream v3.1.2 source; the bridge has not been run with rDNA in the release environment. Test on a copy and a synthetic database first. It does not import or validate a DNA database's review status. The researcher must check that all included records are human validated, and confirm each parameter and the correct database.

Start an interactive R session from the skill directory and run:

```r
source("scripts/dna_bridge.R")
# Give paths explicitly. Set a real coder ID and password interactively.
# The user enters the password in the R console; do not save it in a script.
pw <- readline("DNA coder password: ")
dna_export_reviewed(database = "path/to/reviewed.dna", coder_id = 1L,
  password = pw, output = "path/to/new-network.graphml",
  network_type = "twomode", statement_type = "DNA Statement",
  variable1 = "organization", variable2 = "concept", qualifier = "agreement",
  aggregation = "ignore", normalization = "no", duplicates = "include",
  start_date = "01.01.2024", stop_date = "31.12.2024",
  confirmed_human_review = TRUE)
rm(pw)
```

`readline` may echo characters in some consoles and R history may retain commands. Use a private session and follow local security policy. Database changes, credential prompt, and Java logs are controlled by upstream tools, not guaranteed read-only. Set the other values according to your own database. Check `help("dna_network", package="rDNA")` for valid parameters. Verify the GraphML file with the Python tool and open it in visone. The function cannot certify scientific interpretation, sampling, all review decisions or visual inspection. Do not run it on sensitive data where an agent or service lacks permission.
