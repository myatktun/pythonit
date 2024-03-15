import os
import pandoc
import re
import sys
from dotenv import load_dotenv
from pandoc.types import *


def convert_md_to_html(files_to_convert: list[str]):
    load_dotenv()

    LOCAL_DIR = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']
    INDEX_FILE = f"{LOCAL_DIR}/index.md"

    generate_index(INDEX_FILE)
    generate_html(files_to_convert)


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
