import re

def parse_title(s: str) -> dict or None:
    """
    Parses a string in the format "<label:category[/tab_name]:sort_order>[other_text]".

    Args:
        s: The input string to parse.

    Returns:
        A dictionary containing the parsed components, or None if the string
        does not match the required format.
    """
    # The regular expression to capture the different parts of the string.
    # It handles the optional tab_name and optional other_text.
    #
    # Breakdown of the regex:
    # <([^:]+):   - Matches '<', captures the 'label' (any characters that are not a colon), and matches ':'.
    # ([^/:]+)    - Captures the 'category' (any characters that are not a slash or colon).
    # (?:/([^:]+))? - A non-capturing group for the optional '/tab_name'.
    #              - ?: starts a non-capturing group.
    #              - / matches the literal slash.
    #              - ([^:]+) captures the 'tab_name' (any characters that are not a colon).
    #              - ? makes the entire group optional.
    # :(\d+)      - Matches ':', captures the 'sort_order' (one or more digits).
    # >(.*)       - Matches '>', and captures the 'other_text' (any characters to the end of the string).
    pattern = re.compile(r"<([^:]+):([^/:]+)(?:/([^:]+))?:(\d+)>(.*)")

    match = pattern.match(s)

    if match:
        # Extract the captured groups from the match object.
        label, category, tab_name, sort_order, other_text = match.groups()

        # Construct the result dictionary.
        return {
            "label": label,
            "category": category,
            "tab_name": tab_name if tab_name else "",
            "sort_order": int(sort_order),
            "other_text": other_text.strip()
        }
    else:
        # Return None if the string doesn't match the format.
        return None


if __name__ == "__main__":
    # Example 1 from the problem description
    string1 = "<Prompt:text_prompt:0>"
    print(f"Parsing string: '{string1}'")
    parsed1 = parse_title(string1)
    print("Result:", parsed1)
    print("-" * 20)

    # Example 2 from the problem description
    string2 = "<Result:output/16fps:5> mytext"
    print(f"Parsing string: '{string2}'")
    parsed2 = parse_title(string2)
    print("Result:", parsed2)
    print("-" * 20)
    
    # Additional example with a different format
    string3 = "<Audio:input/mp3:10>"
    print(f"Parsing string: '{string3}'")
    parsed3 = parse_title(string3)
    print("Result:", parsed3)
    print("-" * 20)
    
    # Another example with no other_text and no tab_name
    string4 = "<Debug:log:1>"
    print(f"Parsing string: '{string4}'")
    parsed4 = parse_title(string4)
    print("Result:", parsed4)
    print("-" * 20)
    
    # Example that does not match the format
    invalid_string = "Just some random text."
    print(f"Parsing string: '{invalid_string}'")
    parsed_invalid = parse_title(invalid_string)
    print("Result:", parsed_invalid)
    print("-" * 20)

