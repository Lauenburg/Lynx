import time

import fire


def train() -> int:
    """Train the model"""
    for char in r"Training /\/\/\/\/\/\/\ Done!":
        print(char, end="", flush=True)
        time.sleep(0.1)
    print()
    print("Training completed")
    return 0


if __name__ == "__main__":
    fire.Fire(train)
