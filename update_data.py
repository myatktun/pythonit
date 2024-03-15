import argparse
import os
from dotenv import load_dotenv
from markdown_to_html import main as convert_files
from subprocess import Popen, PIPE
from sync_files_with_s3 import sync_files


def main():

    load_dotenv()
    args = create_argument_parser()

    md_files = sync_md_files(args)

    upload = md_files[0].split(
        ':', 1)[0].split(' ')[-1].lower() == "upload"

    files_to_convert = []
    for o in md_files:
        file = "/".join(o.rsplit('/', 2)[-2:])
        files_to_convert.append(file)

    convert_files(files_to_convert, upload, args)


def sync_md_files(args) -> list[str]:

    dryrun = check_dry_run(args)

    LOCAL_DIR = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']
    S3_BUCKET = os.environ['S3_BUCKET']

    source, destination = get_sync_dirs(LOCAL_DIR, S3_BUCKET, args)

    exclude_pattern = "*.md"
    include_pattern = "*/*.md"

    md_files = sync_files(source, destination, dryrun=dryrun,
                          exclude=exclude_pattern, include=include_pattern)

    return md_files.strip().split('\n')


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


def check_dry_run(args):
    if args.dryrun is None:
        return True

    return args.dryrun


def get_sync_dirs(local_dir, s3_bucket, args):
    if args.download:
        print("Syncing markdown files from s3 bucket to local")
        return (s3_bucket, local_dir)
    elif args.upload:
        print("Syncing markdown files from local to s3 bucket")
        return (local_dir, s3_bucket)

    local_time, s3_time = get_last_modified_times(local_dir, s3_bucket)

    if local_time == s3_time:
        print("All files are in sync")
        exit(0)

    if local_time < s3_time:
        print("Syncing markdown files from s3 bucket to local")
        return (s3_bucket, local_dir)

    print("Syncing markdown files from local to s3 bucket")
    return (local_dir, s3_bucket)


def get_last_modified_times(local_dir, s3_bucket):
    command1 = ["find", f"{local_dir}", "-mindepth", "2", "-type",
                "f", "-exec", "stat", "-c", "%y", "{}", "+"]

    command2 = ["aws", "s3", "ls", f"{s3_bucket}", "--recursive"]

    local_time = get_time(command1)
    s3_time = get_time(command2)

    return (local_time.split(".")[0], s3_time)


def get_time(command):
    time_list = Popen(command, stdout=PIPE)
    assert time_list.stdout is not None

    sorted_time_list = Popen(
        ["sort", "-r"], stdin=time_list.stdout, stdout=PIPE)
    time_list.stdout.close()
    assert sorted_time_list.stdout is not None

    top_row = Popen(["head", "-n", "1"],
                    stdin=sorted_time_list.stdout, stdout=PIPE)
    sorted_time_list.stdout.close()
    assert top_row.stdout is not None

    first_column = Popen(
        ["awk", '{print $1 " " $2}'], stdin=top_row.stdout, stdout=PIPE)
    top_row.stdout.close()

    latest_time = first_column.communicate()[0].decode("utf-8")

    return latest_time.strip()


if __name__ == "__main__":
    main()
