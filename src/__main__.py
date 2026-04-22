import torch
import json
from src.parsing import parsing
from llm_sdk import Small_LLM_Model

class Model:
    def __init__(self, model):
        self.model = model
        self.logits = []

    def masquer(self, ids_autorises):
        masque = [float('-inf')] * len(self.logits)
        for id in ids_autorises:
            masque[id] = self.logits[id]
        return masque

    def constrained_decoding(self, dico_promt, dico_fonction):


        vocab_path = self.model.get_path_to_vocab_file()
        with open(vocab_path, 'r') as f:
            vocab = json.load(f)

        lettres_autorisees = set("{:\t'}_1234567890abcdefghijklmnopqrstuvwxyz,\n")
        ids_autorises = []
        for token_text, token_id in vocab.items():
            token_clean = token_text.replace("Ġ", " ").replace("▁", " ").lower()
            if token_clean and all(c in lettres_autorisees for c in token_clean):
                ids_autorises.append(token_id)

        for prom in dico_promt:
            text_encode = self.model.encode(
                "Choose the function from the list to answer the input,Your answer is json 100% correctexactly like output"
                f"list: {dico_fonction}"
                f"input: {prom.get('prompt')}"
                "output: {\n'fonction':<name_fonction>\n'arguments':{'parm': <value>}\n}'"
                "{\n\t'"
            )[0].tolist()
            anser = [515, 197]
            egal = self.count_token(anser)
            while not egal:
                self.logits = self.model.get_logits_from_input_ids(text_encode)
                masque = self.masquer(ids_autorises)
                best_id = masque.index(max(masque))
                text_encode.append(best_id)
                anser.append(best_id)
                egal = self.count_token(anser)
            print(self.model.decode(anser))

    def count_token(self, lst):
        opens = 0
        close = 0
        for token in self.model.decode(lst):
            if token == "{":
                opens += 1
            if token == "}":
                close += 1
        return opens == close


def main():
    model = Model(Small_LLM_Model())
    pars = parsing()
    model.constrained_decoding(pars[0], pars[1])


main()
