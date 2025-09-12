# Gemini Code Review
This is a quick tool for automating a workflow that I've found myself doing a lot: 

- Packaging all of the code from a repo into a single Markdown file 

- Prompting `gemini-2.5-pro` with this entire file, and asking it to perform a "code review" of sorts 

- Structuring the various issues found into a single file (`.xlsx` / `.json`) for easy review 

### Requirements

- A `GOOGLE_API_KEY` envvar set (see [this site](https://aistudio.google.com/app/apikey) for more detail)
- [The `repomix` library](https://github.com/yamadashy/repomix) installed + added to your PATH (so that you can invoke it via `repomix`)

### Installation

You can install this tool via [the `pipx` package](https://github.com/pypa/pipx): 
```bash
pipx install . --force
```

The `--force` flag ensures that any existing installation is overwritten.

### Usage

```bash
gemini_code_review [--path PATH] [--issues N] [--instructions "text"] [--keep] [--non-interactive]
```

Flags:

- `--path PATH` : Root of repository to analyze (default current directory)
- `--issues N` : Number of issues you want surfaced (default 10). If omitted (and not using `--non-interactive`) you'll be prompted.
- `--instructions "..."` : Additional free-form guidance for the model.
- `--keep` : Keep the intermediate XML file produced by `repomix` (printed to stderr with its path) for inspection.
- `--non-interactive` : Disable any prompting; useful for scripts / CI.

If run interactively without specifying `--issues` and/or `--instructions`, the CLI will ask:

1. How many issues would you like surfaced? (default 10)
2. Any additional user instructions? (blank for none)

### Output

Two outputs are produced:

1. An Excel file named `gemini_code_reivew_[mm]-[dd]-[yyyy]_[hh]-[mm].xlsx` in the current working directory containing a tabular set of issues and an `ABOUT` sheet with run metadata (timestamp, repository path, output file name, token count and method, requested/returned issues, user instructions, and notes).
2. A JSON representation of the full structured response printed to stdout (so you can redirect / pipe it):

```bash
gemini_code_review > gemini_code_review.json
```

### Exit Codes

- `0` Success
- `1` Failure while generating XML
- `2` `repomix` not found / unavailable
- `3` Prompting subsystem not available (bad/missing API key or dependency)
- `4` Model invocation failed
- `5` Failed to write Excel file

### Token counting

- The tool prints the repository token count to stderr after running `repomix`. Tokenization uses `tiktoken` when available, falling back to a simple approximation if needed. See `tiktoken` here: [`openai/tiktoken`](https://github.com/openai/tiktoken).

### Notes

- Ensure that `GOOGLE_API_KEY` is defined in your environment or in a `.env` file located at the project root.
- The tool loads the entire repository context via `repomix`; very large repos may increase latency / token usage. Repomix project: [`yamadashy/repomix`](https://github.com/yamadashy/repomix).
