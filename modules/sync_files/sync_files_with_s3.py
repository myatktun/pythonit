from dataclasses import dataclass
from subprocess import run as subprocess_run


@dataclass
class SyncOptions:
    source: str
    destination: str
    exclude_pattern: str = ""
    include_pattern: str = ""
    dryrun: bool = True


def _sync_files(option: SyncOptions) -> None:

    command = ["aws", "s3", "sync", option.source, option.destination,
               "--exclude", option.exclude_pattern,
               "--include", option.include_pattern, "--size-only"]

    if option.dryrun:
        command.append("--dryrun")

    subprocess_run(command)
