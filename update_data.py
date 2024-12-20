from modules.sync_files import sync_templates, sync_markdown, sync_html

import argparse
import datetime
import logging
from subprocess import run as subprocess_run
import sys


def main():
    logging.basicConfig(
        level=logging.ERROR,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    args = create_argument_parser()
    dryrun = check_dry_run(args)

    if (args.templates_only):
        sync_templates(args, dryrun=dryrun)
        return

    if (args.html_only):
        sync_html(True, dryrun=dryrun)
        return

    sync_markdown(args, dryrun=dryrun)
    sync_html(True, dryrun=dryrun)

    push_html_to_github()


def push_html_to_github() -> None:
    commit_msg = datetime.datetime.now().strftime(
        "[%Y-%m-%d %H:%M:%S]: Update HTML files")

    exit_code = subprocess_run(["./commit_files.sh", commit_msg]).returncode

    if exit_code:
        logging.error("Failed to push html files to github repository")
        exit(1)


def check_dry_run(args) -> bool:
    if args.dryrun is None:
        return True

    return args.dryrun


def create_argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "Sync files between local directory and s3 bucket")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    parser.add_argument(
        "--dryrun",
        help="sync files or only dryrun (default: dryrun)",
        action=argparse.BooleanOptionalAction)

    parser.add_argument(
        "--html-only",
        help="convert and sync all html files from local to s3 bucket",
        action="store_true")

    parser.add_argument(
        "--templates-only",
        help="sync files in templates directory",
        action="store_true")

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


if __name__ == "__main__":
    main()
