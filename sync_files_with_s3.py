import subprocess
import os
import argparse
from dotenv import load_dotenv


def checkDryRun(args):
    if args.dryrun is None:
        return True

    return args.dryrun


def getLastModifiedTimes(localDir, s3Bucket):
    command1 = f"find {localDir} -type f -exec stat -c \"%y %n\" {{}} + | sort -r | head -n 1 | awk '{{print $1 \" \" $2}}'"
    command2 = f"aws s3 ls {s3Bucket} --recursive | sort | tail -n 1 | awk '{{print $1 \" \" $2}}'"

    localTime = subprocess.run(command1, stdout=subprocess.PIPE, shell=True).stdout.decode("utf-8")
    s3Time = subprocess.run(command2, stdout=subprocess.PIPE, shell=True).stdout.decode("utf-8")

    return (localTime, s3Time)


def createArgumentParser():
    parser = argparse.ArgumentParser("Sync note files between local directory and s3 bucket")
    parser.add_argument("--dryrun", help="sync files or only dryrun (default: dryrun)", action=argparse.BooleanOptionalAction)

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--download", help="sync files from s3 bucket to local", action="store_true")
    group.add_argument("--upload", help="sync files from local to s3 bucket", action="store_true")

    return parser.parse_args()


def getSyncDirs(localDir, s3Bucket, args):
    if (args.download):
        print("Syncing files from s3 bucket to local")
        return (s3Bucket, localDir)
    elif (args.upload):
        print("Syncing files from local to s3 bucket")
        return (localDir, s3Bucket)

    localTime, s3Time = getLastModifiedTimes(localDir, s3Bucket)

    if (localTime < s3Time):
        print("Syncing files from s3 bucket to local")
        return (s3Bucket, localDir)

    print("Syncing files from local to s3 bucket")
    return (localDir, s3Bucket)


def main():

    load_dotenv()

    args = createArgumentParser()
    dryRun = checkDryRun(args)

    localDir = os.environ['HOME'] + "/" + os.environ['LOCAL_DIR']
    s3Bucket = os.environ['S3_BUCKET']

    source, destination = getSyncDirs(localDir, s3Bucket, args)

    excludePattern = "*.md"
    includePattern = "*/*.md"

    command = ["aws", "s3", "sync", source, destination, "--exclude", excludePattern, "--include", includePattern, "--size-only"]

    if (dryRun):
        command.append("--dryrun")

    subprocess.run(command)


if __name__ == "__main__":

    main()
