import sys
import json
from src.error_type import ErrorJson, ErrorParsing
from typing import Any, List
from src.enum_pormpt import Prompt


def open_json_files(name_file: str) -> list[Any]:
    """Open and load a JSON file, returning its data as a list.

    Args:
        name_file: Path to the JSON file.

    Returns:
        The loaded data as a list.

    Raises:
        ErrorJson: If the file is not found, permission is denied,
        or JSON is invalid.
    """
    try:
        with open(name_file, "r") as json_file:
            data: list[Any] = json.load(json_file)
        if not len(data):
            raise ErrorJson('JSON is empty')
        return data
    except FileNotFoundError:
        raise ErrorJson("File not found")
    except PermissionError:
        raise ErrorJson("You need to have permission of the file")
    except Exception as e:
        raise ErrorJson(f"[ERROR JSON]: {e} in {name_file}")


def check_data(data, name_file, utils):
    for element in data:
        if utils:
            if not all(k in element for k in ['name', 'description', 'parameters']):
                raise ErrorJson(
                    f"File {name_file} is wrong\n"
                    f"{Prompt.EXEMPLE_FUNC.value}"
                )
            keys = list(element.get('parameters').keys())
            for key in keys:
                if not isinstance(element.get('parameters')[key], dict):
                    raise ErrorJson(
                        f"File {name_file} is wrong\n"
                        f"{Prompt.EXEMPLE_FUNC.value}"
                    )
        else:
            if 'prompt' not in element:
                raise ErrorJson(
                    f"File {name_file} is wrong\n"
                    f"{Prompt.EXEMPLE_PROM.value}"
                )


def parsing() -> tuple[List[Any], List[Any], str]:
    """Parse command-line arguments and load JSON data for prompts and
    functions.

    Returns:
        Tuple containing prompt data, function data, and output file path.

    Raises:
        ErrorParsing: If arguments are invalid or files cannot be loaded.
    """
    try:
        arg = sys.argv
        option_names = ['--functions_definition', '--input', '--output']
        functions_path: str | None = None
        prompt_path: str | None = None
        output: str | None = None
        if len(arg) == 1:
            prompt_data = open_json_files(
                "data/input/function_calling_tests.json"
            )
            check_data(prompt_data, "data/input/function_calling_tests.json", 0)
            function_data = open_json_files(
                "data/input/functions_definition.json"
            )
            check_data(function_data, "data/input/functions_definition.json", 1)
        else:
            arg.pop(0)
            for i in range(len(arg)):
                if ((arg[i] not in option_names and
                     i != 0 and
                     arg[i - 1] not in option_names) or (
                     arg[i] not in option_names and
                     i == 0)):
                    raise ErrorParsing(f'{arg[i]} is not a good arguments')
                if (len(arg) % 2 != 0):
                    raise ErrorParsing("bad argument implementation. "
                                       "Example: --input <path>")
                if arg[i] == '--functions_definition':
                    if (i + 1 < len(arg)):
                        functions_path = arg[i + 1]
                if arg[i] == '--input':
                    if (i + 1 < len(arg)):
                        prompt_path = arg[i + 1]
                if arg[i] == '--output':
                    if (i + 1 < len(arg)):
                        output = arg[i + 1]
            if prompt_path is None:
                prompt_path = "data/input/function_calling_tests.json"
            if functions_path is None:
                functions_path = "data/input/functions_definition.json"
            prompt_data = open_json_files(prompt_path)
            check_data(prompt_data, prompt_path, 0)
            function_data = open_json_files(functions_path)
            check_data(function_data, functions_path, 1)
        if output is None:
            output = "data/output/function_calling_results.json"
        if output.split(".")[-1] != "json":
            raise ErrorParsing("output file need .json not ."
                               f"{output.split('.')[-1]}")
        return (prompt_data, function_data, output)
    except Exception as e:
        raise ErrorParsing(f"[ERROR]: {e}")
