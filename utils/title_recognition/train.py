import random
import tensorflow
import tflearn
import numpy
import json
import nltk
import pickle


with open("anime_titles.json") as file:
    animes = json.load(file)

words = []
labels = []
docs_x = []
docs_y = []


for anime in animes:
    for alternative_title in anime["alternative"]:
        tokenized = nltk.word_tokenize(alternative_title)
        words.extend(tokenized)
        docs_x.append(tokenized)
        docs_y.append(anime["title"])

    if anime["title"] not in labels:
        labels.append(anime["title"])

words = [w.lower() for w in words]
words = sorted(list(set(words)))

labels = sorted(labels)


training = []
output = []

out_empty = [0 for _ in range(len(animes))]

for x, doc in enumerate(docs_x):
    bag = []
    _words = [w.lower() for w in doc]

    for w in words:
        if w in _words:
            bag.append(1)
        else:
            bag.append(0)

    output_row = out_empty[:]
    output_row[labels.index(docs_y[x])] = 1
    training.append(bag)
    output.append(output_row)

training = numpy.array(training)
output = numpy.array(output)

print("\nwords")
print(words)
print("\ndocs x")
print(docs_x)
print("\ndocs y")
print(docs_y)
print("\n training")
print(training)
print("\n output")
print(output)

with open("anime_titles.pickle", "wb") as f:
    pickle.dump((words, labels, training, output), f)


net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 50)
net = tflearn.fully_connected(net, 50)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)
model.fit(training, output, n_epoch=500, batch_size=8, show_metric=True)
model.save("title_recognition.tflearn")
