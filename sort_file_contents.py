import os
from dotenv import load_dotenv

load_dotenv()

HOME = os.environ['HOME']
LOCAL_DIR = os.environ['LOCAL_DIR']

f = open(f"{HOME}/{LOCAL_DIR}/index.md", "r+")

print("Reading file contents")
text = f.read()
header = text.split('\n')[0]

fileNames = text.split('\n')[2:-1]
fileNames.sort(key=lambda x: (r'\[(.*?)\]', x))
print(f"{len(fileNames)} file contents have been sorted")

sortedContents = "\n"
sortedContents = header + '\n\n' + sortedContents.join(fileNames)

print("Writing sorted file contents")
f.seek(0)
f.write(sortedContents)
f.close()
