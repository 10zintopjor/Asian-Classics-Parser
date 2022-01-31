import re


with open("test.txt") as f:
    text = f.read()

text = text.strip("\n")

base = re.split("\n\n\n",text)

for txt in base:
    txt=txt.replace("[?]","")
    imgnum = re.search("^\[(.*)\](.*)",txt,re.DOTALL)
    print(imgnum.group(1))
    print("******************")
