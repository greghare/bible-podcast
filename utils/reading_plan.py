from concurrent.futures.process import BrokenProcessPool
import json 
from datetime import datetime

curYear = datetime.now().year
 
# File downloaded from https://bibleplan.org/plans/bible-in-a-year/
# Expand all, and copy and paste to file
raw_file = open('reading_plan.raw', 'r')
lines = raw_file.readlines()

# Read verses_per_chapter.json
f = open('verses_per_chapter.json')
VPC = json.load(f) # Verses Per Chapter

# Create a new reading plan dictionary
reading_plan = {}

# Loop through each line of raw reading plan
for line in lines:

    # Remove whitespace
    line = line.strip()

    # Switching months
    if str(curYear) in line:
        continue

    # Skip over days with no reading
    if "no reading" in line:
        continue

    # Split lines in the falling format to retrieve date and list of readings
    # Sunday December 11th:	Titus 2 | Titus 3 | Philemon 1 | Hebrews 1 | Hebrews 2
    part = line.split(":")
    date = part[0].strip()
    readings = part[1].strip().split(" | ")

    # Split date into Day of week, Month, Day of month
    date = date.split();

    # Cleanup day of month, removing "st", "nd", "rd", "th" endings
    date[2] = date[2].strip("st").strip("nd").strip("rd").strip("th")

    day = date[1] + " " + date[2]
    print(day)

    # Create a dictionary object for the current day
    plan_for_day = {}
    reading_plan[day] = {}

    # Keep track of the prev_book, to know when to combine readings
    prev_book = ""

    # Loop through each reading and add book/chapters to plan_for_day dictionary
    for reading in readings:
        part = reading.rsplit(" ", 1)
        book = part[0]
        chapter = part[1]

        if book == prev_book:
            plan_for_day[book].append(int(chapter))
        else:
            plan_for_day[book] = [] 
            plan_for_day[book].append(int(chapter))

            prev_book = book

    print(plan_for_day)

    # Combine chapters like Genesis 1, Genesis 2 and Genesis 3 into
    # Genesis 1-3
    reading = ""
    verse_count = 0
    first = True
    for book in plan_for_day:

        if first:
            first = False
        else:
            reading += ', '

        chapters = plan_for_day[book]

        # Get verse count for day, to stay inside API agreement of 500
        for chapter in chapters:
            verse_count += VPC[book][str(chapter)]

        if len(chapters) > 1:
            
            reading += book + " " + str(min(plan_for_day[book])) + "-" + str(max(plan_for_day[book]))
        else:
            reading += book + " " + str(chapters[0])
        
    reading_plan[day]["reading"] = reading
    reading_plan[day]["verse_count"] = verse_count

json_object = json.dumps(reading_plan, indent = 4) 

with open("../reading_plan.json", "w") as outfile:
    outfile.write(json_object)