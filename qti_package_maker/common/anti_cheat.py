
# Standard Library
import os
import re
import random

# Pip3 Library

# QTI Package Maker
from qti_package_maker.common import string_functions

# ============================ Anti-Cheating Configuration ============================

# 1. Hidden Terms: Inserts nearly invisible words to detect unauthorized content-sharing.
use_insert_hidden_terms = False  # Enable/Disable hidden term insertion
hidden_term_density = 0.7  # Probability of inserting a hidden term after a word
hidden_term_bank = None  # Will store the hidden term list once loaded

# 2. No-Click Div: Prevents right-click, text selection, copying, and context menu.
add_no_click_div = False  # Enable/Disable anti-click div wrapper

# 3. Anti-Copy JavaScript: Prevents printing, copying, and screenshots.
use_anticopy_script = False  # Enable/Disable anti-copy script
noPrint = True  # Disable printing
noCopy = True  # Disable copying
noScreenshot = False  # Disable screenshots (not foolproof)
autoBlur = True  # Blur content when switching tabs (prevents screen recording)

# =====================================================================================

def anticheat_modify_string(string_text):
    """
    Applies anti-cheating modifications to the given string.

    - Inserts hidden terms (if enabled)
    - Wraps the text in a non-clickable div (if enabled)
    - Injects anti-copy JavaScript (if enabled)

    Args:
        string_text (str): The text content to be protected.

    Returns:
        str: Modified text with anti-cheating protections applied.
    """
    if use_insert_hidden_terms:
        string_text = insert_hidden_terms(string_text)
    if add_no_click_div:
        string_text = wrap_text_in_no_click_div(string_text)
    if use_anticopy_script:
        js_function_string = get_anticopy_js_function()
        # Prepend JavaScript to execute before the content loads
        string_text = js_function_string + string_text
    return string_text

# =======================================================================
# Anti-Copy Protection: Prevents text selection, copying, right-clicking
# =======================================================================

def wrap_text_in_no_click_div(string_text):
    """
    Wraps the given text in a non-clickable <div> to prevent copying, selecting, and right-clicking.

    - Blocks text selection
    - Disables context menu (right-click)
    - Prevents pasting and cutting
    - Stops onmousedown selection

    Args:
        string_text (str): The text content to be protected.

    Returns:
        str: Wrapped HTML string with anti-cheating properties.
    """
    rand_crc16 = string_functions.get_random_crc16()  # Generate a unique identifier
    output = f'<div id="drv_{rand_crc16}" ' \
             'oncopy="return false;" onpaste="return false;" oncut="return false;" ' \
             'oncontextmenu="return false;" onmousedown="return false;" onselectstart="return false;">'
    output += string_text
    output += '</div>'
    return output

# =======================================================================
# Hidden Terms: Embeds invisible markers to detect unauthorized sharing
# =======================================================================

def get_git_root():
    """
    Returns the root directory of the Git repository (if applicable).

    This function is used to locate the 'data/all_short_words.txt' file
    which contains words for the hidden term bank.

    Returns:
        str: Absolute path of the Git repository root or None if not inside a repo.
    """
    import subprocess
    try:
        base = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"], text=True
        ).strip()
        return base
    except subprocess.CalledProcessError:
        return None  # Not inside a Git repository

def load_hidden_term_bank():
    """
    Loads a list of hidden words from a predefined file.

    These words are inserted randomly into assessment content to help detect unauthorized content sharing.

    Returns:
        list: A list of words to be hidden in the text.
    """
    git_root = get_git_root()
    data_file_path = os.path.join(git_root, 'data/all_short_words.txt')
    with open(data_file_path, 'r') as file:
        terms = file.readlines()
    return [term.strip() for term in terms]

def insert_hidden_terms(text_content):
    """
    Randomly inserts hidden words into the text to detect unauthorized distribution.

    - Invisible words are added inside `<span>` elements with `font-size: 1px; color: white;`
    - Spaces between words are replaced with '@' to create valid insertion points.
    - Words inside `<table>` and `<code>` blocks are left untouched to avoid breaking syntax.

    Args:
        text_content (str): The original assessment content.

    Returns:
        str: The modified content with hidden words.
    """
    if not use_insert_hidden_terms:
        return text_content

    global hidden_term_bank
    if hidden_term_bank is None:
        hidden_term_bank = load_hidden_term_bank()

    # Split the content into sections, preserving tables and code blocks
    parts = re.split(r'(<table>.*?</table>|<code>.*?</code>)', text_content, flags=re.DOTALL)

    new_parts = []
    for part in parts:
        if part.startswith('<table>') or part.startswith('<code>'):
            new_parts.append(part)  # Keep structured content unchanged
        else:
            part = re.sub(r'([a-z]) +([a-z])(?![^<>]*>)', r'\1@\2', part)  # Preserve inline elements
            words = part.split('@')  # Split words where spaces were
            new_words = []
            for word in words:
                new_words.append(word)
                if random.random() < hidden_term_density:
                    hidden_term = random.choice(hidden_term_bank)
                    new_words.append(f"<span style='font-size: 1px; color: white;'>{hidden_term}</span>")
                else:
                    new_words.append(" ")  # Restore spaces
            new_parts.append(''.join(new_words))

    return ''.join(new_parts)

# =======================================================================
# Anti-Copy JavaScript: Disables printing, copying, and screenshots
# =======================================================================

def get_anticopy_js_function():
    """
    Generates JavaScript to prevent various forms of content theft.

    - `noPrint`: Disables printing via `window.print()`
    - `noCopy`: Disables right-click and copying
    - `noScreenshot`: Attempts to block screenshots (not foolproof)
    - `autoBlur`: Detects tab-switching and blurs content

    Returns:
        str: JavaScript `<script>` tag with anti-copy functionality.
    """
    js_code = (
        '<script>'
        f'var noPrint={str(noPrint).lower()};'
        f'var noCopy={str(noCopy).lower()};'
        f'var noScreenshot={str(noScreenshot).lower()};'
        f'var autoBlur={str(autoBlur).lower()};'
        '</script>'
    )
    js_code += (
        '<script type="text/javascript" '
        'src="https://cdn.jsdelivr.net/gh/vosslab/biology-problems@main/javascript/noprint.js">'
        '</script>'
    )
    return js_code

