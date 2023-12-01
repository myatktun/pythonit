import subprocess
import os
import argparse
from dotenv import load_dotenv


def create_argument_parser():
    parser = argparse.ArgumentParser(
        "Sync note files between local directory and s3 bucket")

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


def get_last_modified_times(local_dir, s3_bucket):
    command_1 = f"find {local_dir} -type f -exec stat -c \"%y %n\" {{}} + | sort -r | head -n 1 | awk '{{print $1 \" \" $2}}'"
    command_2 = f"aws s3 ls {s3_bucket} --recursive | sort | tail -n 1 | awk '{{print $1 \" \" $2}}'"

    local_time = subprocess.run(
        command_1, stdout=subprocess.PIPE, shell=True).stdout.decode("utf-8")

    s3_time = subprocess.run(command_2, stdout=subprocess.PIPE,
                             shell=True).stdout.decode("utf-8")

    return (local_time, s3_time)


def get_sync_dirs(local_dir, s3_bucket, args):
    if args.download:
        print("Syncing files from s3 bucket to local")
        return (s3_bucket, local_dir)
    elif args.upload:
        print("Syncing files from local to s3 bucket")
        return (local_dir, s3_bucket)

    local_time, s3_time = get_last_modified_times(local_dir, s3_bucket)

    if local_time < s3_time:
        print("Syncing files from s3 bucket to local")
        return (s3_bucket, local_dir)

    print("Syncing files from local to s3 bucket")
    return (local_dir, s3_bucket)


def main():
    load_dotenv()

    args = create_argument_parser()
    dry_run = check_dry_run(args)

    LOCAL_DIR = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']
    S3_BUCKET = os.environ['S3_BUCKET']

    source, destination = get_sync_dirs(LOCAL_DIR, S3_BUCKET, args)

    exclude_pattern = "*.md"
    include_pattern = "*/*.md"

    command = ["aws", "s3", "sync", source, destination, "--exclude",
               exclude_pattern, "--include", include_pattern, "--size-only"]

    if dry_run:
        command.append("--dryrun")

    subprocess.run(command)


if __name__ == "__main__":
    main()