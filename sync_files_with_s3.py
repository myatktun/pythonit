import subprocess
import sys
import os

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

def setSyncDirs():
    localDir = f"{HOME}/Documents/Vimwiki"
    s3Bucket = "s3://projectxnotes"
    if "--download" in sys.argv:
        print("Syncing files from s3 bucket to local")
        return (s3Bucket, localDir)

    print("Syncing files from local to s3 bucket")
    return (localDir, s3Bucket)

dryRun = checkDryRun()
source, destination = setSyncDirs()
command = ["aws", "s3", "sync", source, destination, "--exclude", excludePattern, "--include", includePattern]

if (dryRun):
    command.append("--dryrun")

subprocess.run(command)
