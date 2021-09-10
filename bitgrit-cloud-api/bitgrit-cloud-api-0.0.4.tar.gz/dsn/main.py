import argparse


def main():
    parser = argparse.ArgumentParser(
        description='bitgrit dataset microservice')

    parser.add_argument(
        "--bucket",
        help='Google Bucket that contains the dataset',
        required=True
    )

    args = parser.parse_args()
    bucket_name = args.bucket


if __name__ == '__main__':
    main()
