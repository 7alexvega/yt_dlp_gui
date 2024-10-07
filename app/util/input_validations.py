import re


def input_contains_regex(input_string: str, regex: str):
    return re.search(regex, input_string) is not None

def input_is_empty(input_string: str):
    return input_string == ""