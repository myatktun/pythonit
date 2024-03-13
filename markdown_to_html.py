import pandoc
import glob
import re
from dotenv import load_dotenv
import os

load_dotenv()

LOCAL_DIR = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']
MARKDOWN_DIR = f"{LOCAL_DIR}/CS/BackendEngineering.md"

for file in glob.glob(MARKDOWN_DIR):
    with open(file, "r", encoding="utf-8") as input_file:
        file_name = f"{re.split('[/ .]', file)[-2]}.html"
        # with open(f"html/{file_name}", "w", encoding="utf-8", errors="xmlcharrefreplace") as output_file:
        text = input_file.read()
        doc = pandoc.read(text, format="markdown_strict")
        html = pandoc.write(
            doc, format="html", file=f"html/{file_name}",
            options=["--template=html/template.html"]
        )
