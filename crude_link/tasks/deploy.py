import time

import fire


def deploy() -> int:
    for char in "Deploying ............. Up!":
        print(char, end="", flush=True)
        time.sleep(0.1)
    print()
    print("Application Deployed")
    return 0


if __name__ == "__main__":
    fire.Fire(deploy)
