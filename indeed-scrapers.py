from bs4 import BeautifulSoup
import requests
from preprocess import process
import nltk
from nltk import word_tokenize
import json
from random import random
from time import sleep
import re


###################################
#       CODING SECTION            #
###################################

# Global variables that store all skills for the specified job title #
bag_of_skills = {}
bag_of_skills_bigram = {}


# Preprocessing functions #
def generate_url(job_title, job_location):
    # This function generates the url (Indeed's search page) from job_title and job_location
    url_template = "https://www.indeed.ca/jobs?q={}&l={}"
    url = url_template.format(job_title, job_location)
    return url


def collect_job_cards_from_page(html):
    # This function finds and returns the html elements that contain specified keyword
    soup = BeautifulSoup(html, 'html.parser')
    cards = soup.find_all('div', 'slider_container')
    return cards, soup


def extract_job_card_data(card):
    # This function gets the data from the cards that are found from collect_job_cards_from_page function
    post_url = "https://www.indeed.com" + card.parent.get('href')

    print(post_url)

    main_html = request_jobs_from_indeed(post_url)
    if main_html:
        main_soup = BeautifulSoup(main_html, 'html.parser')
    else:
        return None
    main_card = main_soup.find(id="jobDescriptionText")
    if main_card:
        target_list = pick_skill(main_card)
    else:
        return None
    processed_target_list = []
    for target in target_list:
        processed_target_list.append(process(target))

    for target in processed_target_list:
        get_skills_stat(target)
        get_skill_stats_bigram(target)


def request_jobs_from_indeed(url):
    # This function goes to the url and grabs the its content
    response = requests.get(url, allow_redirects=True)
    print(response.status_code)
    if response.status_code == 200:
        return response.content
    else:
        return None


def find_next_page(soup):
    # This function finds if there is next page for the current search page, if not it stops the program
    try:
        pagination = soup.find("a", {"aria-label": "Next"}).get("href")
        return "https://www.indeed.com" + pagination
    except AttributeError:
        return None


# Extract skills functions #
def pick_skill(data):
    # This function find the qualification section in the job posting and grab the text as the raw data

    # Read targeted words from target-words.txt that is created using generate-target-words.py
    with open("target-words.txt", 'r', encoding='utf-8') as list_words:
        target_words = json.load(list_words)

    target_list = []

    for word in target_words:
        for x in data.find_all(string=re.compile(word, re.IGNORECASE)):
            if x.find_parents('li'):
                target_list.append(x.parent.parent)
            else:
                target_ul = x.findNext('ul')
                if target_ul.has_attr('class') and target_ul['class'][0] == 'icl-GlobalFooter-items':
                    pass
                else:
                    target_list.append(target_ul)

    # Remove repetitive targets
    target_list = list(set(target_list))
    return target_list


def get_skills_stat(data):
    # This function counts the number of occurrences for unigram skills list
    text = word_tokenize(data)
    tagged_list = nltk.pos_tag(text)

    for i in range(len(tagged_list)):
        if tagged_list[i][1] == 'NN':
            target_word = tagged_list[i][0]
            if target_word in bag_of_skills:
                bag_of_skills[target_word] = bag_of_skills[target_word] + 1
            else:
                bag_of_skills[target_word] = 1


def get_bigrams(sentence):
    # This function returns bigram skills list
    tokens = nltk.word_tokenize(sentence)
    return zip(tokens, tokens[1:])


def get_skill_stats_bigram(data):
    # This function counts the number of occurrences for bigram skills list
    temp = [' '.join(b) for b in get_bigrams(data)]
    tagged_list = nltk.pos_tag(temp)

    for i in range(len(tagged_list)):
        if tagged_list[i][1] == 'NN' or tagged_list[i][1] == 'NNS':
            target_word = tagged_list[i][0]
            if target_word in bag_of_skills_bigram:
                bag_of_skills_bigram[target_word] = bag_of_skills_bigram[target_word] + 1
            else:
                bag_of_skills_bigram[target_word] = 1


def chose_skills_bigram(list_skills):
    # This function selects the skills that have high enough occurrences from the list of bigram skills (threshold can be changed)
    chosen_skill_list = []

    # Define threshold to pick skills
    bigram_threshold = len(list_skills) * 0.3 / 100

    # Pick skills by browsing the list of bigram skills
    for key, value in list_skills.items():
        if value >= bigram_threshold:
            chosen_skill_list.append(key)
        else:
            break
    return chosen_skill_list


def chose_skills(list_skills):
    # This function selects the skills that have high enough occurrences from the list of unigram skills (threshold can be changed)
    chosen_skill_list = []

    # Define threshold to pick skills
    unigram_threshold = len(list_skills) * 4.5 / 100

    # Pick skills by browsing the list of unigram skills
    for key, value in list_skills.items():
        if value >= unigram_threshold:
            chosen_skill_list.append(key)
        else:
            break
    return chosen_skill_list


# Miscellaneous function #
def sleep_for_random_interval():
    # This function allows the application to get more jobs before Indeed's bot algorithm bans the IP address
    seconds = random() * 10
    sleep(seconds)


# Main function #
def main(job_title, job_location):
    number_jobs = 0
    print("Starting to scrape indeed for `{}` in `{}`".format(job_title, job_location))
    url = generate_url(job_title, job_location)

    # Browsing through the job searching pages and updating
    while True:
        print(url)
        html = request_jobs_from_indeed(url)
        if not html:
            break
        cards, soup = collect_job_cards_from_page(html)
        for card in cards:
            extract_job_card_data(card)
            number_jobs += 1
        sleep_for_random_interval()
        url = find_next_page(soup)
        if not url:
            break

    # Save lists of skills into data_collection folder
    with open("data_collection/" + title + "-" + job_location + "-skills.txt", 'w') as f:
        json.dump(bag_of_skills, f)
    with open("data_collection/" + title + "-" + job_location + "-skills-bigram.txt", 'w') as f:
        json.dump(bag_of_skills_bigram, f)

    print('Finished collecting {:,d} job postings.'.format(number_jobs))

    # Choose skills from bigram list of skills
    sorted_list_bigram = dict(sorted(bag_of_skills_bigram.items(), key=lambda item: item[1], reverse=True))
    chosen_skills_bigram = chose_skills_bigram(sorted_list_bigram)

    # Save list of chosen bigram skills into data_collection folder
    with open("data_collection/" + title + "-" + job_location + "-chosen-skills-bigram.txt", 'w') as f:
        json.dump(chosen_skills_bigram, f)
    print('Most common skills from bigram skills list: \n' + str(chosen_skills_bigram))

    # Create the list of word from skills of the bigram list to remove according skill in unigram list of skill
    remove_skills = []
    for skill in chosen_skills_bigram:
        first_word, second_word = skill.split(' ')
        remove_skills.append(first_word)
        remove_skills.append(second_word)
    remove_skills = list(set(remove_skills))

    copy_bag_of_skills = dict(bag_of_skills)
    for remove_skill in remove_skills:
        for key, value in bag_of_skills.items():
            if key == remove_skill:
                del copy_bag_of_skills[key]

    # Choose skills from unigram list of skills that has been sorted
    sorted_list = dict(sorted(copy_bag_of_skills.items(), key=lambda item: item[1], reverse=True))
    chosen_skills = chose_skills(sorted_list)

    # Save list of chosen unigram skills into data_collection folder
    with open("data_collection/" + title + "-" + job_location + "-chosen-skills.txt", 'w') as f:
        json.dump(chosen_skills, f)
    print('Most common skills from single skills list: \n' + str(chosen_skills))


###################################
#       RUNNING & TESTING         #
###################################


if __name__ == '__main__':
    # job search settings
    title = 'Back End Developer'
    location = ''
    main(title, location)
