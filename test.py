import os

for root, dirs, files in sorted(os.walk("./temp")):
    if "RTF" in dirs:
        dirs.remove("RTF")
    for file in files:
        print(f"Dealing with file {root}/{file}")