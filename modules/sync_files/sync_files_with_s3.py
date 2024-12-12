from subprocess import run as subprocess_run


def _sync_files(source: str, destination: str, *,
                dryrun=True, exclude="", include=""):

    command = ["aws", "s3", "sync", source, destination, "--exclude",
               exclude, "--include", include, "--size-only"]

    if dryrun:
        command.append("--dryrun")

    subprocess_run(command)
