# Independent bridge written for the public rDNA 3.1.2 API.
# Not executed against rDNA in this release. Use a reviewed database copy.
dna_export_reviewed <- function(database, coder_id, password, output,
  network_type, statement_type, variable1, variable2, qualifier,
  aggregation, normalization, duplicates, start_date, stop_date,
  confirmed_human_review = FALSE) {
  if (!isTRUE(confirmed_human_review)) stop("Researcher must confirm review of all included statements.")
  if (!requireNamespace("rDNA", quietly = TRUE)) stop("Install and verify rDNA first.")
  if (as.character(utils::packageVersion("rDNA")) != "3.1.2") stop("Bridge targets rDNA 3.1.2; review compatibility first.")
  if (!file.exists(database)) stop("Database not found.")
  if (file.exists(output)) stop("Output already exists; choose a new output path.")
  if (!dir.exists(dirname(output))) stop("Output parent directory does not exist.")
  if (!grepl("\\.graphml$", output, ignore.case = TRUE)) stop("Output must end in .graphml.")
  if (!network_type %in% c("onemode", "twomode")) stop("Use onemode or twomode.")
  if (!is.character(password) || length(password) != 1L || !nzchar(password)) stop("A coder password is required.")
  rDNA::dna_init()
  rDNA::dna_openDatabase(database, coderId = as.integer(coder_id), coderPassword = password)
  rDNA::dna_network(networkType = network_type, statementType = statement_type,
    variable1 = variable1, variable2 = variable2, qualifier = qualifier,
    qualifierAggregation = aggregation, normalization = normalization,
    duplicates = duplicates, start.date = start_date, stop.date = stop_date,
    timeWindow = "no", fileFormat = "graphml", outfile = output)
  if (!file.exists(output) || is.na(file.info(output)$size) || file.info(output)$size == 0) stop("No nonempty output found; inspect DNA logs privately.")
  message("File exists. Validate its content and document execution before reporting a result.")
  invisible(output)
}
