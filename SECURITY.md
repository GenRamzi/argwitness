# Security policy

ArgWitness 0.1.x is experimental. It reads local JSON; it does not run tool servers,
tool calls, shell commands from schemas, or network reference retrieval.

Do not treat these properties as a sandbox. JSON Schema regular expressions, recursive
references, and large logical combinations can cause excessive CPU or recursion.
Use an OS/container time and memory limit for untrusted input. File and search limits
reduce accidental resource use but do not establish a hard wall-clock bound.

Reports suppress raw argument values by default. Names, schema paths, and catalog
digests remain visible. `normalize` prints the full catalog. `--show-values` can expose
values derived from recorded calls and schemas. Sanitize before uploading any report.

Report security problems through GitHub's private vulnerability reporting if enabled
on the repository. Otherwise open an issue containing only a request for private
coordination; do not publish exploit details or secrets. No response-time SLA is offered.

Local witnesses and hashes are not signed provenance. Anyone controlling the input
schemas can change the question being tested. Pin trusted baselines and recheck evidence.
