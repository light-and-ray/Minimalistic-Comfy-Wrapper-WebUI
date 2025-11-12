import re, json
import urllib.error
from urllib.parse import urljoin, urlencode, urlparse, parse_qs, urlunparse
from mcww import opts


def parseMinMaxStep(other_text: str):
    numbers_as_strings = re.findall(r"[-+]?\d*\.?\d+", other_text)

    if len(numbers_as_strings) not in [2, 3]:
        return None

    try:
        min_val = float(numbers_as_strings[0])
        max_val = float(numbers_as_strings[1])
        step_val = float(numbers_as_strings[2]) if len(numbers_as_strings) == 3 else None
    except (IndexError, ValueError) as e:
        return None

    return (min_val, max_val, step_val)



def parse_title(title: str) -> dict or None:
    """
    Parses a string in the format:
    <Label:category[/tab]:sortRowNumber[/sortColNumber]> other args

    Returns a dictionary with parsed fields, or None if the format doesn't match.
    """
    # Explanation of the new regex pattern:
    # 1. <([^:]+):                 - Start tag, capture Label (Group 1)
    # 2. ([^/:]+)                  - Capture Category (Group 2)
    # 3. (?:/([^/:]+))?            - Optional non-capturing group for the next segment (tab).
    # 5. :(\d+)                    - Separator ':', capture sortRowNumber (Group 5)
    # 6. (?:/(\d+))?               - Optional non-capturing group for '/sortColNumber'. sortColNumber is captured (Group 6).
    # 7. >(.*)                     - End tag '>', capture other args (Group 7)

    pattern = re.compile(
        r"<([^:]+):"               # Group 1: Label
        r"([^/:]+)"                # Group 2: Category
        r"(?:/([^/:]+))?"          # Group 3: Optional tab_name
        r":(\d+)"                  # Group 5: sortRowNumber
        r"(?:/(\d+))?"             # Group 6: Optional sortColNumber
        r">(.*)"                   # Group 7: other_text
    )

    match = pattern.match(title)

    if match:
        label, category, tab_name, sort_row_number_str, sort_col_number_str, other_text = match.groups()
        if tab_name:
            tab_name.strip()
        # Convert sort numbers
        sort_row_number = int(sort_row_number_str)
        # sortColNumber is optional, so it might be None
        sort_col_number = int(sort_col_number_str) if sort_col_number_str else None

        return {
            "label": label.strip(),
            "category": category.strip(),
            "tab_name": tab_name,
            "sort_row_number": sort_row_number,
            "sort_col_number": sort_col_number,
            "other_text": other_text.strip()
        }
    else:
        return None

def _getComfyPathUrl(path: str, schema: str):
    base_url = f"{schema}://{opts.COMFY_ADDRESS}"
    url = urljoin(base_url, path)
    if opts.COMFY_UI_LOGIN_EXTENSION_TOKEN:
        # Parse the URL to handle existing query parameters
        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        # Add or update the token parameter
        query_params["token"] = [opts.COMFY_UI_LOGIN_EXTENSION_TOKEN]
        # Reconstruct the URL with the updated query
        updated_query = urlencode(query_params, doseq=True)
        url = urlunparse(parsed_url._replace(query=updated_query))
    return url

def getHttpComfyPathUrl(path: str):
    schema = "https" if opts.COMFY_TLS else "http"
    return _getComfyPathUrl(path, schema)

def getWsComfyPathUrl(path: str):
    schema = "wss" if opts.COMFY_TLS else "ws"
    return _getComfyPathUrl(path, schema)


class ComfyIsNotAvailable(Exception):
    pass


def checkForComfyIsNotAvailable(e: Exception):
    if type(e) == OSError and "No route to host" in str(e):
        raise ComfyIsNotAvailable(str(e))
    if type(e) == urllib.error.URLError:
        raise ComfyIsNotAvailable(str(e))
    if type(e) == ConnectionResetError:
        raise ComfyIsNotAvailable(str(e))


def tryGetJsonFromURL(url: str):
    try:
        with urllib.request.urlopen(url) as response:
            if response.getcode() == 404:
                return None
            return json.loads(response.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise
    except Exception:
        raise

