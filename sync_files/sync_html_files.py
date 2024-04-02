import os
from dotenv import load_dotenv
from .markdown_to_html import convert_md_to_html
from .sync_files_with_s3 import sync_files


def sync_html(md_files: tuple[bool, list[str]], *, dryrun=True):
    load_dotenv()

    upload = md_files[0]

    files_to_convert = ["/".join(f.rsplit('/', 2)[-2:]) for f in md_files[1]]

    LOCAL_DIR = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']

    files_to_convert = ["/".join([LOCAL_DIR, f]) for f in files_to_convert]
    convert_md_to_html(files_to_convert)

    (source, destination) = get_sync_dirs(upload)

    sync_files(source, destination, dryrun=dryrun)


def get_sync_dirs(upload: bool) -> tuple[str, str]:
    LOCAL_HTML_DIR = "/tmp/html"
    S3_BUCKET = os.environ['S3_HTML_BUCKET']

    if upload:
        print("Syncing html files from local to s3 bucket")
        return (LOCAL_HTML_DIR, S3_BUCKET)

    print("Syncing html files from s3 bucket to local")
    return (S3_BUCKET, LOCAL_HTML_DIR)
