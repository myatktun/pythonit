import os
import re
import logging
from dotenv import load_dotenv

load_dotenv()

MD_DIR = os.environ['MD_DIR']
SECTION_HEADER_PREFIX = "## "
RST_DIR = os.environ['RST_DIR']

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def process_code_block(line):
    '''
    Format:
    .. code-block:: language

       code
    '''

    def replace(match):
        leading_spaces = match.group(1)
        language = match.group(2)

        if not language:
            return ""

        return f"{leading_spaces}.. code-block:: {language}\n"

    line = re.sub(r"^(\s*)```(\w*)$", replace, line)

    return line


def generate_back_to_top(line):
    '''
    Format:
    `back to top <#main-header>`_
    '''

    match = re.search(r"\((#[^)]+)\)", line)

    if match:
        main_header = match.group(1)
        line = f"`back to top <{main_header}>`_\n"

    return line


def process_bullet_line(line):
    # change starting '-' to '*', '>+' to '-', and '>' to whitespace
    # add extra backticks if line contains word with backticks
    def replace(m: re.Match[str]):
        if m.group(2):  # - or >+ or >
            if m.group(2) == ">":
                return f"{m.group(1)}  "
            elif m.group(2) == ">+":
                return f"{m.group(1)}- "
            return f"{m.group(1)}* "
        elif m.group(4):  # backticks
            return f"``{m.group(4)}``"

        return m.group(0)

    line = re.sub(r"^(\s*)(-|\>\+|\>)\s*|(>\+)|`([^`]*)`", replace, line)

    return line


def generate_section_content(content_list):
    '''
    Format:
    * `content1`_ , `content2`_
    '''

    line = "* "
    idx = 0

    while idx < len(content_list):
        line += f"`{content_list[idx]}`_"
        if idx != len(content_list) - 1:
            line += ", "
        idx += 1

    line += '\n'
    return line


def generate_section_sub_header(line):
    '''
    Format:
    Section Sub Header
    ------------------
    '''

    section_sub_header_regex = r"\*\*(.*?)\*\*"

    match = re.search(section_sub_header_regex, line)
    if match is not None:
        header = match.group(1)
        line = '\n' + header + '\n' + generate_section_line('-', len(header)) \
            + '\n'

    return line


def generate_header(line, is_main_header=False):
    '''
    Format:
    ===========
    Main Header
    ===========

    Format:
    Section Header
    ==============
    '''

    header = line.split(' ', maxsplit=1)[1].strip()
    if is_main_header:
        line = generate_section_line("=", len(header)) + '\n' + \
            header + '\n' + \
            generate_section_line("=", len(header)) + '\n'
    else:
        line = header + '\n' + \
            generate_section_line('=', len(header)) + '\n'

    return line


def generate_section_line(format_str, length):
    return format_str * length


def process_md(md_file):
    prefixes = {
        "main_content": r"^\d+.*$",
        "section_content": "* [",
        "section_sub_header": "* **",
        "back_to_top": "##### ",
        "code_block_start": r"^\s*```\w*$",
        "code_block_end": r"^\s*```$"
    }

    content_regex = r"\[(.*?)\]"
    in_code_block = False

    rst_file = os.path.join(RST_DIR, os.path.splitext(
        os.path.basename(md_file))[0] + '.rst')

    with open(md_file, "r") as original, open(rst_file, "w+") as temp:

        main_content_num = 1

        for line_num, line in enumerate(original):
            # main header, overline and underline
            if line_num == 0:
                line = generate_header(line, is_main_header=True)

            # main content
            if re.match(prefixes["main_content"], line):
                match = re.search(content_regex, line)
                if match is not None:
                    line = f"{main_content_num}. `{match.group(1)}`_\n"
                    main_content_num += 1

            # section header
            if line.startswith(SECTION_HEADER_PREFIX):
                line = generate_header(line)

            # section sub header
            if line.startswith(prefixes["section_sub_header"]):
                line = generate_section_sub_header(line)

            # section content
            if line.startswith(prefixes["section_content"]):
                match = re.findall(content_regex, line)
                line = generate_section_content(match)

            # process each bullet point line
            # avoid section content line and code block line
            if not re.match(r"^\*\s`.*`_", line) and not in_code_block and \
                    re.match(r"^\s*(?:[-*>`])\s*", line):
                line = process_bullet_line(line)

            # "back to top"
            if line.startswith(prefixes["back_to_top"]):
                line = generate_back_to_top(line)

            # code block
            if in_code_block:
                # need to line up with "c" in ".. code-block::"
                line = (" " * len(".. ")) + line

            # code block
            if re.match(prefixes["code_block_start"], line):
                in_code_block = True

                if re.match(prefixes["code_block_end"], line):
                    in_code_block = False

                line = process_code_block(line)

            temp.write(line)


def generate_index_list():
    index_list = []

    for path, _, files in os.walk(MD_DIR):
        if path == MD_DIR:
            continue

        for file_name in files:
            if file_name.endswith(".md"):
                index_content = file_name.rsplit('.', maxsplit=1)[0]
                index_list.append(index_content)

    index_list.sort()

    return index_list


def process_index_rst():
    index_file_template = """Notes
=====

.. toctree::
   :maxdepth: 1
   :caption: Contents:

"""

    logging.info(f'Starting processing for file "index.md"')

    index_list = generate_index_list()

    with open(f"{RST_DIR}/index.rst", "w") as f:
        f.write(index_file_template)
        for index in index_list:
            f.write("   " + index + '\n')

    logging.info(f'Completed processing for file "index.md"')


def convert_md_to_rst():

    process_index_rst()

    for path, _, files in os.walk(MD_DIR):
        if path == MD_DIR:
            continue

        for file_name in files:
            if file_name.endswith(".md"):
                logging.info(f'Starting processing for file "{file_name}"')
                file = os.path.join(path, file_name)
                process_md(file)
                logging.info(f'Completed processing for file "{file_name}"')

    logging.info('Completed converting markdown files to rst')
