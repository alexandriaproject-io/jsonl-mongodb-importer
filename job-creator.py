import sys
from mongo import count_dataset_size, get_dataset_cursor, create_new_job, delete_job, set_job_queued
from pymongo.errors import DuplicateKeyError
from rabbit import queue_job, close_queue
from pika.exceptions import AMQPError

job_types = ['generate', 'expand', 'rephrase']
job_targets = ['system', 'messages', 'context']
job_sources = ['system', 'messages', 'context']
job_tools = ['default', 'gpt-3.5', 'gpt-4', 'gpt-4-1106-preview', 'llama-7b', 'llama-7b-chat', 'llama-13b',
             'llama-13b-chat']


def get_user_confirmation():
    while True:
        user_input = input("Press 'y' to proceed or 'n' to exit: ").lower()
        if user_input == 'y':
            return True
        elif user_input == 'n':
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


if __name__ == "__main__":
    print("")
    if len(sys.argv) < 6 or 'using' not in sys.argv or 'with' not in sys.argv:
        print("Usage: python job-creator.py <dataset_id> <job-type> <target> using <source> [<source> ...] with <tool>")
        sys.exit(1)

    dataset_id = sys.argv[1]

    job_type = sys.argv[2]
    if job_type not in job_types:
        print(f"Error: Unsupported job type '{job_type}'. Supported job types are: {', '.join(job_types)}")
        sys.exit(1)

    job_target = sys.argv[3]
    if job_target not in job_targets:
        print(f"Error: Unsupported job target '{job_target}'. Supported job targets are: {', '.join(job_targets)}")
        sys.exit(1)

    using_index = sys.argv.index('using')
    with_index = sys.argv.index('with')

    if with_index <= using_index:
        print("Error: Invalid argument order. 'with' should come after 'using'.")
        sys.exit(1)

    sources = sys.argv[using_index + 1:with_index]
    for source in sources:
        if source not in job_sources:
            print(f"Error: Unsupported source '{source}'. Supported sources are: {', '.join(job_sources)}")
            sys.exit(1)

    if with_index == len(sys.argv) - 1:
        print("Error: No tool specified after 'with'.")
        sys.exit(1)

    tool = sys.argv[with_index + 1]
    if tool not in job_tools:
        print(f"Error: Unsupported tool '{tool}'. Supported tools are: {', '.join(job_tools)}")
        sys.exit(1)

    print(f"Dataset ID: {dataset_id}")
    print(f"Job Type: {job_type}")
    print(f"Job Target: {job_target}")
    print(f"Job Sources: {sources}")
    print(f"Job Tool: {tool}")

    collection_size = count_dataset_size(dataset_id)
    if collection_size == 0:
        print("No data rows found! Check your dataset id")
        exit(0)

    print(f"Found {collection_size} rows in dataset")
    print("")
    if not get_user_confirmation():
        print("Operation cancelled by the user.")
        sys.exit(0)
    print("")

    data_cursor = get_dataset_cursor(dataset_id)
    jobs_count = 0
    for document in data_cursor:
        # Process each document
        jobs_count += 1

        try:
            job_id, job_data = create_new_job(dataset_id, document, job_type, job_target, job_sources, 'queued')
            try:
                queue_job(job_id, job_data)
                print(f"Job {jobs_count}/{collection_size} - Created.")
            except TypeError as e:
                delete_job(job_id)
                print(f"Job {jobs_count}/{collection_size} - Failed to serialize json.")
            except AMQPError as e:
                print(e)
                delete_job(job_id)
                print(f"Job {jobs_count}/{collection_size} - Failed to create.")

        except DuplicateKeyError as e:
            print(f"Job {jobs_count}/{collection_size} - Already exists.")

    print("Done!")
    print("")
    close_queue()
