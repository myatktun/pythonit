from modules.sync_files import sync_with_s3, S3Options
from modules.file_converter import convert_md_to_rst, convert_rst_to_html

import argparse
from argparse import Namespace
import datetime
from dotenv import load_dotenv
import logging
import os
from subprocess import run as subprocess_run
import sys


def main():
    load_dotenv()

    logging.basicConfig(
        level=logging.ERROR,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    args = create_argument_parser()

    if not args.html_only:
        update_markdown(args)

    if not args.markdown_only:
        update_html(args)


def update_markdown(args: Namespace) -> None:
    LOCAL_MD_DIR = os.environ['LOCAL_MD_DIR']
    S3_MD_BUCKET = os.environ['S3_MD_BUCKET']

    sync_options = S3Options(source=LOCAL_MD_DIR, destination=S3_MD_BUCKET,
                             include_pattern="*/*.md", exclude_pattern="*.md",
                             dryrun=check_dryrun(args.dryrun))

    sync_with_s3(sync_options)


def update_html(args: Namespace) -> None:
    LOCAL_HTML_DIR = os.environ['LOCAL_HTML_DIR']
    S3_HTML_BUCKET = os.environ['S3_HTML_BUCKET']

    sync_options = S3Options(source=LOCAL_HTML_DIR, destination=S3_HTML_BUCKET,
                             exclude_pattern=".buildinfo.bak",
                             dryrun=check_dryrun(args.dryrun))

    if not check_dryrun(args.dryrun):
        convert_md_to_rst()
        convert_rst_to_html()
        push_html_to_github()

    sync_with_s3(sync_options)


def push_html_to_github() -> None:
    commit_msg = datetime.datetime.now().strftime(
        "[%Y-%m-%d %H:%M:%S]: Update HTML files")

    exit_code = subprocess_run(["./commit_files.sh", commit_msg]).returncode

    if exit_code:
        logging.error("Failed to push html files to github repository")
        exit(1)


def check_dryrun(dryrun: bool | None) -> bool:
    if dryrun is None:
        return True

    return dryrun


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
        help="only convert and sync html files from local to s3 bucket",
        action="store_true")

    parser.add_argument(
        "--markdown-only",
        help="only sync markdown files from local to s3 bucket",
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
