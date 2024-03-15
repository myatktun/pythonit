import os
import pandoc
import re
import sys
from dotenv import load_dotenv
from pandoc.types import *
from subprocess import run as subprocess_run
from sync_files_with_s3 import sync_files


def main(files_to_convert, upload, args):
    load_dotenv()

    dry_run = check_dry_run(args)

    LOCAL_DIR = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']
    INDEX_FILE = f"{LOCAL_DIR}/index.md"

    for i in range(len(files_to_convert)):
        files_to_convert[i] = "/".join([LOCAL_DIR, files_to_convert[i]])

    generate_index(INDEX_FILE)
    generate_html(files_to_convert)

    source = os.environ['PWD'] + "html"
    destination = "s3://notes-html1"

    if upload:
        print("Syncing html files from local to s3 bucket")

    if not upload:
        print("Syncing html files from s3 bucket to local")
        source, destination = destination, source

    sync_files(source, destination, dryrun=dry_run)


def check_dry_run(args):
    if args.dryrun is None:
        return True

    return args.dryrun


def generate_index(index_file):
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


def generate_html(markdown_dir):
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
