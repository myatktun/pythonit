import sys
from subprocess import PIPE, run as subprocess_run


def _sync_files(source: str, destination: str, *,
                dryrun=True, exclude="", include="") -> str:

    command = ["aws", "s3", "sync", source, destination, "--exclude",
               exclude, "--include", include, "--size-only"]

    if dryrun:
        command.append("--dryrun")

    output = subprocess_run(command, stdout=PIPE,
                            encoding="utf-8").stdout

    if len(output) == 0:
        print("No files to sync: All files are up to date")
        sys.exit(0)

    print(output)

    return output
