from enum import Enum


class Prompt(Enum):
    LOGO = ("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n "
            "\n\n\n\n\n\n\n\n\n\n"
            "\033[34m              _  _                                       "
            "       _\033[0m\n"
            "\033[34m             | || |                                      "
            "      | |\033[0m\n"
            "\033[34m  ___   __ _ | || |  _ __ ___    ___   _ __ ___    __ _  "
            "_   _ | |__    ___\033[0m\n"
            "\033[34m / __| / _` || || | | '_ ` _ \\  / _ \\ | '_ ` _ \\  / _`"
            " || | | || '_ \\  / _ \\\033[0m\n"
            "\033[34m| (__ | (_| || || | | | | | | ||  __/ | | | | | || (_| ||"
            " |_| || |_) ||  __/\033[0m\n"
            "\033[34m \\___| \\__,_||_||_| |_| |_| |_| \\___| |_| |_| |_| \\__"
            ",_| \\__, ||_.__/  \\___|\033[0m\n"
            "\033[34m                                                         "
            " __/ |\033[0m\n"
            "\033[34m                                                         "
            "|___/\033[0m\n")
    EXEMPLE_PROM = ("Exemple:\n[\n\t{\n\t\t\"prompt\": \"What is the sum of 2 "
                    "and 3?\"\n"
                    "\t},\n\t{\n\t\t\"prompt\": \"What is the sum of 265 and "
                    "345?\""
                    "\n\t}\n]")
    EXEMPLE_FUNC = ("Exemple:\n[\n\t{\n\t\t\"name\": \"fn_add_numbers\",\n\t\t"
                    "\"description\": \"Add two numbers together and return "
                    "their sum.\",\n\t\t\"parameters\": {\n\t\t\t\"a\": {\n\t"
                    "\t\t\t\"type\": \"number\"\n\t\t\t},\n\t\t\t\"b\": {\n\t"
                    "\t\t\t\"type\": \"number\"\n\t\t\t}\n\t\t},\n\t\t\""
                    "returns\""
                    ": {\n\t\t\t\"type\": \"number\"\n\t\t}\n\t}\n]")
