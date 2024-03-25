import os
from dotenv import load_dotenv
from subprocess import Popen, PIPE
from .sync_files_with_s3 import sync_files


def sync_markdown(args, *, dryrun=True) -> list[str]:
    load_dotenv()

    LOCAL_DIR = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']
    S3_BUCKET = os.environ['S3_BUCKET']

    source, destination = get_sync_dirs(LOCAL_DIR, S3_BUCKET, args)

    exclude_pattern = "*.md"
    include_pattern = "*/*.md"

    md_files = sync_files(source, destination, dryrun=dryrun,
                          exclude=exclude_pattern, include=include_pattern)

    return [f for f in md_files.strip().split('\n')
            if not f.startswith("Completed")]


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
