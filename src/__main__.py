from pydantic import BaseModel
import time
from typing import Any
import numpy as np
import json
from src.parsing import parsing
from src.output import write_output
from llm_sdk import Small_LLM_Model


class Model(BaseModel):
    model: Any
    logits: list
    lst_output: list

    def masquer(self, ids_autorises):
        masque = np.array([float('-inf')] * len(self.logits))
        for id in ids_autorises:
            masque[id] = self.logits[id]
        return masque

    def take_best(self, text_encode, anser, ids_autorises):
        self.logits = self.model.get_logits_from_input_ids(text_encode)
        masque = self.masquer(ids_autorises)
        best_id = int(masque.argmax())
        text_encode.append(best_id)
        anser.append(best_id)
        return (text_encode, anser, best_id)

    @staticmethod
    def is_sublist(main_lst, sub_lst):
        n = len(sub_lst)
        for i in range(len(main_lst) - n + 1):
            if main_lst[i:i + n] == sub_lst:
                return True

    def constrained_decoding(self, dico_promt, dico_fonction):
        self.lst_output = []
        ids_number = self.create_autoris_key(set(",0123456789"))
        ids_string = self.create_autoris_key(set(",0123456789abcdefghijklmnopqrstuvwxyz "))
        name_fonction = self.model.encode(
            "".join(d.get("name") for d in dico_fonction)
        )[0].tolist()
        add_parmeter_str = self.model.encode(", parameters:")[0].tolist()
        i = 0
        for prom in dico_promt:
            i += 1
            text_encode = self.model.encode(
                f"Select the function from {dico_fonction} to answer the input\n"
                f"input: {prom.get('prompt')}\n"
                "output format: function:<function_name>\n"
                "function: "
            )[0].tolist()
            anser = self.model.encode("function: ")[0].tolist()
            anser, text_encode, fonction_name = self.research_fonc_name(text_encode, name_fonction, add_parmeter_str, anser)
            fonction_name_dec = self.model.decode(fonction_name)
            lst_type, dico_fonction_chose = self.take_parm_fonction(fonction_name_dec, dico_fonction)
            text_encode_parm = self.model.encode(
                f"This function {dico_fonction_chose} completes the parameters by responding to the input, your answer must be only the output line\n"
                f"input: {prom.get('prompt')}\n"
                "output: parameters: <name>:<value>,\n"
                "parameters:"
            )[0].tolist()
            print(
                "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
                "\033[34m              _  _                                              _\033[0m\n"
                "\033[34m             | || |                                            | |\033[0m\n"
                "\033[34m  ___   __ _ | || |  _ __ ___    ___   _ __ ___    __ _  _   _ | |__    ___\033[0m\n"
                "\033[34m / __| / _` || || | | '_ ` _ \\  / _ \\ | '_ ` _ \\  / _` || | | || '_ \\  / _ \\\033[0m\n"
                "\033[34m| (__ | (_| || || | | | | | | ||  __/ | | | | | || (_| || |_| || |_) ||  __/\033[0m\n"
                "\033[34m \\___| \\__,_||_||_| |_| |_| |_| \\___| |_| |_| |_| \\__,_| \\__, ||_.__/  \\___|\033[0m\n"
                "\033[34m                                                          __/ |\033[0m\n"
                "\033[34m                                                         |___/\033[0m\n"
                f"{i}/{len(dico_promt)}prompt\n"
                f"---> prompt: {prom.get('prompt')}\n"
                f"---> function name: {fonction_name_dec}:\n"
                "---> parameter: ", end=""
            )
            for name_parm, type_parm in lst_type:
                end = False
                token = 0
                for element in self.model.encode(f" {name_parm}:")[0].tolist():
                    text_encode_parm.append(element)
                    anser.append(element)
                    print(self.model.decode(element), end="")
                while (not end) and token <= 20:
                    if type_parm == "number":
                        text_encode_parm, anser, best_id = self.take_best(text_encode_parm, anser, ids_number)
                    if type_parm == "string":
                        text_encode_parm, anser, best_id = self.take_best(text_encode_parm, anser, ids_string)
                    best_id_str = self.model.decode(best_id)
                    print(best_id_str, end="", flush=True)
                    if ',' in best_id_str:
                        end = True
                    token += 1
            print()
            decode_anser = self.model.decode(anser)
            self.lst_output.append([prom.get('prompt'), decode_anser])

    def take_parm_fonction(self, function_name, dico_fonction):
        lst_type = []
        for d in dico_fonction:
            if d.get("name", "") == function_name:
                param_name = d.get("parameters", d).keys()
                for element in param_name:
                    lst_type.append((element, d.get("parameters", d)[element].get("type", "")))
                break
        return lst_type, d

    def research_fonc_name(self, text_encode, name_fonction, add_parmeter_str, anser):
        fonction_name = []
        end = False
        while not end:
            text_encode, fonction_name, best_id = self.take_best(text_encode, fonction_name, name_fonction)
            if not self.is_sublist(name_fonction, fonction_name):
                end = True
        text_encode.pop()
        fonction_name.pop()
        for element in fonction_name:
            anser.append(element)
        for element in add_parmeter_str:
            text_encode.append(element)
            anser.append(element)
        return anser, text_encode, fonction_name

    def create_autoris_key(self, key_str):
        vocab_path = self.model.get_path_to_vocab_file()
        with open(vocab_path, 'r') as f:
            vocab = json.load(f)
        ids_autorises = []
        for token_text, token_id in vocab.items():
            token_clean = token_text.replace("Ġ", " ").replace("▁", " ").lower()
            if token_clean and all(c in key_str for c in token_clean):
                ids_autorises.append(token_id)
        return ids_autorises


def main():
    debut = time.time()
    model = Model(model=Small_LLM_Model(), logits=[], lst_output=[])
    pars = parsing()
    model.constrained_decoding(pars[0], pars[1])
    write_output(model.lst_output)
    fin = time.time()
    print("Temps final:", fin - debut, "secondes")


if __name__ == "__main__":
    main()
