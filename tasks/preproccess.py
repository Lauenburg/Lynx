import time

import fire


def read_file(file_path: str) -> str:
    """Read the file"""
    with open(file_path) as file:
        content = file.read()
    return content


def data_processing(input_file: str, nr_images: int, filters: bool) -> int:
    """Process the data"""
    for char in "Processing ------------> GO!":
        print(char, end="", flush=True)
        time.sleep(0.1)
    print()
    print(f"{nr_images} processed ...")
    print("The file states: ", read_file(input_file))
    print(f"Filters applied: {filters}")
    return 0


if __name__ == "__main__":
    fire.Fire(data_processing)
