import os


def parsing_promt(promt):
    pars_promt = ""
    for letre in promt:
        if letre == "\"":
            pars_promt += "\\" + letre
        else:
            pars_promt += letre
    return (pars_promt)


def parsing_llm_anser(output):
    try:
        dico = {}
        lst_var = []
        output_split = output.split(", ")
        fonc_name = output_split[0]
        _, value = fonc_name.split("function:")
        dico['name'] = value.strip()
        parm = output.split("parameters: ")
        parm = parm[1].split("returns:")[0]
        parm = parm.split(",")
        for varibale in parm:
            var_split = varibale.split(":")
            if len(var_split) == 2:
                lst_var.append((var_split[0].strip(), var_split[1].strip()))
        dico['var'] = lst_var
    except Exception as e:
        raise ValueError(e)
    return (dico)


def write_output(lst):
    os.makedirs("data/output", exist_ok=True)
    with open("data/output/function_calling_results.json", 'w') as output:
        output.write("[\n")
        j = 0
        for promt, llm_output in lst:
            try:
                j += 1
                promt = parsing_promt(promt)
                dico_llm = parsing_llm_anser(llm_output)
                output.write("\t{\n")
                output.write(f"\t\t\"prompt\": \"{promt}\",\n")
                output.write(f"\t\t\"name\": \"{dico_llm['name']}\",\n")
                output.write("\t\t\"parameters\": {")
                i = 0
                for key, value in dico_llm['var']:
                    i += 1
                    try:
                        value = float(value)
                        output.write(f"\"{key}\": {value}")
                    except Exception:
                        output.write(f"\"{key}\": \"{value}\"")
                    if i != len(dico_llm['var']):
                        output.write(", ")
                output.write("}\n")
                output.write("\t}")
                if j != len(lst):
                    output.write(",")
                output.write("\n")
            except ValueError as e:
                print(e)
                output.write("\t{\n")
                output.write(f"\t\t\"prompt\": \"{promt}\"\n")
                output.write("\t}")
                if j != len(lst):
                    output.write(",")
                output.write("\n")
        output.write("]\n")
