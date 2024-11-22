import re
import os
import json


def ordinal_suffix(n):
    if 10 <= n % 100 <= 20:
        suffix = 'th'
    else:
        suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
    return str(n) + suffix


def extract_role_ids(roles):
    role_ids = []
    for role in roles:
        role_ids.append(str(role.id))
    return role_ids


def add_spaces_to_capital_letters(input_string):
    """
    Use regular expression to add space before capital letters
    :param input_string:
    :return: string with space separation between capital letters
    """

    output_string = re.sub(r'([A-Z])', r' \1', input_string)
    return output_string.strip()


def format_string(input_string, char1='_', char2=' ', capital=True):
    """
    Formats a string by replacing char1 by char 2. By default, add capital letter, otherwise return lowercase string.

    :param input_string: The string to format.
    :param char1: '_' by default
    :param char2: ' ' by default
    :param capital: bool, True by default

    Returns:
        str: The formatted string.
    """
    if capital:
        formatted = input_string.replace(char1, char2).capitalize()
    else:
        formatted = input_string.replace(char1, char2).lower()
    return formatted


def scrub(table_name):
    """
    Clean table name to avoid code injection and prevent hack. Only alphanumeric characters are allowed.
    :param table_name:
    :return: clean name
    """
    return ''.join(chr for chr in table_name if chr.isalnum())


def open_json(path='roles.json'):
    """Helper function to load roles data"""
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return {}


def has_link(message):
    # Regular expression to find URLs
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', message.content.lower())
    return urls


# Dictionary methods
def concatenate_dict_values(dictionary):
    """
    Concatenates all the lists in a dictionary into a single list.

    Args:
        dictionary (dict): A dictionary where all values are lists.

    Returns:
        list: A single list containing all elements from the lists in the dictionary.
    """
    result = []
    for value_list in dictionary.values():
        result.extend(value_list)
    return result


def get_key_by_value(value, dictionary):
    """
    Returns the key from the dictionary for which the value is present in the list of values.

    Args:
        value: The value to search for in the dictionary's lists.
        dictionary (dict): A dictionary where values are lists.

    Returns:
        key: The key for which the value is present in the list, or None if not found.
    """
    for key, value_list in dictionary.items():
        if value in value_list:
            return key
    return None
