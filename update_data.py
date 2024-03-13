import argparse
from sync_files_with_s3 import main as sync_files
from markdown_to_html import main as convert_files


def main():
    args = create_argument_parser()

    output = sync_files(args).strip().split('\n')

    upload = output[0].split(':', 1)[0].split(' ')[-1].lower() == "upload"

    files_to_convert = []
    for o in output:
        file = "/".join(o.rsplit('/', 2)[-2:])
        files_to_convert.append(file)

    convert_files(files_to_convert, upload, args)


def create_argument_parser():
    parser = argparse.ArgumentParser(
        "Sync files between local directory and s3 bucket")

    parser.add_argument(
        "--dryrun",
        help="sync files or only dryrun (default: dryrun)",
        action=argparse.BooleanOptionalAction)

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "--download",
        help="sync files from s3 bucket to local",
        action="store_true")
    group.add_argument(
        "--upload",
        help="sync files from local to s3 bucket",
        action="store_true")

    return parser.parse_args()


if __name__ == "__main__":
    main()
