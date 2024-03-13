import pandoc
from pandoc.types import *
import glob
import re
from dotenv import load_dotenv
import os

load_dotenv()

LOCAL_DIR = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']
MARKDOWN_DIR = f"{LOCAL_DIR}/*/*.md"
INDEX_FILE = f"{LOCAL_DIR}/index.md"

with open(INDEX_FILE, "r", encoding="utf-8") as input_file:
    html_file = f"{re.split('[/ .]', INDEX_FILE)[-2]}.html"
    text = input_file.read()
    doc = pandoc.read(text, format="markdown_mmd")

    for elt in pandoc.iter(doc[1]):
        if isinstance(elt, Link):
            elt[-1] = (f"{elt[-1][0]}.html", '')

    html = pandoc.write(
        doc, format="html", file=f"html/{html_file}",
        options=["--template=html/template.html"]
    )

for file in glob.glob(MARKDOWN_DIR):
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
