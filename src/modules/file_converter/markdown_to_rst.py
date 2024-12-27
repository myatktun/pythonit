from dotenv import load_dotenv
import logging
import os
from pathlib import Path
import re

load_dotenv()

SECTION_HEADER_PREFIX = "## "
RST_DIR = os.environ['RST_DIR']

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def convert_md_to_rst(source: str) -> None:

    for file_path in Path(source).rglob("*"):
        if file_path.is_dir():
            continue

        logging.info(f'Starting processing for file "{file_path}"')
        if file_path.name == "index.md":
            _process_index_file(file_path.absolute().as_posix())
        else:
            _process_md(file_path)
        logging.info(f'Completed processing for file "{file_path}"')

    logging.info('Completed converting markdown files to rst')


def _process_index_file(source: str) -> None:
    index_file_template = """Notes
=====

.. toctree::
   :maxdepth: 1
   :caption: Contents:

"""

    index_list: list[str] = _generate_index_list(source)

    with open(f"{RST_DIR}/index.rst", "w") as f:
        f.write(index_file_template)
        for index in index_list:
            f.write("   " + index + '\n')


def _generate_index_list(source: str) -> list[str]:
    index_list = []

    with open(source, "r") as f:
        for line in f:
            pattern = r"\[(.+?)\]"
            match = re.search(pattern, line)
            if match:
                index_list.append(match.group(1))

    index_list.sort()

    return index_list


def _process_md(md_file) -> None:
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
                line = _generate_header(line, is_main_header=True)

            # main content
            if re.match(prefixes["main_content"], line):
                match = re.search(content_regex, line)
                if match is not None:
                    line = f"{main_content_num}. `{match.group(1)}`_\n"
                    main_content_num += 1

            # section header
            if line.startswith(SECTION_HEADER_PREFIX):
                line = _generate_header(line)

            # section sub header
            if line.startswith(prefixes["section_sub_header"]):
                line = _generate_section_sub_header(line)

            # section content
            if line.startswith(prefixes["section_content"]):
                match = re.findall(content_regex, line)
                line = _generate_section_content(match)

            # process each bullet point line
            # avoid section content line and code block line
            if not re.match(r"^\*\s`.*`_", line) and not in_code_block and \
                    re.match(r"^\s*(?:[-*>`])\s*", line):
                line = _generate_bullet_line(line)

            # "back to top"
            if line.startswith(prefixes["back_to_top"]):
                line = _generate_back_to_top(line)

            # code block
            if in_code_block:
                # need to line up with "c" in ".. code-block::"
                line = (" " * len(".. ")) + line

            # code block
            if re.match(prefixes["code_block_start"], line):
                in_code_block = True

                if re.match(prefixes["code_block_end"], line):
                    in_code_block = False

                line = _generate_code_block(line)

            temp.write(line)


def _generate_header(line, is_main_header=False) -> str:
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
        line = _generate_section_line("=", len(header)) + '\n' + \
            header + '\n' + \
            _generate_section_line("=", len(header)) + '\n'
    else:
        line = header + '\n' + \
            _generate_section_line('=', len(header)) + '\n'

    return line


def _generate_section_sub_header(line) -> str:
    '''
    Format:
    Section Sub Header
    ------------------
    '''

    section_sub_header_regex = r"\*\*(.*?)\*\*"

    match = re.search(section_sub_header_regex, line)
    if match is not None:
        header = match.group(1)
        line = f"\n{header}\n{_generate_section_line('-', len(header))}\n"

    return line


def _generate_section_content(content_list) -> str:
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


def _generate_bullet_line(line) -> str:
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


def _generate_back_to_top(line) -> str:
    '''
    Format:
    `back to top <#main-header>`_
    '''

    match = re.search(r"\((#[^)]+)\)", line)

    if match:
        main_header = match.group(1)
        line = f"`back to top <{main_header}>`_\n"

    return line


def _generate_code_block(line) -> str:
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


def _generate_section_line(format_str, length) -> str:
    return format_str * length
