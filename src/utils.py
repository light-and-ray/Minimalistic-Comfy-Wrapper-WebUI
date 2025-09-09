import re

def save_string_to_file(data: str, filepath: str) -> bool:
    """
    Saves a string to a file at the specified path.

    Args:
        data (str): The string content to be saved.
        filepath (str): The path to the file where the string will be saved.

    Returns:
        bool: True if the file was saved successfully, False otherwise.
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
        print(f"Successfully saved content to {filepath}")
        return True
    except IOError as e:
        print(f"Error saving file to {filepath}: {e}")
        return False

def natural_sort_key(s):
    """
    A helper function to generate a key for natural sorting.
    It splits a string into a list of text and number parts.
    For example, 'node10' becomes ['node', 10].
    """
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split('([0-9]+)', s)
    ]
