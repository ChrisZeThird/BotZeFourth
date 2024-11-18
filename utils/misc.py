import re



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


def scrub(table_name):
    """
    Clean table name to avoid code injection and prevent hack. Only alphanumeric characters are allowed.
    :param table_name:
    :return: clean name
    """
    return ''.join(chr for chr in table_name if chr.isalnum())

