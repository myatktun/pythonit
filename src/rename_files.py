from pathlib import Path
import sys


def main():
    path = sys.argv[1]

    print(f"Renaming files in {path}")
    rename_files(path)


def rename_files(path: str):
    f_count: int = 0

    for f in Path(path).iterdir():
        f_count += f.is_file()

    f_count = len(str(f_count)) + 1

    f_suffix = 0
    curr_fname = ""

    files = sorted(Path(path).iterdir(), key=lambda f: f.name)

    for f in files:
        if not curr_fname or f.stem != curr_fname:
            curr_fname = f.stem
            f_suffix += 1

        splits = f.as_posix().split("/")
        video_name = splits[-2]
        extension = f.suffix
        new_fname = f"{f.parent}/{video_name}_{f_suffix:0{f_count}d}{extension}"
        if new_fname != f.as_posix():
            print(f"Rename: {f.as_posix()} -> {new_fname}")
            f.rename(new_fname)


if __name__ == "__main__":
    main()
