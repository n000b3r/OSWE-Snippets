#!/usr/bin/env python3
"""
Common utilities shared across all OSWE exploit scripts.
Copy the helpers you need into your exploit script.
"""
import requests

import random
import re
import string
import base64
import urllib.parse
import subprocess

# ==============================================================================
# SESSION
# ==============================================================================

requests.packages.urllib3.disable_warnings()

session = requests.Session()
session.verify = False

BURP_PROXIES = {
    "http":  "http://127.0.0.1:8080",
    "https": "http://127.0.0.1:8080",
}

# ==============================================================================
# CONSOLE HELPERS (copy into your main script if not already there)
# ==============================================================================

_ANSI = re.compile(r'\x1b\[[0-9;]*m')

def print_ok(msg: str)   -> None: print(f"  [+] {msg}")
def print_info(msg: str) -> None: print(f"  [*] {msg}")
def print_err(msg: str)  -> None: print(f"  [-] {msg}")

def strip_ansi(text: str) -> str:
    return _ANSI.sub('', text).strip()

def print_banner(title: str) -> None:
    width = 70
    print("=" * width)
    print(f"  {title}")
    print("=" * width)

def print_stage(n: int, description: str) -> None:
    print(f"\n[STAGE {n}] {description}")
    print("-" * 50)

# ==============================================================================
# ENCODERS (copy encode_base64 / encode_url into your main script)
# ==============================================================================

def encode_base64(text: str) -> str:
    """CyberChef: To Base64"""
    return base64.b64encode(text.encode('utf-8')).decode('utf-8')

def encode_url(text: str) -> str:
    """CyberChef: URL Encode (Encode all special chars checked)"""
    return urllib.parse.quote(text, safe='')

def string_to_decimal(s):
    """CyberChef: To decimal"""
    return ",".join(str(ord(c)) for c in s)

# ==============================================================================
# DECODERS (copy decode_base64 into your main script)
# ==============================================================================

def decode_base64(b64_text: str) -> str:
    """CyberChef: From Base64"""
    # Decoding the base64 string back into a standard utf-8 string
    return base64.b64decode(b64_text).decode('utf-8')

def decode_base64_to_hex(b64_text: str) -> str:
    """Decode Base64 to raw bytes, then convert to hex string (like CyberChef's 'To Hex', Delimiter is None)."""
    raw_bytes = base64.b64decode(b64_text)
    return raw_bytes.hex()

# ==============================================================================
# RANDOM GENERATORS (copy generate_password / generate_random_name into your main script)
# ==============================================================================

def generate_password(length: int = 16) -> str:
    """
    Password guaranteed to satisfy common validation policies:
    uppercase + lowercase + digit + special. No shell-breaking chars.
    """
    required = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*()_+-="),
    ]
    pool = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
    rest = random.choices(pool, k=length - len(required))
    password = required + rest
    random.shuffle(password)
    return "".join(password)


def generate_random_name(length: int = 10) -> str:
    """Random lowercase alphabetical identifier (no digits, safe as usernames)."""
    return "".join(random.sample(string.ascii_lowercase, length))


def create_token_gen_php_file():
    php_content = r'''<?php
function generateToken($seed) {
    srand($seed);
    $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_';
    $ret = '';
    for ($i = 0; $i < 32; $i++) {
        $ret .= $chars[rand(0,strlen($chars)-1)];
    }
    return $ret;
}

$ts = $argv[1];
print(generateToken($ts)."\n");
?>
'''
    with open("token_gen.php", "w") as f:
        f.write(php_content)

def generate_php_token(seed):
    result = subprocess.run(
        ["php", "token_gen.php", str(seed)],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

# ==============================================================================
# REGEX EXTRACTION (copy the extract_* helpers into your main script)
# ==============================================================================

def extract_between_markers(content, start_marker, end_marker=None):
    """
    Extracts text between a start_marker and an end_marker, 
    or until the end of the string if end_marker is None.
    """
    text_content = content.decode('utf-8', errors='ignore') if isinstance(content, bytes) else str(content)
    
    # If no end marker, stop at the end of the string ($)
    if end_marker is None or end_marker == "":
        pattern = re.escape(start_marker) + r"(.*)$"
    else:
        pattern = re.escape(start_marker) + r"(.*?)" + re.escape(end_marker)
        
    match = re.search(pattern, text_content, re.DOTALL)
    
    if match:
        return match.group(1)
    return None


def extract_all_between_markers(response_text: str, start: str, end: str) -> list[str]:
    """Extract all matches — use when the response contains multiple rows."""
    pattern = rf"{re.escape(start)}(.*?){re.escape(end)}"
    return re.findall(pattern, response_text, re.DOTALL)

# ==============================================================================
# POWERSHELL ENCODING (copy encode_ps1 into your main script)
# ==============================================================================

def encode_ps1(payload: str) -> str:
    """
    Encode a PowerShell command for use with -EncodedCommand.
    Avoids quoting/escaping issues when injecting PS1 through a webshell or URL param.

    Usage:
        b64 = encode_ps1("whoami")
        cmd = f"powershell.exe -EncodedCommand {b64}"
    """
    import base64
    return base64.b64encode(payload.encode("utf-16le")).decode("utf-8")
