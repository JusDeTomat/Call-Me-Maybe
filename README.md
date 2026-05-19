*This project has been created as part of the 42 curriculum by mbichet.*

# Call Me Maybe

## Description

This project explores function calling with large language models by implementing a constrained decoding pipeline. The goal is to convert natural language prompts into structured function call outputs using a small LLM, custom prompt engineering, and token-level decoding control.

The repository loads prompt data and function definitions from JSON files, runs a constrained decoding process to generate function names and parameters, and writes the results back to a JSON output file.

## Instructions

### Requirements

- Python 3.10 or newer
- Dependencies from `pyproject.toml`:
  - `pydantic`
  - `numpy`
  - `transformers`
  - `huggingface_hub`
  - `torch`

### Install

```
make install
```

### Run

Use the default input files when no arguments are provided:

```bash
python -m src
```
or 
```bash
make run
```

Or provide explicit JSON paths:

```bash
python -m src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calling_results.json
```

## Resources

- OpenAI Function Calling documentation
- Hugging Face Transformers documentation
- NumPy documentation
- Pydantic documentation
- Articles on constrained decoding and guided generation

### AI usage

AI assistance was used to help summarize the project structure, explain the constrained decoding approach, and generate the README content. The core implementation remains based on the repository code and manual design choices.

## Algorithm explanation

The constrained decoding pipeline is implemented as follows:

1. Load prompts and function definitions from JSON files.
2. Build an authorized token set for numeric and string values.
3. Encode the prompt and function metadata into input token sequences.
4. Use the LLM logits to select the next token from a constrained set, ensuring only allowed tokens are produced.
5. Detect the function name by searching for encoded function tokens in the output stream.
6. Once the function name is identified, switch to parameter extraction and decode argument values according to allowed token sets.
7. Parse the resulting output into a structured dictionary with function name and parameter values.

This approach avoids free-form text generation by masking logits and guiding the model toward valid structured output.

## Design decisions

- `src/__main__.py` contains the main execution flow and model orchestration.
- `src/parsing.py` handles command-line parameter parsing and JSON file loading.
- `src/output.py` parses LLM outputs and serializes the final JSON results.
- Pydantic is used for the `Model` class to enforce data validation and structure.
- The pipeline uses character-level masks from the vocabulary to keep output tokens within allowed sets for parameters.
- Default JSON paths are provided, while command-line arguments allow custom file locations.

## Performance analysis

- **Accuracy**: The constrained decoding strategy improves the chance of valid function-call output over unconstrained generation, but accuracy depends heavily on the underlying LLM and prompt quality.
- **Speed**: The approach is iterative and token-by-token, so it is slower than a standard single-pass generation. The main overhead is repeated encoding and decoding of tokens.
- **Reliability**: The solution is more reliable for structured output when the model and token masks align correctly. Edge cases may still occur if the model emits unexpected tokens or if JSON parsing fails.

## Challenges faced

- Parsing the LLM output consistently into a function name and parameter list required careful string handling.
- Constrained decoding requires managing token-level masks and authorized character sets, which introduces complexity.
- The project needed a clear prompt format to force the model toward function-style responses.
- Ensuring the code remained compatible with Python typing and linting rules while updating variable names and output formatting.

## Testing strategy

- Manual validation using the provided JSON input files under `data/input`.
- Running the module with default and custom paths to confirm expected output generation.
- Static checks with Python compilation and type validation.
- Inspecting generated `data/output/function_calling_results.json` after execution.

## Example usage

Default execution:

```bash
python -m src
```

Explicit file paths:

```bash
python -m src --functions_definition data/input/functions_definition.json --input data/input/function_calling_tests.json --output data/output/function_calling_results.json
```

Expected output is a JSON file in `data/output` containing prompt, function name, and validated parameters.

---

## Notes

- If the output file path does not end with `.json`, the program raises a parsing error.
- The implementation currently assumes the model returns a function-style answer that includes `function:` and `parameters:` sections.
