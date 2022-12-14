#!/usr/bin/env python3

# Title: PR-to-YT_marks.py
# This script takes in a markers .txt or .csv file exported from Premiere Pro and outputs a text file that can be used to create YouTube markers. Simply copy the text from the output file and paste it into the YouTube description.


import csv
import sys
import os
import pyperclip

# Check to see if the file exists
if os.path.isfile(sys.argv[1]):
    print("File exists")
else:
    print("File does not exist")
    sys.exit()

# Open the file
with open(sys.argv[1], 'r', encoding="utf-16") as csvfile:
    reader = csv.reader(csvfile, delimiter='\t')
    data = list(reader)

# Strip row 1 headings (Marker Name, Description, In, Out, Duration, Marker Type)
del data[0]

# check for empty values or tabs and delete them
for row in data:
    if row[0] == '':
        del row[0]
    if row[1] == '':
        del row[1]
    if row[2] == '':
        del row[2]
    if row[3] == '':
        del row[3]
    if row[4] == '':
        del row[4]
    if row[5] == '':
        del row[5]

# Strip the frame numbers (the last colon and following two digits)
for row in data:
    row[2] = row[2][:-3]
    row[3] = row[3][:-3]
    row[4] = row[4][:-3]

# Strip the hours if they are 00 (the first two digits and following colon. Example: "00:")
for row in data:
    if row[2][:3] == "00:":
        row[2] = row[2][3:]
    if row[3][:3] == "00:":
        row[3] = row[3][3:]
    if row[4][:3] == "00:":
        row[4] = row[4][3:]

# Check to make sure there is a chapter at 00:00
if data[0][2] != "00:00":
    print("There is no chapter at 00:00")
    sys.exit()

# Output the chapter marker before the comment (Example: "01:31:42 See you next Friday")
for row in data:
    print(row[2] + "\t" + row[0])

# Write new .txt file with -YT appended to the name
with open(sys.argv[1][:-4] + "-YT.txt", 'w') as final_file:
    for row in data:
        final_file.write(row[2] + "\t" + row[0] + "\n")

# Copy the text to the clipboard
with open(sys.argv[1][:-4] + "-YT.txt", 'r') as final_file:
    final_file_data = final_file.read()

pyperclip.copy(final_file_data)