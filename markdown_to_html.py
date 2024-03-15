import os
import pandoc
import re
import sys
from dotenv import load_dotenv
from pandoc.types import *
from sync_files_with_s3 import sync_files


def main(md_files: list[str], *, dryrun=True):
    load_dotenv()

    upload = check_upload(md_files[0])

    files_to_convert: list[str] = [
        "/".join(f.rsplit('/', 2)[-2:]) for f in md_files]

    LOCAL_DIR = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']
    INDEX_FILE = f"{LOCAL_DIR}/index.md"

    files_to_convert = ["/".join([LOCAL_DIR, f]) for f in files_to_convert]

    generate_index(INDEX_FILE)
    generate_html(files_to_convert)

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


def generate_index(index_file: str):
    with open(index_file, "r", encoding="utf-8") as input_file:
        html_file = f"{re.split('[/ .]', index_file)[-2]}.html"
        text = input_file.read()
        doc = pandoc.read(text, format="markdown_mmd")

        if doc is None:
            sys.exit("Pandoc cannot convert file")

        for elt in pandoc.iter(doc[1]):
            if isinstance(elt, Link):
                elt[-1] = (f"{elt[-1][0]}.html", '')

        pandoc.write(doc, format="html", file=f"html/{html_file}",
                     options=["--template=html/template.html"])


def generate_html(markdown_dir: list[str]):
    for file in markdown_dir:
        with open(file, "r", encoding="utf-8") as input_file:
            [category, html_file] = re.split('[/ .]', file)[-3:-1]
            html_file = "".join([html_file, ".html"])
            os.makedirs(f"html/{category}", exist_ok=True)
            with open(f"html/{category}/{html_file}", "w",
                      encoding="utf-8") as output_file:
                text = input_file.read()
                doc = pandoc.read(text, format="markdown_mmd")
                html = pandoc.write(doc, format="html", options=[
                                    "--template=html/template.html"])
                output_file.write(html)
