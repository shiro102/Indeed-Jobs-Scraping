from dictances import bhattacharyya_coefficient
import json

# This file calculates the bhattacharyya coefficient for two specific jobs

# Variables that can be changed for testing
first_job_name = 'Python Developer'
second_job_name = 'UI designer'
location = ''

# Accessing files in the data_collection folder, please check naming if program does not run
with open("data_collection/" + first_job_name + "-" + location + "-skills-bigram.txt", 'r', encoding='utf-8') as list_words:
    first_job_bigram = json.load(list_words)
with open("data_collection/" + second_job_name + "-" + location + "-skills-bigram.txt", 'r', encoding='utf-8') as list_words:
    second_job_bigram = json.load(list_words)

# Printing result
print('Result for Bhattacharyya coefficient between ' + first_job_name + ' and ' + second_job_name + ' : ' +
      str(bhattacharyya_coefficient(first_job_bigram, second_job_bigram)))


