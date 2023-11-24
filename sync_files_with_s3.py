import subprocess, sys, os

HOME = os.environ['HOME']
excludePattern = "*.md"
includePattern = "*/*.md"

def checkDryRun():
    if "--dryrun" in sys.argv:
        dryRunIndex = sys.argv.index("--dryrun") + 1;
        if (dryRunIndex < len(sys.argv)) and (sys.argv[dryRunIndex].lower() in ("true", "false")):
            return sys.argv[dryRunIndex].lower() == "true"

        print("Provide a valid value for --dryrun")
        exit(1)

    return True

def determineTime(localDir, s3Bucket):
    command1 = f"find {localDir} -type f -exec stat -c \"%y %n\" {{}} + | sort -r | head -n 1 | awk '{{print $1 \" \" $2}}'"
    command2 = f"aws s3 ls {s3Bucket} --recursive | sort | tail -n 1 | awk '{{print $1 \" \" $2}}'"
    localTime = subprocess.run(command1, stdout=subprocess.PIPE, shell=True).stdout.decode("utf-8")
    s3Time = subprocess.run(command2, stdout=subprocess.PIPE, shell=True).stdout.decode("utf-8")
    return(localTime, s3Time)

def setSyncDirs():
    localDir = f"{HOME}/Documents/Vimwiki"
    s3Bucket = "s3://projectxnotes"
    localTime, s3Time = determineTime(localDir, s3Bucket)
    if (localTime < s3Time):
        print("Syncing files from s3 bucket to local")
        return (s3Bucket, localDir)

    print("Syncing files from local to s3 bucket")
    return (localDir, s3Bucket)

dryRun = checkDryRun()
source, destination = setSyncDirs()
command = ["aws", "s3", "sync", source, destination, "--exclude", excludePattern, "--include", includePattern, "--size-only"]

if (dryRun):
    command.append("--dryrun")

subprocess.run(command)
