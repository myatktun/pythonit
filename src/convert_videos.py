import signal
import subprocess
import sys
from types import FunctionType
from pathlib import Path


def handle_sigint(signum, frame):
    sys.exit(0)


def convert_2_mp4(input: str, output: str):
    cmd = [
        "ffmpeg",
        "-i", input,
        "-vf", "scale=1920:1080",
        "-c:v", "libx265",
        "-crf", "18",
        "-preset", "slow",
        "-c:a", "aac",
        "-b:a", "192k",
        output
    ]

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def convert_2_916ratio(input: str, output: str):
    cmd = [
        "ffmpeg",
        "-i", input,
        "-vf", "crop=607:1080:(in_w-607)/2:0,scale=1080:1920,setsar=1",
        "-c:a", "copy",
        output
    ]

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=True)


def process_file(path: Path, func: FunctionType):
    splits = path.as_posix().split(".")
    video_name = splits[0]
    extension = "mp4"
    new_fname = f"{video_name}.{extension}"
    new_fname = new_fname.replace("original", "converted")
    func(path.as_posix(), new_fname)


def main():
    signal.signal(signal.SIGINT, handle_sigint)

    if len(sys.argv) < 2:
        print("Too few arguments", file=sys.stderr)
        exit(1)

    functions = (convert_2_mp4, convert_2_916ratio)

    for i, f in enumerate(functions, start=1):
        print(f"{i}. {f.__name__}")

    choice = int(input("\nChoose a function: "))

    func = functions[choice - 1]

    path = Path(sys.argv[1])

    if path.is_dir():
        files = path.iterdir()

        for f in files:
            process_file(f, func)
    else:
        process_file(path, func)


if __name__ == "__main__":
    main()
