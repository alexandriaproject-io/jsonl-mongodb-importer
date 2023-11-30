import json


def read_jsonl_file(file_path, callback):
    print("Counting total lines in the jsonl file")
    with open(file_path, 'r') as file:
        num_lines = sum(1 for _ in file)
    print("Found " + str(num_lines) + " lines")
    with open(file_path, 'r') as file:
        current_line = 0
        for line in file:
            current_line += 1
            try:
                json_data = json.loads(line)
                if not callback(line, json_data, current_line, num_lines):
                    print(f"Stopping at line {current_line}")
                    break
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON: {e}")
                # Handle the error or continue to the next line
