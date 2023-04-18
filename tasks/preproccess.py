import argparse


def data_processing(input_file: str, nr_images: int, filters: bool) -> int:
    # dummy processing code here
    print("Data processing complete")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_file", type=str)
    parser.add_argument("--nr_images", type=int)
    parser.add_argument("--filters", type=bool)
    args = parser.parse_args()
    data_processing(args.input_file, args.nr_images, args.filters)
