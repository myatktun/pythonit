import boto3
from dataclasses import dataclass
from subprocess import run as subprocess_run
from pathlib import Path


@dataclass
class S3Options:
    source: str
    destination: str
    exclude_pattern: str = ""
    include_pattern: str = ""
    dryrun: bool = True


def sync_with_s3(sync_option: S3Options) -> None:

    source, destination = _get_sync_dirs(sync_option)

    command = ["aws", "s3", "sync", source, destination,
               "--exclude", sync_option.exclude_pattern,
               "--include", sync_option.include_pattern, "--size-only"]

    if sync_option.dryrun:
        command.append("--dryrun")

    subprocess_run(command)


def _get_sync_dirs(sync_option: S3Options) -> tuple[str, str]:
    # if download:
    #     print("Syncing markdown files from s3 bucket to local")
    #     return (destination, source)
    # elif upload:
    #     print("Syncing markdown files from local to s3 bucket")
    #     return (source, destination)

    print("Syncing files based on last modified time")
    local_time, s3_time = _get_last_modified(
        sync_option.source, sync_option.destination)

    if local_time == s3_time:
        print("All files are in sync")
        exit(0)

    if local_time < s3_time:
        print("Syncing files from s3 bucket to local")
        return (sync_option.destination, sync_option.source)

    print("Syncing files from local to s3 bucket")
    return (sync_option.source, sync_option.destination)


def _get_last_modified(source: str, destination: str) -> tuple[float, float]:

    local_last_mod_time = _get_local_time(source)
    s3_last_mod_time = _get_remote_time(destination)

    return (local_last_mod_time, s3_last_mod_time)


def _get_local_time(source: str) -> float:
    last_mod_time: float = 0.0

    for file_path in Path(source).rglob("*"):
        if file_path.is_file():
            mod_time = file_path.stat().st_mtime
            if mod_time > last_mod_time:
                last_mod_time = mod_time

    return last_mod_time


def _get_remote_time(source: str) -> float:
    last_mod_time: float = 0.0
    s3_client = boto3.client("s3")
    source = source.removeprefix("s3://")

    response = s3_client.list_objects_v2(Bucket=source)

    files = response["Contents"]
    for f in files:
        mod_time = f["LastModified"].timestamp()
        if mod_time > last_mod_time:
            last_mod_time = mod_time

    return last_mod_time
