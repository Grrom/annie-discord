import pickle
import json
import random
import tensorflow
import tflearn
import numpy
import nltk


# with open("utils/intention_recognition/intention.json") as file:
with open("intention.json") as file:
    data = json.load(file)

# with open("utils/intention_recognition/intentions.pickle", "rb") as f:
with open("intentions.pickle", "rb") as f:
    words, labels, training, output = pickle.load(f)

tensorflow.compat.v1.reset_default_graph()

net = tflearn.input_data(shape=[None, len(training[0])])
net = tflearn.fully_connected(net, 20)
net = tflearn.fully_connected(net, 20)
net = tflearn.fully_connected(net, len(output[0]), activation="softmax")
net = tflearn.regression(net)

model = tflearn.DNN(net)
# model.load("utils/intention_recognition/intention_recognition.tflearn")
model.load("intention_recognition.tflearn")


def bag_of_words(s, words):
    bag = [0 for _ in range(len(words))]

    s_words = nltk.word_tokenize(s)
    s_words = [word.lower() for word in s_words]

    for se in s_words:
        for i, w in enumerate(words):
            if w == se:
                bag[i] = 1

    return numpy.array(bag)


def get_intention(inp):
    results = model.predict([bag_of_words(inp, words)])
    results_index = numpy.argmax(results)

    return labels[results_index]


def chat():
    print("Enter message (type quit to stop)!")
    while True:
        inp = input("You: ")
        if inp.lower() == "quit":
            break

        results = model.predict([bag_of_words(inp, words)])
        results_index = numpy.argmax(results)

        if (len(results[results > .5]) == 0):
            print("no accurate prediction")
        else:
            print(labels[results_index])


# chat()
