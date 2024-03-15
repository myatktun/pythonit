import sys
from subprocess import PIPE, run as subprocess_run


def sync_files(source: str, destination: str, *,
               dryrun=True, exclude="", include="") -> str:

    command = ["aws", "s3", "sync", source, destination, "--exclude",
               exclude, "--include", include, "--size-only"]

    if dryrun:
        command.append("--dryrun")

    output = subprocess_run(command, stdout=PIPE).stdout.decode()

    if len(output) == 0:
        sys.exit("No files to sync")

    return output
