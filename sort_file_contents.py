import os

HOME = os.environ['HOME']

f = open(f"{os.environ['HOME']}/Documents/Vimwiki/index.md", "r+")

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
