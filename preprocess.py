import re
from nltk.corpus import stopwords


# This file contains the function that is used in indeed-scrapers.py
def process(raw_data):
    # This method process the data and return it

    # Get the list of stop words
    stopWords = set(stopwords.words('english'))

    # Create a list of characters that need to be processed
    boundary_markers = ['!\n\n', '?\n\n', '.\n\n', ':\n\n', '!\n', '?\n', '.\n', ':\n', '!', '?', '.', ':']
    punctuations = [',']
    contractions = ["'s", "'t", "'m", "'ve", "'re", "'ll"]
    contraction_meanings = [" is", " not", " am", " have", " are", " will"]

    data = str(raw_data)

    # Remove all tags
    data = re.sub('<.*?>', ' ', data)
    # Replace contractions
    for contraction in contractions:
        index = contractions.index(contraction)
        data = data.replace(contraction, contraction_meanings[index])

    # Remove boundary markers, special words and punctuations
    for marker in boundary_markers:
        data = data.replace(marker, "\n")
    for punctuation in punctuations:
        data = data.replace(punctuation, "")

    # Remove all number
    data = re.sub("\d", "", data)

    # Convert data to lowercase
    data = data.lower()

    # Remove all special characters
    data = re.sub("[^a-z: \n]", "", data)

    # Remove empty lines
    data = re.sub("\n{2,}", "\n", data)

    # Remove stop words
    for stopWord in stopWords:
        data = re.sub(r"\b%s\b" % stopWord, '', data)

    # Remove extra space
    data = re.sub(" +", " ", data)

    return data
