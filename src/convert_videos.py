import subprocess
import sys
from pathlib import Path


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


def main():
    if len(sys.argv) < 2:
        print("Too few arguments", file=sys.stderr)
        exit(1)

    path = Path(sys.argv[1])
    files = path.iterdir()

    for f in files:
        splits = f.as_posix().split(".")
        video_name = splits[0]
        extension = "mp4"
        new_fname = f"{video_name}.{extension}"
        new_fname = new_fname.replace("original", "converted")
        convert_2_916ratio(f.as_posix(), new_fname)


if __name__ == "__main__":
    main()
