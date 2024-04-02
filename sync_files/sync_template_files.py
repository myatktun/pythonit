import os
import sys
from dotenv import load_dotenv
from .sync_files_with_s3 import sync_files


def sync_templates(args, *, dryrun=True):
    load_dotenv()

    print("Syncing templates files only")

    LOCAL_DIR = "templates"
    S3_BUCKET = os.environ['S3_HTML_BUCKET']
    (source, destination) = get_sync_dirs(LOCAL_DIR, S3_BUCKET, args)

    exclude_pattern = "*/*.html"

    sync_files(source, destination, dryrun=dryrun, exclude=exclude_pattern)

    sys.exit(0)


def get_sync_dirs(local_dir, s3_bucket, args):
    if args.download:
        print("Syncing template files from s3 bucket to local")
        return (s3_bucket, local_dir)

    print("Syncing template files from local to s3 bucket")
    return (local_dir, s3_bucket)
