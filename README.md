*This project has been created as part of the 42 curriculum by mbichet.*

# Call Me Maybe

## Description

Call Me Maybe is a function-calling pipeline built on top of a small large language model (LLM). Its goal is to convert natural language prompts into structured, valid function call outputs — without relying on free-form text generation.

The project implements a constrained decoding strategy: instead of letting the model generate any token it wants, the pipeline restricts generation at each step to only tokens that are valid for the expected output structure (function names, parameter names, values). This makes the output predictable and machine-readable.

Concretely, the pipeline reads prompts and function definitions from JSON files, runs the constrained decoding process, and writes the results (function name + resolved parameters) to an output JSON file.

---

## Instructions

### Requirements

- Python 3.10 or newer
- Dependencies listed in `pyproject.toml`:
  - `pydantic`
  - `numpy`
  - `transformers`
  - `huggingface_hub`
  - `torch`

### Installation

```bash
make install
```

### Execution

Run with the default input files:

```bash
python -m src
```

or equivalently:

```bash
make run
```

Run with explicit file paths:

```bash
python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

> **Note:** The output path must end with `.json`, otherwise the program raises a parsing error.

---

## Algorithm Explanation

The constrained decoding pipeline works as follows:

1. **Load inputs** — prompts and function definitions are read from their respective JSON files.
2. **Build token masks** — an authorized token set is constructed for valid numeric and string values, based on the model's vocabulary.
3. **Encode the prompt** — the prompt and function metadata are combined into an input token sequence fed to the LLM.
4. **Constrained token selection** — at each generation step, the model produces logits over its full vocabulary; only tokens belonging to the authorized set are kept (all others are masked out). The highest-scoring valid token is selected.
5. **Function name detection** — the pipeline scans the output token stream to identify when a known function name has been produced.
6. **Parameter extraction** — once the function name is confirmed, the pipeline switches to argument decoding, applying the appropriate token masks for each expected parameter type.
7. **Output serialization** — the decoded output is parsed into a structured dictionary containing the function name and its resolved parameter values, then written to the output JSON file.

This token-level control avoids free-form text and steers the model toward syntactically valid, structured output at every step.

---

## Design Decisions

- **`src/__main__.py`** — orchestrates the main execution flow: model loading, prompt encoding, generation loop, and output writing.
- **`src/parsing.py`** — handles CLI argument parsing and JSON file loading/validation.
- **`src/output.py`** — parses the raw LLM output into structured results and serializes them to JSON.
- **Pydantic for the `Model` class** — used to enforce data validation and structure on inputs and outputs, catching malformed data early.
- **Character-level vocabulary masks** — token masks are derived from the model vocabulary by filtering on allowed characters, keeping the implementation general and not hardcoded to specific token IDs.
- **Default paths with CLI overrides** — sensible defaults are provided so the program can be run with zero arguments during development, while explicit paths support integration in other workflows.

---

## Performance Analysis

- **Accuracy** — constrained decoding significantly improves the rate of valid, parseable function-call outputs compared to unconstrained generation. That said, overall accuracy still depends on the quality of the underlying LLM and the clarity of the prompt.
- **Speed** — generation is token-by-token and iterative, making it slower than a single-pass forward pass. The main overhead comes from repeated encoding and decoding at each step.
- **Reliability** — the pipeline is robust for well-formed inputs where the model's vocabulary aligns correctly with the token masks. Edge cases can arise if the model emits unexpected token sequences or if JSON parsing encounters malformed output.

---

## Challenges Faced

- **Consistent output parsing** — extracting a function name and structured parameter list from the raw token stream required careful string handling and multiple edge case checks.
- **Token mask management** — building and applying character-level masks at each generation step added significant complexity compared to standard generation loops.
- **Prompt format** — finding a prompt structure that reliably guided the model toward function-style output (rather than free-form prose) required iterative tuning.
- **Python typing compatibility** — keeping the code clean and compatible with strict typing and linting rules while refactoring variable names and output formatting was an ongoing constraint throughout development.

---

## Testing Strategy

- **Manual validation** — the pipeline was run against the provided JSON input files under `data/input/` and outputs were inspected manually for correctness.
- **Default and custom paths** — both invocation modes (`make run` and explicit CLI args) were tested to confirm correct file loading and output generation.
- **Static checks** — Python compilation and type validation were used throughout to catch structural errors early.
- **Output inspection** — the generated `data/output/function_calling_results.json` was reviewed after each run to verify that function names and parameters matched expectations.

---

## Example Usage

Default execution (uses built-in file paths):

```bash
python -m src
```

Explicit file paths:

```bash
python -m src \
  --functions_definition data/input/functions_definition.json \
  --input data/input/function_calling_tests.json \
  --output data/output/function_calling_results.json
```

Expected output is a JSON file in `data/output/` with the following structure per entry:

```json
{
		"prompt": "What is the sum of 265 and 345?",
		"name": "fn_add_numbers",
		"parameters": {"a": 265.0, "b": 345.0}
}
```

---

## Resources

- [OpenAI Function Calling documentation](https://platform.openai.com/docs/guides/function-calling)
- [Hugging Face Transformers documentation](https://huggingface.co/docs/transformers)
- [NumPy documentation](https://numpy.org/doc/)
- [Pydantic documentation](https://docs.pydantic.dev/)
- Articles on constrained decoding and guided generation (e.g., Outlines, LMQL, guidance)

### AI Usage

AI was used to:
- Understand and clarify the constrained decoding approach and how token-level masking interacts with LLM logits.
- Generate and refine the README content.