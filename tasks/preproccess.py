import argparse
import time


def read_file(file_path):
    with open(file_path, "r") as file:
        content = file.read()
    return content


def data_processing(input_file: str, nr_images: int, filters: bool) -> int:
    for char in "Processing ------------> GO!":
        print(char, end="", flush=True)
        time.sleep(0.1)
    print()
    print(f"{nr_images} processed ...")
    print("The file states: ", read_file(input_file))
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str)
    parser.add_argument("--nr_images", type=int)
    parser.add_argument("--filters", type=bool)
    args = parser.parse_args()
    print("args: ", args)
    data_processing(args.input_file, args.nr_images, args.filters)
