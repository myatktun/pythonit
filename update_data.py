import argparse
from sync_files import sync_markdown, sync_html, sync_templates


def main():
    args = create_argument_parser()
    dryrun = check_dry_run(args)

    if (args.templates_only):
        sync_templates(args, dryrun=dryrun)

    md_files = sync_markdown(args, dryrun=dryrun)
    sync_html(md_files, dryrun=dryrun)


def check_dry_run(args) -> bool:
    if args.dryrun is None:
        return True

    return args.dryrun


def create_argument_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        "Sync files between local directory and s3 bucket")

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
