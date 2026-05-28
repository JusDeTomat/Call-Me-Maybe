# Copilot Instructions

This repository implements a constrained decoding pipeline for function calling using a small local LLM.

## What matters most
- `src/__main__.py` is the entry point. It loads prompts, function definitions, runs token-level constrained decoding, and writes JSON output.
- `llm_sdk/__init__.py` is a local wrapper around Hugging Face `transformers`. It provides `Small_LLM_Model` with `encode`, `decode`, and `get_logits_from_input_ids`.
- `src/parsing.py` parses CLI style arguments from `sys.argv` and validates JSON input files. Default files are in `data/input/`.
- `src/output.py` parses the model output string and serializes final results to JSON in `data/output/`.

## Key patterns
- The model loop is implemented with `Model.take_best(...)`, which applies a token mask then selects the highest logit.
- Authorized token sets are built from the tokenizer vocabulary in `Model.create_authorized_key(...)` using allowed characters.
- Function names are identified by matching token sublists; parameter decoding is split into `number`/`integer` versus string-based tokens.
- CLI handling is manual: accepted options are `--functions_definition`, `--input`, `--output`.
- Error handling is custom and lightweight: `src/error_type.py` defines `ErrorJson`, `ErrorParsing`, and `ErrorOutput`.

## Data expectations
- `data/input/functions_definition.json` must contain function objects with `name`, `description`, and `parameters`.
- `data/input/function_calling_tests.json` must contain objects with `prompt`.
- Output must be JSON and default to `data/output/function_calling_results.json`.

## Useful commands
- Install dependencies: `make install`
- Run default pipeline: `python -m src`
- Run with explicit files:
  `python -m src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calling_results.json`

## Integration notes
- The repo depends on `pydantic`, `numpy`, `transformers`, `huggingface_hub`, and `torch` from `pyproject.toml`.
- The local `llm_sdk` package downloads tokenizer/vocab files from the HF Hub and auto-selects `mps`, `cuda`, or `cpu`.
- `src/output.py` writes JSON manually, so any change to output formatting should preserve the existing `parse_llm_answer(...)` expectations.

## What to avoid
- Do not assume a standard CLI library is used; changes should preserve the `sys.argv` parsing style unless the whole CLI is refactored.
- Avoid changing prompt templates lightly: the decoding loop depends on exact prompt phrases such as `function:`, `parameters:`, and the internal `function selector` text.

## Suggested focus areas for edits
- Keep the constrained decoding logic centered in `src/__main__.py`.
- Preserve JSON schema validation in `src/parsing.py`.
- When modifying model behavior, update both `create_authorized_key(...)` and `take_best(...)` to maintain function-call reliability.

> If any section is unclear or incomplete, let me know and I’ll revise the instructions to better match this repo.