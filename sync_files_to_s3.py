import subprocess
import sys
import os

HOME = os.environ['HOME']
localDir = f"{HOME}/Documents/Vimwiki"
s3Bucket = "s3://projectxnotes"
excludePattern = "*.md"
includePattern = "*/*.md"
dryRun = True

if "--dryrun" in sys.argv:
    flag = sys.argv.index("--dryrun") + 1;
    if (flag < len(sys.argv)) and (sys.argv[flag].lower() in ("true", "false")):
        dryRun = sys.argv[flag].lower() == "true"
    else:
        print("!!!Provide a valid value for --dryrun")

command = ["aws", "s3", "sync", localDir, s3Bucket, "--exclude", excludePattern, "--include", includePattern]

if (dryRun):
    command.append("--dryrun")

subprocess.run(command)
