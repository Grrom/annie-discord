import random
import tensorflow
import tflearn
import numpy
import json
import nltk
import pickle


with open("intention.json") as file:
    intentions = json.load(file)

words = []
labels = []
docs_x = []
docs_y = []


for intention in intentions:
    for phrase in intention["phrases"]:
        tokenized = nltk.word_tokenize(phrase)
        words.extend(tokenized)
        docs_x.append(tokenized)
        docs_y.append(intention["intention"])

    if intention["intention"] not in labels:
        labels.append(intention["intention"])

words = [w.lower() for w in words]
words = sorted(list(set(words)))

labels = sorted(labels)


training = []
output = []

out_empty = [0 for _ in range(len(intentions))]

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

with open("intentions.pickle", "wb") as f:
    pickle.dump((words, labels, training, output), f)


net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 20)
net = tflearn.fully_connected(net, 20)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)
model.fit(training, output, n_epoch=1000, batch_size=8, show_metric=True)
model.save("intention_recognition.tflearn")
