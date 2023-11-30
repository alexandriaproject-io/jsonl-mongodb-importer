import sys
from jsonl_reader import read_jsonl_file
import re

# Import the insert_data function from the relevant script
from mongo import insert_raw_data, insert_mapped_data


def split_text_into_messages(text):
    # Define the pattern to match [INST] and [/INST] tags
    pattern = r"(\[/?INST\])"

    # Split the text based on the pattern
    parts = re.split(pattern, text)

    messages = []
    current_type = None

    for part in parts:
        if part == "[INST]":
            current_type = "user"
        elif part == "[/INST]":
            current_type = "assistant"
        else:
            if current_type and part.strip():  # Ignore empty strings
                messages.append({"provider": current_type, "message": part.strip()})

    return messages


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python process_and_insert.py <dataset_id> <file_url>")
        sys.exit(1)
    dataset_id = sys.argv[1]
    file_url = sys.argv[2]


    def process_json_line(raw_json_string, json_data, current_line_number, total_lines):
        print('Processing ' + str(current_line_number) + " / " + str(total_lines))
        series_position = 0
        messages = split_text_into_messages(json_data.get('text'))

        raw_json_id = insert_raw_data(dataset_id, raw_json_string)
        grouped_messages = []
        for message in messages:
            grouped_messages.append(message)
            if message['provider'] == 'assistant':
                insert_mapped_data(dataset_id, raw_json_id, {
                    'seriesPosition': series_position,
                    "messages": grouped_messages
                })
                series_position += 1
        return True

    read_jsonl_file(file_url, process_json_line)
