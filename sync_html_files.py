import os
from dotenv import load_dotenv
from markdown_to_html import convert_md_to_html
from sync_files_with_s3 import sync_files


def sync_html(md_files: list[str], *, dryrun=True):
    load_dotenv()
    upload = check_upload(md_files[0])

    files_to_convert = ["/".join(f.rsplit('/', 2)[-2:]) for f in md_files]

    LOCAL_DIR = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']

    files_to_convert = ["/".join([LOCAL_DIR, f]) for f in files_to_convert]
    convert_md_to_html(files_to_convert)

    (source, destination) = get_sync_dirs(upload)

    output = sync_files(source, destination, dryrun=dryrun)

    print(output)


def get_sync_dirs(upload: bool) -> tuple[str, str]:
    LOCAL_HTML_DIR = os.environ['PWD'] + "html"
    S3_BUCKET = os.environ['S3_HTML_BUCKET']

    if upload:
        print("Syncing html files from local to s3 bucket")
        return (LOCAL_HTML_DIR, S3_BUCKET)

    print("Syncing html files from s3 bucket to local")
    return (S3_BUCKET, LOCAL_HTML_DIR)


def check_upload(f: str) -> bool:
    return f.split(':', 1)[0].split(' ')[-1].lower() == "upload"
