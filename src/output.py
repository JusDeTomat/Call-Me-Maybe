import os
from typing import Any, Dict, List, Tuple
from src.error_type import ErrorOutput


def parse_prompt(prompt: str) -> str:
    """Escape double quotes and backslashes in the prompt string.

    Args:
        prompt: The input prompt string.

    Returns:
        The escaped prompt string.
    """
    escaped_prompt = ""
    for char in prompt:
        if char == '"' or char == '\\':
            escaped_prompt += '\\' + char
        else:
            escaped_prompt += char
    return escaped_prompt


def parse_llm_answer(output: str) -> Dict[str, Any]:
    """Parse the LLM output string into a dictionary with
    function name and parameters.

    Args:
        output: The output string from the LLM.

    Returns:
        A dictionary with keys 'name' and 'var' (list of parameter tuples).

    Raises:
        ErrorOutput: If parsing fails.
    """
    try:
        result: Dict[str, Any] = {}
        param_pairs: List[Tuple[str, str]] = []
        output_split = output.split(", ")
        function_name_line = output_split[0]
        _, value = function_name_line.split("function:")
        result['name'] = value.strip()
        parts = output.split("parameters: ")
        param_str = parts[1].split("returns:")[0]
        param_list: List[str] = param_str.split(",")
        for variable in param_list:
            var_split = variable.split(":")
            if len(var_split) == 2:
                param_pairs.append(
                    (var_split[0].strip(), var_split[1].strip())
                )
        result['var'] = param_pairs
    except Exception as e:
        raise ErrorOutput(e)
    return result


def write_output(
    lst: List[Tuple[str, str]],
    name_file: str,
    type_params: List[List[Tuple[str, str]]]
) -> None:
    """Write the processed prompts and LLM outputs to a JSON file.

    Args:
        lst: List of tuples (prompt, llm_output).
        name_file: Output file path.
        type_params: List of parameter type information for each prompt.
    """
    os.makedirs("data/output", exist_ok=True)
    with open(name_file, 'w') as output:
        output.write("[\n")
        j = 0
        for prompt, llm_output in lst:
            try:
                j += 1
                prompt = parse_prompt(prompt)
                llm_data = parse_llm_answer(llm_output)
                output.write("\t{\n")
                output.write(f"\t\t\"prompt\": \"{prompt}\",\n")
                output.write(f"\t\t\"name\": \"{llm_data['name']}\",\n")
                output.write("\t\t\"parameters\": {")
                i = 0
                for key, value in llm_data['var']:
                    i += 1
                    try:
                        if type_params[j - 1][i - 1][1] == "number":
                            value = float(value)
                        elif type_params[j - 1][i - 1][1] == "integer":
                            value = int(value)
                        else:
                            raise Exception()
                        output.write(f"\"{key}\": {value}")
                    except Exception:
                        output.write(f"\"{key}\": \"{value}\"")
                    if i != len(llm_data['var']):
                        output.write(", ")
                output.write("}\n")
                output.write("\t}")
                if j != len(lst):
                    output.write(",")
                output.write("\n")
            except ErrorOutput:
                output.write("\t{\n")
                output.write(f"\t\t\"prompt\": \"{prompt}\"\n")
                output.write("\t}")
                if j != len(lst):
                    output.write(",")
                output.write("\n")
        output.write("]\n")
