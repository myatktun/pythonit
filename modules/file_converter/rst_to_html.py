from subprocess import run as subprocess_run
import os


def convert_rst_to_html():
    # use "make" to generate html with Sphinx
    command = ["make", "-C", os.environ["MAKE_DIRECTORY"], "html"]

    subprocess_run(command)
