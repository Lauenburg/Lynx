import time

import fire


def validate(input_file: str, forty_two: int) -> int:
    """Validate the input file"""
    for char in "Validating *********** Top!":
        print(char, end="", flush=True)
        time.sleep(0.1)
    print()
    print("Application Validated")
    print(f"The file states: {input_file}")
    print(f"{forty_two} - The answer to the Ultimate Question of Life, the Universe, and Everything,")
    return 0


if __name__ == "__main__":
    fire.Fire(validate)
