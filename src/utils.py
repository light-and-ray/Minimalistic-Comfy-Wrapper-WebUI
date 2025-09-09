import re

def save_string_to_file(data: str, filepath: str) -> bool:
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(data)
        return True
    except IOError as e:
        print(f"Error saving file to {filepath}: {e}")
        return False

def natural_sort_key(s):
    return [
        int(text) if text.isdigit() else text.lower()
        for text in re.split('([0-9]+)', s)
    ]
