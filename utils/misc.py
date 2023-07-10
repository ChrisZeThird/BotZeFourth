import re


def extract_role_ids(roles):
    role_ids = []
    for role in roles:
        role_ids.append(str(role.id))
    return role_ids


def scrub(table_name):
    """
    Clean table name to avoid code injection and prevent hack. Only alphanumeric characters are allowed.
    :param table_name:
    :return: clean name
    """
    return ''.join(chr for chr in table_name if chr.isalnum())

