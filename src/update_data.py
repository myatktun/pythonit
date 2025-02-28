from modules.sync_files import sync_with_s3, S3Options
from modules.file_converter import md_to_rst

import argparse
from argparse import Namespace
from datetime import datetime
from dotenv import load_dotenv
import logging
import os
from pathlib import Path
from subprocess import run as subprocess_run
import sys


def main():
    load_dotenv()

    args = create_argument_parser()

    setup_logging(args.log)

    if not args.html_only:
        update_markdown(args)

    if not args.markdown_only:
        update_html(args)


def setup_logging(log_level: str) -> None:
    numeric_level = getattr(logging, log_level.upper(), None)

    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {log_level}")

    root_dir = Path(__file__).parent.parent.absolute().as_posix()

    log_dir = f"{root_dir}/logs"

    Path(log_dir).mkdir(exist_ok=True)

    def log_file_name() -> str:
        log_file = datetime.now().strftime('output_%Y%m%d_%H%M%S.log')
        return f"{log_dir}/{log_file}"

    logging.basicConfig(
        level=numeric_level,
        format="[%(asctime)s] (%(name)s) %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file_name(),
                                mode="w", encoding="utf-8")
        ]
    )


def update_markdown(args: Namespace) -> None:
    source = os.environ['LOCAL_MD_DIR']
    destination = os.environ['S3_MD_BUCKET']
    last_modified = True

    if args.download:
        source, destination = destination, source
        last_modified = False

    sync_options = S3Options(source=source, destination=destination,
                             include_pattern="*/*.md",
                             last_modified=last_modified,
                             dryrun=is_dryrun(args.dryrun))

    sync_with_s3(sync_options)


def update_html(args: Namespace) -> None:
    source = os.environ['LOCAL_HTML_DIR']
    destination = os.environ['S3_HTML_BUCKET']
    last_modified = True

    if args.download:
        source, destination = destination, source
        last_modified = False

    sync_options = S3Options(source=source, destination=destination,
                             include_pattern="*.html",
                             last_modified=last_modified,
                             dryrun=is_dryrun(args.dryrun))

    if not is_dryrun(args.dryrun):
        md_to_rst(os.environ['LOCAL_MD_DIR'], os.environ['LOCAL_RST_DIR'])
        push_to_github()

    sync_with_s3(sync_options)


def push_to_github() -> None:
    commit_msg = datetime.now().strftime(
        "[%Y-%m-%d %H:%M:%S]: Update HTML files")

    script_dir = Path(__file__).parent.absolute().as_posix()

    exit_code = subprocess_run(
        [f"{script_dir}/commit_files.sh", commit_msg]).returncode

    if exit_code:
        logging.error("Failed to push html files to github repository")
        exit(1)


def is_dryrun(dryrun: bool | None) -> bool:
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
        "--log",
        help="set log level (default: info)",
        default="info",
        choices=("debug", "info", "error")
    )

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
