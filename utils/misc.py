def scrub(table_name):
    """
    Clean table name to avoid code injection and prevent hack. Only alphanumeric characters are allowed.
    :param table_name:
    :return: clean name
    """
    return ''.join(chr for chr in table_name if chr.isalnum())
