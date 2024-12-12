import os
from dotenv import load_dotenv
from .sync_files_with_s3 import _sync_files
from modules.file_converter import convert_md_to_rst, convert_rst_to_html


def sync_html(upload: bool, dryrun=True):
    load_dotenv()

    convert_md_to_rst()
    convert_rst_to_html()

    (source, destination) = _get_sync_dirs(upload)

    _sync_files(source, destination, dryrun=dryrun)


def _get_sync_dirs(upload: bool) -> tuple[str, str]:
    LOCAL_HTML_DIR = os.environ["LOCAL_HTML_DIR"]
    S3_BUCKET = os.environ['S3_HTML_BUCKET']

    if upload:
        print("Syncing html files from local to s3 bucket")
        return (LOCAL_HTML_DIR, S3_BUCKET)

    print("Syncing html files from s3 bucket to local")
    return (S3_BUCKET, LOCAL_HTML_DIR)
