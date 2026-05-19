from pydantic import BaseModel, ValidationError
import time
from typing import Any, Dict, List, Tuple
import numpy as np
import json
from src.enum import Prompt
from src.parsing import parsing
from src.output import write_output
from llm_sdk import Small_LLM_Model


class Model(BaseModel):
    model: Any
    logits: List[float]
    lst_output: List[Any]

    def mask_logits(self, authorized_ids: list[int]) -> np.ndarray:
        """Mask logits except for authorized ids.

        Args:
            authorized_ids: List of authorized token ids.

        Returns:
            Masked logits array.
        """
        mask = np.array([float('-inf')] * len(self.logits))
        for id in authorized_ids:
            mask[id] = self.logits[id]
        return mask

    def take_best(
        self,
        text_encode: list[int],
        answer: list[int],
        authorized_ids: list[int]
    ) -> tuple[list[int], list[int], int]:
        """Select the best token id from masked logits and update sequences.

        Args:
            text_encode: Current input token ids.
            answer: Current answer token ids.
            authorized_ids: List of authorized token ids.

        Returns:
            Updated text_encode, answer, and the best token id.
        """
        self.logits = self.model.get_logits_from_input_ids(text_encode)
        mask = self.mask_logits(authorized_ids)
        best_id = int(mask.argmax())
        text_encode.append(best_id)
        answer.append(best_id)
        return (text_encode, answer, best_id)

    @staticmethod
    def is_sublist(main_lst: list[Any], sub_lst: list[Any]) -> bool:
        """Check if sub_lst is a contiguous sublist of main_lst.

        Args:
            main_lst: The main list.
            sub_lst: The sublist to check.

        Returns:
            True if sub_lst is a sublist of main_lst, else False.
        """
        n = len(sub_lst)
        for i in range(len(main_lst) - n + 1):
            if main_lst[i:i + n] == sub_lst:
                return True
        return False

    def constrained_decoding(
        self,
        prompt_data: List[Dict[str, Any]],
        function_data: List[Dict[str, Any]]
    ) -> List[List[Tuple[str, str]]]:
        """
        Perform constrained decoding for all prompts and functions.

        Args:
            prompt_data: List of prompt dictionaries.
            function_data: List of function dictionaries.

        Returns:
            List of parameter type lists for each prompt.
        """
        self.lst_output = []
        all_type: List[List[Tuple[str, str]]] = []
        lst_type: List[Tuple[str, str]] = []
        ids_number = self.create_authorized_key(set(",.0123456789"))
        ids_string = self.create_authorized_key(
            set(".,0123456789abcdefghijklmnopqrstuvwxyz "
                "/-*"))
        name_function = self.model.encode(
            "".join(
                d["name"] for d in function_data
                if isinstance(d.get("name"), str)
            )
        )[0].tolist()
        add_parameter_str = self.model.encode(", parameters:")[0].tolist()
        i = 0
        for prompt_entry in prompt_data:
            i += 1
            text_encode = self.model.encode(
                f"function selector function={function_data} to answer "
                "the input\n"
                f"input: {prompt_entry.get('prompt')}\n"
                "output format: function:<function_name>\n"
                "function: "
            )[0].tolist()
            answer = self.model.encode("function: ")[0].tolist()
            (answer,
             text_encode,
             function_name_tokens) = self.find_function_name(
                text_encode,
                name_function,
                add_parameter_str,
                answer
            )
            function_name_decoded = self.model.decode(function_name_tokens)
            (lst_type,
             chosen_function_data) = self.get_function_parameters(
                function_name_decoded,
                function_data
            )
            all_type.append(lst_type)
            text_encode_params = self.model.encode(
                f"function={chosen_function_data} parameters={lst_type}"
                "Extract full intact parameters from input\n"
                f"input: {prompt_entry.get('prompt')}\n"
                "output: parameters: <name>:<value>,\n"
                "parameters:"
            )[0].tolist()
            print(
                f"{Prompt.LOGO.value}\n"
                f"{i}/{len(prompt_data)} prompt\n"
                f"---> prompt: {prompt_entry.get('prompt')}\n"
                f"---> function name: {function_name_decoded}:\n"
                "---> parameter: ", end=""
            )
            self.extract_parameters(
                lst_type,
                text_encode_params,
                answer,
                ids_number,
                ids_string,
                prompt_entry
            )
        return all_type

    def extract_parameters(
        self,
        lst_type: List[Tuple[str, str]],
        text_encode_params: list[int],
        answer: list[int],
        ids_number: list[int],
        ids_string: list[int],
        prompt_entry: Dict[str, Any]
    ) -> None:
        """
        Extract and print parameters for a prompt using constrained decoding.

        Args:
            lst_type: List of (parameter name, type) tuples.
            text_encode_params: Encoded parameter tokens.
            answer: Current answer token ids.
            ids_number: Authorized ids for numbers.
            ids_string: Authorized ids for strings.
            prompt_entry: The prompt dictionary.
        """
        for param_name, param_type in lst_type:
            end = False
            token = 0
            for element in self.model.encode(f" {param_name}:")[0].tolist():
                text_encode_params.append(element)
                answer.append(element)
                print(self.model.decode(element), end="")
            while (not end) and token <= 15:
                if param_type == "number" or param_type == "integer":
                    (text_encode_params,
                        answer,
                        best_id) = self.take_best(text_encode_params,
                                                  answer,
                                                  ids_number)
                else:
                    (text_encode_params,
                        answer,
                        best_id) = self.take_best(text_encode_params,
                                                  answer,
                                                  ids_string)
                best_id_str = self.model.decode(best_id)
                print(best_id_str, end="", flush=True)
                if ',' in best_id_str:
                    end = True
                token += 1
        print()
        decoded_answer = self.model.decode(answer)
        self.lst_output.append([prompt_entry.get('prompt'), decoded_answer])

    @staticmethod
    def get_function_parameters(
        function_name: str,
        function_data: List[Dict[str, Any]]
    ) -> tuple[List[Tuple[str, str]], Dict[str, Any]]:
        """
        Get parameter types for a given function name from the
        function dictionary.

        Args:
            function_name: Name of the function.
            function_data: List of function dictionaries.

        Returns:
            Tuple of (list of (parameter name, type), function dictionary).
        """
        lst_type = []
        for d in function_data:
            if d.get("name", "") == function_name:
                param_name = d.get("parameters", d).keys()
                for element in param_name:
                    lst_type.append(
                        (element,
                         d.get("parameters", d)[element].get("type", "")))
                break
        return lst_type, d

    def find_function_name(
        self,
        text_encode: list[int],
        name_function: list[int],
        add_parameter_str: list[int],
        answer: list[int]
    ) -> tuple[list[int], list[int], list[int]]:
        """
        Find the function name in the encoded sequence and append
        parameter string.

        Args:
            text_encode: Current input token ids.
            name_function: Encoded function name token ids.
            add_parameter_str: Encoded parameter string token ids.
            answer: Current answer token ids.

        Returns:
            Tuple of (answer, text_encode, function_name_tokens).
        """
        function_name_tokens: list[int] = []
        end = False
        while not end:
            (text_encode,
             function_name_tokens,
             best_id) = self.take_best(text_encode,
                                       function_name_tokens,
                                       name_function)
            if not self.is_sublist(name_function, function_name_tokens):
                end = True
        text_encode.pop()
        function_name_tokens.pop()
        for element in function_name_tokens:
            answer.append(element)
        for element in add_parameter_str:
            text_encode.append(element)
            answer.append(element)
        return answer, text_encode, function_name_tokens

    def create_authorized_key(self, key_str: set[str]) -> list[int]:
        """
        Create a list of authorized token ids from a set of
        allowed characters.

        Args:
            key_str: Set of allowed characters.

        Returns:
            List of authorized token ids.
        """
        vocab_path = self.model.get_path_to_vocab_file()
        with open(vocab_path, 'r') as f:
            vocab = json.load(f)
        authorized_ids: List[int] = []
        for token_text, token_id in vocab.items():
            token_clean = token_text.replace("Ġ", " ").replace("▁",
                                                               " ").lower()
            if token_clean and all(c in key_str for c in token_clean):
                authorized_ids.append(token_id)
        return authorized_ids


def main() -> None:
    """Main entry point for running the constrained decoding pipeline."""
    try:
        start = time.time()
        model = Model(model=Small_LLM_Model(), logits=[], lst_output=[])
        pars = parsing()
        param_type = model.constrained_decoding(pars[0], pars[1])
        write_output(model.lst_output, pars[2], param_type)
        end = time.time()
        print("Final time:", end - start, "seconds")
    except ValidationError:
        print("You have a wrong parameter in your Model(class) implementation")
    except Exception as e:
        print(e)
    except BaseException:
        print("\nyou killed the program")


if __name__ == "__main__":
    main()
