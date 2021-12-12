import json

# This file generate the list of targeted words that can be the signals to find qualification section (or required skills) in a job posting #

list_of_words = ['Requirement', 'Required', 'Skill', 'Knowledge', 'Qualification', 'Qualified', 'Preference',
                 'Preferred', 'Experience', 'Need', 'Needed', 'Expected', 'Looking for', 'Must have']

# Save the list into target-words.txt
with open("target-words.txt", 'w') as f:
    json.dump(list(set(list_of_words)), f)
