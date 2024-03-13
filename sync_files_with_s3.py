import os
import sys
from subprocess import Popen, PIPE, run as subprocess_run
from dotenv import load_dotenv


def main(args):
    load_dotenv()

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

    output = subprocess_run(command, stdout=PIPE).stdout.decode()

    if len(output) == 0:
        sys.exit("No files to sync")

    print(output)

    return output


def check_dry_run(args):
    if args.dryrun is None:
        return True

    return args.dryrun


def get_sync_dirs(local_dir, s3_bucket, args):
    if args.download:
        print("Syncing files from s3 bucket to local")
        return (s3_bucket, local_dir)
    elif args.upload:
        print("Syncing files from local to s3 bucket")
        return (local_dir, s3_bucket)

    local_time, s3_time = get_last_modified_times(local_dir, s3_bucket)

    if local_time == s3_time:
        print("All files are in sync")
        exit(0)

    if local_time < s3_time:
        print("Syncing files from s3 bucket to local")
        return (s3_bucket, local_dir)

    print("Syncing files from local to s3 bucket")
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
