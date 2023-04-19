import argparse
import time


def validate(input_file: str) -> int:
    for char in "Validating *********** Top!":
        print(char, end="", flush=True)
        time.sleep(0.1)
    print()
    print("Application Validated")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str)
    args = parser.parse_args()
    validate(args.input_file)
