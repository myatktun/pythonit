import os
from subprocess import run as subprocess_run
from dotenv import load_dotenv

load_dotenv()


def main():
    file_location = f"{os.environ['HOME']}/{os.environ['LOCAL_DIR']}"
    write_to_file(file_location)


def write_to_file(file_location):
    sorted_contents = get_sorted_contents(file_location)
    print("Writing sorted file contents")
    f = open(f"{file_location}/index.md", "w")
    f.write(sorted_contents)
    f.close()


def get_sorted_contents(file_location):
    file_list = get_file_list(file_location)
    sorted_contents = "# Contents\n\n"
    for file in file_list:
        (category, file_name) = file.split("/")
        file_name = file_name.split(".")[0]
        content = f"* [{file_name}](./{category}/{file_name})\n"
        sorted_contents += content

    return sorted_contents


def get_file_list(file_location):
    files = subprocess_run(
        ["find", f"{file_location}", "-mindepth", "2", "-type", "f"], capture_output=True)

    file_list = files.stdout.decode("utf-8")
    file_list = file_list.strip().split("\n")
    file_list = [f.split("/", 5)[-1] for f in file_list]
    file_list.sort(key=lambda f: f.split("/")[1])
    print(f"{len(file_list)} files found and sorted")

    return file_list


if __name__ == "__main__":
    main()
