import boto3
from dataclasses import dataclass
from pathlib import Path


@dataclass
class S3Options:
    source: str
    destination: str
    exclude_pattern: str = ""
    include_pattern: str = ""
    last_modified: bool = True
    dryrun: bool = True


def sync_with_s3(sync_options: S3Options) -> None:

    s3_client = boto3.client("s3")

    if sync_options.last_modified:
        print("Syncing files based on last modified time")
        _choose_sync_dirs(sync_options, s3_client)

    if sync_options.destination.startswith("s3://"):
        _upload_to_s3(sync_options, s3_client)
    else:
        _download_from_s3(sync_options, s3_client)


def _choose_sync_dirs(sync_options: S3Options, s3_client) -> None:

    local_time, s3_time = _get_last_modified(
        sync_options.source, sync_options.destination, s3_client)

    if local_time < s3_time:
        print("Syncing files from s3 bucket to local")
        original_source = sync_options.source
        sync_options.source = sync_options.destination
        sync_options.destination = original_source
    else:
        print("Syncing files from local to s3 bucket")


def _get_last_modified(source: str, destination: str,
                       s3_client) -> tuple[float, float]:

    local_last_mod_time: float = _get_local_time(source)
    s3_last_mod_time: float = _get_remote_time(destination, s3_client)

    return (local_last_mod_time, s3_last_mod_time)


def _get_local_time(source: str) -> float:

    last_mod_time: float = 0.0

    for file_path in Path(source).rglob("*"):
        if file_path.is_file():
            mod_time = file_path.stat().st_mtime
            if mod_time > last_mod_time:
                last_mod_time = mod_time

    return last_mod_time


def _get_remote_time(source: str, s3_client) -> float:

    last_mod_time: float = 0.0

    source = source.removeprefix("s3://")

    response = s3_client.list_objects_v2(Bucket=source)

    files = response["Contents"]
    for f in files:
        mod_time = f["LastModified"].timestamp()
        if mod_time > last_mod_time:
            last_mod_time = mod_time

    return last_mod_time


def _upload_to_s3(sync_options: S3Options, s3_client) -> None:

    files_to_sync: dict[str, str] = _get_file_list(
        sync_options.source, sync_options.destination, s3_client)

    if len(files_to_sync) == 0:
        print("All files are in sync")
        return

    bucket: str = sync_options.destination.removeprefix("s3://")

    for file, key in files_to_sync.items():
        destination = sync_options.destination + '/' + key
        if sync_options.dryrun:
            print(f"(upload: dryrun) {file} -> {destination}")
        else:
            print(f"(upload) {file} -> {destination}")
            s3_client.upload_file(file, bucket, key)


def _download_from_s3(sync_options: S3Options, s3_client) -> None:

    files_to_sync: dict[str, str] = _get_file_list(
        sync_options.destination, sync_options.source, s3_client)

    if len(files_to_sync) == 0:
        print("All files are in sync")
        return

    bucket: str = sync_options.destination.removeprefix("s3://")

    for key, file in files_to_sync.items():
        destination = sync_options.destination + '/' + key
        if sync_options.dryrun:
            print(f"(download: dryrun) {destination} <- {file}")
        else:
            print(f"(download) {destination} <- {file}")
            s3_client.download_file(bucket, key, file)


def _get_file_list(source: str, destination: str, s3_client) -> dict[str, str]:

    local_files: dict[str, int]
    s3_files: dict[str, int]

    upload: bool = False

    if destination.startswith("s3://"):
        upload = True
        local_files = _get_local_file_list(source)
        s3_files = _get_s3_file_list(destination, s3_client)
    else:
        local_files = _get_local_file_list(destination)
        s3_files = _get_s3_file_list(source, s3_client)

    files_to_sync: dict[str, str] = {}

    for file, size in local_files.items():
        file_name = "/".join(file.rsplit("/", maxsplit=2)[1:])
        if file_name in s3_files and size != s3_files[file_name]:
            if upload:
                files_to_sync[file] = file_name
            else:
                files_to_sync[file_name] = file

    return files_to_sync


def _get_local_file_list(source: str) -> dict[str, int]:

    file_list: dict[str, int] = {}

    for file_path in Path(source).rglob("*"):
        if file_path.is_file():
            file_list[file_path.absolute().as_posix()
                      ] = file_path.stat().st_size

    return file_list


def _get_s3_file_list(bucket: str, s3_client) -> dict[str, int]:

    file_list: dict[str, int] = {}
    bucket = bucket.removeprefix("s3://")

    response = s3_client.list_objects_v2(Bucket=bucket)

    files = response["Contents"]
    for f in files:
        file_list[f["Key"]] = f["Size"]

    return file_list
