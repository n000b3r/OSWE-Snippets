import urllib.parse

def format_burp_payload(raw_payload):
    # Parse the URL-encoded string into a dictionary
    parsed_data = urllib.parse.parse_qs(raw_payload)
    
    # parse_qs puts everything in a list, so we flatten it
    formatted_data = {k: v[0] for k, v in parsed_data.items()}
    
    print("\n[!] Here is your payload dictionary for requests:\n")
    print("data = {")
    for key, value in formatted_data.items():
        print(f"    '{key}': '{value}',")
    print("}")

if __name__ == '__main__':
    # You can paste your messy string right here
    raw_input = input("Paste your Burp POST data here: ")
    format_burp_payload(raw_input)
