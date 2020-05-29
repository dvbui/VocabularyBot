
f = open("VinceGREWordListRaw.txt", "r")
lines = f.read().split('\n')
f.close()
total = {}
for line in lines:
    words = line.replace("\t", " ").split(' ')
    for word in words:
        total[word.strip()] = ""

g = open("VinceGREWordListFormatted.txt", "w")
for key in total:
    g.write(key+"\n")
g.close()

f = open("WordPowerMadeEasy.txt", "r")
lines = f.read().split('\n')
f.close()
total = {}
for line in lines:
    words = line.replace(", "," ").split(" ")
    for word in words:
        if word.strip().lower().isalpha():
            total[word.strip().lower()] = ""

g = open("WordPowerMadeEasyFormatted.txt", "w")
for key in total:
    g.write(key+"\n")
g.close()