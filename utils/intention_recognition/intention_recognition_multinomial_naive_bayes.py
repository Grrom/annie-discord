from nltk.stem.lancaster import LancasterStemmer
import random
import tensorflow
import tflearn
import numpy
import json
import nltk


stemmer = LancasterStemmer()


with open("intention.json") as file:
    dataset = json.load(file)

intentions = list(set([a["intention"] for a in dataset]))


corpus_words = {}
intention_words = {}

for intention in intentions:
    intention_words[intention] = []

for data in dataset:
    for phrase in data["phrases"]:
        for word in nltk.word_tokenize(phrase):
            if word not in ["?", "'s"]:
                stemmed_word = stemmer.stem(word.lower())
                if stemmed_word not in corpus_words:
                    corpus_words[stemmed_word] = 1
                else:
                    corpus_words[stemmed_word] += 1
                intention_words[data["intention"]].extend([stemmed_word])


def score_intentions(message, intention):
    score = 0
    for word in nltk.word_tokenize(message):
        if stemmer.stem(word.lower()) in intention_words[intention]:
            score += (1 / corpus_words[stemmer.stem(word.lower())])
    return score


intention_scores = {}
for intention in intention_words:
    intention_scores[intention] = score_intentions(
        "handle me the sauce senpai", intention)

print("\n\n\n\nIntention scores: ")
print(intention_scores)


print("\nThe user's intention is: ")
print(sorted(intention_scores.items(),
      key=lambda item: item[1], reverse=True)[0])
print("\n\n")
