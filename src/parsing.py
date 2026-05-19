import sys
import json
from src.error_type import ErrorJson, ErrorParsing


def open_json_files(name_file):
    try:
        with open(name_file, "r") as json_file:
            data = json.load(json_file)
        if not len(data):
            raise ErrorJson('JSON is empty')
        return data
    except FileNotFoundError:
        raise ErrorJson("File not found")
    except PermissionError:
        raise ErrorJson("You need to have permission of the file")
    except Exception as e:
        raise ErrorJson(f"[ERROR JSON]: {e} in {name_file}")


def parsing():
    try:
        arg = sys.argv
        parm_lst = ['--functions_definition', '--input', '--output']
        funct = None
        prompt = None
        output = None
        if len(arg) == 1:
            dico_promt = open_json_files(
                "data/input/function_calling_tests.json"
            )
            dico_func = open_json_files(
                "data/input/functions_definition.json"
            )
        else:
            arg.pop(0)
            for i in range(len(arg)):
                if ((arg[i] not in parm_lst and
                     i != 0 and
                     arg[i - 1] not in parm_lst) or (
                     arg[i] not in parm_lst and
                     i == 0)):
                    raise ErrorParsing(f'{arg[i]} is not a good arguments')
                if (len(arg) % 2 != 0):
                    raise ErrorParsing("bad argument implementation. "
                                       "Exemple: --input <path>")
                if arg[i] == '--functions_definition':
                    if (i + 1 < len(arg)):
                        funct = arg[i + 1]
                if arg[i] == '--input':
                    if (i + 1 < len(arg)):
                        prompt = arg[i + 1]
                if arg[i] == '--output':
                    if (i + 1 < len(arg)):
                        output = arg[i + 1]
            if prompt is None:
                prompt = "data/input/function_calling_tests.json"
            if funct is None:
                funct = "data/input/functions_definition.json"
            dico_promt = open_json_files(prompt)
            dico_func = open_json_files(funct)
        if output is None:
            output = "data/output/function_calling_results.json"
        if output.split(".")[-1] != "json":
            raise ErrorParsing("output file need .json not ."
                               f"{output.split('.')[-1]}")
        return (dico_promt, dico_func, output)
    except Exception as e:
        raise ErrorParsing(f"[ERROR]: {e}")
