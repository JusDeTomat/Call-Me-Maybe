import json


def open_json_files(name_file):
    try:
        with open(name_file, "r") as json_file:
            data = json.load(json_file)
        return data
    except FileNotFoundError:
        print("File not found")
    except PermissionError:
        print("You need to have permision on the file")


def parsing():
    dico_promt = open_json_files("data/input/function_calling_tests.json")
    dico_fonc = open_json_files("data/input/functions_definition.json")
    return (dico_promt, dico_fonc)
