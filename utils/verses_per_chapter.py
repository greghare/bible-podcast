import json 
 
raw_file = open('verses_per_chapter.raw', 'r')
lines = raw_file.readlines()
 
bible = {}
 
count = 0
last_book = ""

for line in lines:
    count += 1
    split1 = line.strip().split(" - ")
    book = split1[0]
    split2 = split1[1].split(" _ ")
    chapter = split2[0]
    verses = split2[1]

    if book != last_book:
        bible[book] = {}
        last_book = book
    
    bible[book][chapter] = int(verses)

    print("Book: " + book + " Chapter: " + chapter + " Verses: " + verses)

json_object = json.dumps(bible, indent = 4) 
print(json_object)

with open("verses_per_chapter.json", "w") as outfile:
    outfile.write(json_object)