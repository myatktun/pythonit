import os
from subprocess import run as subprocess_run
import pandoc
import re
import sys
from dotenv import load_dotenv
from pandoc.types import *
from .markdown_to_rst import convert_md_to_rst


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

        os.makedirs(f"/tmp/html", exist_ok=True)
        pandoc.write(doc, format="html", file=f"/tmp/html/{html_file}",
                     options=["--template=templates/template.html",
                              "--standalone", "--metadata", "title=Notes"])


def generate_html(markdown_dir: list[str]):
    for file in markdown_dir:
        with open(file, "r", encoding="utf-8") as input_file:
            [category, html_file] = re.split('[/ .]', file)[-3:-1]
            title = html_file
            html_file = "".join([html_file, ".html"])
            os.makedirs(f"/tmp/html/{category}", exist_ok=True)
            with open(f"/tmp/html/{category}/{html_file}", "w",
                      encoding="utf-8") as output_file:
                text = input_file.read()
                doc = pandoc.read(text, format="markdown_mmd")
                html = pandoc.write(doc, format="html", options=[
                                    "--template=templates/template.html",
                                    "--standalone", "--mathjax",
                                    "--metadata", f"title={title}"])
                output_file.write(html)


def convert_with_pandoc(files_to_convert: list[str]):
    LOCAL_DIR = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']
    INDEX_FILE = f"{LOCAL_DIR}/index.md"

    generate_index(INDEX_FILE)
    generate_html(files_to_convert)


def convert_with_sphinx():
    convert_md_to_rst()

    # use "make" to generate html with Sphinx
    command = ["make", "-C", os.environ["MAKE_DIRECTORY"], "html"]

    subprocess_run(command)


def convert_md_to_html(files_to_convert: list[str]):
    load_dotenv()

    convert_with_sphinx()
