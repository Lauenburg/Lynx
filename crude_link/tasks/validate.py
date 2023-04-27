import argparse
import time

import fire


def validate(input_file: str) -> int:
    for char in "Validating *********** Top!":
        print(char, end="", flush=True)
        time.sleep(0.1)
    print()
    print("Application Validated")
    return 0


if __name__ == "__main__":
    fire.Fire(validate)
